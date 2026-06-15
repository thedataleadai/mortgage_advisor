# Databricks notebook source
# DBTITLE 1,Unity Catalog Governance Features
# Databricks notebook source
# MAGIC %md
# MAGIC # Unity Catalog Governance for Mortgage Advisor System
# MAGIC 
# MAGIC This notebook demonstrates Unity Catalog governance features:
# MAGIC 
# MAGIC ## 1. **Row-Level Security (RLS)**
# MAGIC    - Restrict customer data by region
# MAGIC    - Advisor-specific data access
# MAGIC    - Branch-level filtering
# MAGIC 
# MAGIC ## 2. **Column Masking**
# MAGIC    - Mask sensitive PII (SSN, account numbers)
# MAGIC    - Partial masking for income data
# MAGIC    - Email and phone number redaction
# MAGIC 
# MAGIC ## 3. **Governance Tags**
# MAGIC    - PII classification tags
# MAGIC    - Data sensitivity levels
# MAGIC    - Regulatory compliance tags
# MAGIC 
# MAGIC **Prerequisites:** 
# MAGIC * Unity Catalog workspace
# MAGIC * Admin or appropriate permissions to set policies

# COMMAND ----------

# DBTITLE 1,Setup
# COMMAND ----------

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

CATALOG = "mortgage"

print("="*70)
print("Unity Catalog Governance Setup")
print("="*70)
print(f"\nCatalog: {CATALOG}")
print("\nThis notebook demonstrates governance features.")
print("Note: Some features require admin privileges.")
print("="*70)

# COMMAND ----------

# DBTITLE 1,Add Region Column for RLS Demo
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Add region column to customer profiles for RLS demonstration
# MAGIC ALTER TABLE mortgage.customer_data.customer_profiles 
# MAGIC ADD COLUMN IF NOT EXISTS region STRING;
# MAGIC
# MAGIC -- Update regions for demo
# MAGIC UPDATE mortgage.customer_data.customer_profiles
# MAGIC SET region = CASE 
# MAGIC   WHEN customer_id IN ('CUST001', 'CUST002', 'CUST003') THEN 'WEST'
# MAGIC   WHEN customer_id IN ('CUST004', 'CUST005', 'CUST006') THEN 'EAST'
# MAGIC   WHEN customer_id IN ('CUST007', 'CUST008') THEN 'CENTRAL'
# MAGIC   ELSE 'SOUTH'
# MAGIC END
# MAGIC WHERE region IS NULL;
# MAGIC
# MAGIC SELECT 'Region column added and populated' AS status;

# COMMAND ----------

# DBTITLE 1,Row-Level Security Example
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- MAGIC %md
# MAGIC -- MAGIC ### Row-Level Security (RLS) Filter
# MAGIC -- MAGIC 
# MAGIC -- MAGIC Example RLS policy that restricts data access by region.
# MAGIC -- MAGIC This would typically be applied using `ALTER TABLE ... SET ROW FILTER`
# MAGIC
# MAGIC -- Example RLS filter function (for documentation)
# MAGIC -- CREATE OR REPLACE FUNCTION mortgage.customer_data.region_filter(region STRING)
# MAGIC -- RETURNS BOOLEAN
# MAGIC -- RETURN 
# MAGIC --   CASE
# MAGIC --     WHEN IS_ACCOUNT_GROUP_MEMBER('west_advisors') THEN region = 'WEST'
# MAGIC --     WHEN IS_ACCOUNT_GROUP_MEMBER('east_advisors') THEN region = 'EAST'
# MAGIC --     WHEN IS_ACCOUNT_GROUP_MEMBER('central_advisors') THEN region = 'CENTRAL'
# MAGIC --     WHEN IS_ACCOUNT_GROUP_MEMBER('south_advisors') THEN region = 'SOUTH'
# MAGIC --     WHEN IS_ACCOUNT_GROUP_MEMBER('admin') THEN TRUE  -- Admins see all
# MAGIC --     ELSE FALSE
# MAGIC --   END;
# MAGIC
# MAGIC -- Apply RLS filter to table (requires admin):
# MAGIC -- ALTER TABLE mortgage.customer_data.customer_profiles
# MAGIC -- SET ROW FILTER mortgage.customer_data.region_filter ON (region);
# MAGIC
# MAGIC SELECT 
# MAGIC   'RLS Example' AS feature,
# MAGIC   'Restricts customer data by advisor region' AS description,
# MAGIC   'Requires group membership: west_advisors, east_advisors, etc.' AS implementation;

# COMMAND ----------

# DBTITLE 1,Verify Region Distribution
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Verify region distribution
# MAGIC SELECT 
# MAGIC   region,
# MAGIC   COUNT(*) AS customer_count,
# MAGIC   ROUND(AVG(annual_income), 2) AS avg_income
# MAGIC FROM mortgage.customer_data.customer_profiles
# MAGIC GROUP BY region
# MAGIC ORDER BY region;

# COMMAND ----------

# DBTITLE 1,Column Masking Examples
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- MAGIC %md
# MAGIC -- MAGIC ### Column Masking Functions
# MAGIC -- MAGIC 
# MAGIC -- MAGIC Examples of masking functions for sensitive PII data:
# MAGIC
# MAGIC -- Create masking functions in the customer_data schema
# MAGIC CREATE OR REPLACE FUNCTION mortgage.customer_data.mask_ssn(ssn STRING)
# MAGIC RETURNS STRING
# MAGIC RETURN 
# MAGIC   CASE
# MAGIC     WHEN IS_ACCOUNT_GROUP_MEMBER('compliance_team') OR IS_ACCOUNT_GROUP_MEMBER('admin') THEN ssn
# MAGIC     ELSE CONCAT('XXX-XX-', RIGHT(ssn, 4))
# MAGIC   END;
# MAGIC
# MAGIC SELECT 'SSN masking function created' AS status;

# COMMAND ----------

# DBTITLE 1,Create Income Masking Function
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC CREATE OR REPLACE FUNCTION mortgage.customer_data.mask_income(income DOUBLE)
# MAGIC RETURNS STRING
# MAGIC RETURN 
# MAGIC   CASE
# MAGIC     WHEN IS_ACCOUNT_GROUP_MEMBER('financial_analysts') OR IS_ACCOUNT_GROUP_MEMBER('admin') THEN CAST(income AS STRING)
# MAGIC     WHEN IS_ACCOUNT_GROUP_MEMBER('advisors') THEN 
# MAGIC       -- Show income range instead of exact value
# MAGIC       CASE
# MAGIC         WHEN income < 50000 THEN '<$50k'
# MAGIC         WHEN income < 100000 THEN '$50k-$100k'
# MAGIC         WHEN income < 150000 THEN '$100k-$150k'
# MAGIC         ELSE '>$150k'
# MAGIC       END
# MAGIC     ELSE 'REDACTED'
# MAGIC   END;
# MAGIC
# MAGIC SELECT 'Income masking function created' AS status;

# COMMAND ----------

# DBTITLE 1,Create Email Masking Function
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC CREATE OR REPLACE FUNCTION mortgage.customer_data.mask_email(email STRING)
# MAGIC RETURNS STRING
# MAGIC RETURN 
# MAGIC   CASE
# MAGIC     WHEN IS_ACCOUNT_GROUP_MEMBER('customer_service') OR IS_ACCOUNT_GROUP_MEMBER('admin') THEN email
# MAGIC     ELSE CONCAT(LEFT(email, 2), '***@', SPLIT(email, '@')[1])
# MAGIC   END;
# MAGIC
# MAGIC SELECT 'Email masking function created' AS status;

# COMMAND ----------

# DBTITLE 1,Test Masking Functions
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Test the masking functions
# MAGIC SELECT 
# MAGIC   'Masking Function Tests' AS test_suite,
# MAGIC   mortgage.customer_data.mask_ssn('123-45-6789') AS masked_ssn,
# MAGIC   mortgage.customer_data.mask_income(75000) AS masked_income_75k,
# MAGIC   mortgage.customer_data.mask_income(125000) AS masked_income_125k,
# MAGIC   mortgage.customer_data.mask_email('john.doe@example.com') AS masked_email;

# COMMAND ----------

# DBTITLE 1,Apply Column Masking Example
# COMMAND ----------

print("""\nColumn Masking Policy Examples\n" + "="*70)

# Example commands to apply column masking (requires admin)
apply_commands = '''
-- Apply SSN masking (if SSN column existed)
-- ALTER TABLE mortgage.customer_data.customer_profiles
-- ALTER COLUMN ssn SET MASK mortgage.customer_data.mask_ssn;

-- Apply income masking
-- ALTER TABLE mortgage.customer_data.customer_profiles
-- ALTER COLUMN annual_income SET MASK mortgage.customer_data.mask_income;

-- Apply email masking  
-- ALTER TABLE mortgage.customer_data.customer_profiles
-- ALTER COLUMN email SET MASK mortgage.customer_data.mask_email;
'''

print(apply_commands)
print("\n" + "="*70)
print("Note: Column masking requires appropriate permissions.")
print("Once applied, different user groups will see masked data automatically.")
print("="*70)

# COMMAND ----------

# DBTITLE 1,Governance Tags - PII Classification
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- MAGIC %md
# MAGIC -- MAGIC ### Governance Tags
# MAGIC -- MAGIC 
# MAGIC -- MAGIC Tag tables and columns with governance metadata:
# MAGIC
# MAGIC -- Tag the customer profiles table as containing PII
# MAGIC ALTER TABLE mortgage.customer_data.customer_profiles
# MAGIC SET TAGS ('data_classification' = 'PII', 'sensitivity' = 'HIGH');
# MAGIC
# MAGIC -- Tag application history with compliance requirements
# MAGIC ALTER TABLE mortgage.customer_data.application_history
# MAGIC SET TAGS ('data_classification' = 'FINANCIAL', 'retention_period' = '7_years');
# MAGIC
# MAGIC SELECT 'Governance tags applied to customer tables' AS status;

# COMMAND ----------

# DBTITLE 1,Governance Tags - Compliance Data
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Tag compliance tables
# MAGIC ALTER TABLE mortgage.compliance.rules
# MAGIC SET TAGS ('data_classification' = 'REGULATORY', 'review_frequency' = 'QUARTERLY');
# MAGIC
# MAGIC -- Tag document tables
# MAGIC ALTER TABLE mortgage.documents.payslips
# MAGIC SET TAGS ('data_classification' = 'PII', 'contains' = 'INCOME_DATA');
# MAGIC
# MAGIC ALTER TABLE mortgage.documents.bank_statements
# MAGIC SET TAGS ('data_classification' = 'FINANCIAL', 'contains' = 'ACCOUNT_DATA');
# MAGIC
# MAGIC SELECT 'Governance tags applied to compliance and document tables' AS status;

# COMMAND ----------

# DBTITLE 1,View Applied Tags
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- View tags on customer profiles table
# MAGIC DESCRIBE EXTENDED mortgage.customer_data.customer_profiles;

# COMMAND ----------

# DBTITLE 1,Governance Summary
# COMMAND ----------

print("="*70)
print("Unity Catalog Governance Features Applied!")
print("="*70)
print("\n1. ROW-LEVEL SECURITY (RLS)")
print("   ✓ Region column added to customer_profiles")
print("   ✓ Example RLS filter function documented")
print("   - Restricts data by advisor region (WEST, EAST, CENTRAL, SOUTH)")
print("   - Admins see all regions")
print("\n2. COLUMN MASKING")
print("   ✓ mask_ssn() - Masks SSN except last 4 digits")
print("   ✓ mask_income() - Shows income ranges instead of exact values")
print("   ✓ mask_email() - Masks email addresses")
print("   - Different user groups see different levels of masking")
print("\n3. GOVERNANCE TAGS")
print("   ✓ customer_profiles - PII, HIGH sensitivity")
print("   ✓ application_history - FINANCIAL, 7-year retention")
print("   ✓ compliance.rules - REGULATORY, quarterly review")
print("   ✓ documents.* - PII/FINANCIAL with content tags")
print("\nGovernance Features by User Role:")
print("  • Advisors: See own region, masked income ranges, masked email")
print("  • Financial Analysts: See all data, exact income, masked PII")
print("  • Compliance Team: See all data including SSN")
print("  • Admins: Full access to all data")
print("\nNext Steps:")
print("  1. Set up user groups in Unity Catalog")
print("  2. Apply RLS filters: ALTER TABLE ... SET ROW FILTER")
print("  3. Apply column masks: ALTER COLUMN ... SET MASK")
print("  4. Create demo notebook showcasing governance")
print("="*70)

# COMMAND ----------

