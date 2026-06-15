# Databricks notebook source
# DBTITLE 1,Load Sample Data into Unity Catalog
# Databricks notebook source
# MAGIC %md
# MAGIC # Load Sample Data into Unity Catalog
# MAGIC 
# MAGIC This notebook loads all CSV sample data into Unity Catalog tables:
# MAGIC 
# MAGIC **Customer Data:**
# MAGIC * `customer_profiles` - Customer demographics and financial info
# MAGIC * `application_history` - Mortgage applications and status
# MAGIC 
# MAGIC **Products:**
# MAGIC * `lender_products` - Mortgage products from various lenders
# MAGIC 
# MAGIC **Compliance:**
# MAGIC * `compliance_rules` - Regulatory compliance rules
# MAGIC 
# MAGIC **Documents:**
# MAGIC * `payslips` - Payslip data
# MAGIC * `bank_statements` - Bank statement data
# MAGIC * `property_documents` - Property appraisals, inspections
# MAGIC * `mortgage_documents` - W2s, tax returns, etc.
# MAGIC 
# MAGIC **Prerequisites:** Run `01_setup_catalog` first

# COMMAND ----------

# DBTITLE 1,Setup - Define paths
# COMMAND ----------

import pandas as pd
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Define paths
base_data_dir = "/Workspace/Users/paul.karikari@thedatalead.ai/mortgage advisor/data"
sample_data_dir = f"{base_data_dir}/sample_data"
documents_dir = f"{base_data_dir}/documents"

print(f"Sample data directory: {sample_data_dir}")
print(f"Documents directory: {documents_dir}")

# COMMAND ----------

# DBTITLE 1,Load Customer Profiles
# COMMAND ----------

print("Loading customer_profiles...")

# Read CSV
df_customers = spark.read.csv(
    f"{sample_data_dir}/customer_profiles.csv",
    header=True,
    inferSchema=True
)

# Write to Unity Catalog
df_customers.write.mode("overwrite").saveAsTable("mortgage.customer_data.customer_profiles")

print(f"✓ Loaded {df_customers.count()} customer profiles")
display(df_customers.limit(5))

# COMMAND ----------

# DBTITLE 1,Load Application History
# COMMAND ----------

print("Loading application_history...")

# Read CSV
df_applications = spark.read.csv(
    f"{sample_data_dir}/application_history.csv",
    header=True,
    inferSchema=True
)

# Write to Unity Catalog
df_applications.write.mode("overwrite").saveAsTable("mortgage.customer_data.application_history")

print(f"✓ Loaded {df_applications.count()} application records")
display(df_applications.limit(5))

# COMMAND ----------

# DBTITLE 1,Load Lender Products
# COMMAND ----------

print("Loading lender_products...")

# Read CSV
df_products = spark.read.csv(
    f"{sample_data_dir}/lender_products.csv",
    header=True,
    inferSchema=True
)

# Write to Unity Catalog
df_products.write.mode("overwrite").saveAsTable("mortgage.products.lender_products")

print(f"✓ Loaded {df_products.count()} lender products")
display(df_products.limit(5))

# COMMAND ----------

# DBTITLE 1,Load Compliance Rules
# COMMAND ----------

print("Loading compliance_rules...")

# Read CSV
df_compliance = spark.read.csv(
    f"{sample_data_dir}/compliance_rules.csv",
    header=True,
    inferSchema=True
)

# Write to Unity Catalog
df_compliance.write.mode("overwrite").saveAsTable("mortgage.compliance.rules")

print(f"✓ Loaded {df_compliance.count()} compliance rules")
display(df_compliance.limit(5))

# COMMAND ----------

# DBTITLE 1,Load Document Data
# COMMAND ----------

print("Loading document data...")

# Payslips
df_payslips = spark.read.csv(
    f"{documents_dir}/payslips.csv",
    header=True,
    inferSchema=True
)
df_payslips.write.mode("overwrite").saveAsTable("mortgage.documents.payslips")
print(f"✓ Loaded {df_payslips.count()} payslip records")

# Bank statements
df_bank = spark.read.csv(
    f"{documents_dir}/bank_statements.csv",
    header=True,
    inferSchema=True
)
df_bank.write.mode("overwrite").saveAsTable("mortgage.documents.bank_statements")
print(f"✓ Loaded {df_bank.count()} bank statement records")

# Property documents
df_property = spark.read.csv(
    f"{documents_dir}/property_documents.csv",
    header=True,
    inferSchema=True
)
df_property.write.mode("overwrite").saveAsTable("mortgage.documents.property_documents")
print(f"✓ Loaded {df_property.count()} property document records")

# Mortgage documents
df_mortgage_docs = spark.read.csv(
    f"{documents_dir}/mortgage_documents.csv",
    header=True,
    inferSchema=True
)
df_mortgage_docs.write.mode("overwrite").saveAsTable("mortgage.documents.mortgage_documents")
print(f"✓ Loaded {df_mortgage_docs.count()} mortgage document records")

# COMMAND ----------

# DBTITLE 1,Verify All Tables
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Verify customer data tables
# MAGIC SELECT 'customer_profiles' AS table_name, COUNT(*) AS row_count FROM mortgage.customer_data.customer_profiles
# MAGIC UNION ALL
# MAGIC SELECT 'application_history', COUNT(*) FROM mortgage.customer_data.application_history
# MAGIC UNION ALL
# MAGIC -- Verify products
# MAGIC SELECT 'lender_products', COUNT(*) FROM mortgage.products.lender_products
# MAGIC UNION ALL
# MAGIC -- Verify compliance
# MAGIC SELECT 'compliance_rules', COUNT(*) FROM mortgage.compliance.rules
# MAGIC UNION ALL
# MAGIC -- Verify documents
# MAGIC SELECT 'payslips', COUNT(*) FROM mortgage.documents.payslips
# MAGIC UNION ALL
# MAGIC SELECT 'bank_statements', COUNT(*) FROM mortgage.documents.bank_statements
# MAGIC UNION ALL
# MAGIC SELECT 'property_documents', COUNT(*) FROM mortgage.documents.property_documents
# MAGIC UNION ALL
# MAGIC SELECT 'mortgage_documents', COUNT(*) FROM mortgage.documents.mortgage_documents;

# COMMAND ----------

# DBTITLE 1,Summary
# COMMAND ----------

print("="*70)
print("Data Loading Complete!")
print("="*70)
print("\nTables created:")
print("\nCustomer Data:")
print("  • mortgage.customer_data.customer_profiles")
print("  • mortgage.customer_data.application_history")
print("\nProducts:")
print("  • mortgage.products.lender_products")
print("\nCompliance:")
print("  • mortgage.compliance.rules")
print("\nDocuments:")
print("  • mortgage.documents.payslips")
print("  • mortgage.documents.bank_statements")
print("  • mortgage.documents.property_documents")
print("  • mortgage.documents.mortgage_documents")
print("\nNext steps:")
print("  1. Run: %run ./03_create_uc_functions")
print("  2. Run: %run ./04_setup_vector_search")
print("  3. Run: %run ./05_apply_governance")
print("="*70)

# COMMAND ----------

