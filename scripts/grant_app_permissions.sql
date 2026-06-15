
-- ============================================================================
-- MORTGAGE ADVISOR APP - PERMISSIONS SETUP
-- ============================================================================
-- Service Principal: app-ynf0vl agent-mortgage-advisor-2
-- App Name: agent-mortgage-advisor-2
-- Generated: 2026-06-15
-- ============================================================================

-- Step 1: Catalog and Schema Access
-- ============================================================================
GRANT USE CATALOG ON CATALOG mortgage TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT USE SCHEMA ON SCHEMA mortgage.customer_data TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT USE SCHEMA ON SCHEMA mortgage.products TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT USE SCHEMA ON SCHEMA mortgage.compliance TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT USE SCHEMA ON SCHEMA mortgage.documents TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT USE SCHEMA ON SCHEMA mortgage.finance TO `app-ynf0vl agent-mortgage-advisor-2`;

-- Step 2: Table Permissions (SELECT access)
-- ============================================================================

-- Customer Data Tables
GRANT SELECT ON TABLE mortgage.customer_data.customer_profiles TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT SELECT ON TABLE mortgage.customer_data.application_history TO `app-ynf0vl agent-mortgage-advisor-2`;

-- Product Tables
GRANT SELECT ON TABLE mortgage.products.lender_products TO `app-ynf0vl agent-mortgage-advisor-2`;

-- Compliance Tables
GRANT SELECT ON TABLE mortgage.compliance.rules TO `app-ynf0vl agent-mortgage-advisor-2`;

-- Document Tables
GRANT SELECT ON TABLE mortgage.documents.mortgage_documents TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT SELECT ON TABLE mortgage.documents.property_documents TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT SELECT ON TABLE mortgage.documents.bank_statements TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT SELECT ON TABLE mortgage.documents.payslips TO `app-ynf0vl agent-mortgage-advisor-2`;

-- Step 3: UC Function Permissions (EXECUTE access)
-- ============================================================================
GRANT EXECUTE ON FUNCTION mortgage.finance.calculate_monthly_payment TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT EXECUTE ON FUNCTION mortgage.finance.calculate_dti_ratio TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT EXECUTE ON FUNCTION mortgage.finance.calculate_ltv_ratio TO `app-ynf0vl agent-mortgage-advisor-2`;
GRANT EXECUTE ON FUNCTION mortgage.finance.check_eligibility TO `app-ynf0vl agent-mortgage-advisor-2`;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Check catalog grants
-- SHOW GRANTS ON CATALOG mortgage;

-- Check table grants (example)
-- SHOW GRANTS ON TABLE mortgage.customer_data.customer_profiles;

-- Check function grants (example)
-- SHOW GRANTS ON FUNCTION mortgage.finance.calculate_monthly_payment;

