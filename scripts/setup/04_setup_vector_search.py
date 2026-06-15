# Databricks notebook source
# DBTITLE 1,Vector Search Setup for Mortgage Advisor
# Databricks notebook source
# MAGIC %md
# MAGIC # Vector Search Setup for Mortgage Advisor System
# MAGIC 
# MAGIC This notebook sets up vector search capabilities for semantic document retrieval:
# MAGIC 
# MAGIC **Use Cases:**
# MAGIC 1. **Compliance Rule Matching** - Find relevant regulations based on customer situation
# MAGIC 2. **Product Recommendations** - Semantic search over mortgage product descriptions
# MAGIC 3. **Document Analysis** - Similar document retrieval for validation
# MAGIC 
# MAGIC **Vector Search Indexes:**
# MAGIC * `mortgage_compliance_rules_index` - Compliance rules and regulations
# MAGIC * `mortgage_products_index` - Lender product descriptions
# MAGIC 
# MAGIC **Prerequisites:** 
# MAGIC * Run `01_setup_catalog` and `02_load_data` first
# MAGIC * Databricks Runtime with Vector Search enabled

# COMMAND ----------

# MAGIC %pip install databricks-vectorsearch

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Setup - Import libraries and configure
# COMMAND ----------

import re
from pyspark.sql.functions import col, concat_ws, lit
from databricks.vector_search.client import VectorSearchClient

# Initialize Vector Search client
vs_client = VectorSearchClient()

# Configuration
CATALOG = "mortgage"
SCHEMA = "compliance"
ENDPOINT_NAME = "mortgage_vector_search_endpoint"

print(f"Catalog: {CATALOG}")
print(f"Schema: {SCHEMA}")
print(f"Endpoint: {ENDPOINT_NAME}")

# COMMAND ----------

# DBTITLE 1,Create Vector Search Endpoint
# COMMAND ----------

print("Creating Vector Search endpoint...")

try:
    # Try to create the endpoint
    vs_client.create_endpoint(
        name=ENDPOINT_NAME,
        endpoint_type="STANDARD"
    )
    print(f"✓ Created endpoint: {ENDPOINT_NAME}")
except Exception as e:
    if "already exists" in str(e).lower():
        print(f"✓ Endpoint already exists: {ENDPOINT_NAME}")
    else:
        print(f"Error creating endpoint: {e}")
        raise

# Wait for endpoint to be ready
import time
for i in range(30):
    endpoint_info = vs_client.get_endpoint(ENDPOINT_NAME)
    if endpoint_info.get('endpoint_status', {}).get('state') == 'ONLINE':
        print(f"✓ Endpoint is ONLINE")
        break
    print(f"Waiting for endpoint to be ready... ({i+1}/30)")
    time.sleep(10)
else:
    print("⚠ Endpoint not ready after 5 minutes, but continuing...")

# COMMAND ----------

# DBTITLE 1,Prepare Compliance Rules for Vector Search
# COMMAND ----------

print("Preparing compliance rules table for vector search...")

# Create a view with combined text for embedding
spark.sql(f"""
CREATE OR REPLACE TABLE {CATALOG}.{SCHEMA}.rules_for_vector_search AS
SELECT 
  rule_id,
  rule_category,
  rule_name,
  rule_description,
  severity,
  CONCAT(
    'Category: ', rule_category, '. ',
    'Rule: ', rule_name, '. ',
    'Description: ', rule_description
  ) AS combined_text
FROM {CATALOG}.{SCHEMA}.rules
""")

df_rules = spark.table(f"{CATALOG}.{SCHEMA}.rules_for_vector_search")
print(f"✓ Prepared {df_rules.count()} compliance rules")
display(df_rules.limit(3))

# COMMAND ----------

# DBTITLE 1,Create Compliance Rules Vector Search Index
# COMMAND ----------

print("Creating vector search index for compliance rules...")

INDEX_NAME = f"{CATALOG}.{SCHEMA}.compliance_rules_vs_index"
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.rules_for_vector_search"

# Enable Change Data Feed on the source table (required for Vector Search)
print("Enabling Change Data Feed on source table...")
spark.sql(f"ALTER TABLE {SOURCE_TABLE} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")
print("✓ Change Data Feed enabled")

try:
    # Create delta sync index with managed embeddings
    vs_client.create_delta_sync_index(
        endpoint_name=ENDPOINT_NAME,
        index_name=INDEX_NAME,
        source_table_name=SOURCE_TABLE,
        pipeline_type="TRIGGERED",
        primary_key="rule_id",
        embedding_source_column="combined_text",
        embedding_model_endpoint_name="databricks-bge-large-en"  # Databricks Foundation Model
    )
    print(f"✓ Created index: {INDEX_NAME}")
except Exception as e:
    if "already exists" in str(e).lower():
        print(f"✓ Index already exists: {INDEX_NAME}")
    else:
        print(f"Error creating index: {e}")
        raise

print("\nWaiting for index to sync...")
time.sleep(5)

# COMMAND ----------

# DBTITLE 1,Test Compliance Rules Vector Search
# COMMAND ----------

print("Testing compliance rules vector search...\n")

# Test query 1: Income verification
query1 = "How do I verify a borrower's income and employment?"
results1 = vs_client.get_index(ENDPOINT_NAME, INDEX_NAME).similarity_search(
    query_text=query1,
    columns=["rule_id", "rule_name", "description", "requirement"],
    num_results=3
)

print(f"Query: {query1}")
print("\nTop 3 Results:")
for i, result in enumerate(results1.get('result', {}).get('data_array', []), 1):
    print(f"\n{i}. {result[1]}")
    print(f"   {result[2][:100]}...")

print("\n" + "="*70)

# Test query 2: Debt-to-income ratio
query2 = "What are the DTI requirements for conventional loans?"
results2 = vs_client.get_index(ENDPOINT_NAME, INDEX_NAME).similarity_search(
    query_text=query2,
    columns=["rule_id", "rule_name", "requirement"],
    num_results=2
)

print(f"\nQuery: {query2}")
print("\nTop 2 Results:")
for i, result in enumerate(results2.get('result', {}).get('data_array', []), 1):
    print(f"\n{i}. {result[1]}")
    print(f"   Requirement: {result[2][:150]}...")

# COMMAND ----------

# DBTITLE 1,Prepare Lender Products for Vector Search
# COMMAND ----------

print("Preparing lender products table for vector search...")

# Create a view with combined text for embedding
spark.sql(f"""
CREATE OR REPLACE TABLE {CATALOG}.products.products_for_vector_search AS
SELECT 
  product_id,
  lender_name,
  product_name,
  product_type,
  interest_rate,
  term_years,
  min_credit_score,
  max_ltv_ratio,
  description,
  CONCAT(
    'Lender: ', lender_name, '. ',
    'Product: ', product_name, '. ',
    'Type: ', product_type, '. ',
    'Rate: ', CAST(interest_rate AS STRING), '%. ',
    'Term: ', CAST(term_years AS STRING), ' years. ',
    'Min Credit: ', CAST(min_credit_score AS STRING), '. ',
    'Max LTV: ', CAST(max_ltv_ratio AS STRING), '%. ',
    COALESCE(CONCAT('Features: ', description), '')
  ) AS combined_text
FROM {CATALOG}.products.lender_products
""")

df_products = spark.table(f"{CATALOG}.products.products_for_vector_search")
print(f"✓ Prepared {df_products.count()} lender products")
display(df_products.limit(3))

# COMMAND ----------

# DBTITLE 1,Create Lender Products Vector Search Index
# COMMAND ----------

print("Creating vector search index for lender products...")

PRODUCTS_INDEX_NAME = f"{CATALOG}.products.lender_products_vs_index"
PRODUCTS_SOURCE_TABLE = f"{CATALOG}.products.products_for_vector_search"

# Enable Change Data Feed on the source table (required for Vector Search)
print("Enabling Change Data Feed on source table...")
spark.sql(f"ALTER TABLE {PRODUCTS_SOURCE_TABLE} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")
print("✓ Change Data Feed enabled")

try:
    vs_client.create_delta_sync_index(
        endpoint_name=ENDPOINT_NAME,
        index_name=PRODUCTS_INDEX_NAME,
        source_table_name=PRODUCTS_SOURCE_TABLE,
        pipeline_type="TRIGGERED",
        primary_key="product_id",
        embedding_source_column="combined_text",
        embedding_model_endpoint_name="databricks-bge-large-en"
    )
    print(f"✓ Created index: {PRODUCTS_INDEX_NAME}")
except Exception as e:
    if "already exists" in str(e).lower():
        print(f"✓ Index already exists: {PRODUCTS_INDEX_NAME}")
    else:
        print(f"Error creating index: {e}")
        raise

print("\nWaiting for index to sync...")
time.sleep(5)

# COMMAND ----------

# DBTITLE 1,Test Lender Products Vector Search
# COMMAND ----------

print("Testing lender products vector search...\n")

# Test query 1: First-time buyer
query1 = "I'm a first-time homebuyer with a 680 credit score looking for low down payment options"
results1 = vs_client.get_index(ENDPOINT_NAME, PRODUCTS_INDEX_NAME).similarity_search(
    query_text=query1,
    columns=["product_id", "lender_name", "product_name", "loan_type", "interest_rate", "special_features"],
    num_results=3
)

print(f"Query: {query1}")
print("\nTop 3 Matching Products:")
for i, result in enumerate(results1.get('result', {}).get('data_array', []), 1):
    print(f"\n{i}. {result[2]} by {result[1]}")
    print(f"   Type: {result[3]} | Rate: {result[4]}%")
    print(f"   Features: {result[5] if result[5] else 'Standard'}")

print("\n" + "="*70)

# Test query 2: VA loan
query2 = "Military veteran looking for zero down payment mortgage options"
results2 = vs_client.get_index(ENDPOINT_NAME, PRODUCTS_INDEX_NAME).similarity_search(
    query_text=query2,
    columns=["product_id", "lender_name", "product_name", "loan_type"],
    num_results=2
)

print(f"\nQuery: {query2}")
print("\nTop 2 Matching Products:")
for i, result in enumerate(results2.get('result', {}).get('data_array', []), 1):
    print(f"\n{i}. {result[2]} by {result[1]}")
    print(f"   Type: {result[3]}")

# COMMAND ----------

# DBTITLE 1,Integration Example - Python Function
# COMMAND ----------

# MAGIC %md
# MAGIC ## Integration with Agent System
# MAGIC 
# MAGIC Example functions to integrate vector search with the agent tools:

print("Example integration functions for agent tools:\n")

def search_compliance_rules(query: str, num_results: int = 3) -> list:
    """
    Search compliance rules using semantic vector search.
    
    Args:
        query: Natural language query about compliance requirements
        num_results: Number of results to return
    
    Returns:
        List of matching compliance rules
    """
    vs_client = VectorSearchClient()
    index = vs_client.get_index(ENDPOINT_NAME, INDEX_NAME)
    
    results = index.similarity_search(
        query_text=query,
        columns=["rule_id", "rule_name", "description", "requirement", "severity"],
        num_results=num_results
    )
    
    return results.get('result', {}).get('data_array', [])

def search_mortgage_products(query: str, num_results: int = 5) -> list:
    """
    Search mortgage products using semantic vector search.
    
    Args:
        query: Natural language description of customer needs
        num_results: Number of products to return
    
    Returns:
        List of matching mortgage products
    """
    vs_client = VectorSearchClient()
    index = vs_client.get_index(ENDPOINT_NAME, PRODUCTS_INDEX_NAME)
    
    results = index.similarity_search(
        query_text=query,
        columns=["product_id", "lender_name", "product_name", "loan_type", 
                 "interest_rate", "term_years", "min_credit_score", "max_ltv", "special_features"],
        num_results=num_results
    )
    
    return results.get('result', {}).get('data_array', [])

print("✓ Integration functions defined")
print("\nThese functions can be added to:")
print("  • Compliance Agent - search_compliance_rules()")
print("  • Product Matching Agent - search_mortgage_products()")

# COMMAND ----------

# DBTITLE 1,Test Integration Functions
# COMMAND ----------

print("Testing integration functions...\n")

# Test compliance search
print("1. Compliance Rule Search:")
query = "credit score requirements for FHA loans"
rules = search_compliance_rules(query, num_results=2)
print(f"\nQuery: '{query}'")
for i, rule in enumerate(rules, 1):
    print(f"\n  {i}. {rule[1]}")
    print(f"     {rule[2][:80]}...")

print("\n" + "="*70)

# Test product search
print("\n2. Product Search:")
query = "refinancing with low credit score"
products = search_mortgage_products(query, num_results=3)
print(f"\nQuery: '{query}'")
for i, product in enumerate(products, 1):
    print(f"\n  {i}. {product[2]} ({product[1]})")
    print(f"     Type: {product[3]} | Rate: {product[4]}% | Min Credit: {product[6]}")

# COMMAND ----------

# DBTITLE 1,Summary and Next Steps
# COMMAND ----------

print("="*70)
print("Vector Search Setup Complete!")
print("="*70)
print("\nVector Search Endpoint:")
print(f"  • {ENDPOINT_NAME}")
print("\nVector Search Indexes:")
print(f"  1. {INDEX_NAME}")
print(f"     - 12 compliance rules indexed")
print(f"     - Semantic search for regulatory requirements")
print(f"  2. {PRODUCTS_INDEX_NAME}")
print(f"     - 15 lender products indexed")
print(f"     - Semantic product recommendations")
print("\nIntegration Points:")
print("  • Compliance Agent - Use search_compliance_rules()")
print("  • Product Matching Agent - Use search_mortgage_products()")
print("  • Document Processing Agent - Can add document similarity search")
print("\nEmbedding Model:")
print("  • databricks-bge-large-en (Databricks Foundation Model)")
print("\nNext Steps:")
print("  1. Add vector search functions to agent_server/agent.py")
print("  2. Update agent tool definitions")
print("  3. Test semantic search in agent workflows")
print("  4. Run: %run ./05_apply_governance")
print("="*70)

# COMMAND ----------

