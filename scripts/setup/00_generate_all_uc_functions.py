# Databricks notebook source
# DBTITLE 1,Generate UC Function SQL Files
# Databricks notebook source
# MAGIC %md
# MAGIC # Generate Unity Catalog Function SQL Files
# MAGIC 
# MAGIC This notebook creates all SQL files for Unity Catalog functions used in the Mortgage Advisor system.
# MAGIC 
# MAGIC **Functions to create:**
# MAGIC 1. `calculate_monthly_payment` - Amortization formula
# MAGIC 2. `calculate_dti_ratio` - Debt-to-income ratio
# MAGIC 3. `calculate_ltv_ratio` - Loan-to-value ratio  
# MAGIC 4. `check_eligibility` - Eligibility checker
# MAGIC 
# MAGIC **Run this notebook to generate all SQL files in `/mortgage advisor/scripts/uc_functions/`**

# COMMAND ----------

# DBTITLE 1,Setup - Define base directory
# COMMAND ----------

import os

base_dir = "/Workspace/Users/paul.karikari@thedatalead.ai/mortgage advisor/scripts/uc_functions"
os.makedirs(base_dir, exist_ok=True)

print(f"UC Functions directory: {base_dir}")

# COMMAND ----------

# DBTITLE 1,Create calculate_monthly_payment function
# COMMAND ----------

# 1. Calculate Monthly Payment Function
monthly_payment_sql = """-- ============================================================================
-- Unity Catalog Function: Calculate Monthly Mortgage Payment
-- ============================================================================
-- This function calculates the monthly mortgage payment using the standard
-- amortization formula: M = P * (r(1+r)^n) / ((1+r)^n - 1)
--
-- Usage:
--   SELECT mortgage.finance.calculate_monthly_payment(300000, 6.5, 30);
--
-- Returns: Monthly payment amount
-- ============================================================================

CREATE OR REPLACE FUNCTION mortgage.finance.calculate_monthly_payment(
  loan_amount DOUBLE,
  annual_rate DOUBLE,
  years INT
)
RETURNS DOUBLE
LANGUAGE SQL
COMMENT 'Calculate monthly mortgage payment using amortization formula'
RETURN
  CASE
    -- Handle zero interest rate edge case
    WHEN annual_rate = 0 THEN loan_amount / (years * 12)
    
    -- Standard amortization calculation
    ELSE (
      SELECT 
        loan_amount * (
          (monthly_rate * POWER(1 + monthly_rate, num_payments)) /
          (POWER(1 + monthly_rate, num_payments) - 1)
        )
      FROM (
        SELECT 
          (annual_rate / 100) / 12 AS monthly_rate,
          years * 12 AS num_payments
      )
    )
  END;

-- ============================================================================
-- Test Cases
-- ============================================================================
-- SELECT mortgage.finance.calculate_monthly_payment(300000, 6.5, 30) AS monthly_payment;
-- Expected: ~$1,896.20
--
-- SELECT mortgage.finance.calculate_monthly_payment(200000, 7.0, 15) AS monthly_payment;
-- Expected: ~$1,797.66
-- ============================================================================
"""

with open(f"{base_dir}/01_calculate_monthly_payment.sql", "w") as f:
    f.write(monthly_payment_sql)

print("✓ Created 01_calculate_monthly_payment.sql")

# COMMAND ----------

# DBTITLE 1,Create calculate_dti_ratio function
# COMMAND ----------

# 2. Calculate DTI Ratio Function
dti_sql = """-- ============================================================================
-- Unity Catalog Function: Calculate Debt-to-Income Ratio
-- ============================================================================
-- Calculates the debt-to-income ratio as a percentage
--
-- Usage:
--   SELECT mortgage.finance.calculate_dti_ratio(8000, 2400);
--
-- Returns: DTI ratio as percentage
-- ============================================================================

CREATE OR REPLACE FUNCTION mortgage.finance.calculate_dti_ratio(
  monthly_gross_income DOUBLE,
  monthly_debt_payments DOUBLE
)
RETURNS DOUBLE
LANGUAGE SQL
COMMENT 'Calculate debt-to-income ratio as percentage'
RETURN
  CASE
    WHEN monthly_gross_income = 0 THEN NULL
    ELSE (monthly_debt_payments / monthly_gross_income) * 100
  END;

-- ============================================================================
-- Test Cases
-- ============================================================================
-- SELECT mortgage.finance.calculate_dti_ratio(8000, 2400) AS dti_ratio;
-- Expected: 30.0
--
-- SELECT mortgage.finance.calculate_dti_ratio(10000, 4300) AS dti_ratio;
-- Expected: 43.0 (at the max for conventional loans)
-- ============================================================================
"""

with open(f"{base_dir}/02_calculate_dti_ratio.sql", "w") as f:
    f.write(dti_sql)

print("✓ Created 02_calculate_dti_ratio.sql")

# COMMAND ----------

# DBTITLE 1,Create calculate_ltv_ratio function
# COMMAND ----------

# 3. Calculate LTV Ratio Function
ltv_sql = """-- ============================================================================
-- Unity Catalog Function: Calculate Loan-to-Value Ratio
-- ============================================================================
-- Calculates the loan-to-value ratio as a percentage
--
-- Usage:
--   SELECT mortgage.finance.calculate_ltv_ratio(240000, 300000);
--
-- Returns: LTV ratio as percentage
-- ============================================================================

CREATE OR REPLACE FUNCTION mortgage.finance.calculate_ltv_ratio(
  loan_amount DOUBLE,
  property_value DOUBLE
)
RETURNS DOUBLE
LANGUAGE SQL
COMMENT 'Calculate loan-to-value ratio as percentage'
RETURN
  CASE
    WHEN property_value = 0 THEN NULL
    ELSE (loan_amount / property_value) * 100
  END;

-- ============================================================================
-- Test Cases
-- ============================================================================
-- SELECT mortgage.finance.calculate_ltv_ratio(240000, 300000) AS ltv_ratio;
-- Expected: 80.0 (exactly at PMI threshold)
--
-- SELECT mortgage.finance.calculate_ltv_ratio(285000, 300000) AS ltv_ratio;
-- Expected: 95.0 (requires PMI)
-- ============================================================================
"""

with open(f"{base_dir}/03_calculate_ltv_ratio.sql", "w") as f:
    f.write(ltv_sql)

print("✓ Created 03_calculate_ltv_ratio.sql")

# COMMAND ----------

# DBTITLE 1,Create check_eligibility function
# COMMAND ----------

# 4. Check Eligibility Function
eligibility_sql = """-- ============================================================================
-- Unity Catalog Function: Check Mortgage Eligibility
-- ============================================================================
-- Checks if a borrower is eligible for a mortgage based on key criteria
--
-- Usage:
--   SELECT mortgage.finance.check_eligibility(740, 35.0, 80.0, 'conventional');
--
-- Returns: STRUCT with eligibility status and details
-- ============================================================================

CREATE OR REPLACE FUNCTION mortgage.finance.check_eligibility(
  credit_score INT,
  dti_ratio DOUBLE,
  ltv_ratio DOUBLE,
  loan_type STRING
)
RETURNS STRUCT<
  eligible: BOOLEAN,
  reason: STRING,
  recommendation: STRING
>
LANGUAGE SQL
COMMENT 'Check mortgage eligibility based on credit, DTI, and LTV'
RETURN
  CASE
    -- Conventional Loan Checks
    WHEN loan_type = 'conventional' THEN
      CASE
        WHEN credit_score < 620 THEN 
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'Credit score below minimum (620) for conventional',
            'recommendation', 'Consider FHA loan or work on improving credit score'
          )
        WHEN dti_ratio > 43.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'DTI ratio exceeds maximum (43%) for conventional',
            'recommendation', 'Reduce monthly debts or increase income'
          )
        WHEN ltv_ratio > 97.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'LTV exceeds maximum (97%) for conventional',
            'recommendation', 'Increase down payment to at least 3%'
          )
        ELSE
          NAMED_STRUCT(
            'eligible', TRUE,
            'reason', 'Meets conventional loan requirements',
            'recommendation', 'Proceed with conventional loan application'
          )
      END
    
    -- FHA Loan Checks
    WHEN loan_type = 'fha' THEN
      CASE
        WHEN credit_score < 500 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'Credit score below FHA minimum (500)',
            'recommendation', 'Work on improving credit score before applying'
          )
        WHEN credit_score < 580 AND ltv_ratio > 90.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'Credit score 500-579 requires 10% down payment',
            'recommendation', 'Increase down payment or improve credit to 580+'
          )
        WHEN dti_ratio > 50.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'DTI ratio exceeds FHA maximum (50%)',
            'recommendation', 'Reduce monthly debts or increase income'
          )
        WHEN ltv_ratio > 96.5 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'LTV exceeds FHA maximum (96.5%)',
            'recommendation', 'Increase down payment to at least 3.5%'
          )
        ELSE
          NAMED_STRUCT(
            'eligible', TRUE,
            'reason', 'Meets FHA loan requirements',
            'recommendation', 'Proceed with FHA loan application'
          )
      END
    
    -- VA Loan Checks
    WHEN loan_type = 'va' THEN
      CASE
        WHEN dti_ratio > 41.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'DTI ratio exceeds VA guideline (41%)',
            'recommendation', 'May need compensating factors or debt reduction'
          )
        ELSE
          NAMED_STRUCT(
            'eligible', TRUE,
            'reason', 'Meets VA loan requirements (verify COE)',
            'recommendation', 'Proceed with VA loan - verify Certificate of Eligibility'
          )
      END
    
    -- Default
    ELSE
      NAMED_STRUCT(
        'eligible', FALSE,
        'reason', 'Unknown loan type',
        'recommendation', 'Specify valid loan type: conventional, fha, or va'
      )
  END;

-- ============================================================================
-- Test Cases
-- ============================================================================
-- SELECT mortgage.finance.check_eligibility(740, 35.0, 80.0, 'conventional') AS eligibility;
-- Expected: eligible = TRUE
--
-- SELECT mortgage.finance.check_eligibility(590, 45.0, 85.0, 'conventional') AS eligibility;
-- Expected: eligible = FALSE (credit too low)
--
-- SELECT mortgage.finance.check_eligibility(620, 48.0, 93.5, 'fha') AS eligibility;
-- Expected: eligible = TRUE
-- ============================================================================
"""

with open(f"{base_dir}/04_check_eligibility.sql", "w") as f:
    f.write(eligibility_sql)

print("✓ Created 04_check_eligibility.sql")

# COMMAND ----------

# DBTITLE 1,Create README for UC functions
# COMMAND ----------

# 5. Create README
readme = """# Unity Catalog Functions for Mortgage Advisor

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

2. Run each SQL script in order from the Databricks SQL editor or notebook.

3. Or use the deployment script:
   ```python
   %run ./01_setup_catalog
   %run ./03_create_uc_functions
   ```

## Testing

Each SQL file includes test cases in comments. Run them to verify the functions work correctly.

## Integration with Agent System

These UC functions can be called from:
- Python tools via `spark.sql()`
- MCP server system.ai.python_exec
- Direct SQL queries in Financial Analytics Agent

Example integration:
```python
result = spark.sql(
    "SELECT mortgage.finance.calculate_monthly_payment(300000, 6.5, 30) as payment"
).collect()[0]['payment']
```
"""

with open(f"{base_dir}/README.md", "w") as f:
    f.write(readme)

print("✓ Created README.md")

# COMMAND ----------

# DBTITLE 1,Summary
# COMMAND ----------

print("\n" + "="*70)
print("Unity Catalog Function SQL Scripts Created Successfully!")
print("="*70)
print(f"\nLocation: {base_dir}/")
print("\nFiles created:")
print("  1. 01_calculate_monthly_payment.sql")
print("  2. 02_calculate_dti_ratio.sql")
print("  3. 03_calculate_ltv_ratio.sql")
print("  4. 04_check_eligibility.sql")
print("  5. README.md")
print("\nNext steps:")
print("  1. Run: %run ./01_setup_catalog")
print("  2. Run: %run ./03_create_uc_functions")
print("  3. Test the functions with the provided examples")
print("="*70)

# COMMAND ----------

