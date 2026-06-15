# Unity Catalog Functions for Mortgage Advisor

This directory contains SQL scripts to create Unity Catalog functions for mortgage calculations and eligibility checks.

## Functions

### 1. calculate_monthly_payment
Calculates monthly mortgage payment using the standard amortization formula.

**Signature:**
```sql
mortgage.finance.calculate_monthly_payment(loan_amount DOUBLE, annual_rate DOUBLE, years INT) -> DOUBLE
```

**Example:**
```sql
SELECT mortgage.finance.calculate_monthly_payment(300000, 6.5, 30);
-- Returns: 1896.20
```

### 2. calculate_dti_ratio
Calculates debt-to-income ratio as a percentage.

**Signature:**
```sql
mortgage.finance.calculate_dti_ratio(monthly_gross_income DOUBLE, monthly_debt_payments DOUBLE) -> DOUBLE
```

**Example:**
```sql
SELECT mortgage.finance.calculate_dti_ratio(8000, 2400);
-- Returns: 30.0
```

### 3. calculate_ltv_ratio
Calculates loan-to-value ratio as a percentage.

**Signature:**
```sql
mortgage.finance.calculate_ltv_ratio(loan_amount DOUBLE, property_value DOUBLE) -> DOUBLE
```

**Example:**
```sql
SELECT mortgage.finance.calculate_ltv_ratio(240000, 300000);
-- Returns: 80.0
```

### 4. check_eligibility
Checks mortgage eligibility based on credit score, DTI, LTV, and loan type.

**Signature:**
```sql
mortgage.finance.check_eligibility(credit_score INT, dti_ratio DOUBLE, ltv_ratio DOUBLE, loan_type STRING) 
-> STRUCT<eligible BOOLEAN, reason STRING, recommendation STRING>
```

**Example:**
```sql
SELECT mortgage.finance.check_eligibility(740, 35.0, 80.0, 'conventional');
-- Returns: {eligible: true, reason: "Meets conventional loan requirements", ...}
```

## Setup

1. Ensure you have a catalog named `mortgage` with a schema named `finance`:
   ```sql
   CREATE CATALOG IF NOT EXISTS mortgage;
   CREATE SCHEMA IF NOT EXISTS mortgage.finance;
   ```

2. Run each SQL script in order:
   ```bash
   databricks workspace import-dir ./uc_functions /Workspace/mortgage_advisor/uc_functions
   ```

3. Or use the setup script:
   ```bash
   python scripts/setup/03_create_uc_functions.py
   ```

## Testing

Each SQL file includes test cases in comments. Uncomment and run them to verify the functions work correctly.

## Integration with Agent System

These UC functions can be called from:
- Python tools via `spark.sql()`
- MCP server system.ai.python_exec
- Direct SQL queries in Financial Analytics Agent

Example integration:
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

# Calculate monthly payment via UC function
result = w.workspace.execute_statement(
    catalog="mortgage",
    schema="finance", 
    statement="SELECT calculate_monthly_payment(300000, 6.5, 30) as payment"
)
```
