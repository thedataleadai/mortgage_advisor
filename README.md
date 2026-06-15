# Mortgage Advisor Multi-Agent System

This application is a **sophisticated mortgage advisory platform** powered by a multi-agent architecture. It provides personalized mortgage guidance, affordability calculations, and scenario analysis using specialized AI agents working collaboratively.

## 🏡 System Overview

The system employs **six specialized agents** coordinated by an intelligent orchestrator:

### 1. **Triage Agent**
- Greets customers and collects basic information
- Identifies customer needs and intent
- Routes requests to appropriate specialist agents
- Provides immediate responses to simple queries
- Ensures smooth handoff between agents

### 2. **Document Processing Agent**
- Extracts data from payslips, bank statements, and financial documents
- Validates document authenticity and completeness
- Structures unstructured document data
- Tools: `extract_payslip_data`, `extract_bank_statement_data`

### 3. **Financial Analytics Agent**
- Calculates debt-to-income (DTI) ratios
- Computes loan-to-value (LTV) ratios
- Determines maximum borrowing capacity
- Performs "what-if" scenario analysis
- Uses Unity Catalog SQL functions for calculations
- Tools: `calculate_dti_ratio`, `calculate_ltv_ratio`, `analyze_financial_capacity`

### 4. **Product Matching Agent**
- Searches lender product databases
- Matches customer profiles to suitable mortgage products
- Compares rates, terms, and features across lenders
- Identifies special programs (FHA, VA, USDA, first-time buyer)
- Tools: `search_lender_products`, `match_customer_to_products`

### 5. **Compliance Agent**
- Verifies regulatory compliance (TILA, RESPA, ECOA)
- Performs Anti-Money Laundering (AML) checks
- Validates lending criteria adherence
- Flags potential red flags or missing requirements
- Tools: `check_lending_compliance`, `verify_aml_requirements`

### 6. **Customer Communication Agent**
- Translates technical analysis into clear, human-friendly explanations
- Drafts personalized mortgage recommendations
- Creates decision summaries and action plans
- Explains complex mortgage concepts in simple terms

### Coordinator Agent
The **Mortgage Advisor Coordinator** orchestrates the workflow:
- Routes requests to appropriate agents based on intent
- Manages multi-agent workflows and handoffs
- Ensures data flows through the proper sequence
- Aggregates results from multiple agents
- Handles errors and fallback scenarios

## 🗄️ Unity Catalog Data Architecture

The system uses Unity Catalog for governance and organization:

### Catalog: `mortgage`

**Schemas:**
* **`finance`** - Mortgage calculation UC functions and financial analytics
* **`customer_data`** - Customer profiles and application history
* **`products`** - Lender mortgage products and rates
* **`compliance`** - Regulatory rules and AML requirements
* **`documents`** - Document metadata (payslips, bank statements, property docs)

**Unity Catalog Functions in `mortgage.finance`:**
* `calculate_monthly_payment(loan_amount, annual_rate, years)` - Monthly payment calculator
* `calculate_dti_ratio(income, debts)` - Debt-to-income ratio
* `calculate_ltv_ratio(loan_amount, property_value)` - Loan-to-value ratio
* `check_eligibility(credit_score, dti, ltv, loan_type)` - Eligibility checker

**Sample Data Tables:**
* `mortgage.customer_data.customer_profiles` - 10 sample customers
* `mortgage.customer_data.application_history` - 5 mortgage applications
* `mortgage.products.lender_products` - 15 mortgage products
* `mortgage.compliance.rules` - 12 compliance rules
* `mortgage.documents.*` - Document metadata tables

## 🛠️ Agent Tools

**Document Processing:**
* `extract_payslip_data` - Extracts income from payslip documents
* `extract_bank_statement_data` - Extracts account balances and transactions

**Financial Analytics:**
* `calculate_dti_ratio` - Computes DTI using income and debt payments
* `calculate_ltv_ratio` - Computes LTV using loan amount and property value
* `analyze_financial_capacity` - Comprehensive affordability analysis

**Product Matching:**
* `search_lender_products` - Searches products by criteria
* `match_customer_to_products` - Finds suitable products for customer profile

**Compliance:**
* `check_lending_compliance` - Verifies regulatory compliance
* `verify_aml_requirements` - Performs AML checks

## 💬 Example Conversations

**Customer**: "I make $120,000/year with $500/month in debts. I have $60,000 saved for a down payment. What can I afford?"

**System Response**:
1. Data Researcher fetches current mortgage rates
2. Analyst calculates affordability and scenarios
3. Report Writer synthesizes into a comprehensive report with:
   - Maximum home price
   - Monthly payment estimates
   - Comparison of 15yr vs 30yr mortgages
   - Impact of different down payment amounts
   - Personalized recommendations

**Customer**: "Compare a 15-year mortgage at 6.5% vs 30-year at 7.0% for a $400,000 loan"

**System Response**:
- Detailed side-by-side comparison
- Monthly payment difference
- Total interest savings
- Breakeven analysis
- Recommendation based on customer's situation

## 🔍 Observability & Monitoring

Comprehensive MLflow tracing integrated into the agent system:

**Tracing Features:**
* Custom spans for each agent execution
* Session tracking with unique IDs
* Duration metrics (milliseconds per agent)
* Event counting for streaming responses
* User query preview in metadata
* Architecture tracking (6-agent system)
* Success/failure status indicators

**Tracing Handlers:**
* `invoke_handler` - Non-streaming requests with detailed spans
* `stream_handler` - Streaming requests with event counting

View traces in the MLflow UI to monitor agent performance, debug issues, and optimize workflows.

## 🚀 Quick Setup

Run these notebooks in sequence to set up the complete system:

```bash
# 0. Generate UC function SQL files
%run ./scripts/setup/00_generate_all_uc_functions

# 1. Create Unity Catalog structure
%run ./scripts/setup/01_setup_catalog

# 2. Load sample data into UC tables
%run ./scripts/setup/02_load_data

# 3. Deploy UC functions
%run ./scripts/setup/03_create_uc_functions
```

**Setup Scripts:**
* `00_generate_all_uc_functions.py` - Generates SQL files for UC functions
* `01_setup_catalog.py` - Creates catalog and schemas
* `02_load_data.py` - Loads CSV data into UC tables
* `03_create_uc_functions.py` - Deploys UC functions and runs tests
* `04_setup_vector_search.py` - (Coming soon) Vector search setup
* `05_apply_governance.py` - (Coming soon) Apply RLS, masking, tags

## Build with AI Assistance

We recommend using AI coding assistants (Claude Code, Cursor, GitHub Copilot) to customize and deploy this template. Agent Skills in `.claude/skills/` provide step-by-step guidance for common tasks like setup, adding tools, and deployment. These skills are automatically detected by Claude, Cursor, and GitHub Copilot.

## Quick start

Run the `uv run quickstart` script to quickly set up your local environment and start the agent server. At any step, if there are issues, refer to the manual local development loop setup below.

This script will:

1. Verify uv, nvm, and Databricks CLI installations
2. Configure Databricks authentication
3. Configure agent tracing, by creating and linking an MLflow experiment to your app
4. Start the agent server and chat app

```bash
uv run quickstart
```

After the setup is complete, you can start the agent server and the chat app locally with:

```bash
uv run start-app
```

This will start the agent server and the chat app at http://localhost:8000.

**Next steps**: see [modifying your agent](#modifying-your-agent) to customize and iterate on the agent code.

## Manual local development loop setup

1. **Set up your local environment**
   Install `uv` (python package manager), `nvm` (node version manager), and the Databricks CLI:

   - [`uv` installation docs](https://docs.astral.sh/uv/getting-started/installation/)
   - [`nvm` installation](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating)
     - Run the following to use Node 20 LTS:
       ```bash
       nvm use 20
       ```
   - [`databricks CLI` installation](https://docs.databricks.com/aws/en/dev-tools/cli/install)

2. **Set up local authentication to Databricks**

   In order to access Databricks resources from your local machine while developing your agent, you need to authenticate with Databricks. Choose one of the following options:

   **Option 1: OAuth via Databricks CLI (Recommended)**

   Authenticate with Databricks using the CLI. See the [CLI OAuth documentation](https://docs.databricks.com/aws/en/dev-tools/cli/authentication#oauth-user-to-machine-u2m-authentication).

   ```bash
   databricks auth login
   ```

   Set the `DATABRICKS_CONFIG_PROFILE` environment variable in your .env file to the profile you used to authenticate:

   ```bash
   DATABRICKS_CONFIG_PROFILE="DEFAULT" # change to the profile name you chose
   ```

   **Option 2: Personal Access Token (PAT)**

   See the [PAT documentation](https://docs.databricks.com/aws/en/dev-tools/auth/pat#databricks-personal-access-tokens-for-workspace-users).

   ```bash
   # Add these to your .env file
   DATABRICKS_HOST="https://host.databricks.com"
   DATABRICKS_TOKEN="dapi_token"
   ```

   See the [Databricks SDK authentication docs](https://docs.databricks.com/aws/en/dev-tools/sdk-python#authenticate-the-databricks-sdk-for-python-with-your-databricks-account-or-workspace).

3. **Create and link an MLflow experiment to your app**

   Create an MLflow experiment to enable tracing and version tracking. This is automatically done by the `uv run quickstart` script.

   Create the MLflow experiment via the CLI:

   ```bash
   DATABRICKS_USERNAME=$(databricks current-user me | jq -r .userName)
   databricks experiments create-experiment /Users/$DATABRICKS_USERNAME/agents-on-apps
   ```

   Make a copy of `.env.example` to `.env` and update the `MLFLOW_EXPERIMENT_ID` in your `.env` file with the experiment ID you created. The `.env` file will be automatically loaded when starting the server.

   ```bash
   cp .env.example .env
   # Edit .env and fill in your experiment ID
   ```

   See the [MLflow experiments documentation](https://docs.databricks.com/aws/en/mlflow/experiments#create-experiment-from-the-workspace).

4. **Test your agent locally**

   Start up the agent server and chat UI locally:

   ```bash
   uv run start-app
   ```

   Query your agent via the UI (http://localhost:8000) or REST API:

   **Advanced server options:**

   ```bash
   uv run start-server --reload   # hot-reload the server on code changes
   uv run start-server --port 8001 # change the port the server listens on
   uv run start-server --workers 4 # run the server with multiple workers
   ```

   - Example streaming request:
     ```bash
     curl -X POST http://localhost:8000/invocations \
     -H "Content-Type: application/json" \
     -d '{ "input": [{ "role": "user", "content": "I make $120k with $500 debts and $60k down payment. What can I afford?" }], "stream": true }'
     ```
   - Example non-streaming request:
     ```bash
     curl -X POST http://localhost:8000/invocations  \
     -H "Content-Type: application/json" \
     -d '{ "input": [{ "role": "user", "content": "Compare 15yr at 6.5% vs 30yr at 7% for $400k loan" }] }'
     ```

## Modifying your agent

See the [OpenAI Agents SDK documentation](https://platform.openai.com/docs/guides/agents-sdk) for more information on how to edit your own agent.

### Architecture Files

The mortgage advisor system is defined in:

- **`agent_server/agent.py`**: Contains all agent logic including:
  - Mortgage calculation tools (`calculate_monthly_payment`, `calculate_affordability`, `compare_mortgage_scenarios`)
  - Four specialized agents (Data Researcher, Analyst, Report Writer, Coordinator)
  - Agent orchestration logic
  
- **`agent_server/start_server.py`**: Initializes and runs the MLflow `AgentServer` with agent_type="ResponsesAgent". You don't have to modify this file for most common use cases, but can add additional server routes (e.g. a `/metrics` endpoint) here

### Customization Ideas

**Adding Data Sources**:
- Connect to Unity Catalog tables with mortgage rate history
- Integrate with property value APIs
- Add Vector Search for document retrieval (loan documents, property listings)
- Connect to Genie spaces for natural language queries

**Enhancing Tools**:
- Add refinancing analysis tools
- Include property tax and insurance calculators
- Build credit score impact models
- Add closing cost estimators

**Extending Agents**:
- Add a Compliance Agent for regulatory checks
- Create a Document Agent for loan paperwork
- Build a Follow-up Agent for customer engagement

**Common customization questions:**

**Q: Can I add additional files or folders to my agent?**
Yes. Add additional files or folders as needed. Ensure the script within `pyproject.toml` runs the correct script that starts the server and sets up MLflow tracing.

**Q: How do I add dependencies to my agent?**
Run `uv add <package_name>` (e.g., `uv add "mlflow-skinny[databricks]"`). See the [python pyproject.toml guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#dependencies-and-requirements).

**Q: Can I add custom tracing beyond the built-in tracing?**
Yes. This template uses MLflow's agent server, which comes with automatic tracing for agent logic decorated with `@invoke()` and `@stream()`. It also uses [MLflow autologging APIs](https://mlflow.org/docs/latest/genai/tracing/#one-line-auto-tracing-integrations) to capture traces from LLM invocations. However, you can add additional instrumentation to capture more granular trace information when your agent runs. See the [MLflow tracing documentation](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/app-instrumentation/).

**Q: How can I extend this example with additional tools and capabilities?**
This template can be extended by integrating additional MCP servers, Vector Search Indexes, UC Functions, and other Databricks tools. See the [\"Agent Framework Tools Documentation\"](https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-tool).

## Evaluating your agent

Evaluate your agent by calling the invoke function you defined for the agent locally.

- Update your `evaluate_agent.py` file with the preferred evaluation dataset and scorers.

Run the evaluation using the evaluation script:

```bash
uv run agent-evaluate
```

After it completes, open the MLflow UI link for your experiment to inspect results.

## Deploying to Databricks Apps

This template uses [Databricks Asset Bundles (DABs)](https://docs.databricks.com/aws/en/dev-tools/bundles/) for deployment. The `databricks.yml` file defines the app configuration and resource permissions.

> **`app.yaml` vs `databricks.yml`**: `app.yaml` is used when deploying via `databricks apps deploy` (manual path). When deploying via DABs (`databricks bundle deploy`), the `config:` section in `databricks.yml` takes precedence. If you change environment variables or the start command, update `databricks.yml` — that's what DABs reads.

Ensure you have the [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/tutorial) installed and configured.

1. **Run the pre-flight check**

   Start the agent locally, send a test request, and verify the response to catch configuration and code errors early:

   ```bash
   uv run preflight
   ```

2. **Validate the bundle configuration**

   Catch any configuration errors before deploying:

   ```bash
   databricks bundle validate
   ```

3. **Deploy the bundle**

   This uploads your code and configures resources (MLflow experiment, serving endpoints, etc.) defined in `databricks.yml`:

   ```bash
   databricks bundle deploy
   ```

4. **Run the app**

   Start your deployed app:

   ```bash
   databricks bundle run agent_openai_agents_sdk
   ```

5. **Access the app**

   After deployment, your app will be available in the Databricks workspace. Find it in the **Apps** section or use:

   ```bash
   databricks apps list
   databricks apps get <your-app-name>
   ```

## Testing Your Mortgage Advisor

Here are some test scenarios to validate the system:

```bash
# Affordability analysis
curl -X POST http://localhost:8000/invocations -H "Content-Type: application/json" \
-d '{ "input": [{ "role": "user", "content": "I earn $150k annually with $800 in monthly debts and $80k saved. What home price can I afford?" }] }'

# Scenario comparison
curl -X POST http://localhost:8000/invocations -H "Content-Type: application/json" \
-d '{ "input": [{ "role": "user", "content": "Compare a $500k loan: 15yr at 6.5% vs 30yr at 7% vs 20yr at 6.75%" }] }'

# Monthly payment calculation
curl -X POST http://localhost:8000/invocations -H "Content-Type: application/json" \
-d '{ "input": [{ "role": "user", "content": "What would my monthly payment be on a $350,000 loan at 7.25% for 30 years?" }] }'

# Refinancing analysis
curl -X POST http://localhost:8000/invocations -H "Content-Type: application/json" \
-d '{ "input": [{ "role": "user", "content": "I have $280k left on my mortgage at 8% with 25 years remaining. Current rates are 6.5% for 30yr. Should I refinance?" }] }'
```

## 📊 Next Steps

1. **Add data sources**: Connect Unity Catalog tables with real mortgage rate data
2. **Enhance tools**: Add property tax calculators, PMI calculations, closing costs
3. **Expand agents**: Create specialized agents for refinancing, credit analysis, or document processing
4. **Integrate APIs**: Connect to property listing APIs, credit scoring services
5. **Build UI**: Create custom front-end for better user experience
6. **Deploy**: Use DABs to deploy to production with proper permissions

## 🔗 Resources

- [OpenAI Agents SDK](https://platform.openai.com/docs/guides/agents-sdk)
- [Databricks Agent Framework](https://docs.databricks.com/aws/en/generative-ai/agent-framework/)
- [MLflow Agent Tracking](https://mlflow.org/docs/latest/genai/flavors/responses-agent-intro/)
- [Databricks Asset Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/)
