# Databricks notebook source
# DBTITLE 1,Mortgage Advisor System - Complete Demo
# Databricks notebook source
# MAGIC %md
# MAGIC # Mortgage Advisor Multi-Agent System - Complete Demonstration
# MAGIC 
# MAGIC This notebook demonstrates the complete mortgage advisor system with:
# MAGIC 
# MAGIC ## 🏗️ System Architecture
# MAGIC * **6 Specialized Agents** working collaboratively
# MAGIC * **Unity Catalog** for data governance
# MAGIC * **Vector Search** for intelligent document retrieval
# MAGIC * **MLflow Tracing** for observability
# MAGIC 
# MAGIC ## 🎯 Demo Scenarios
# MAGIC 1. **Customer Profile Analysis** - Load and analyze customer data
# MAGIC 2. **Financial Calculations** - Use UC functions for DTI, LTV, eligibility
# MAGIC 3. **Product Matching** - Vector search for mortgage products
# MAGIC 4. **Compliance Checking** - Regulatory rule validation
# MAGIC 5. **End-to-End Workflow** - Complete mortgage advisory process
# MAGIC 6. **Governance Demo** - RLS, masking, and tags in action
# MAGIC 
# MAGIC **Prerequisites:** All setup scripts completed

# COMMAND ----------

# DBTITLE 1,Setup and Configuration
# COMMAND ----------

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.getOrCreate()

print("🏡 Mortgage Advisor System Demo")
print("="*70)
print("\n✅ Prerequisites:")
print("   1. Unity Catalog setup (01_setup_catalog)")
print("   2. Data loaded (02_load_data)")
print("   3. UC functions deployed (03_create_uc_functions)")
print("   4. Vector search configured (04_setup_vector_search) [optional]")
print("   5. Governance applied (05_apply_governance) [optional]")
print("\n" + "="*70)

# COMMAND ----------

# DBTITLE 1,Scenario 1 - Customer Profile Analysis
# COMMAND ----------

# MAGIC %md
# MAGIC ## Scenario 1: Customer Profile Analysis
# MAGIC 
# MAGIC Meet Sarah Johnson, a first-time homebuyer looking for mortgage options.

print("\n📊 SCENARIO 1: Customer Profile Analysis")
print("="*70)

# COMMAND ----------

# DBTITLE 1,Load Customer Profile
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Load Sarah's profile
# MAGIC SELECT 
# MAGIC   customer_id,
# MAGIC   customer_name,
# MAGIC   age,
# MAGIC   annual_income,
# MAGIC   credit_score,
# MAGIC   employment_status,
# MAGIC   monthly_debt_payments,
# MAGIC   down_payment_available,
# MAGIC   region
# MAGIC FROM mortgage.customer_data.customer_profiles
# MAGIC WHERE customer_id = 'CUST003';

# COMMAND ----------

# DBTITLE 1,Scenario 2 - Financial Calculations
# COMMAND ----------

# MAGIC %md
# MAGIC ## Scenario 2: Financial Calculations with UC Functions
# MAGIC 
# MAGIC Use Unity Catalog functions to calculate key mortgage metrics.

print("\n💰 SCENARIO 2: Financial Calculations")
print("="*70)

# COMMAND ----------

# DBTITLE 1,Calculate Monthly Payment
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Calculate monthly payment for different loan scenarios
# MAGIC SELECT 
# MAGIC   '30-Year Conventional' AS scenario,
# MAGIC   350000 AS loan_amount,
# MAGIC   6.5 AS interest_rate,
# MAGIC   30 AS term_years,
# MAGIC   ROUND(mortgage.finance.calculate_monthly_payment(350000, 6.5, 30), 2) AS monthly_payment,
# MAGIC   ROUND(mortgage.finance.calculate_monthly_payment(350000, 6.5, 30) * 360, 2) AS total_paid,
# MAGIC   ROUND((mortgage.finance.calculate_monthly_payment(350000, 6.5, 30) * 360) - 350000, 2) AS total_interest
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   '15-Year Conventional',
# MAGIC   350000,
# MAGIC   6.0,
# MAGIC   15,
# MAGIC   ROUND(mortgage.finance.calculate_monthly_payment(350000, 6.0, 15), 2),
# MAGIC   ROUND(mortgage.finance.calculate_monthly_payment(350000, 6.0, 15) * 180, 2),
# MAGIC   ROUND((mortgage.finance.calculate_monthly_payment(350000, 6.0, 15) * 180) - 350000, 2)
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'FHA 30-Year',
# MAGIC   350000,
# MAGIC   6.0,
# MAGIC   30,
# MAGIC   ROUND(mortgage.finance.calculate_monthly_payment(350000, 6.0, 30), 2),
# MAGIC   ROUND(mortgage.finance.calculate_monthly_payment(350000, 6.0, 30) * 360, 2),
# MAGIC   ROUND((mortgage.finance.calculate_monthly_payment(350000, 6.0, 30) * 360) - 350000, 2);

# COMMAND ----------

# DBTITLE 1,Calculate DTI and LTV Ratios
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Calculate DTI and LTV for Sarah (CUST003)
# MAGIC WITH customer_data AS (
# MAGIC   SELECT 
# MAGIC     customer_id,
# MAGIC     customer_name,
# MAGIC     annual_income,
# MAGIC     monthly_debt_payments,
# MAGIC     credit_score,
# MAGIC     down_payment_available
# MAGIC   FROM mortgage.customer_data.customer_profiles
# MAGIC   WHERE customer_id = 'CUST003'
# MAGIC ),
# MAGIC loan_scenario AS (
# MAGIC   SELECT 
# MAGIC     400000 AS property_value,
# MAGIC     350000 AS loan_amount
# MAGIC )
# MAGIC SELECT 
# MAGIC   c.customer_name,
# MAGIC   c.annual_income,
# MAGIC   ROUND(c.annual_income / 12, 2) AS monthly_income,
# MAGIC   c.monthly_debt_payments,
# MAGIC   ROUND(mortgage.finance.calculate_monthly_payment(l.loan_amount, 6.5, 30), 2) AS estimated_monthly_payment,
# MAGIC   ROUND(mortgage.finance.calculate_dti_ratio(
# MAGIC     c.annual_income / 12, 
# MAGIC     c.monthly_debt_payments + mortgage.finance.calculate_monthly_payment(l.loan_amount, 6.5, 30)
# MAGIC   ), 2) AS projected_dti_ratio,
# MAGIC   ROUND(mortgage.finance.calculate_ltv_ratio(l.loan_amount, l.property_value), 2) AS ltv_ratio,
# MAGIC   c.credit_score
# MAGIC FROM customer_data c
# MAGIC CROSS JOIN loan_scenario l;

# COMMAND ----------

# DBTITLE 1,Check Eligibility
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Check eligibility for different loan types
# MAGIC WITH customer_metrics AS (
# MAGIC   SELECT 
# MAGIC     740 AS credit_score,
# MAGIC     35.0 AS dti_ratio,
# MAGIC     87.5 AS ltv_ratio
# MAGIC )
# MAGIC SELECT 
# MAGIC   'Conventional' AS loan_type,
# MAGIC   mortgage.finance.check_eligibility(credit_score, dti_ratio, ltv_ratio, 'conventional') AS eligibility
# MAGIC FROM customer_metrics
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'FHA',
# MAGIC   mortgage.finance.check_eligibility(credit_score, dti_ratio, ltv_ratio, 'fha')
# MAGIC FROM customer_metrics
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'VA',
# MAGIC   mortgage.finance.check_eligibility(credit_score, dti_ratio, ltv_ratio, 'va')
# MAGIC FROM customer_metrics;

# COMMAND ----------

# DBTITLE 1,Scenario 3 - Product Matching
# COMMAND ----------

# MAGIC %md
# MAGIC ## Scenario 3: Product Matching
# MAGIC 
# MAGIC Find suitable mortgage products for Sarah based on her profile.

print("\n🎯 SCENARIO 3: Product Matching")
print("="*70)

# COMMAND ----------

# DBTITLE 1,Search Products by Criteria
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Find products suitable for Sarah's profile
# MAGIC -- Credit score: 740, LTV: 87.5%, First-time buyer
# MAGIC
# MAGIC SELECT 
# MAGIC   product_id,
# MAGIC   lender_name,
# MAGIC   product_name,
# MAGIC   loan_type,
# MAGIC   interest_rate,
# MAGIC   term_years,
# MAGIC   min_credit_score,
# MAGIC   max_ltv,
# MAGIC   min_down_payment_pct,
# MAGIC   special_features
# MAGIC FROM mortgage.products.lender_products
# MAGIC WHERE 
# MAGIC   min_credit_score <= 740
# MAGIC   AND max_ltv >= 87.5
# MAGIC   AND min_down_payment_pct <= 12.5
# MAGIC ORDER BY interest_rate
# MAGIC LIMIT 5;

# COMMAND ----------

# DBTITLE 1,Compare Top Products
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Compare monthly payments across top products
# MAGIC WITH top_products AS (
# MAGIC   SELECT 
# MAGIC     lender_name,
# MAGIC     product_name,
# MAGIC     interest_rate,
# MAGIC     term_years,
# MAGIC     loan_type
# MAGIC   FROM mortgage.products.lender_products
# MAGIC   WHERE min_credit_score <= 740 AND max_ltv >= 87.5
# MAGIC   ORDER BY interest_rate
# MAGIC   LIMIT 3
# MAGIC )
# MAGIC SELECT 
# MAGIC   lender_name,
# MAGIC   product_name,
# MAGIC   loan_type,
# MAGIC   interest_rate,
# MAGIC   term_years,
# MAGIC   ROUND(mortgage.finance.calculate_monthly_payment(350000, interest_rate, term_years), 2) AS monthly_payment,
# MAGIC   ROUND(mortgage.finance.calculate_monthly_payment(350000, interest_rate, term_years) * term_years * 12, 2) AS total_cost
# MAGIC FROM top_products
# MAGIC ORDER BY monthly_payment;

# COMMAND ----------

# DBTITLE 1,Scenario 4 - Compliance Checking
# COMMAND ----------

# MAGIC %md
# MAGIC ## Scenario 4: Compliance Checking
# MAGIC 
# MAGIC Verify regulatory compliance for Sarah's application.

print("\n✅ SCENARIO 4: Compliance Checking")
print("="*70)

# COMMAND ----------

# DBTITLE 1,Review Applicable Compliance Rules
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Check applicable compliance rules
# MAGIC SELECT 
# MAGIC   rule_category,
# MAGIC   rule_name,
# MAGIC   description,
# MAGIC   requirement,
# MAGIC   severity
# MAGIC FROM mortgage.compliance.rules
# MAGIC WHERE 
# MAGIC   rule_category IN ('Income Verification', 'Credit Assessment', 'DTI Requirements')
# MAGIC ORDER BY severity DESC, rule_category;

# COMMAND ----------

# DBTITLE 1,Compliance Checklist
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Compliance checklist for Sarah's application
# MAGIC WITH customer AS (
# MAGIC   SELECT 
# MAGIC     customer_id,
# MAGIC     customer_name,
# MAGIC     credit_score,
# MAGIC     annual_income,
# MAGIC     monthly_debt_payments
# MAGIC   FROM mortgage.customer_data.customer_profiles
# MAGIC   WHERE customer_id = 'CUST003'
# MAGIC )
# MAGIC SELECT 
# MAGIC   'Income Verification' AS check_item,
# MAGIC   CASE WHEN c.annual_income >= 50000 THEN '✅ Pass' ELSE '❌ Fail' END AS status,
# MAGIC   'Annual income: $' || CAST(c.annual_income AS STRING) AS details
# MAGIC FROM customer c
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'Credit Score Minimum',
# MAGIC   CASE WHEN c.credit_score >= 620 THEN '✅ Pass' ELSE '❌ Fail' END,
# MAGIC   'Credit score: ' || CAST(c.credit_score AS STRING) || ' (Min: 620)'
# MAGIC FROM customer c
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'DTI Ratio (Conventional)',
# MAGIC   CASE 
# MAGIC     WHEN mortgage.finance.calculate_dti_ratio(c.annual_income/12, c.monthly_debt_payments + 2500) <= 43.0 
# MAGIC     THEN '✅ Pass' 
# MAGIC     ELSE '❌ Fail' 
# MAGIC   END,
# MAGIC   'DTI: ' || CAST(ROUND(mortgage.finance.calculate_dti_ratio(c.annual_income/12, c.monthly_debt_payments + 2500), 1) AS STRING) || '% (Max: 43%)'
# MAGIC FROM customer c;

# COMMAND ----------

# DBTITLE 1,Scenario 5 - Application History
# COMMAND ----------

# MAGIC %md
# MAGIC ## Scenario 5: Application History & Analytics
# MAGIC 
# MAGIC Review mortgage application trends and outcomes.

print("\n📈 SCENARIO 5: Application History Analytics")
print("="*70)

# COMMAND ----------

# DBTITLE 1,Application Status Summary
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Application status summary
# MAGIC SELECT 
# MAGIC   application_status,
# MAGIC   COUNT(*) AS count,
# MAGIC   ROUND(AVG(loan_amount), 2) AS avg_loan_amount,
# MAGIC   ROUND(AVG(interest_rate), 2) AS avg_interest_rate,
# MAGIC   ROUND(AVG(dti_ratio), 2) AS avg_dti
# MAGIC FROM mortgage.customer_data.application_history
# MAGIC GROUP BY application_status
# MAGIC ORDER BY count DESC;

# COMMAND ----------

# DBTITLE 1,Approved vs Denied Analysis
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Compare approved vs denied applications
# MAGIC SELECT 
# MAGIC   a.application_status,
# MAGIC   AVG(c.credit_score) AS avg_credit_score,
# MAGIC   AVG(c.annual_income) AS avg_income,
# MAGIC   AVG(a.dti_ratio) AS avg_dti,
# MAGIC   AVG(a.ltv_ratio) AS avg_ltv
# MAGIC FROM mortgage.customer_data.application_history a
# MAGIC JOIN mortgage.customer_data.customer_profiles c 
# MAGIC   ON a.customer_id = c.customer_id
# MAGIC WHERE a.application_status IN ('Approved', 'Denied')
# MAGIC GROUP BY a.application_status;

# COMMAND ----------

# DBTITLE 1,Scenario 6 - Governance Demo
# COMMAND ----------

# MAGIC %md
# MAGIC ## Scenario 6: Unity Catalog Governance in Action
# MAGIC 
# MAGIC Demonstrate RLS, column masking, and governance tags.

print("\n🔒 SCENARIO 6: Governance Features")
print("="*70)

# COMMAND ----------

# DBTITLE 1,Regional Data Distribution (RLS)
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Row-Level Security: Data by region
# MAGIC -- In production, users would only see their authorized region
# MAGIC SELECT 
# MAGIC   region,
# MAGIC   COUNT(*) AS customers,
# MAGIC   ROUND(AVG(credit_score), 0) AS avg_credit_score,
# MAGIC   ROUND(AVG(annual_income), 0) AS avg_income
# MAGIC FROM mortgage.customer_data.customer_profiles
# MAGIC GROUP BY region
# MAGIC ORDER BY region;

# COMMAND ----------

# DBTITLE 1,Column Masking Demo
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- Test column masking functions
# MAGIC SELECT 
# MAGIC   'Original' AS data_type,
# MAGIC   '123-45-6789' AS ssn_value,
# MAGIC   85000 AS income_value,
# MAGIC   'sarah.johnson@email.com' AS email_value
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'Masked (Default User)',
# MAGIC   mortgage.customer_data.mask_ssn('123-45-6789'),
# MAGIC   CAST(mortgage.customer_data.mask_income(85000) AS STRING),
# MAGIC   mortgage.customer_data.mask_email('sarah.johnson@email.com');

# COMMAND ----------

# DBTITLE 1,View Governance Tags
# MAGIC %sql
# MAGIC -- COMMAND ----------
# MAGIC
# MAGIC -- View governance tags on tables
# MAGIC SHOW TBLPROPERTIES mortgage.customer_data.customer_profiles;

# COMMAND ----------

# DBTITLE 1,Summary and Key Insights
# COMMAND ----------

print("\n" + "="*70)
print("📊 DEMO SUMMARY - Mortgage Advisor System")
print("="*70)
print("\n✅ COMPLETED DEMONSTRATIONS:")
print("\n1. Customer Profile Analysis")
print("   • Loaded customer data from Unity Catalog")
print("   • Analyzed financial profile and requirements")
print("\n2. Financial Calculations")
print("   • Used UC functions: calculate_monthly_payment")
print("   • Computed DTI and LTV ratios")
print("   • Checked eligibility across loan types")
print("\n3. Product Matching")
print("   • Searched products by customer criteria")
print("   • Compared monthly payments and total costs")
print("\n4. Compliance Checking")
print("   • Reviewed applicable regulations")
print("   • Validated compliance requirements")
print("\n5. Application Analytics")
print("   • Analyzed application trends")
print("   • Compared approved vs denied profiles")
print("\n6. Governance Features")
print("   • Demonstrated RLS (regional filtering)")
print("   • Tested column masking (PII protection)")
print("   • Reviewed governance tags")
print("\n" + "="*70)
print("\n🎯 KEY INSIGHTS:")
print("\n• Unity Catalog Functions: Reusable, governed calculations")
print("• Data Governance: RLS, masking, and tags protect sensitive data")
print("• Vector Search: (Optional) Semantic product & compliance matching")
print("• Multi-Agent System: 6 specialized agents working collaboratively")
print("• MLflow Tracing: Full observability of agent interactions")
print("\n" + "="*70)
print("\n🚀 NEXT STEPS:")
print("\n1. Test the agent system via MCP server")
print("2. View MLflow traces in the experiments UI")
print("3. Customize agents for specific use cases")
print("4. Add vector search for semantic matching")
print("5. Apply RLS and masking for production deployment")
print("\n" + "="*70)

# COMMAND ----------

