-- ============================================================================
-- Unity Catalog Function: Calculate Loan-to-Value Ratio
-- ============================================================================
-- Calculates the loan-to-value ratio as a percentage
--
-- Usage:
--   SELECT mortgage.finance.calculate_ltv_ratio(240000, 300000);
--
-- Returns: LTV ratio as percentage
-- ============================================================================

CREATE OR REPLACE FUNCTION mortgage.finance.calculate_ltv_ratio(
  loan_amount DOUBLE,
  property_value DOUBLE
)
RETURNS DOUBLE
LANGUAGE SQL
COMMENT 'Calculate loan-to-value ratio as percentage'
RETURN
  CASE
    WHEN property_value = 0 THEN NULL
    ELSE (loan_amount / property_value) * 100
  END;

-- ============================================================================
-- Test Cases
-- ============================================================================
-- SELECT mortgage.finance.calculate_ltv_ratio(240000, 300000) AS ltv_ratio;
-- Expected: 80.0 (exactly at PMI threshold)
--
-- SELECT mortgage.finance.calculate_ltv_ratio(285000, 300000) AS ltv_ratio;
-- Expected: 95.0 (requires PMI)
-- ============================================================================
