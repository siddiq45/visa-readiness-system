"""
canada_rules.py
Enhanced rule-based readiness assessment and document checklist engine for Canadian Visas:
- Study Permit (IRPA & IRPR, PAL/TAL Mandate, CAD $20,635 Maintenance Rule)
- Visitor Visa (Temporary Resident Visa - TRV, IRPA s.179(b))
"""

def evaluate_canada_study(data: dict) -> dict:
    checklist = []
    missing_docs = []
    strengths = []
    recommendations = []

    # 1. Admission & Provincial Attestation Letter (Weight: 30)
    adm_score = 0
    adm_max = 30

    has_loa = data.get("has_loa", False)
    if has_loa:
        adm_score += 15
        checklist.append({"item": "Letter of Acceptance (LOA) from DLI", "status": "Verified", "category": "Admission"})
        strengths.append("Unconditional acceptance letter from Designated Learning Institution (DLI).")
    else:
        checklist.append({"item": "Letter of Acceptance (LOA)", "status": "Missing", "category": "Admission"})
        missing_docs.append("Official Letter of Acceptance from a Canadian DLI.")

    has_pal = data.get("has_pal_or_exemption", False)
    if has_pal:
        adm_score += 15
        checklist.append({"item": "Provincial Attestation Letter (PAL) / Exemption", "status": "Verified", "category": "Admission"})
        strengths.append("Complies with mandatory IRCC Provincial Attestation Letter quota requirements.")
    else:
        checklist.append({"item": "Provincial Attestation Letter (PAL)", "status": "Action Required", "category": "Admission"})
        missing_docs.append("Provincial Attestation Letter (PAL) from the province of study (Mandatory for post-secondary study permits).")

    # 2. Financial Sufficiency (CAD $20,635 Living + Tuition) (Weight: 35)
    fin_score = 0
    fin_max = 35

    tuition_cad = float(data.get("tuition_fee_cad", 22000))
    min_living_cost_cad = 20635.0  # IRCC official standard
    total_required_cad = tuition_cad + min_living_cost_cad

    available_funds_cad = float(data.get("available_funds_cad", 0))
    has_gic = data.get("has_gic_certificate", False)

    if has_gic:
        fin_score += 15
        checklist.append({"item": "Guaranteed Investment Certificate (GIC) of CAD $20,635+", "status": "Verified", "category": "Finances"})
        strengths.append("GIC certificate confirmed with participating Canadian financial institution.")
    else:
        checklist.append({"item": "GIC Certificate", "status": "Recommended", "category": "Finances"})
        recommendations.append("A CAD $20,635 GIC substantially simplifies proof of living expenses and expedites IRCC file assessment.")

    coverage = available_funds_cad / total_required_cad if total_required_cad > 0 else 0
    if coverage >= 1.15:
        fin_score += 20
        checklist.append({"item": f"Proof of 1st Year Costs (CAD ${available_funds_cad:,.0f} vs ${total_required_cad:,.0f})", "status": "Verified", "category": "Finances"})
        strengths.append(f"Documented funds cover {coverage:.1f}x combined tuition + mandatory living expenses.")
    elif coverage >= 1.0:
        fin_score += 15
        checklist.append({"item": f"Proof of 1st Year Costs (CAD ${available_funds_cad:,.0f})", "status": "Satisfactory", "category": "Finances"})
    else:
        fin_score += 5
        checklist.append({"item": "Proof of 1st Year Costs", "status": "Deficient", "category": "Finances"})
        missing_docs.append(f"Financial shortfall: Requires at least CAD ${total_required_cad:,.0f} (Tuition CAD ${tuition_cad:,.0f} + Living CAD $20,635).")

    # 3. Statement of Purpose & Academic Continuity (Weight: 20)
    sop_score = 0
    sop_max = 20

    has_study_plan = data.get("has_detailed_study_plan", True)
    course_matches_career = data.get("course_matches_academic_history", True)
    has_study_gap = data.get("has_study_gap", False)

    if has_study_plan and course_matches_career:
        sop_score += 20
        checklist.append({"item": "Statement of Purpose (SOP) with Study Plan & Career Rationale", "status": "Verified", "category": "Study Plan"})
        strengths.append("SOP demonstrates clear educational progression and domestic career benefits.")
    elif has_study_plan:
        sop_score += 12
        checklist.append({"item": "Statement of Purpose", "status": "Needs Clarification", "category": "Study Plan"})
        recommendations.append("Articulate in your SOP why this Canadian program is worth the international investment compared to local alternatives.")
    else:
        checklist.append({"item": "Statement of Purpose (SOP)", "status": "Missing", "category": "Study Plan"})
        missing_docs.append("Structured Statement of Purpose explaining academic intent and domestic employment outlook.")

    if has_study_gap:
        recommendations.append("Provide verifiable employment records and tax slips to account for all post-graduation gap periods.")

    # 4. Clearances & Language (Weight: 15)
    clear_score = 0
    clear_max = 15

    has_ielts = data.get("has_language_test", True)
    has_medical = data.get("has_upfront_medical", False)
    has_pcc = data.get("has_police_certificate", False)

    if has_ielts:
        clear_score += 7
        checklist.append({"item": "Official Language Test Scorecard (IELTS / PTE / CELPIP)", "status": "Verified", "category": "Clearances"})
    else:
        checklist.append({"item": "Language Test Scorecard", "status": "Missing", "category": "Clearances"})
        missing_docs.append("Official language proficiency test results.")

    if has_medical:
        clear_score += 4
        checklist.append({"item": "Upfront Medical Examination (eMedical)", "status": "Verified", "category": "Clearances"})
    else:
        checklist.append({"item": "Upfront Medical Exam", "status": "Pending", "category": "Clearances"})

    if has_pcc:
        clear_score += 4
        checklist.append({"item": "Police Clearance Certificate (PCC)", "status": "Verified", "category": "Clearances"})
    else:
        checklist.append({"item": "Police Clearance Certificate", "status": "Pending", "category": "Clearances"})

    total_score = adm_score + fin_score + sop_score + clear_score

    if total_score >= 85:
        level = "High Readiness (Complete Application Profile)"
        color = "green"
    elif total_score >= 65:
        level = "Moderate Readiness (Key Actions Required)"
        color = "orange"
    else:
        level = "Low Readiness (Substantial Compliance Gaps)"
        color = "red"

    return {
        "country": "Canada",
        "visa_category": "Study Permit (Post-Secondary)",
        "readiness_score": total_score,
        "max_score": 100,
        "readiness_level": level,
        "indicator_color": color,
        "category_scores": {
            "DLI & PAL Admission": round((adm_score / adm_max) * 100, 1),
            "Financial Maintenance": round((fin_score / fin_max) * 100, 1),
            "Study Plan & Continuity": round((sop_score / sop_max) * 100, 1),
            "Clearances & Language": round((clear_score / clear_max) * 100, 1)
        },
        "checklist": checklist,
        "missing_documents": missing_docs,
        "strengths": strengths,
        "recommendations": recommendations,
        "legal_basis": "Immigration and Refugee Protection Act (IRPA) s.30 & IRPR Part 12 (Study Permits)"
    }


def evaluate_canada_visitor(data: dict) -> dict:
    checklist = []
    missing_docs = []
    strengths = []
    recommendations = []

    # 1. Statutory Forms & Passport (Weight: 25)
    doc_score = 0
    doc_max = 25

    imm5257_filled = data.get("imm5257_completed", True)
    imm5645_filled = data.get("imm5645_completed", True)
    passport_valid = data.get("passport_valid_6m", True)

    if imm5257_filled and imm5645_filled:
        doc_score += 15
        checklist.append({"item": "IMM 5257 (Application) & IMM 5645 (Family Info)", "status": "Verified", "category": "Documentation"})
    else:
        checklist.append({"item": "IMM 5257 & Family Info Forms", "status": "Pending", "category": "Documentation"})
        missing_docs.append("Completed Application for Visitor Visa (IMM 5257) and Family Information (IMM 5645).")

    if passport_valid:
        doc_score += 10
        checklist.append({"item": "Passport (Valid for Canadian Visit)", "status": "Verified", "category": "Documentation"})
    else:
        checklist.append({"item": "Passport Validity Check", "status": "Deficient", "category": "Documentation"})
        missing_docs.append("Valid travel document with blank visa pages.")

    # 2. Ties to Country of Residence (IRPA s.179(b)) (Weight: 35)
    ties_score = 0
    ties_max = 35

    emp_status = data.get("employment_status", "Employed")
    has_leave_letter = data.get("has_approved_leave_letter", False)
    has_property = data.get("owns_property_or_business", False)
    has_family_ties = data.get("has_dependent_family_in_home_country", True)

    if emp_status in ["Employed", "Business Owner"]:
        ties_score += 15
        checklist.append({"item": f"Documented Employment Anchor: {emp_status}", "status": "Verified", "category": "Home Ties"})
        strengths.append(f"Ongoing occupational anchor: {emp_status}.")
    else:
        checklist.append({"item": "Employment Anchor", "status": "Deficient", "category": "Home Ties"})
        recommendations.append("Provide proof of local family responsibilities, community standing, or pension under IRPA s.179(b).")

    if has_leave_letter:
        ties_score += 10
        checklist.append({"item": "Employer Leave Certificate with Job Guarantee", "status": "Verified", "category": "Home Ties"})
        strengths.append("Employer letter confirming sanctioned leave and continuation of employment.")
    else:
        checklist.append({"item": "Employer Leave Certificate", "status": "Missing", "category": "Home Ties"})
        missing_docs.append("Employer leave approval letter indicating salary, tenure, and return date.")

    if has_property or has_family_ties:
        ties_score += 10
        checklist.append({"item": "Proof of Domestic Real Estate / Family Anchor", "status": "Verified", "category": "Home Ties"})
        strengths.append("Established domestic property ownership and immediate family remaining in home country.")

    # 3. Financial Means (Weight: 25)
    fin_score = 0
    fin_max = 25

    trip_days = int(data.get("trip_duration_days", 14))
    funds_cad = float(data.get("available_funds_cad", 6500))
    estimated_cost_cad = trip_days * 250 + 2000

    if funds_cad >= estimated_cost_cad * 1.5:
        fin_score += 25
        checklist.append({"item": f"Certified Bank Statements (CAD ${funds_cad:,.0f} vs ${estimated_cost_cad:,.0f} est. cost)", "status": "Verified", "category": "Finances"})
        strengths.append("6 months certified bank statements demonstrating unencumbered liquid funds.")
    elif funds_cad >= estimated_cost_cad:
        fin_score += 18
        checklist.append({"item": f"Certified Bank Statements (CAD ${funds_cad:,.0f})", "status": "Satisfactory", "category": "Finances"})
    else:
        fin_score += 5
        checklist.append({"item": "Certified Bank Statements", "status": "Insufficient", "category": "Finances"})
        missing_docs.append(f"Financial shortfall: CAD ${funds_cad:,.0f} held vs estimated visit budget of CAD ${estimated_cost_cad:,.0f}.")

    # 4. Travel Purpose & Prior Travel (Weight: 15)
    purp_score = 0
    purp_max = 15

    has_invitation = data.get("has_invitation_letter", False)
    has_itinerary = data.get("has_travel_itinerary", True)
    has_past_travel = data.get("has_previous_international_travel", False)

    if has_invitation:
        purp_score += 10
        checklist.append({"item": "Host Invitation Letter & Legal Status (PR/Citizen)", "status": "Verified", "category": "Travel Purpose"})
        strengths.append("Host invitation letter backed by host's Canadian status / Notice of Assessment.")
    elif has_itinerary:
        purp_score += 10
        checklist.append({"item": "Tourism Itinerary & Accommodation Bookings", "status": "Verified", "category": "Travel Purpose"})

    if has_past_travel:
        purp_score += 5
        checklist.append({"item": "Past Compliant International Travel", "status": "Verified", "category": "Travel Purpose"})
        strengths.append("Documented history of international visa compliance.")

    total_score = doc_score + ties_score + fin_score + purp_score

    if total_score >= 80:
        level = "High Readiness"
        color = "green"
    elif total_score >= 60:
        level = "Moderate Readiness"
        color = "orange"
    else:
        level = "Low Readiness (Refusal Risk Under s.179(b))"
        color = "red"

    return {
        "country": "Canada",
        "visa_category": "Visitor Visa (Temporary Resident Visa)",
        "readiness_score": total_score,
        "max_score": 100,
        "readiness_level": level,
        "indicator_color": color,
        "category_scores": {
            "Documentation": round((doc_score / doc_max) * 100, 1),
            "Ties to Home Country": round((ties_score / ties_max) * 100, 1),
            "Financial Means": round((fin_score / fin_max) * 100, 1),
            "Travel Purpose & History": round((purp_score / purp_max) * 100, 1)
        },
        "checklist": checklist,
        "missing_documents": missing_docs,
        "strengths": strengths,
        "recommendations": recommendations,
        "legal_basis": "Immigration and Refugee Protection Regulations (IRPR) s.179(b)"
    }
