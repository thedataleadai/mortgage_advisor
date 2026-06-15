-- ============================================================================
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
