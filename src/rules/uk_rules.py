"""
uk_rules.py
Enhanced rule-based readiness assessment and document checklist engine for United Kingdom Visas:
- Student Visa (Points-Based System: 70 Points requirement, 28-day financial holding rule)
- Standard Visitor Visa (Immigration Rules Appendix V: Visitor)
"""

def evaluate_uk_student(data: dict) -> dict:
    checklist = []
    missing_docs = []
    strengths = []
    recommendations = []

    # UK Points-Based System (PBS) - 70 Points
    pbs_points = 0

    # 1. CAS Prerequisite (50 Points) (Weight in Readiness: 40)
    cas_score = 0
    cas_max = 40

    has_cas = data.get("has_cas_letter", False)
    if has_cas:
        pbs_points += 50
        cas_score += 40
        checklist.append({"item": "Confirmation of Acceptance for Studies (CAS) [50/50 PBS Points]", "status": "Verified", "category": "CAS Admission"})
        strengths.append("Valid CAS reference number issued by a licensed Student Sponsor institution.")
    else:
        checklist.append({"item": "Confirmation of Acceptance for Studies (CAS) [0/50 PBS Points]", "status": "Missing", "category": "CAS Admission"})
        missing_docs.append("Confirmation of Acceptance for Studies (CAS) - Required before booking appointment.")

    # 2. English Language SELT (10 Points) (Weight in Readiness: 15)
    eng_score = 0
    eng_max = 15

    has_english = data.get("has_ukvi_english_test", True)
    if has_english:
        pbs_points += 10
        eng_score += 15
        checklist.append({"item": "English Language SELT (CEFR B2 Level) [10/10 PBS Points]", "status": "Verified", "category": "English Qualification"})
        strengths.append("Approved Secure English Language Test (IELTS for UKVI / PTE UKVI) meets requirement.")
    else:
        checklist.append({"item": "English Language SELT [0/10 PBS Points]", "status": "Missing", "category": "English Qualification"})
        missing_docs.append("Approved Secure English Language Test (SELT) certificate showing minimum B2 level.")

    # 3. Financial Maintenance (10 Points) & 28-Day Rule (Weight in Readiness: 30)
    fin_score = 0
    fin_max = 30

    studying_in_london = data.get("studying_in_london", False)
    tuition_unpaid_gbp = float(data.get("tuition_unpaid_gbp", 14000))
    monthly_living = 1334.0 if studying_in_london else 1023.0
    total_maintenance = tuition_unpaid_gbp + (monthly_living * 9)

    available_funds_gbp = float(data.get("available_funds_gbp", 0))
    funds_held_28_days = data.get("funds_held_28_days", False)

    if available_funds_gbp >= total_maintenance:
        if funds_held_28_days:
            pbs_points += 10
            fin_score += 30
            checklist.append({"item": f"Maintenance Funds (£{available_funds_gbp:,.0f} held 28+ days) [10/10 PBS Points]", "status": "Verified", "category": "Maintenance Funds"})
            strengths.append(f"Financial maintenance satisfied (£{available_funds_gbp:,.0f} held for 28+ consecutive days).")
        else:
            fin_score += 15
            checklist.append({"item": "Maintenance Funds (28-Day Rule Not Met)", "status": "Critical Timing Gap", "category": "Maintenance Funds"})
            missing_docs.append("Funds must be held continuously for at least 28 consecutive days before the visa application submission date.")
            recommendations.append("UKVI strictly rejects applications if bank balance dips below the required amount at any single point during the 28-day window.")
    else:
        checklist.append({"item": "Maintenance Funds Threshold", "status": "Deficient", "category": "Maintenance Funds"})
        missing_docs.append(f"Maintenance shortfall: £{available_funds_gbp:,.0f} held vs £{total_maintenance:,.0f} required (Tuition £{tuition_unpaid_gbp:,.0f} + 9-month living £{(monthly_living * 9):,.0f}).")

    # 4. ATAS Clearance & TB Certificate (Weight in Readiness: 15)
    clear_score = 0
    clear_max = 15

    requires_atas = data.get("requires_atas_clearance", False)
    has_atas = data.get("has_atas_certificate", False)
    has_tb = data.get("has_tb_certificate", True)

    if requires_atas:
        if has_atas:
            clear_score += 8
            checklist.append({"item": "ATAS (Academic Technology Approval Scheme) Certificate", "status": "Verified", "category": "Clearances"})
            strengths.append("Valid ATAS clearance obtained.")
        else:
            checklist.append({"item": "ATAS Certificate", "status": "Action Required", "category": "Clearances"})
            missing_docs.append("ATAS clearance certificate (Mandatory for specified science/tech/engineering disciplines).")
    else:
        clear_score += 8
        checklist.append({"item": "ATAS Requirement Check", "status": "Exempt / Not Required", "category": "Clearances"})

    if has_tb:
        clear_score += 7
        checklist.append({"item": "Tuberculosis (TB) Certificate from Approved Clinic", "status": "Verified", "category": "Clearances"})
    else:
        checklist.append({"item": "Tuberculosis (TB) Certificate", "status": "Missing", "category": "Clearances"})
        missing_docs.append("Official TB test clearance certificate from a UKVI-approved clinic.")

    total_score = cas_score + eng_score + fin_score + clear_score

    if pbs_points == 70 and total_score >= 85:
        level = "Full PBS 70/70 Points Met (High Readiness)"
        color = "green"
    elif pbs_points >= 50:
        level = f"Partial PBS ({pbs_points}/70 Points) - Maintenance or English Incomplete"
        color = "orange"
    else:
        level = f"Incomplete PBS ({pbs_points}/70 Points) - Critical Requirements Missing"
        color = "red"

    return {
        "country": "UK",
        "visa_category": "Student Visa (Points-Based System)",
        "readiness_score": total_score,
        "max_score": 100,
        "pbs_points_awarded": pbs_points,
        "pbs_points_required": 70,
        "readiness_level": level,
        "indicator_color": color,
        "category_scores": {
            "CAS & Admission": round((cas_score / cas_max) * 100, 1),
            "English SELT": round((eng_score / eng_max) * 100, 1),
            "Financial Maintenance": round((fin_score / fin_max) * 100, 1),
            "Clearances & Health": round((clear_score / clear_max) * 100, 1)
        },
        "checklist": checklist,
        "missing_documents": missing_docs,
        "strengths": strengths,
        "recommendations": recommendations,
        "legal_basis": "UK Immigration Rules Appendix Student & Appendix Finance"
    }


def evaluate_uk_visitor(data: dict) -> dict:
    checklist = []
    missing_docs = []
    strengths = []
    recommendations = []

    # 1. Travel Documentation & Passport (Weight: 25)
    doc_score = 0
    doc_max = 25

    passport_valid = data.get("passport_valid_6m", True)
    has_itinerary = data.get("has_travel_itinerary", True)

    if passport_valid:
        doc_score += 15
        checklist.append({"item": "Passport with Blank Vignette Page", "status": "Verified", "category": "Documentation"})
    else:
        checklist.append({"item": "Passport Check", "status": "Deficient", "category": "Documentation"})
        missing_docs.append("Valid travel document with blank page for visa vignette.")

    if has_itinerary:
        doc_score += 10
        checklist.append({"item": "Planned Itinerary & Accommodation Reservations", "status": "Verified", "category": "Documentation"})
    else:
        checklist.append({"item": "Itinerary & Accommodation", "status": "Missing", "category": "Documentation"})
        missing_docs.append("Travel itinerary showing planned UK destinations and hotel bookings.")

    # 2. Genuine Intention to Leave & Ties (Weight: 35)
    ties_score = 0
    ties_max = 35

    emp_status = data.get("employment_status", "Employed")
    has_leave_letter = data.get("has_approved_leave_letter", False)
    has_property = data.get("owns_property_or_business", False)
    has_family_ties = data.get("has_dependent_family_in_home_country", True)

    if emp_status in ["Employed", "Business Owner"]:
        ties_score += 15
        checklist.append({"item": f"Occupational Attachment: {emp_status}", "status": "Verified", "category": "Home Ties"})
        strengths.append(f"Verifiable ongoing employment anchor: {emp_status}.")
    else:
        checklist.append({"item": "Occupational Attachment", "status": "Deficient", "category": "Home Ties"})
        recommendations.append("Provide evidence of ongoing university studies, retirement income, or dependent care duties to satisfy the genuine visitor test.")

    if has_leave_letter:
        ties_score += 10
        checklist.append({"item": "Employer Permission Letter & Salary Slips", "status": "Verified", "category": "Home Ties"})
        strengths.append("Employer letter confirming approved leave and continuing employment upon return.")
    else:
        checklist.append({"item": "Employer Permission Letter", "status": "Missing", "category": "Home Ties"})
        missing_docs.append("Formal letter from employer specifying role, salary, date of employment, and confirmation that holiday is approved.")

    if has_property or has_family_ties:
        ties_score += 10
        checklist.append({"item": "Domestic Property & Dependent Family Ties", "status": "Verified", "category": "Home Ties"})
        strengths.append("Documented property and family anchors in country of residence.")

    # 3. Financial Solvency & Funds Origin (Weight: 30)
    fin_score = 0
    fin_max = 30

    trip_days = int(data.get("trip_duration_days", 14))
    funds_gbp = float(data.get("available_funds_gbp", 3500))
    estimated_cost = trip_days * 150 + 1000

    has_6m = data.get("has_6_months_bank_statements", True)
    has_unexplained_deposit = data.get("has_recent_unexplained_large_deposits", False)

    if funds_gbp >= estimated_cost:
        if has_6m and not has_unexplained_deposit:
            fin_score += 30
            checklist.append({"item": f"6 Months Bank Statements (£{funds_gbp:,.0f} vs £{estimated_cost:,.0f} est. cost)", "status": "Verified", "category": "Finances"})
            strengths.append("Healthy bank history demonstrating genuine origin of funds matching declared salary.")
        elif has_unexplained_deposit:
            fin_score += 15
            checklist.append({"item": "Bank Statements (Unexplained Large Deposit)", "status": "High Scrutiny Warning", "category": "Finances"})
            missing_docs.append("Proof of legitimate origin for recent large lump-sum deposit (e.g. sale contract, bonus slip, investment maturity).")
            recommendations.append("UKVI caseworkers routinely refuse visas if accounts display sudden unexplained deposits ('funds parking').")
        else:
            fin_score += 20
            checklist.append({"item": "Bank Statements (Limited History)", "status": "Partial", "category": "Finances"})
    else:
        checklist.append({"item": "Bank Statements", "status": "Deficient", "category": "Finances"})
        missing_docs.append(f"Insufficient funds: £{funds_gbp:,.0f} held vs estimated visit cost of £{estimated_cost:,.0f}.")

    # 4. Prior Travel Compliance (Weight: 10)
    has_past_travel = data.get("has_previous_international_travel", False)
    travel_score = 10 if has_past_travel else 5
    checklist.append({"item": "Prior Visas & Travel Track Record", "status": "Verified" if has_past_travel else "First-Time Traveler", "category": "Travel Record"})
    if has_past_travel:
        strengths.append("Established track record of international visa compliance.")

    total_score = doc_score + ties_score + fin_score + travel_score

    if total_score >= 80:
        level = "High Readiness"
        color = "green"
    elif total_score >= 60:
        level = "Moderate Readiness"
        color = "orange"
    else:
        level = "Low Readiness (Genuine Visitor / Financial Scrutiny Risk)"
        color = "red"

    return {
        "country": "UK",
        "visa_category": "Standard Visitor Visa",
        "readiness_score": total_score,
        "max_score": 100,
        "readiness_level": level,
        "indicator_color": color,
        "category_scores": {
            "Documentation": round((doc_score / doc_max) * 100, 1),
            "Home Ties & Job": round((ties_score / ties_max) * 100, 1),
            "Funds & Origin": round((fin_score / fin_max) * 100, 1),
            "Travel Compliance": round((travel_score / 10) * 100, 1)
        },
        "checklist": checklist,
        "missing_documents": missing_docs,
        "strengths": strengths,
        "recommendations": recommendations,
        "legal_basis": "UK Immigration Rules Appendix V: Visitor"
    }
