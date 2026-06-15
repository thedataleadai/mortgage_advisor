# Databricks notebook source
# DBTITLE 1,Deploy Unity Catalog Functions
# Databricks notebook source
# MAGIC %md
# MAGIC # Deploy Unity Catalog Functions
# MAGIC 
# MAGIC This notebook deploys all UC functions for mortgage calculations:
# MAGIC 
# MAGIC 1. **calculate_monthly_payment** - Monthly mortgage payment calculator
# MAGIC 2. **calculate_dti_ratio** - Debt-to-income ratio calculator
# MAGIC 3. **calculate_ltv_ratio** - Loan-to-value ratio calculator
# MAGIC 4. **check_eligibility** - Mortgage eligibility checker
# MAGIC 
# MAGIC **Prerequisites:** 
# MAGIC * Run `00_generate_all_uc_functions` to create SQL files
# MAGIC * Run `01_setup_catalog` to create catalog structure

# COMMAND ----------

# DBTITLE 1,Setup
# COMMAND ----------

import os

uc_functions_dir = "/Workspace/Users/paul.karikari@thedatalead.ai/mortgage advisor/scripts/uc_functions"

print(f"UC Functions directory: {uc_functions_dir}")

# COMMAND ----------

# DBTITLE 1,Deploy calculate_monthly_payment
# COMMAND ----------

print("Deploying calculate_monthly_payment...")

with open(f"{uc_functions_dir}/01_calculate_monthly_payment.sql", "r") as f:
    sql = f.read()
    # Extract only the CREATE FUNCTION statement (exclude comments and test cases)
    sql = sql.split("-- ============================================================================\n-- Test Cases")[0]
    spark.sql(sql)

print("✓ Function deployed: mortgage.finance.calculate_monthly_payment")

# COMMAND ----------

# DBTITLE 1,Test calculate_monthly_payment
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Test the function
# MAGIC SELECT 
# MAGIC   mortgage.finance.calculate_monthly_payment(300000, 6.5, 30) AS monthly_payment_30yr,
# MAGIC   mortgage.finance.calculate_monthly_payment(300000, 6.5, 15) AS monthly_payment_15yr;

# COMMAND ----------

# DBTITLE 1,Deploy calculate_dti_ratio
# COMMAND ----------

print("Deploying calculate_dti_ratio...")

with open(f"{uc_functions_dir}/02_calculate_dti_ratio.sql", "r") as f:
    sql = f.read()
    sql = sql.split("-- ============================================================================\n-- Test Cases")[0]
    spark.sql(sql)

print("✓ Function deployed: mortgage.finance.calculate_dti_ratio")

# COMMAND ----------

# DBTITLE 1,Test calculate_dti_ratio
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Test the function
# MAGIC SELECT 
# MAGIC   mortgage.finance.calculate_dti_ratio(8000, 2400) AS dti_ratio_30pct,
# MAGIC   mortgage.finance.calculate_dti_ratio(10000, 4300) AS dti_ratio_43pct;

# COMMAND ----------

# DBTITLE 1,Deploy calculate_ltv_ratio
# COMMAND ----------

print("Deploying calculate_ltv_ratio...")

with open(f"{uc_functions_dir}/03_calculate_ltv_ratio.sql", "r") as f:
    sql = f.read()
    sql = sql.split("-- ============================================================================\n-- Test Cases")[0]
    spark.sql(sql)

print("✓ Function deployed: mortgage.finance.calculate_ltv_ratio")

# COMMAND ----------

# DBTITLE 1,Test calculate_ltv_ratio
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Test the function
# MAGIC SELECT 
# MAGIC   mortgage.finance.calculate_ltv_ratio(240000, 300000) AS ltv_ratio_80pct,
# MAGIC   mortgage.finance.calculate_ltv_ratio(285000, 300000) AS ltv_ratio_95pct;

# COMMAND ----------

# DBTITLE 1,Deploy check_eligibility
# COMMAND ----------

print("Deploying check_eligibility...")

with open(f"{uc_functions_dir}/04_check_eligibility.sql", "r") as f:
    sql = f.read()
    sql = sql.split("-- ============================================================================\n-- Test Cases")[0]
    spark.sql(sql)

print("✓ Function deployed: mortgage.finance.check_eligibility")

# COMMAND ----------

# DBTITLE 1,Test check_eligibility
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Test the function
# MAGIC SELECT 
# MAGIC   mortgage.finance.check_eligibility(740, 35.0, 80.0, 'conventional') AS eligible_conventional,
# MAGIC   mortgage.finance.check_eligibility(590, 45.0, 85.0, 'conventional') AS ineligible_credit_low,
# MAGIC   mortgage.finance.check_eligibility(620, 48.0, 93.5, 'fha') AS eligible_fha;

# COMMAND ----------

# DBTITLE 1,List All Functions
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- List all functions in the finance schema
# MAGIC SHOW FUNCTIONS IN mortgage.finance;

# COMMAND ----------

# DBTITLE 1,Summary
# COMMAND ----------

print("="*70)
print("Unity Catalog Functions Deployed Successfully!")
print("="*70)
print("\nFunctions created in mortgage.finance:")
print("  1. calculate_monthly_payment(loan_amount, annual_rate, years)")
print("  2. calculate_dti_ratio(monthly_gross_income, monthly_debt_payments)")
print("  3. calculate_ltv_ratio(loan_amount, property_value)")
print("  4. check_eligibility(credit_score, dti_ratio, ltv_ratio, loan_type)")
print("\nThese functions can now be used by:")
print("  • Financial Analytics Agent")
print("  • SQL queries in notebooks")
print("  • MCP server system.ai.python_exec")
print("  • Any Spark SQL query")
print("\nNext steps:")
print("  1. Run: %run ./04_setup_vector_search")
print("  2. Run: %run ./05_apply_governance")
print("="*70)

# COMMAND ----------

