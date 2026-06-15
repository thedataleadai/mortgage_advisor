# Databricks notebook source
# DBTITLE 1,Setup Unity Catalog Structure
# Databricks notebook source
# MAGIC %md
# MAGIC # Unity Catalog Setup for Mortgage Advisor System
# MAGIC 
# MAGIC This notebook creates the Unity Catalog structure for the mortgage advisor demonstration:
# MAGIC 
# MAGIC * **Catalog:** `mortgage`
# MAGIC * **Schemas:**
# MAGIC   * `finance` - Mortgage calculation functions and financial data
# MAGIC   * `customer_data` - Customer profiles and applications
# MAGIC   * `products` - Lender products and rates
# MAGIC   * `compliance` - Regulatory rules and checks
# MAGIC   * `documents` - Document metadata and extracts
# MAGIC 
# MAGIC **Run this notebook first before loading data or creating functions.**

# COMMAND ----------

# DBTITLE 1,Create Catalog
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Create mortgage catalog
# MAGIC CREATE CATALOG IF NOT EXISTS mortgage
# MAGIC COMMENT 'Mortgage advisor system - Customer data, products, compliance, and analytics';
# MAGIC
# MAGIC USE CATALOG mortgage;
# MAGIC
# MAGIC SELECT 'Catalog created: mortgage' AS status;

# COMMAND ----------

# DBTITLE 1,Create Finance Schema
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Finance schema for calculation functions and financial analytics
# MAGIC CREATE SCHEMA IF NOT EXISTS mortgage.finance
# MAGIC COMMENT 'Mortgage calculation functions (monthly payment, DTI, LTV, eligibility)';
# MAGIC
# MAGIC SELECT 'Schema created: mortgage.finance' AS status;

# COMMAND ----------

# DBTITLE 1,Create Customer Data Schema
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Customer data schema
# MAGIC CREATE SCHEMA IF NOT EXISTS mortgage.customer_data
# MAGIC COMMENT 'Customer profiles, applications, and financial information';
# MAGIC
# MAGIC SELECT 'Schema created: mortgage.customer_data' AS status;

# COMMAND ----------

# DBTITLE 1,Create Products Schema
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Products schema for lender products
# MAGIC CREATE SCHEMA IF NOT EXISTS mortgage.products
# MAGIC COMMENT 'Lender mortgage products, rates, and offerings';
# MAGIC
# MAGIC SELECT 'Schema created: mortgage.products' AS status;

# COMMAND ----------

# DBTITLE 1,Create Compliance Schema
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Compliance schema
# MAGIC CREATE SCHEMA IF NOT EXISTS mortgage.compliance
# MAGIC COMMENT 'Regulatory compliance rules, AML checks, and lending criteria';
# MAGIC
# MAGIC SELECT 'Schema created: mortgage.compliance' AS status;

# COMMAND ----------

# DBTITLE 1,Create Documents Schema
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Documents schema
# MAGIC CREATE SCHEMA IF NOT EXISTS mortgage.documents
# MAGIC COMMENT 'Document metadata for payslips, bank statements, property docs, and mortgage docs';
# MAGIC
# MAGIC SELECT 'Schema created: mortgage.documents' AS status;

# COMMAND ----------

# DBTITLE 1,Verify Catalog Structure
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Verify all schemas were created
# MAGIC SHOW SCHEMAS IN mortgage;

# COMMAND ----------

# DBTITLE 1,Summary
# COMMAND ----------

print("="*70)
print("Unity Catalog Setup Complete!")
print("="*70)
print("\nCatalog: mortgage")
print("\nSchemas created:")
print("  1. finance - Calculation functions")
print("  2. customer_data - Customer profiles and applications")
print("  3. products - Lender products and rates")
print("  4. compliance - Regulatory rules")
print("  5. documents - Document metadata")
print("\nNext steps:")
print("  1. Run: %run ./02_load_data")
print("  2. Run: %run ./03_create_uc_functions")
print("="*70)

# COMMAND ----------

