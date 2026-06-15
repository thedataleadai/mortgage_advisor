"""Generate all sample data CSV files for the mortgage advisor demo."""
import pandas as pd
import os

def generate_application_history():
    """Generate application history data."""
    return pd.DataFrame({
        'application_id': ['APP001', 'APP002', 'APP003', 'APP004', 'APP005', 'APP006', 'APP007', 'APP008', 'APP009', 'APP010', 'APP011', 'APP012', 'APP013', 'APP014', 'APP015'],
        'customer_id': ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005', 'CUST006', 'CUST007', 'CUST008', 'CUST009', 'CUST010', 'CUST011', 'CUST012', 'CUST013', 'CUST014', 'CUST015'],
        'application_date': ['2024-01-15', '2024-01-18', '2024-01-20', '2024-01-22', '2024-02-01', '2024-02-03', '2024-02-05', '2024-02-08', '2024-02-10', '2024-02-12', '2024-02-15', '2024-02-18', '2024-02-20', '2024-02-22', '2024-02-25'],
        'loan_amount': [380000, 280000, 640000, 200000, 450000, 320000, 560000, 240000, 400000, 480000, 360000, 520000, 280000, 720000, 160000],
        'property_value': [475000, 350000, 800000, 250000, 500000, 400000, 700000, 300000, 500000, 600000, 450000, 650000, 350000, 900000, 200000],
        'property_address': [
            '123 Oak St, San Francisco, CA 94102',
            '456 Maple Ave, Austin, TX 78701',
            '789 Pine Rd, Seattle, WA 98101',
            '321 Birch Ln, Denver, CO 80202',
            '654 Cedar Dr, Portland, OR 97201',
            '987 Elm St, Chicago, IL 60601',
            '147 Willow Way, Boston, MA 02101',
            '258 Ash Ct, Phoenix, AZ 85001',
            '369 Spruce Ave, Miami, FL 33101',
            '741 Redwood Blvd, San Diego, CA 92101',
            '852 Hickory St, Nashville, TN 37201',
            '963 Poplar Rd, Raleigh, NC 27601',
            '159 Magnolia Dr, Atlanta, GA 30301',
            '357 Cypress Ln, Los Angeles, CA 90001',
            '486 Sycamore Ave, Detroit, MI 48201'
        ],
        'property_type': ['Single Family', 'Condo', 'Single Family', 'Townhouse', 'Single Family', 'Condo', 'Single Family', 'Single Family', 'Condo', 'Single Family', 'Single Family', 'Single Family', 'Townhouse', 'Single Family', 'Condo'],
        'occupancy_type': ['Primary Residence', 'Primary Residence', 'Primary Residence', 'Primary Residence', 'Second Home', 'Primary Residence', 'Primary Residence', 'Primary Residence', 'Investment Property', 'Primary Residence', 'Primary Residence', 'Primary Residence', 'Primary Residence', 'Primary Residence', 'Primary Residence'],
        'application_status': ['Approved', 'In Review', 'Approved', 'Conditional', 'Denied', 'Approved', 'Approved', 'In Review', 'Conditional', 'Approved', 'In Review', 'Approved', 'Conditional', 'Approved', 'Approved'],
        'approval_date': ['2024-01-22', '', '2024-01-25', '', '', '2024-02-10', '2024-02-12', '', '', '2024-02-18', '', '2024-02-25', '', '2024-02-28', '2024-03-02'],
        'loan_officer': ['LO-Sarah-Johnson', '', 'LO-Michael-Chen', '', '', 'LO-Emily-Rodriguez', 'LO-Sarah-Johnson', '', '', 'LO-Michael-Chen', '', 'LO-Emily-Rodriguez', '', 'LO-Sarah-Johnson', 'LO-Michael-Chen'],
        'estimated_closing_date': ['2024-02-28', '', '2024-03-15', '', '', '2024-03-20', '2024-03-25', '', '', '2024-03-30', '', '2024-04-05', '', '2024-04-10', '2024-04-15'],
        'rate_locked': ['TRUE', 'FALSE', 'TRUE', 'FALSE', 'FALSE', 'TRUE', 'TRUE', 'FALSE', 'FALSE', 'TRUE', 'FALSE', 'TRUE', 'FALSE', 'TRUE', 'TRUE'],
        'locked_rate': ['6.875', '', '6.75', '', '', '7.125', '6.625', '', '', '6.95', '', '7.0', '', '6.875', '7.25'],
        'notes': [
            'Credit excellent; fast approval',
            'Awaiting employment verification',
            'VA loan; zero down payment',
            'Need additional income documentation',
            'DTI ratio too high (48%)',
            'First-time homebuyer program',
            'Jumbo loan; strong financials',
            'Credit score borderline (682)',
            'Need larger down payment (25% for investment)',
            'Excellent credit; pre-qualified in 24 hours',
            'Self-employed; reviewing tax returns',
            'Clean financials; smooth process',
            'Need gift letter for down payment',
            'High-value property; jumbo loan',
            'FHA loan; 3.5% down payment'
        ]
    })


def generate_property_documents():
    """Generate property document metadata."""
    return pd.DataFrame({
        'doc_id': ['PDOC001', 'PDOC002', 'PDOC003', 'PDOC004', 'PDOC005', 'PDOC006', 'PDOC007', 'PDOC008', 'PDOC009', 'PDOC010'],
        'customer_id': ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST006', 'CUST007', 'CUST010', 'CUST012', 'CUST013', 'CUST014'],
        'application_id': ['APP001', 'APP002', 'APP003', 'APP004', 'APP006', 'APP007', 'APP010', 'APP012', 'APP013', 'APP014'],
        'doc_type': ['Property Appraisal', 'Home Inspection', 'Property Appraisal', 'Title Report', 'Property Appraisal', 'Property Appraisal', 'Home Inspection', 'Property Appraisal', 'Title Report', 'Property Appraisal'],
        'content_summary': [
            'Property appraised at $475,000. Excellent condition, recent renovations. Comparable sales support value.',
            'Minor issues identified: roof needs repair in 5 years, HVAC system 8 years old. Overall good condition.',
            'Property appraised at $800,000. Premium location, updated kitchen and bathrooms. No issues found.',
            'Title clear. No liens or encumbrances. Ready for closing.',
            'Property appraised at $400,000. Good condition, needs cosmetic updates. Value aligns with market.',
            'Property appraised at $700,000. Historic home, well-maintained. Comparable sales strong.',
            'Excellent condition throughout. New roof (2 years), updated electrical and plumbing. No concerns.',
            'Property appraised at $650,000. Move-in ready, modern finishes. Strong market demand.',
            'Title shows prior lien (resolved). Clear for transfer. HOA documents reviewed.',
            'Property appraised at $900,000. Luxury finishes, premium location. Appraisal supports purchase price.'
        ],
        'upload_date': ['2024-01-20', '2024-01-25', '2024-01-28', '2024-02-01', '2024-02-12', '2024-02-15', '2024-02-20', '2024-02-28', '2024-03-02', '2024-03-05'],
        'verified_status': ['Verified', 'Verified', 'Verified', 'Verified', 'Verified', 'Verified', 'Verified', 'Verified', 'Pending', 'Verified'],
        'verified_by': ['Appraiser-J-Smith', 'Inspector-M-Lee', 'Appraiser-R-Davis', 'Title-Company-ABC', 'Appraiser-J-Smith', 'Appraiser-S-Wilson', 'Inspector-T-Brown', 'Appraiser-R-Davis', '', 'Appraiser-J-Smith'],
        'file_size_kb': [245, 1820, 312, 156, 198, 287, 2104, 234, 89, 298]
    })


def generate_mortgage_documents():
    """Generate mortgage document metadata (structured data)."""
    return pd.DataFrame({
        'doc_id': ['MDOC001', 'MDOC002', 'MDOC003', 'MDOC004', 'MDOC005', 'MDOC006', 'MDOC007', 'MDOC008', 'MDOC009', 'MDOC010', 
                   'MDOC011', 'MDOC012', 'MDOC013', 'MDOC014', 'MDOC015', 'MDOC016', 'MDOC017', 'MDOC018', 'MDOC019', 'MDOC020'],
        'customer_id': ['CUST001', 'CUST001', 'CUST002', 'CUST002', 'CUST003', 'CUST003', 'CUST004', 'CUST006', 'CUST006', 'CUST007',
                        'CUST007', 'CUST008', 'CUST010', 'CUST010', 'CUST012', 'CUST012', 'CUST013', 'CUST014', 'CUST014', 'CUST015'],
        'application_id': ['APP001', 'APP001', 'APP002', 'APP002', 'APP003', 'APP003', 'APP004', 'APP006', 'APP006', 'APP007',
                          'APP007', 'APP008', 'APP010', 'APP010', 'APP012', 'APP012', 'APP013', 'APP014', 'APP014', 'APP015'],
        'doc_type': ['W2', 'Tax Return', 'Paystub', 'Bank Statement', 'VA Certificate', 'Tax Return', 'Paystub', 'W2', 'Bank Statement', 'Tax Return',
                     'Bank Statement', 'Paystub', 'W2', 'Bank Statement', 'W2', 'Tax Return', 'Gift Letter', 'Tax Return', 'Bank Statement', 'W2'],
        'content_summary': [
            'W2 2023: Gross income $150,000 from Tech Corp Inc.',
            'Tax Return 2023: AGI $145,000, married filing jointly, no unusual deductions.',
            'Paystub Nov 2024: Monthly gross $8,333, YTD $91,663. Employer: StartUp Labs.',
            'Bank Statement Oct 2024: Savings $45,000, checking $12,000. Good transaction history.',
            'VA Certificate of Eligibility: Active duty 6 years, full entitlement available.',
            'Tax Return 2023: AGI $95,000, includes VA disability compensation (non-taxable).',
            'Paystub Dec 2024: Monthly gross $5,200, YTD $62,400. Employer: City Hospital.',
            'W2 2023: Gross income $125,000 from Financial Services Co.',
            'Bank Statement Nov 2024: Savings $72,000, checking $18,000. Strong reserves.',
            'Tax Return 2023: Self-employed income $185,000. Schedule C shows consulting business.',
            'Bank Statement Oct 2024: Business account $95,000, personal savings $120,000.',
            'Paystub Nov 2024: Monthly gross $4,800, YTD $52,800. Employer: Retail Chain Inc.',
            'W2 2023: Gross income $170,000 from Software Company.',
            'Bank Statement Dec 2024: Savings $88,000, checking $24,000. Investment accounts $150,000.',
            'W2 2023: Gross income $195,000 from Consulting Firm LLC.',
            'Tax Return 2023: AGI $190,000, married filing jointly. Bonus income included.',
            'Gift Letter: $35,000 from parents for down payment. Relationship verified, no repayment expected.',
            'Tax Return 2023: AGI $280,000, includes capital gains from investments.',
            'Bank Statement Nov 2024: Savings $180,000, checking $42,000. Multiple investment accounts.',
            'W2 2023: Gross income $55,000 from Tech Support Co.'
        ],
        'upload_date': ['2024-01-16', '2024-01-16', '2024-01-19', '2024-01-19', '2024-01-21', '2024-01-21', '2024-01-23', '2024-02-04', '2024-02-04', '2024-02-06',
                       '2024-02-06', '2024-02-09', '2024-02-13', '2024-02-13', '2024-02-19', '2024-02-19', '2024-02-21', '2024-02-23', '2024-02-23', '2024-02-26'],
        'verified_status': ['Verified', 'Verified', 'Verified', 'Verified', 'Verified', 'Verified', 'Pending', 'Verified', 'Verified', 'Verified',
                           'Verified', 'Pending', 'Verified', 'Verified', 'Verified', 'Verified', 'Verified', 'Verified', 'Verified', 'Verified'],
        'verified_by': ['Underwriter-A-Thompson', 'Underwriter-A-Thompson', 'Underwriter-B-Martinez', 'Underwriter-B-Martinez', 'Underwriter-C-Anderson', 
                       'Underwriter-C-Anderson', '', 'Underwriter-D-White', 'Underwriter-D-White', 'Underwriter-E-Garcia',
                       'Underwriter-E-Garcia', '', 'Underwriter-A-Thompson', 'Underwriter-A-Thompson', 'Underwriter-B-Martinez', 
                       'Underwriter-B-Martinez', 'Underwriter-C-Anderson', 'Underwriter-D-White', 'Underwriter-D-White', 'Underwriter-E-Garcia'],
        'file_size_kb': [42, 156, 28, 234, 38, 168, 31, 45, 287, 189, 312, 29, 48, 298, 51, 178, 12, 201, 345, 44]
    })


def main():
    """Generate and save all sample data files."""
    
    # Define base directories
    base_dir = "/Workspace/Users/paul.karikari@thedatalead.ai/mortgage advisor"
    sample_data_dir = f"{base_dir}/data/sample_data"
    documents_dir = f"{base_dir}/data/documents"
    
    print("=" * 70)
    print("Generating Sample Data for Mortgage Advisor Demo")
    print("=" * 70)
    
    # Generate and save application history
    print("\n1. Generating application_history.csv...")
    app_history = generate_application_history()
    app_history.to_csv(f"{sample_data_dir}/application_history.csv", index=False)
    print(f"   ✓ Created {len(app_history)} application records")
    
    # Generate and save property documents
    print("\n2. Generating property_documents.csv...")
    prop_docs = generate_property_documents()
    prop_docs.to_csv(f"{documents_dir}/property_documents.csv", index=False)
    print(f"   ✓ Created {len(prop_docs)} property document records")
    
    # Generate and save mortgage documents
    print("\n3. Generating mortgage_documents.csv...")
    mort_docs = generate_mortgage_documents()
    mort_docs.to_csv(f"{documents_dir}/mortgage_documents.csv", index=False)
    print(f"   ✓ Created {len(mort_docs)} mortgage document records")
    
    print("\n" + "=" * 70)
    print("Sample Data Generation Complete!")
    print("=" * 70)
    print(f"\nFiles created:")
    print(f"  • {sample_data_dir}/application_history.csv")
    print(f"  • {documents_dir}/property_documents.csv")
    print(f"  • {documents_dir}/mortgage_documents.csv")
    print("\nExisting files:")
    print(f"  • {sample_data_dir}/customer_profiles.csv")
    print(f"  • {sample_data_dir}/lender_products.csv")
    print(f"  • {sample_data_dir}/compliance_rules.csv")
    print(f"  • {documents_dir}/payslips.csv")
    print(f"  • {documents_dir}/bank_statements.csv")
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("  1. Review the generated CSV files")
    print("  2. Run setup scripts to load into Unity Catalog")
    print("  3. Create UC functions for calculations")
    print("  4. Set up vector search indexes")
    print("  5. Apply governance policies")
    print("=" * 70)


if __name__ == "__main__":
    main()
