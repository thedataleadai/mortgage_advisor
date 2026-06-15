-- ============================================================================
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
