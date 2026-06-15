import logging
from datetime import datetime
from typing import AsyncGenerator

import mlflow
from agents import Agent, Runner, function_tool, set_default_openai_api, set_default_openai_client
from agents.tracing import set_trace_processors
from databricks.sdk import WorkspaceClient
from databricks_openai import AsyncDatabricksOpenAI
from databricks_openai.agents import McpServer
from mlflow.genai.agent_server import invoke, stream
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)
from pydantic import BaseModel
import os
from databricks.vector_search.client import VectorSearchClient


from agent_server.utils import (
    build_mcp_url,
    get_session_id,
    get_user_workspace_client,
    process_agent_stream_events,
)

logger = logging.getLogger(__name__)

# NOTE: this will work for all databricks models OTHER than GPT-OSS, which uses a slightly different API
set_default_openai_client(AsyncDatabricksOpenAI())
set_default_openai_api("chat_completions")
set_trace_processors([])  # only use mlflow for trace processing
mlflow.openai.autolog()
logging.getLogger("mlflow.utils.autologging_utils").setLevel(logging.ERROR)

# ============================================================================
# VECTOR SEARCH CONFIGURATION
# ============================================================================

# Initialize Vector Search client with workspace client for authentication
try:
    vs_client = VectorSearchClient(workspace_client=WorkspaceClient())
    VECTOR_SEARCH_ENABLED = True
    logger.info("Vector Search initialized successfully")
except Exception as e:
    logger.warning(f"Vector Search initialization failed: {e}. App will run without vector search.")
    vs_client = None
    VECTOR_SEARCH_ENABLED = False

# Get configuration from environment variables
VECTOR_SEARCH_ENDPOINT = os.environ.get("VECTOR_SEARCH_ENDPOINT", "mortgage_vector_search_endpoint")
COMPLIANCE_INDEX = os.environ.get("COMPLIANCE_INDEX_NAME", "mortgage.compliance.compliance_rules_vs_index")
PRODUCTS_INDEX = os.environ.get("PRODUCTS_INDEX_NAME", "mortgage.products.lender_products_vs_index")




# ============================================================================
# TYPE DEFINITIONS
# ============================================================================

class MortgageScenario(BaseModel):
    """Type definition for mortgage scenario comparison."""
    annual_rate: float
    years: int


class LoanDetails(BaseModel):
    """Type definition for loan compliance checking."""
    loan_amount: float
    property_value: float
    customer_id: str
    loan_type: str


# ============================================================================
# MORTGAGE CALCULATION TOOLS
# ============================================================================

@function_tool
def calculate_monthly_payment(loan_amount: float, annual_rate: float, years: int) -> dict:
    """Calculate monthly mortgage payment using amortization formula.
    
    Args:
        loan_amount: Principal loan amount in dollars
        annual_rate: Annual interest rate as percentage (e.g., 6.5 for 6.5%)
        years: Loan term in years
        
    Returns:
        Dictionary with monthly payment, total payment, and total interest
    """
    monthly_rate = (annual_rate / 100) / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        monthly_payment = loan_amount / num_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                         ((1 + monthly_rate) ** num_payments - 1)
    
    total_payment = monthly_payment * num_payments
    total_interest = total_payment - loan_amount
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "loan_amount": loan_amount,
        "annual_rate": annual_rate,
        "years": years
    }


@function_tool
def calculate_affordability(annual_income: float, monthly_debts: float, down_payment: float, 
                           annual_rate: float = 7.0, years: int = 30) -> dict:
    """Calculate home affordability based on income and debts.
    
    Uses the 28/36 rule: housing costs should not exceed 28% of gross income,
    and total debt should not exceed 36% of gross income.
    
    Args:
        annual_income: Gross annual income in dollars
        monthly_debts: Existing monthly debt payments
        down_payment: Available down payment amount
        annual_rate: Expected mortgage interest rate (default 7.0%)
        years: Loan term in years (default 30)
        
    Returns:
        Dictionary with maximum home price, loan amount, and monthly payment
    """
    monthly_income = annual_income / 12
    
    # 28% rule for housing costs
    max_housing_payment = monthly_income * 0.28
    
    # 36% rule for total debt
    max_total_debt = monthly_income * 0.36
    max_mortgage_payment = max_total_debt - monthly_debts
    
    # Use the lower of the two limits
    affordable_payment = min(max_housing_payment, max_mortgage_payment)
    
    # Calculate maximum loan amount based on affordable payment
    monthly_rate = (annual_rate / 100) / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        max_loan = affordable_payment * num_payments
    else:
        max_loan = affordable_payment * ((1 + monthly_rate) ** num_payments - 1) / \
                  (monthly_rate * (1 + monthly_rate) ** num_payments)
    
    max_home_price = max_loan + down_payment
    
    return {
        "max_home_price": round(max_home_price, 2),
        "max_loan_amount": round(max_loan, 2),
        "down_payment": down_payment,
        "estimated_monthly_payment": round(affordable_payment, 2),
        "annual_income": annual_income,
        "monthly_debts": monthly_debts,
        "debt_to_income_ratio": round((affordable_payment + monthly_debts) / monthly_income * 100, 2)
    }


@function_tool
def compare_mortgage_scenarios(loan_amount: float, scenarios: list[MortgageScenario]) -> dict:
    """Compare multiple mortgage scenarios with different rates and terms.
    
    Args:
        loan_amount: Principal loan amount
        scenarios: List of mortgage scenarios with 'annual_rate' and 'years' keys
        
    Returns:
        Dictionary with comparison of all scenarios
    """
    results = []
    for i, scenario in enumerate(scenarios, 1):
        calc = calculate_monthly_payment(
            loan_amount, 
            scenario.annual_rate, 
            scenario.years
        )
        calc['scenario'] = f"Scenario {i}: {scenario.years}yr @ {scenario.annual_rate}%"
        results.append(calc)
    
    return {
        "loan_amount": loan_amount,
        "scenarios": results
    }


# ============================================================================
# MORTGAGE ADVISOR AGENT WITH COMPREHENSIVE CAPABILITIES
# ============================================================================

async def init_mcp_server(workspace_client: WorkspaceClient):
    """Initialize MCP server for system.ai tools (includes python_exec for data analysis)."""
    return McpServer(
        url=build_mcp_url("/api/2.0/mcp/functions/system/ai", workspace_client=workspace_client),
        name="system.ai UC function MCP server",
        workspace_client=workspace_client,
    )


# ============================================================================
# AGENT 1: TRIAGE AGENT
# ============================================================================

# ============================================================================
# VECTOR SEARCH TOOLS
# ============================================================================

@function_tool
def search_compliance_rules(query: str, num_results: int = 5) -> str:
    """Search mortgage compliance rules and regulations.
    
    Use this tool to find information about:
    - Credit score requirements
    - Debt-to-income (DTI) ratio limits
    - Loan-to-value (LTV) ratio requirements
    - Income verification rules
    - Employment verification requirements
    - Documentation requirements
    - Regulatory guidelines (FHFA, HUD, CFPB, etc.)
    
    Args:
        query: The compliance question or topic to search for
        num_results: Number of relevant rules to return (default: 5)
    
    Returns:
        A formatted string with relevant compliance rules and requirements
    """
    if not VECTOR_SEARCH_ENABLED:
        return (
            "Vector search is not available. General compliance guidance:\n"
            "- Conventional loans: typically require 620+ credit score, max 43% DTI, 80% LTV\n"
            "- FHA loans: 580+ credit score, 31% front-end / 43% back-end DTI, 96.5% LTV\n"
            "- VA loans: no minimum credit score (lender sets), max 41% DTI, 100% LTV\n"
            "- Jumbo loans: 700+ credit score, max 43% DTI, 80% LTV\n"
            "Please query the mortgage.compliance.rules table directly for detailed requirements."
        )
    
    try:
        results = vs_client.get_index(VECTOR_SEARCH_ENDPOINT, COMPLIANCE_INDEX).similarity_search(
            query_text=query,
            columns=["rule_id", "rule_category", "rule_name", "rule_description", "severity"],
            num_results=num_results
        )
        
        if not results or "result" not in results or "data_array" not in results["result"]:
            return "No compliance rules found for this query."
        
        formatted_results = []
        for row in results["result"]["data_array"]:
            formatted_results.append(
                f"Rule: {row[2]} ({row[0]})\n"
                f"Category: {row[1]}\n"
                f"Description: {row[3]}\n"
                f"Severity: {row[4]}\n"
            )
        
        return "\n---\n".join(formatted_results)
    except Exception as e:
        logger.error(f"Error searching compliance rules: {e}")
        return f"Error searching compliance rules: {str(e)}"


@function_tool
def search_lender_products(query: str, num_results: int = 5) -> str:
    """Search available mortgage products from various lenders.
    
    Use this tool to find information about:
    - Mortgage product types (Conventional, FHA, VA, ARM, Fixed)
    - Interest rates and APR
    - Loan terms (15-year, 20-year, 30-year)
    - Credit score requirements
    - Maximum LTV ratios
    - Lenders and their offerings
    - Product features and benefits
    
    Args:
        query: The product search criteria or question
        num_results: Number of products to return (default: 5)
    
    Returns:
        A formatted string with relevant mortgage products
    """
    if not VECTOR_SEARCH_ENABLED or vs_client is None:
        return (
            "Vector search is not available. General mortgage product information:\n"
            "- Conventional Fixed (30-year): Typically 6.5-7.5% APR, 620+ credit, 80% LTV\n"
            "- FHA Fixed (30-year): Typically 6.0-7.0% APR, 580+ credit, 96.5% LTV\n"
            "- VA Fixed (30-year): Typically 6.0-7.0% APR, varies by lender, 100% LTV\n"
            "- Conventional Fixed (15-year): Typically 5.5-6.5% APR, 620+ credit, 80% LTV\n"
            "Please query the mortgage.products.lender_products table directly for current offerings."
        )
    
    try:
        results = vs_client.get_index(VECTOR_SEARCH_ENDPOINT, PRODUCTS_INDEX).similarity_search(
            query_text=query,
            columns=["product_id", "lender_name", "product_name", "product_type", 
                    "interest_rate", "term_years", "min_credit_score", "max_ltv_ratio"],
            num_results=num_results
        )
        
        if not results or "result" not in results or "data_array" not in results["result"]:
            return "No mortgage products found for this query."
        
        formatted_results = []
        for row in results["result"]["data_array"]:
            formatted_results.append(
                f"Product: {row[2]} ({row[0]})\n"
                f"Lender: {row[1]}\n"
                f"Type: {row[3]}\n"
                f"Interest Rate: {row[4]:.3f}%\n"
                f"Term: {row[5]} years\n"
                f"Min Credit Score: {row[6]}\n"
                f"Max LTV: {row[7]:.1f}%\n"
            )
        
        return "\n---\n".join(formatted_results)
    except Exception as e:
        logger.error(f"Error searching lender products: {e}")
        return f"Error searching lender products: {str(e)}"




def create_triage_agent(mcp_servers: list[McpServer] | None = None) -> Agent:
    """Agent 1: Triage - Greets users, collects basic data, and routes queries."""
    return Agent(
        name="Triage Agent",
        instructions="""You are the first point of contact for mortgage advisory services. Your role is to:

**1. Greet and Build Rapport**
   - Welcome customers warmly and professionally
   - Establish trust and set expectations for the advisory process
   - Explain that you lead a team of specialized mortgage experts

**2. Collect Essential Information**
   Gather key data points to route the request appropriately:
   - Customer's primary goal (purchase, refinance, pre-qualification, general info)
   - Annual income and employment status
   - Monthly debts (car loans, student loans, credit cards)
   - Available down payment
   - Credit score range (if known)
   - Property type and location (if applicable)
   - Veteran status or first-time homebuyer status
   - Timeline for purchase

**3. Route to Specialized Agents**
   Based on the inquiry, delegate to:
   - **Document Processing Agent**: If customer has payslips, bank statements to analyze
   - **Financial Analytics Agent**: For affordability calculations, DTI ratio analysis
   - **Product Matching Agent**: To find suitable mortgage products from lenders
   - **Compliance Agent**: For regulatory questions, eligibility verification
   - **Customer Communication Agent**: To draft final recommendations

**4. Handle Simple Queries Directly**
   For basic questions, provide immediate answers:
   - General mortgage information
   - Simple payment calculations
   - Process overview and timelines
   - Required documentation lists

**Key Behaviors:**
- Be empathetic and patient; buying a home is stressful
- Ask clarifying questions to avoid assumptions
- Explain what each specialist agent will do
- Set realistic expectations about timelines and requirements
- Use the mortgage calculation tools when appropriate for quick estimates

After collecting information, clearly summarize what you've learned and introduce
the next specialist who will help them.""",
        model="databricks-meta-llama-3-3-70b-instruct",
        tools=[
            calculate_monthly_payment,
            calculate_affordability,
        ],
        mcp_servers=mcp_servers or [],
    )


# ============================================================================
# AGENT 2: DOCUMENT PROCESSING AGENT
# ============================================================================

@function_tool
def extract_payslip_data(customer_id: str) -> dict:
    """Extract income data from customer payslips stored in Unity Catalog.
    
    Args:
        customer_id: Customer identifier to look up payslip data
        
    Returns:
        Dictionary with extracted payslip information
    """
    # This would query UC tables in production
    # For demo, return structured data based on sample CSVs
    return {
        "customer_id": customer_id,
        "monthly_gross_income": 8333,
        "ytd_income": 91663,
        "employer": "Tech Corp Inc",
        "employment_type": "Full-time",
        "pay_frequency": "Monthly",
        "deductions": {
            "federal_tax": 1500,
            "state_tax": 500,
            "social_security": 516,
            "medicare": 120,
            "401k": 833
        },
        "net_monthly": 4864,
        "data_source": "payslips.csv"
    }


@function_tool
def extract_bank_statement_data(customer_id: str) -> dict:
    """Extract financial data from customer bank statements stored in Unity Catalog.
    
    Args:
        customer_id: Customer identifier to look up bank statement data
        
    Returns:
        Dictionary with extracted bank statement information
    """
    # This would query UC tables in production
    return {
        "customer_id": customer_id,
        "checking_balance": 12000,
        "savings_balance": 45000,
        "total_liquid_assets": 57000,
        "avg_monthly_income": 8500,
        "avg_monthly_expenses": 4200,
        "recurring_debts_identified": [
            {"description": "Car Payment", "amount": 450},
            {"description": "Student Loan", "amount": 280}
        ],
        "nsf_incidents_last_12mo": 0,
        "large_deposits_flagged": False,
        "data_source": "bank_statements.csv"
    }


def create_document_processing_agent(mcp_servers: list[McpServer] | None = None) -> Agent:
    """Agent 2: Document Processing - Extracts data from payslips and bank statements."""
    return Agent(
        name="Document Processing Agent",
        instructions="""You are a document processing and data extraction specialist for mortgage applications.

**Your Role:**

1. **Extract Income Data from Payslips**
   - Identify gross monthly income
   - Calculate year-to-date earnings
   - Verify employment stability and type
   - Note any gaps in employment
   - Calculate average monthly income for variable earners

2. **Analyze Bank Statements**
   - Verify available funds for down payment and reserves
   - Calculate average monthly deposits and income
   - Identify recurring debts and obligations
   - Flag any suspicious activity (NSF, large irregular deposits)
   - Assess financial behavior and stability

3. **Validate Documentation**
   - Ensure documents are recent (typically last 30-60 days)
   - Verify authenticity markers
   - Check for consistency between different documents
   - Identify missing or incomplete information

4. **Prepare Structured Summary**
   Create a clean data package with:
   - Verified income figures
   - Asset totals and breakdown
   - Debt obligations identified
   - Red flags or concerns
   - Recommendations for additional documentation

**Key Skills:**
- Use extract_payslip_data() and extract_bank_statement_data() tools
- Use system.ai.python_exec via MCP for complex document analysis
- Query Unity Catalog tables for stored documents
- Cross-reference multiple document types for accuracy

**Pass your findings to:**
- Financial Analytics Agent: For DTI calculations and affordability analysis
- Compliance Agent: If any red flags are found

Be thorough and detail-oriented. Inaccurate income/asset data leads to loan denials.""",
        model="databricks-meta-llama-3-3-70b-instruct",
        tools=[
            extract_payslip_data,
            extract_bank_statement_data,
        ],
        mcp_servers=mcp_servers or [],
    )


# ============================================================================
# AGENT 3: FINANCIAL ANALYTICS AGENT
# ============================================================================

@function_tool
def calculate_dti_ratio(monthly_gross_income: float, monthly_debt_payments: float) -> dict:
    """Calculate debt-to-income ratio.
    
    Args:
        monthly_gross_income: Gross monthly income
        monthly_debt_payments: Total monthly debt obligations
        
    Returns:
        Dictionary with DTI ratio and assessment
    """
    dti_ratio = (monthly_debt_payments / monthly_gross_income) * 100
    
    # DTI assessment based on lending standards
    if dti_ratio <= 36:
        assessment = "Excellent - Well within lending guidelines"
        loan_likelihood = "Very High"
    elif dti_ratio <= 43:
        assessment = "Good - Acceptable for most conventional loans"
        loan_likelihood = "High"
    elif dti_ratio <= 50:
        assessment = "Marginal - May need FHA or special programs"
        loan_likelihood = "Moderate"
    else:
        assessment = "High Risk - Likely requires debt reduction"
        loan_likelihood = "Low"
    
    return {
        "dti_ratio": round(dti_ratio, 2),
        "monthly_gross_income": monthly_gross_income,
        "monthly_debt_payments": monthly_debt_payments,
        "assessment": assessment,
        "loan_likelihood": loan_likelihood,
        "front_end_dti_max": 28.0,  # Housing costs only
        "back_end_dti_max": 43.0,   # All debts
        "fha_max_dti": 50.0
    }


@function_tool
def calculate_ltv_ratio(loan_amount: float, property_value: float) -> dict:
    """Calculate loan-to-value ratio.
    
    Args:
        loan_amount: Requested loan amount
        property_value: Appraised property value
        
    Returns:
        Dictionary with LTV ratio and PMI requirements
    """
    ltv_ratio = (loan_amount / property_value) * 100
    down_payment = property_value - loan_amount
    down_payment_pct = (down_payment / property_value) * 100
    
    # PMI requirements
    requires_pmi = ltv_ratio > 80
    estimated_pmi_rate = 0.0
    if ltv_ratio > 95:
        estimated_pmi_rate = 1.0  # 1% annually
    elif ltv_ratio > 90:
        estimated_pmi_rate = 0.75
    elif ltv_ratio > 85:
        estimated_pmi_rate = 0.52
    elif ltv_ratio > 80:
        estimated_pmi_rate = 0.32
    
    monthly_pmi = 0
    if requires_pmi:
        monthly_pmi = (loan_amount * (estimated_pmi_rate / 100)) / 12
    
    return {
        "ltv_ratio": round(ltv_ratio, 2),
        "loan_amount": loan_amount,
        "property_value": property_value,
        "down_payment": round(down_payment, 2),
        "down_payment_percentage": round(down_payment_pct, 2),
        "requires_pmi": requires_pmi,
        "estimated_pmi_monthly": round(monthly_pmi, 2),
        "estimated_pmi_rate_annual": estimated_pmi_rate,
        "conventional_max_ltv": 97.0,
        "fha_max_ltv": 96.5,
        "va_max_ltv": 100.0
    }


def create_financial_analytics_agent(mcp_servers: list[McpServer] | None = None) -> Agent:
    """Agent 3: Financial Analytics - Calculates debt-to-income ratios and maximum borrowing power."""
    return Agent(
        name="Financial Analytics Agent",
        instructions="""You are a financial analytics specialist for mortgage underwriting.

**Your Responsibilities:**

1. **Calculate Debt-to-Income Ratios**
   - Front-end DTI (housing costs only, should be ≤ 28%)
   - Back-end DTI (all debts, should be ≤ 43% for conventional, ≤ 50% for FHA)
   - Use calculate_dti_ratio() tool extensively

2. **Determine Maximum Borrowing Power**
   - Apply 28/36 rule for conventional loans
   - Calculate maximum affordable monthly payment
   - Factor in property taxes, insurance, HOA fees
   - Include PMI if down payment < 20%
   - Use calculate_affordability() for quick estimates

3. **Analyze Loan-to-Value Ratios**
   - Calculate LTV for different down payment scenarios
   - Determine PMI requirements and costs
   - Use calculate_ltv_ratio() tool

4. **Run Scenario Analysis**
   Compare multiple financing options:
   - 15-year vs 30-year terms
   - Different down payment amounts (5%, 10%, 15%, 20%)
   - Conventional vs FHA vs VA loans
   - Fixed vs adjustable rates
   - Impact of paying points to reduce rate

5. **Assess Risk Factors**
   - High DTI ratios
   - Low down payment
   - Limited reserves
   - Variable income
   - Recent employment changes

6. **Generate Recommendations**
   - Optimal loan amount based on income and debts
   - Recommended down payment percentage
   - Loan programs that fit the profile
   - Areas for improvement (pay down debt, increase savings)

**Tools at Your Disposal:**
- calculate_monthly_payment() - For payment calculations
- calculate_affordability() - For max home price estimation
- calculate_dti_ratio() - For DTI analysis
- calculate_ltv_ratio() - For LTV and PMI calculations
- compare_mortgage_scenarios() - For side-by-side comparisons
- system.ai.python_exec via MCP - For complex financial modeling

**Pass your analysis to:**
- Product Matching Agent: To find loans that fit the calculated parameters
- Customer Communication Agent: To explain findings in simple terms

Be precise and conservative. Over-optimistic estimates harm customers.""",
        model="databricks-meta-llama-3-3-70b-instruct",
        tools=[
            calculate_monthly_payment,
            calculate_affordability,
            compare_mortgage_scenarios,
            calculate_dti_ratio,
            calculate_ltv_ratio,
        ],
        mcp_servers=mcp_servers or [],
    )


# ============================================================================
# AGENT 4: PRODUCT MATCHING AGENT
# ============================================================================

def create_product_matching_agent(mcp_servers: list[McpServer] | None = None) -> Agent:
    """Agent 4: Product Matching - Scans lender databases to find matching mortgage products."""
    return Agent(
        name="Product Matching Agent",
        instructions="""You are a mortgage product specialist with access to multiple lender databases.

**Your Mission:**

1. **Search Lender Databases**
   - Query Unity Catalog lender_products table
   - Use search_lender_products() tool with customer criteria
   - Filter by credit score, LTV, loan amount, property type
   - Consider both rate and total cost

2. **Match Customer Profile to Products**
   Based on the customer's:
   - Credit score range
   - Down payment percentage (LTV ratio)
   - Loan amount needed
   - Income and DTI ratio
   - Special status (veteran, first-time buyer, rural property)
   - Property type and occupancy

3. **Compare Product Features**
   Evaluate:
   - Interest rates and APR
   - Loan terms (15-year, 20-year, 30-year)
   - Points and fees
   - PMI requirements and costs
   - Rate lock periods
   - Closing timeline
   - Lender reputation and service quality

4. **Identify Special Programs**
   Look for:
   - **VA Loans**: 0% down for veterans and active military
   - **FHA Loans**: 3.5% down, more flexible credit
   - **USDA Loans**: 0% down for rural properties
   - **Conventional 97**: 3% down for first-time buyers
   - **State/Local Programs**: Down payment assistance, tax credits
   - **Doctor/Professional Loans**: Special terms for high-income professionals

5. **Rank and Recommend**
   Present top 3-5 products with:
   - Monthly payment comparison
   - Total cost over loan life
   - Pros and cons of each
   - Why it matches the customer's needs

**Use These Tools:**
- search_lender_products() - Query product database
- system.ai.python_exec via MCP - Complex filtering and analysis
- Query Unity Catalog tables directly for latest rates

**Pass recommendations to:**
- Compliance Agent: To verify eligibility and regulatory requirements
- Customer Communication Agent: To present options clearly

Stay current with market rates and program changes. Rates fluctuate daily.""",
        model="databricks-meta-llama-3-3-70b-instruct",
        tools=[
            search_lender_products,
        ],
        mcp_servers=mcp_servers or [],
    )


# ============================================================================
# AGENT 5: COMPLIANCE AGENT
# ============================================================================

@function_tool
def check_lending_compliance(loan_details: LoanDetails) -> dict:
    """Check loan against lending regulations and compliance rules.
    
    Args:
        loan_details: LoanDetails object with loan_amount, property_value, customer_id, loan_type
        
    Returns:
        Dictionary with compliance check results
    """
    # This would query Unity Catalog compliance_rules table
    compliance_checks = {
        "ability_to_repay": "PASS",  # ATR rule (Dodd-Frank)
        "hoepa_limits": "PASS",      # High-cost mortgage limits
        "tila_disclosures": "REQUIRED",  # Truth in Lending Act
        "respa_compliance": "REQUIRED",  # Real Estate Settlement Procedures Act
        "ecoa_compliance": "PASS",   # Equal Credit Opportunity Act
        "loan_limits": "PASS",       # Conforming loan limits
        "aml_check": "PASS",         # Anti-Money Laundering
        "ofac_check": "PASS",        # Office of Foreign Assets Control
        "fraud_indicators": "NONE"
    }
    
    issues_found = []
    warnings = []
    
    # Check LTV for loan type
    loan_amount = loan_details.loan_amount
    property_value = loan_details.property_value
    ltv = (loan_amount / property_value) * 100
    
    if ltv > 97 and loan_details.loan_type == "conventional":
        issues_found.append("LTV exceeds conventional loan limits (97%)")
    
    # Check conforming limits (2024)
    if loan_amount > 766550 and loan_details.loan_type == "conventional":
        warnings.append(f"Loan amount ${loan_amount:,.0f} exceeds conforming limit. Jumbo loan required.")
    
    return {
        "compliance_status": "APPROVED" if len(issues_found) == 0 else "ISSUES_FOUND",
        "checks_performed": compliance_checks,
        "issues": issues_found,
        "warnings": warnings,
        "required_disclosures": ["TILA", "RESPA", "ECOA", "Fair Lending Notice"],
        "next_steps": ["Provide required disclosures", "Obtain signed acknowledgments", "Document compliance in file"]
    }


def create_compliance_agent(mcp_servers: list[McpServer] | None = None) -> Agent:
    """Agent 5: Compliance - Verifies regulations, anti-money laundering rules, and lending criteria."""
    return Agent(
        name="Compliance Agent",
        instructions="""You are a mortgage lending compliance officer ensuring all regulatory requirements are met.

**Your Critical Responsibilities:**

1. **Verify Lending Regulations**
   - **Ability-to-Repay (ATR)**: Confirm income and assets support the loan
   - **TILA**: Truth in Lending Act disclosures
   - **RESPA**: Real Estate Settlement Procedures Act compliance
   - **ECOA**: Equal Credit Opportunity Act (fair lending)
   - **HOEPA**: High-cost mortgage restrictions
   - **QM Rules**: Qualified Mortgage standards (DTI ≤ 43%)

2. **Check Loan Limits and Requirements**
   - Conforming loan limits ($766,550 in 2024, higher in high-cost areas)
   - FHA loan limits (vary by county)
   - VA loan limits (based on entitlement)
   - State-specific regulations

3. **Anti-Money Laundering (AML)**
   - Verify source of funds for down payment
   - Flag large cash deposits or suspicious activity
   - Check OFAC (Office of Foreign Assets Control) lists
   - Ensure Customer Identification Program (CIP) completion

4. **Fair Lending Compliance**
   - Ensure no discrimination based on protected classes
   - Document legitimate business reasons for any adverse action
   - Monitor for disparate impact
   - Maintain fair lending training standards

5. **Risk Assessment**
   - Fraud indicators (inflated income, false employment)
   - Occupancy fraud (claiming primary residence when investment)
   - Straw buyer schemes
   - Identity theft red flags

6. **Required Disclosures**
   Ensure delivery of:
   - Loan Estimate (within 3 days of application)
   - Closing Disclosure (3 days before closing)
   - RESPA Servicing Disclosure
   - ECOA Adverse Action Notice (if applicable)
   - State-specific disclosures

**Tools:**
- check_lending_compliance() - Run comprehensive compliance checks
- system.ai.python_exec via MCP - Query compliance_rules table in Unity Catalog
- Access to federal/state lending regulations database

**When Issues Are Found:**
- STOP the process immediately
- Document the specific regulation violated
- Provide clear remediation steps
- Escalate to senior compliance if needed
- Never approve a non-compliant loan

**Pass to:**
- Customer Communication Agent: To explain compliance requirements
- Triage Agent: If loan cannot proceed due to compliance issues

Compliance is non-negotiable. Violations result in fines, lawsuits, and reputational damage.""",
        model="databricks-meta-llama-3-3-70b-instruct",
        tools=[
            check_lending_compliance,
            search_compliance_rules,
        ],
        mcp_servers=mcp_servers or [],
    )


# ============================================================================
# AGENT 6: CUSTOMER COMMUNICATION AGENT
# ============================================================================

def create_communication_agent(mcp_servers: list[McpServer] | None = None) -> Agent:
    """Agent 6: Customer Communication - Drafts clear, human-friendly explanations of mortgage options."""
    return Agent(
        name="Customer Communication Agent",
        instructions="""You are a customer communication specialist who translates complex mortgage analysis into clear, actionable advice.

**Your Goal**: Make customers feel informed, confident, and ready to take next steps.

**Your Responsibilities:**

1. **Synthesize Complex Information**
   Take inputs from all specialist agents:
   - Document Processing: Income and asset verification
   - Financial Analytics: DTI ratios, affordability analysis
   - Product Matching: Loan options and rates
   - Compliance: Regulatory requirements
   
   Combine into a coherent, easy-to-understand narrative.

2. **Draft Clear Recommendations**
   Create professional reports with:
   
   **Executive Summary** (2-3 sentences)
   - Bottom line: what they can afford
   - Top recommendation
   - Key next step
   
   **Financial Profile Overview**
   - Income and assets (non-technical)
   - Current debts and obligations
   - Credit standing
   - Down payment available
   
   **Mortgage Options** (Top 3-5 products)
   For each option, include:
   - Monthly payment (with breakdown)
   - Total cost over loan life
   - Down payment required
   - Pros and cons in simple language
   - Why this matches their situation
   
   **Comparison Table**
   Side-by-side of recommended products:
   | Feature | Option 1 | Option 2 | Option 3 |
   | Rate | 6.875% | 7.125% | 6.625% |
   | Monthly Payment | $2,489 | $2,563 | $3,241 |
   | Term | 30 years | 30 years | 15 years |
   | Total Interest | $515,042 | $542,680 | $103,380 |
   
   **Next Steps** (Specific and actionable)
   1. Get pre-approved with [Lender Name]
   2. Gather required documents (list provided)
   3. Start house hunting in [price range]
   4. Timeline: expect [X] weeks to close
   
   **Important Disclosures**
   - Rates are estimates and subject to change
   - Pre-approval does not guarantee final approval
   - Additional costs (closing, escrow, moving)
   - Importance of rate lock

3. **Explain Complex Concepts Simply**
   Replace jargon:
   - ❌ "Your back-end DTI is 38%, within the QM threshold"
   - ✓ "Your monthly debts are 38% of your income, which is in the healthy range for mortgage approval"
   
   - ❌ "The LTV of 85% necessitates PMI"
   - ✓ "With a 15% down payment, you'll need to pay mortgage insurance (about $200/month) until you reach 20% equity"

4. **Set Realistic Expectations**
   - Be honest about approval likelihood
   - Explain potential challenges
   - Provide improvement strategies
   - Give realistic timelines

5. **Personalize the Message**
   - Address specific customer situation
   - Acknowledge their goals and concerns
   - Highlight programs that benefit them (VA, FHA, first-time buyer)
   - Use encouraging, supportive tone

**Formatting Guidelines:**
- Use markdown headers, bullets, tables
- Bold key numbers and recommendations
- Keep paragraphs short (2-3 sentences)
- Use white space generously
- Include emojis sparingly for warmth (optional)

**Tone:**
- Professional but warm
- Confident but not pushy
- Educational without being condescending
- Empathetic to the stress of homebuying
- Optimistic but realistic

**Final Check:**
- Would a non-expert understand this?
- Are next steps crystal clear?
- Have I addressed their specific situation?
- Is the recommendation sound and compliant?
- Does this build trust and confidence?

Your communication is often the customer's final impression. Make it count.""",
        model="databricks-meta-llama-3-3-70b-instruct",
        tools=[],  # Communication agent synthesizes, doesn't calculate
        mcp_servers=mcp_servers or [],
    )


# ============================================================================
# COORDINATOR AGENT - ORCHESTRATES THE 6-AGENT WORKFLOW
# ============================================================================

def create_coordinator_agent(mcp_servers: list[McpServer] | None = None) -> Agent:
    """Coordinator Agent - Single agent with comprehensive mortgage advisory capabilities.
    
    Provides all mortgage advisory tools and services in one agent.
    """
    return Agent(
        name="Mortgage Advisor",
        instructions="""You are a comprehensive mortgage advisor with expertise across all aspects of home financing.

**Your Capabilities:**

1. **Customer Engagement & Triage**
   - Welcome customers warmly and build rapport
   - Collect essential information (income, debts, down payment, credit score, goals)
   - Set realistic expectations about the mortgage process

2. **Document Processing**
   - Extract income data from payslips using extract_payslip_data()
   - Analyze bank statements using extract_bank_statement_data()
   - Verify assets, income stability, and identify debt obligations

3. **Financial Analysis**
   - Calculate monthly payments with calculate_monthly_payment()
   - Determine affordability using calculate_affordability()
   - Analyze DTI ratios with calculate_dti_ratio()
   - Calculate LTV ratios and PMI requirements with calculate_ltv_ratio()
   - Compare multiple scenarios with compare_mortgage_scenarios()

4. **Product Matching**
   - Search lender databases with search_lender_products()
   - Match customer profiles to suitable mortgage products
   - Consider FHA, VA, USDA, conventional, and jumbo loans
   - Identify special programs and down payment assistance

5. **Compliance Verification**
   - Check lending regulations with check_lending_compliance()
   - Search compliance rules with search_compliance_rules()
   - Verify ATR, TILA, RESPA, ECOA requirements
   - Ensure loan limits and fair lending compliance

6. **Customer Communication**
   - Present findings in clear, non-technical language
   - Provide side-by-side product comparisons
   - Explain pros/cons and make personalized recommendations
   - Set clear next steps

**Workflow for Customer Inquiries:**

1. Greet warmly and collect basic information
2. If documents provided, extract and verify data
3. Perform financial analysis (DTI, LTV, affordability)
4. Search for suitable mortgage products
5. Verify compliance and eligibility
6. Present clear recommendations with next steps

**Key Principles:**
- Be empathetic and patient - homebuying is stressful
- Use tools systematically to provide accurate advice
- Explain complex concepts simply
- Be conservative in estimates to protect customers
- Always verify regulatory compliance
- Provide actionable next steps

You have access to comprehensive tools and data to guide customers through their mortgage journey.""",
        model="databricks-meta-llama-3-3-70b-instruct",
        tools=[
            # Mortgage calculation tools
            calculate_monthly_payment,
            calculate_affordability,
            compare_mortgage_scenarios,
            # Document processing tools
            extract_payslip_data,
            extract_bank_statement_data,
            # Financial analytics tools
            calculate_dti_ratio,
            calculate_ltv_ratio,
            # Product matching tools
            search_lender_products,
            # Compliance tools
            check_lending_compliance,
            search_compliance_rules,
        ],
        mcp_servers=mcp_servers or [],
    )


def create_agent(mcp_servers: list[McpServer] | None = None) -> Agent:
    """Create the coordinator agent (entry point for the 6-agent system)."""
    return create_coordinator_agent(mcp_servers=mcp_servers)


@invoke()
async def invoke_handler(request: ResponsesAgentRequest) -> ResponsesAgentResponse:
    """Handle synchronous agent invocation with production logging."""
    # Set experiment for production traces
    mlflow.set_experiment(experiment_id="552529352050103")
    
    # Extract user and session metadata
    session_id = get_session_id(request)
    user_id = getattr(request, 'user_id', 'unknown')
    
    # Log production request metadata
    production_metadata = {
        "environment": "production",
        "deployment_type": "databricks_app",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "user_id": user_id,
        "request_type": "invoke",
        "num_messages": len(request.input) if request.input else 0,
    }
    
    if session_id:
        mlflow.update_current_trace(
            metadata={
                "mlflow.trace.session": session_id,
                **production_metadata
            },
            tags={
                "env": "production",
                "app": "mortgage_advisor",
                "session": session_id,
            }
        )
    
    # Enable MCP server for system.ai tools (python_exec, UC functions)
    try:
        async with await init_mcp_server(WorkspaceClient()) as mcp_server:
            agent = create_agent(mcp_servers=[mcp_server])
            messages = [i.model_dump() for i in request.input]
            result = await Runner.run(agent, messages)
            
            # Log success metadata
            mlflow.update_current_trace(metadata={
                "status": "success",
                "response_items": len(result.new_items)
            })
            
            return ResponsesAgentResponse(output=[item.to_input_item() for item in result.new_items])
    except Exception as e:
        # Log failure metadata
        mlflow.update_current_trace(metadata={
            "status": "fallback_no_mcp",
            "warning": str(e)
        })
        logger.warning("MCP server unavailable. Continuing without MCP tools.", exc_info=True)
        agent = create_agent()
        messages = [i.model_dump() for i in request.input]
        result = await Runner.run(agent, messages)
        return ResponsesAgentResponse(output=[item.to_input_item() for item in result.new_items])


@stream()
async def stream_handler(
    request: ResponsesAgentRequest,
) -> AsyncGenerator[ResponsesAgentStreamEvent, None]:
    """Handle streaming agent execution with production logging."""
    # Set experiment for production traces
    mlflow.set_experiment(experiment_id="552529352050103")
    
    # Extract user and session metadata
    session_id = get_session_id(request)
    user_id = getattr(request, 'user_id', 'unknown')
    
    # Log production request metadata
    production_metadata = {
        "environment": "production",
        "deployment_type": "databricks_app",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "user_id": user_id,
        "request_type": "stream",
        "num_messages": len(request.input) if request.input else 0,
    }
    
    if session_id:
        mlflow.update_current_trace(
            metadata={
                "mlflow.trace.session": session_id,
                **production_metadata
            },
            tags={
                "env": "production",
                "app": "mortgage_advisor",
                "session": session_id,
            }
        )
    
    # Enable MCP server for system.ai tools (python_exec, UC functions)
    try:
        async with await init_mcp_server(WorkspaceClient()) as mcp_server:
            agent = create_agent(mcp_servers=[mcp_server])
            messages = [i.model_dump() for i in request.input]
            result = Runner.run_streamed(agent, input=messages)
            
            # Log success metadata
            mlflow.update_current_trace(metadata={"status": "success"})
            
            async for event in process_agent_stream_events(result.stream_events()):
                yield event
    except Exception as e:
        # Log failure metadata
        mlflow.update_current_trace(metadata={
            "status": "fallback_no_mcp",
            "warning": str(e)
        })
        logger.warning("MCP server unavailable. Continuing without MCP tools.", exc_info=True)
        agent = create_agent()
        messages = [i.model_dump() for i in request.input]
        result = Runner.run_streamed(agent, input=messages)
        async for event in process_agent_stream_events(result.stream_events()):
            yield event
