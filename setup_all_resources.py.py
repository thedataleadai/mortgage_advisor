# Databricks notebook source
# DBTITLE 1,Mortgage Advisor - Complete Setup
# MAGIC %md
# MAGIC # Mortgage Advisor - Complete Infrastructure Setup
# MAGIC
# MAGIC This notebook orchestrates the complete setup of the Mortgage Advisor system:
# MAGIC
# MAGIC 1. **Catalog & Schemas** - Creates mortgage catalog structure
# MAGIC 2. **Sample Data** - Loads customer, product, compliance, and document data
# MAGIC 3. **UC Functions** - Deploys financial calculation functions
# MAGIC 4. **Permissions** - Grants app service principal access to all resources
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC * Databricks workspace with Unity Catalog enabled
# MAGIC * Appropriate admin permissions to create catalogs and grant permissions
# MAGIC * Mortgage Advisor app deployed (agent-mortgage-advisor-2)
# MAGIC
# MAGIC **Run Time:** ~5-10 minutes

# COMMAND ----------

# DBTITLE 1,Configuration
# Configuration
import os
from datetime import datetime

# App service principal (from apps get output)
APP_SERVICE_PRINCIPAL = "app-ynf0vl agent-mortgage-advisor-2"
APP_NAME = "agent-mortgage-advisor-2"

# Paths
SETUP_DIR = "/Workspace/Users/paul.karikari@thedatalead.ai/mortgage advisor/scripts/setup"
UC_FUNCTIONS_DIR = "/Workspace/Users/paul.karikari@thedatalead.ai/mortgage advisor/scripts/uc_functions"

print("="*70)
print("MORTGAGE ADVISOR - COMPLETE SETUP")
print("="*70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"App: {APP_NAME}")
print(f"Service Principal: {APP_SERVICE_PRINCIPAL}")
print("="*70)

# COMMAND ----------

# DBTITLE 1,Step 1: Create Catalog and Schemas
# MAGIC %md
# MAGIC ## Step 1: Create Catalog and Schemas
# MAGIC
# MAGIC Creates the `mortgage` catalog with schemas:
# MAGIC * `customer_data` - Customer profiles and application history
# MAGIC * `products` - Mortgage product catalog
# MAGIC * `compliance` - Compliance rules and regulations
# MAGIC * `documents` - Document storage tables
# MAGIC * `finance` - Financial calculation functions

# COMMAND ----------

# DBTITLE 1,Run 01_setup_catalog
print("\n📦 Step 1/4: Creating Catalog and Schemas")
print("-" * 70)

try:
    result = dbutils.notebook.run(
        f"{SETUP_DIR}/01_setup_catalog.py",
        timeout_seconds=300
    )
    print("✅ Catalog and schemas created successfully")
    if result:
        print(f"   Result: {result}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    raise

# COMMAND ----------

# DBTITLE 1,Step 2: Load Sample Data
# MAGIC %md
# MAGIC ## Step 2: Load Sample Data
# MAGIC
# MAGIC Loads sample data into tables:
# MAGIC * Customer profiles and application history
# MAGIC * Mortgage products from various lenders
# MAGIC * Compliance rules (DTI, LTV, credit score requirements)
# MAGIC * Document metadata (applications, bank statements, payslips, property docs)

# COMMAND ----------

# DBTITLE 1,Run 02_load_data
print("\n📊 Step 2/4: Loading Sample Data")
print("-" * 70)

try:
    result = dbutils.notebook.run(
        f"{SETUP_DIR}/02_load_data.py",
        timeout_seconds=600
    )
    print("✅ Sample data loaded successfully")
    if result:
        print(f"   Result: {result}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    raise

# COMMAND ----------

# DBTITLE 1,Step 3: Create UC Functions
# MAGIC %md
# MAGIC ## Step 3: Create Unity Catalog Functions
# MAGIC
# MAGIC Deploys SQL-based financial calculation functions:
# MAGIC * `calculate_monthly_payment` - Monthly mortgage payment calculator
# MAGIC * `calculate_dti_ratio` - Debt-to-income ratio
# MAGIC * `calculate_ltv_ratio` - Loan-to-value ratio
# MAGIC * `check_eligibility` - Eligibility checker for different loan types

# COMMAND ----------

# DBTITLE 1,Deploy UC Functions
print("\n⚙️  Step 3/4: Creating Unity Catalog Functions")
print("-" * 70)

functions = [
    "01_calculate_monthly_payment.sql",
    "02_calculate_dti_ratio.sql",
    "03_calculate_ltv_ratio.sql",
    "04_check_eligibility.sql"
]

for func_file in functions:
    func_name = func_file.replace('.sql', '').replace('_', ' ').title()
    print(f"\nDeploying {func_name}...")
    try:
        with open(f"{UC_FUNCTIONS_DIR}/{func_file}", "r") as f:
            sql = f.read()
            # Extract only the CREATE FUNCTION statement
            sql = sql.split("-- ============================================================================\n-- Test Cases")[0]
            spark.sql(sql)
        print(f"   ✓ Function deployed")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        raise

print("\n✅ All UC functions created successfully")

# COMMAND ----------

# DBTITLE 1,Step 4: Grant Permissions
# MAGIC %md
# MAGIC ## Step 4: Grant Permissions to App Service Principal
# MAGIC
# MAGIC Grants the app's service principal access to:
# MAGIC * **Catalog & Schemas** - USE CATALOG and USE SCHEMA
# MAGIC * **Tables** - SELECT on all mortgage tables
# MAGIC * **Functions** - EXECUTE on all finance functions
# MAGIC
# MAGIC This allows the app to query data and call UC functions on behalf of users.

# COMMAND ----------

# DBTITLE 1,Grant Catalog and Schema Permissions
print("\n🔐 Step 4/4: Granting Permissions to App Service Principal")
print("-" * 70)
print(f"Service Principal: {APP_SERVICE_PRINCIPAL}")
print()

try:
    # Catalog and Schema Access
    print("Granting catalog and schema access...")
    schemas = ['customer_data', 'products', 'compliance', 'documents', 'finance']
    
    spark.sql(f"GRANT USE CATALOG ON CATALOG mortgage TO `{APP_SERVICE_PRINCIPAL}`")
    print("   ✓ Catalog access granted")
    
    for schema in schemas:
        spark.sql(f"GRANT USE SCHEMA ON SCHEMA mortgage.{schema} TO `{APP_SERVICE_PRINCIPAL}`")
    print(f"   ✓ Schema access granted ({len(schemas)} schemas)")
    
except Exception as e:
    print(f"   ⚠️  Warning: {str(e)}")
    print("   Note: App service principal may not be recognized yet.")
    print("   You can grant permissions manually via Catalog Explorer.")

# COMMAND ----------

# DBTITLE 1,Grant Table Permissions
try:
    print("\nGranting table permissions...")
    
    tables = [
        "mortgage.customer_data.customer_profiles",
        "mortgage.customer_data.application_history",
        "mortgage.products.lender_products",
        "mortgage.compliance.rules",
        "mortgage.documents.mortgage_documents",
        "mortgage.documents.property_documents",
        "mortgage.documents.bank_statements",
        "mortgage.documents.payslips"
    ]
    
    for table in tables:
        spark.sql(f"GRANT SELECT ON TABLE {table} TO `{APP_SERVICE_PRINCIPAL}`")
    
    print(f"   ✓ Table permissions granted ({len(tables)} tables)")
    
except Exception as e:
    print(f"   ⚠️  Warning: {str(e)}")
    print("   Tables exist but app principal may not be recognized yet.")

# COMMAND ----------

# DBTITLE 1,Grant Function Permissions
try:
    print("\nGranting function permissions...")
    
    functions = [
        "mortgage.finance.calculate_monthly_payment",
        "mortgage.finance.calculate_dti_ratio",
        "mortgage.finance.calculate_ltv_ratio",
        "mortgage.finance.check_eligibility"
    ]
    
    for function in functions:
        spark.sql(f"GRANT EXECUTE ON FUNCTION {function} TO `{APP_SERVICE_PRINCIPAL}`")
    
    print(f"   ✓ Function permissions granted ({len(functions)} functions)")
    
except Exception as e:
    print(f"   ⚠️  Warning: {str(e)}")
    print("   Functions exist but app principal may not be recognized yet.")

# COMMAND ----------

# DBTITLE 1,Verification and Summary
# MAGIC %md
# MAGIC ## Verification and Summary
# MAGIC
# MAGIC Verify that all resources were created successfully and provide a complete summary.

# COMMAND ----------

# DBTITLE 1,Verify Resources
print("\n" + "="*70)
print("VERIFICATION")
print("="*70)

# Check schemas
schemas = spark.sql("SHOW SCHEMAS IN mortgage").collect()
print(f"\n✅ Schemas: {len(schemas)}")
for schema in schemas:
    if schema.databaseName not in ['information_schema', 'default']:
        print(f"   • mortgage.{schema.databaseName}")

# Check tables
print("\n✅ Tables:")
for schema_name in ['customer_data', 'products', 'compliance', 'documents']:
    try:
        tables = spark.sql(f"SHOW TABLES IN mortgage.{schema_name}").collect()
        for table in tables:
            print(f"   • mortgage.{schema_name}.{table.tableName}")
    except:
        pass

# Check functions
print("\n✅ UC Functions:")
try:
    spark.sql("USE CATALOG mortgage")
    functions = spark.sql("SHOW FUNCTIONS IN finance").collect()
    for func in functions:
        if 'mortgage.finance' in func.function:
            print(f"   • {func.function}")
except Exception as e:
    print(f"   Error listing functions: {e}")

# COMMAND ----------

# DBTITLE 1,Final Summary
print("\n" + "="*70)
print("SETUP COMPLETE")
print("="*70)
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("✅ Infrastructure Ready:")
print("   • Catalog: mortgage")
print("   • Schemas: 5 (customer_data, products, compliance, documents, finance)")
print("   • Tables: 8 (with sample data)")
print("   • UC Functions: 4 (financial calculations)")
print()
print("⚠️  Permissions:")
print("   If permission grants failed, manually grant in Catalog Explorer:")
print(f"   1. Navigate to mortgage catalog")
print(f"   2. Add principal: {APP_SERVICE_PRINCIPAL}")
print(f"   3. Grant: USE CATALOG, USE SCHEMA, SELECT on tables, EXECUTE on functions")
print()
print("🚀 Next Steps:")
print(f"   1. Open app: https://agent-mortgage-advisor-2-2893683289492793.aws.databricksapps.com")
print(f"   2. Test the 6-agent system with mortgage queries")
print(f"   3. View MLflow traces: /Users/paul.karikari@thedatalead.ai/mortgage-advisor")
print(f"   4. Run demo: mortgage advisor/notebooks/demo/mortgage_advisor_demo.py")
print("="*70)

# COMMAND ----------

