"""
questionnaires.py
Clean, professional questionnaires for Student and Tourist visa applicants
tailored to the United States, Canada, and the United Kingdom.
Designed for a premium travel and immigration consultancy platform.
"""

import streamlit as st


def render_student_questionnaire(country_code: str) -> dict:
    """
    Renders the student visa questionnaire covering:
    - Education Profile
    - University Admission
    - Funding & Financial Maintenance
    - Sponsor Standing
    - Study Plan & Ties to Home Country
    """
    st.markdown("#### Student Visa Assessment Form")
    st.caption(f"Requirements tailored for **{country_code}** student visa processing.")

    # Section 1: Education Profile
    with st.expander("1. Academic History & Qualifications", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            education_level = st.selectbox(
                "Highest Academic Degree Earned",
                ["High School", "Bachelor's", "Master's", "Doctorate", "Postgraduate Diploma"],
                index=1
            )
            gpa_tier = st.selectbox(
                "Academic Performance / Grade Range",
                ["Distinction / First Class (80%+ or GPA 3.7+)",
                 "Upper Second Class (65% - 79% or GPA 3.0 - 3.6)",
                 "Second Class / Pass (50% - 64% or GPA 2.5 - 2.9)",
                 "Below 50%"],
                index=1
            )
            has_transcripts = st.checkbox(
                "Official academic transcripts and degree certificates ready",
                value=True,
                help="Official certified transcripts are required during visa submission or interview."
            )
        with col2:
            has_english_test = st.checkbox(
                "Approved English language test taken (IELTS, TOEFL, PTE, Duolingo, or university waiver)",
                value=True
            )
            has_study_gap = st.checkbox(
                "Education gap of more than 12 months since last degree",
                value=False
            )
            gap_justified = True
            if has_study_gap:
                gap_justified = st.checkbox(
                    "Work experience letters or official records available explaining the gap period",
                    value=True
                )

    # Section 2: Admission & University Prerequisites
    with st.expander("2. University Admission & Country Requirements", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            institution_name = st.text_input("Institution / University Name", value="State University")
            program_level = st.selectbox(
                "Program Level",
                ["Bachelor's Degree", "Master's / Graduate Degree", "Ph.D. / Research", "Diploma / Certificate"],
                index=1
            )
            admission_type = st.radio("Admission Status", ["Unconditional Offer", "Conditional Offer"], index=0)

        with col2:
            if country_code == "USA":
                has_i20 = st.checkbox("Official Form I-20 received from SEVP-approved school", value=True)
                sevis_fee_paid = st.checkbox("SEVIS I-901 fee ($350) paid with receipt", value=True)
                ds160_submitted = st.checkbox("DS-160 online visa application form completed with barcode", value=True)
            elif country_code == "Canada":
                has_loa = st.checkbox("Letter of Acceptance (LOA) from a Designated Learning Institution (DLI)", value=True)
                has_pal = st.checkbox(
                    "Provincial Attestation Letter (PAL) or official exemption received",
                    value=True,
                    help="Mandatory for most post-secondary study permits in Canada."
                )
                has_upfront_med = st.checkbox("Upfront medical examination completed (eMedical sheet)", value=False)
                has_pcc = st.checkbox("Police clearance certificate available", value=False)
            elif country_code == "UK":
                has_cas = st.checkbox("Confirmation of Acceptance for Studies (CAS) reference number received", value=True)
                studying_in_london = st.checkbox("Campus located within Greater London (higher living cost requirement)", value=False)
                requires_atas = st.checkbox("Course requires ATAS (Academic Technology Approval Scheme) clearance", value=False)
                has_atas = False
                if requires_atas:
                    has_atas = st.checkbox("Valid ATAS clearance certificate received", value=True)
                has_tb = st.checkbox("Tuberculosis (TB) test certificate from an approved clinic", value=True)

    # Section 3: Funding & Financial Maintenance
    with st.expander("3. Tuition, Living Expenses & Available Funds", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if country_code == "USA":
                annual_tuition_living = st.number_input(
                    "Annual Tuition + Estimated Living Costs on Form I-20 (USD)",
                    min_value=5000, max_value=120000, value=40000, step=2000
                )
                liquid_funds = st.number_input(
                    "Documented Liquid Funds (Bank savings, fixed deposits, liquid investments) (USD)",
                    min_value=0, max_value=250000, value=52000, step=2500
                )
            elif country_code == "Canada":
                tuition_cad = st.number_input(
                    "First Year Tuition Fee (CAD)",
                    min_value=5000, max_value=90000, value=24000, step=1000
                )
                st.caption("Canada living requirement: Minimum CAD $20,635 per year.")
                has_gic = st.checkbox("Guaranteed Investment Certificate (GIC) of CAD $20,635+ purchased with an approved bank", value=True)
                available_funds_cad = st.number_input(
                    "Total Documented Funds in CAD (Tuition + Living + Savings)",
                    min_value=0, max_value=250000, value=48000, step=2000
                )
            elif country_code == "UK":
                tuition_unpaid_gbp = st.number_input(
                    "Outstanding First-Year Tuition Fees (GBP)",
                    min_value=0, max_value=60000, value=15000, step=1000
                )
                st.caption("UK living costs: GBP 1,334/month (London) or GBP 1,023/month (outside London) up to 9 months.")
                available_funds_gbp = st.number_input(
                    "Total Documented Living and Tuition Funds (GBP)",
                    min_value=0, max_value=150000, value=26500, step=1000
                )
                funds_held_28_days = st.checkbox(
                    "Funds held continuously for at least 28 consecutive days before application",
                    value=True,
                    help="UKVI requires maintenance funds to remain in your account without dropping below the threshold for 28 consecutive days."
                )

        with col2:
            has_loan = st.checkbox("Education loan sanction letter from an approved bank", value=False)
            sponsor_source = st.selectbox(
                "Primary Funding Source",
                ["Parents / Immediate Family", "Self-Funded (Personal Savings)", "Education Loan", "University Scholarship", "Third-Party Sponsor"],
                index=0
            )
            sponsor_annual_income = st.number_input(
                "Sponsor / Family Annual Income (USD Equivalent)",
                min_value=0, max_value=300000, value=38000, step=2000
            )
            has_sponsor_affidavit = st.checkbox(
                "Sponsor affidavit of support, tax returns (past 2-3 years), and bank statements ready",
                value=True
            )

    # Section 4: Study Plan & Home Country Ties
    with st.expander("4. Study Plan & Ties to Home Country", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            has_sop = st.checkbox("Statement of Purpose (SOP) explaining course choice and post-graduation plans", value=True)
            course_matches_career = st.checkbox("Course aligns logically with previous studies or work history", value=True)
            has_job_offer = st.checkbox("Employer leave letter, job offer, or verified career opportunity upon return", value=False)
        with col2:
            has_family_ties = st.checkbox("Immediate family dependents (parents, spouse, children) residing in home country", value=True)
            owns_property = st.checkbox("Family or applicant owns residential/commercial property or registered business in home country", value=False)
            passport_valid = st.checkbox("Passport valid for at least 6 months beyond intended program end date", value=True)

    data = {
        "passport_valid_6m": passport_valid,
        "education_level": education_level,
        "gpa_tier": gpa_tier,
        "has_academic_transcripts": has_transcripts,
        "has_english_test": has_english_test,
        "has_ukvi_english_test": has_english_test,
        "has_language_test": has_english_test,
        "has_study_gap": has_study_gap,
        "study_gap_justified": gap_justified,
        "has_loan_sanction_letter": has_loan,
        "sponsor_type": sponsor_source,
        "sponsor_annual_income_usd": sponsor_annual_income,
        "annual_income_usd": sponsor_annual_income,
        "has_sponsor_affidavit": has_sponsor_affidavit,
        "has_detailed_study_plan": has_sop,
        "has_career_progression_plan": course_matches_career,
        "course_matches_academic_history": course_matches_career,
        "has_job_offer_or_leave": has_job_offer,
        "has_dependent_family_in_home_country": has_family_ties,
        "owns_property_or_business": owns_property,
    }

    if country_code == "USA":
        data["has_i20"] = has_i20
        data["sevis_fee_paid"] = sevis_fee_paid
        data["ds160_submitted"] = ds160_submitted
        data["annual_tuition_living_usd"] = annual_tuition_living
        data["liquid_funds_usd"] = liquid_funds
    elif country_code == "Canada":
        data["has_loa"] = has_loa
        data["has_pal_or_exemption"] = has_pal
        data["tuition_fee_cad"] = tuition_cad
        data["available_funds_cad"] = available_funds_cad
        data["has_gic_certificate"] = has_gic
        data["has_upfront_medical"] = has_upfront_med
        data["has_police_certificate"] = has_pcc
    elif country_code == "UK":
        data["has_cas_letter"] = has_cas
        data["studying_in_london"] = studying_in_london
        data["tuition_unpaid_gbp"] = tuition_unpaid_gbp
        data["available_funds_gbp"] = available_funds_gbp
        data["funds_held_28_days"] = funds_held_28_days
        data["requires_atas_clearance"] = requires_atas
        data["has_atas_certificate"] = has_atas
        data["has_tb_certificate"] = has_tb

    return data


def render_tourist_questionnaire(country_code: str) -> dict:
    """
    Renders the tourist/visitor visa questionnaire covering:
    - Travel Purpose & Duration
    - Itinerary & Accommodations
    - Employment & Financial Solvency
    - Ties to Home Country
    - International Travel History
    """
    st.markdown("#### Visitor & Tourist Visa Assessment Form")
    st.caption(f"Requirements tailored for **{country_code}** visitor visa processing.")

    # Section 1: Travel Purpose & Duration
    with st.expander("1. Travel Purpose, Schedule & Duration", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            travel_purpose = st.selectbox(
                "Primary Purpose of Travel",
                ["Tourism, Sightseeing & Vacation", "Visiting Family, Relatives or Friends", "Short Business Meetings, Conference or Trade Event", "Medical Visit or Transit"],
                index=0
            )
            trip_duration_days = st.slider("Planned Length of Stay (Days)", min_value=3, max_value=90, value=14, step=1)
        with col2:
            has_itinerary = st.checkbox("Day-by-day travel plan with confirmed or reserved accommodation", value=True)
            has_invitation = False
            if "Visiting Family" in travel_purpose or "Business" in travel_purpose:
                has_invitation = st.checkbox("Formal invitation letter from host or inviting company", value=True)
            passport_valid = st.checkbox("Passport valid for at least 6 months with blank visa pages", value=True)

    # Section 2: Employment Standing & Home Country Anchor
    with st.expander("2. Employment Standing & Work Ties", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            emp_status = st.selectbox(
                "Current Employment Status",
                ["Employed (Salaried)", "Business Owner / Self-Employed", "Active Student in Home Country", "Retired", "Unemployed / In Transition"],
                index=0
            )
            years_in_role = st.number_input("Years at Current Job / Business", min_value=0.1, max_value=40.0, value=3.5, step=0.5)
            monthly_income_usd = st.number_input("Monthly Net Income (USD Equivalent)", min_value=0, max_value=50000, value=2500, step=200)

        with col2:
            has_leave_letter = st.checkbox(
                "Approved leave letter / No-Objection Certificate (NOC) from employer",
                value=True if "Employed" in emp_status else False,
                help="Employer letter confirming authorized leave dates and guaranteed return to position."
            )
            owns_property = st.checkbox("Own residential, commercial property, or registered business in home country", value=False)
            has_family_ties = st.checkbox("Spouse, dependent children, or elderly parents staying in home country", value=True)

    # Section 3: Financial Capacity & Bank Records
    with st.expander("3. Travel Funds & Financial Records", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if country_code == "USA":
                available_funds_usd = st.number_input("Available Liquid Travel Funds (USD)", min_value=500, max_value=100000, value=7500, step=500)
            elif country_code == "Canada":
                available_funds_cad = st.number_input("Available Liquid Travel Funds (CAD)", min_value=500, max_value=120000, value=9000, step=500)
            elif country_code == "UK":
                available_funds_gbp = st.number_input("Available Liquid Travel Funds (GBP)", min_value=300, max_value=80000, value=5000, step=500)

            has_6m_statements = st.checkbox("Past 6 months official certified bank statements available", value=True)

        with col2:
            has_regular_credits = st.checkbox("Bank statements clearly show regular monthly salary or business income credits", value=True)
            has_unexplained_deposit = st.checkbox(
                "Recent large lump-sum deposit in bank account without clear documentation",
                value=False,
                help="Visa officers look closely at sudden unexplained deposits right before application submission."
            )

    # Section 4: Country-Specific Forms & Prior Travel
    with st.expander("4. Application Forms & International Travel History", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if country_code == "USA":
                ds160_submitted = st.checkbox("DS-160 visa application form completed and barcode confirmed", value=True)
            elif country_code == "Canada":
                imm_done = st.checkbox("IMM 5257 (Application) and IMM 5645 (Family Information) completed", value=True)
            elif country_code == "UK":
                uk_form_done = st.checkbox("Standard Visitor online application completed on UKVI portal", value=True)

        with col2:
            has_past_travel = st.checkbox(
                "Previously traveled internationally (e.g., USA, UK, Schengen, Canada, UAE) and followed visa rules",
                value=False
            )
            has_prior_refusals = st.checkbox("Have previously been refused a visa by any country", value=False)
            if has_prior_refusals:
                st.caption("Note: Prior refusals should always be disclosed honestly along with explanations of changed circumstances.")

    data = {
        "passport_valid_6m": passport_valid,
        "travel_purpose": travel_purpose,
        "trip_duration_days": trip_duration_days,
        "has_travel_itinerary": has_itinerary,
        "has_invitation_letter": has_invitation,
        "employment_status": "Employed" if "Employed" in emp_status else ("Business Owner" if "Business" in emp_status else ("Student" if "Student" in emp_status else "Unemployed")),
        "years_at_current_job": years_in_role,
        "annual_income_usd": monthly_income_usd * 12,
        "has_approved_leave_letter": has_leave_letter,
        "owns_property_or_business": owns_property,
        "has_dependent_family_in_home_country": has_family_ties,
        "has_6_months_bank_statements": has_6m_statements,
        "has_regular_credits": has_regular_credits,
        "has_recent_unexplained_large_deposits": has_unexplained_deposit,
        "has_previous_international_travel": has_past_travel,
        "has_prior_visa_refusals": has_prior_refusals,
    }

    if country_code == "USA":
        data["ds160_submitted"] = ds160_submitted
        data["travel_funds_usd"] = available_funds_usd
    elif country_code == "Canada":
        data["imm5257_completed"] = imm_done
        data["imm5645_completed"] = imm_done
        data["available_funds_cad"] = available_funds_cad
    elif country_code == "UK":
        data["available_funds_gbp"] = available_funds_gbp

    return data
