-- ============================================================================
-- Unity Catalog Function: Check Mortgage Eligibility
-- ============================================================================
-- Checks if a borrower is eligible for a mortgage based on key criteria
--
-- Usage:
--   SELECT mortgage.finance.check_eligibility(740, 35.0, 80.0, 'conventional');
--
-- Returns: STRUCT with eligibility status and details
-- ============================================================================

CREATE OR REPLACE FUNCTION mortgage.finance.check_eligibility(
  credit_score INT,
  dti_ratio DOUBLE,
  ltv_ratio DOUBLE,
  loan_type STRING
)
RETURNS STRUCT<
  eligible: BOOLEAN,
  reason: STRING,
  recommendation: STRING
>
LANGUAGE SQL
COMMENT 'Check mortgage eligibility based on credit, DTI, and LTV'
RETURN
  CASE
    -- Conventional Loan Checks
    WHEN loan_type = 'conventional' THEN
      CASE
        WHEN credit_score < 620 THEN 
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'Credit score below minimum (620) for conventional',
            'recommendation', 'Consider FHA loan or work on improving credit score'
          )
        WHEN dti_ratio > 43.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'DTI ratio exceeds maximum (43%) for conventional',
            'recommendation', 'Reduce monthly debts or increase income'
          )
        WHEN ltv_ratio > 97.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'LTV exceeds maximum (97%) for conventional',
            'recommendation', 'Increase down payment to at least 3%'
          )
        ELSE
          NAMED_STRUCT(
            'eligible', TRUE,
            'reason', 'Meets conventional loan requirements',
            'recommendation', 'Proceed with conventional loan application'
          )
      END
    
    -- FHA Loan Checks
    WHEN loan_type = 'fha' THEN
      CASE
        WHEN credit_score < 500 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'Credit score below FHA minimum (500)',
            'recommendation', 'Work on improving credit score before applying'
          )
        WHEN credit_score < 580 AND ltv_ratio > 90.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'Credit score 500-579 requires 10% down payment',
            'recommendation', 'Increase down payment or improve credit to 580+'
          )
        WHEN dti_ratio > 50.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'DTI ratio exceeds FHA maximum (50%)',
            'recommendation', 'Reduce monthly debts or increase income'
          )
        WHEN ltv_ratio > 96.5 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'LTV exceeds FHA maximum (96.5%)',
            'recommendation', 'Increase down payment to at least 3.5%'
          )
        ELSE
          NAMED_STRUCT(
            'eligible', TRUE,
            'reason', 'Meets FHA loan requirements',
            'recommendation', 'Proceed with FHA loan application'
          )
      END
    
    -- VA Loan Checks
    WHEN loan_type = 'va' THEN
      CASE
        WHEN dti_ratio > 41.0 THEN
          NAMED_STRUCT(
            'eligible', FALSE,
            'reason', 'DTI ratio exceeds VA guideline (41%)',
            'recommendation', 'May need compensating factors or debt reduction'
          )
        ELSE
          NAMED_STRUCT(
            'eligible', TRUE,
            'reason', 'Meets VA loan requirements (verify COE)',
            'recommendation', 'Proceed with VA loan - verify Certificate of Eligibility'
          )
      END
    
    -- Default
    ELSE
      NAMED_STRUCT(
        'eligible', FALSE,
        'reason', 'Unknown loan type',
        'recommendation', 'Specify valid loan type: conventional, fha, or va'
      )
  END;

-- ============================================================================
-- Test Cases
-- ============================================================================
-- SELECT mortgage.finance.check_eligibility(740, 35.0, 80.0, 'conventional') AS eligibility;
-- Expected: eligible = TRUE
--
-- SELECT mortgage.finance.check_eligibility(590, 45.0, 85.0, 'conventional') AS eligibility;
-- Expected: eligible = FALSE (credit too low)
--
-- SELECT mortgage.finance.check_eligibility(620, 48.0, 93.5, 'fha') AS eligibility;
-- Expected: eligible = TRUE
-- ============================================================================
