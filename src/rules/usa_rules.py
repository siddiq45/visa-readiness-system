"""
usa_rules.py
Enhanced rule-based readiness assessment and document checklist engine for USA Visas:
- F1 Student Visa (INA Section 101(a)(15)(F) & INA 214(b))
- B1/B2 Tourist Visa (INA Section 101(a)(15)(B) & INA 214(b))
"""

def evaluate_usa_f1(data: dict) -> dict:
    checklist = []
    missing_docs = []
    strengths = []
    recommendations = []

    # 1. Core Mandatory Documents (Weight: 35)
    doc_score = 0
    doc_max = 35

    has_i20 = data.get("has_i20", False)
    if has_i20:
        doc_score += 15
        checklist.append({"item": "Form I-20 from SEVP-Certified School", "status": "Verified", "category": "Documentation"})
        strengths.append("Possesses valid Form I-20 issued by a SEVP-certified institution.")
    else:
        checklist.append({"item": "Form I-20 from SEVP-Certified School", "status": "Missing", "category": "Documentation"})
        missing_docs.append("Form I-20 Certificate of Eligibility (Mandatory prerequisite for visa interview).")

    sevis_paid = data.get("sevis_fee_paid", False)
    if sevis_paid:
        doc_score += 10
        checklist.append({"item": "SEVIS I-901 Fee Receipt ($350)", "status": "Verified", "category": "Documentation"})
        strengths.append("SEVIS I-901 fee recorded and paid.")
    else:
        checklist.append({"item": "SEVIS I-901 Fee Receipt ($350)", "status": "Action Required", "category": "Documentation"})
        missing_docs.append("SEVIS I-901 Fee Payment Receipt (Must be paid before the consular interview).")

    ds160_completed = data.get("ds160_submitted", False)
    if ds160_completed:
        doc_score += 5
        checklist.append({"item": "DS-160 Confirmation Page & Barcode", "status": "Verified", "category": "Documentation"})
    else:
        checklist.append({"item": "DS-160 Confirmation Page & Barcode", "status": "Pending", "category": "Documentation"})
        missing_docs.append("DS-160 Online Nonimmigrant Visa Application Confirmation.")

    passport_valid = data.get("passport_valid_6m", True)
    if passport_valid:
        doc_score += 5
        checklist.append({"item": "Passport (Valid 6+ months beyond stay)", "status": "Verified", "category": "Documentation"})
    else:
        checklist.append({"item": "Passport Validity Check", "status": "Warning", "category": "Documentation"})
        missing_docs.append("Valid passport with at least 6 months validity beyond your intended period of study.")

    # 2. Financial Capability & Sponsorship (Weight: 30)
    fin_score = 0
    fin_max = 30

    tuition_living_usd = float(data.get("annual_tuition_living_usd", 40000))
    liquid_funds_usd = float(data.get("liquid_funds_usd", 0))
    has_loan_sanction = data.get("has_loan_sanction_letter", False)
    sponsor_type = data.get("sponsor_type", "Parents")
    has_sponsor_affidavit = data.get("has_sponsor_affidavit", True)

    effective_funds = liquid_funds_usd + (tuition_living_usd * 0.8 if has_loan_sanction else 0)
    coverage_ratio = effective_funds / tuition_living_usd if tuition_living_usd > 0 else 0

    if coverage_ratio >= 1.3:
        fin_score += 25
        checklist.append({"item": f"Liquid Funds & Loan Coverage ({coverage_ratio:.1f}x I-20)", "status": "Verified", "category": "Finances"})
        strengths.append(f"Substantial financial buffer: documented funds cover {coverage_ratio:.1f}x Year-1 expenses.")
    elif coverage_ratio >= 1.0:
        fin_score += 18
        checklist.append({"item": f"Liquid Funds & Loan Coverage ({coverage_ratio:.1f}x I-20)", "status": "Satisfactory", "category": "Finances"})
        strengths.append("Meets exact Year-1 I-20 financial threshold.")
        recommendations.append("Consider showing documented funding sources or liquid reserves for Year-2 to reinforce financial solvency.")
    else:
        fin_score += 5
        checklist.append({"item": f"Liquid Funds Coverage (Only {coverage_ratio:.1f}x I-20)", "status": "Deficient", "category": "Finances"})
        missing_docs.append(f"Financial shortfall: Current funding is ${(tuition_living_usd - effective_funds):,.0f} below Year-1 Form I-20 requirement.")
        recommendations.append("Obtain an approved educational loan sanction letter or verifiable affidavit of support with sponsor tax filings.")

    if has_sponsor_affidavit or sponsor_type == "Self":
        fin_score += 5
        checklist.append({"item": "Sponsor Affidavit (I-134) & Tax Filings / Bank Statements", "status": "Verified", "category": "Finances"})
    else:
        checklist.append({"item": "Sponsor Affidavit & Tax Returns", "status": "Missing", "category": "Finances"})
        missing_docs.append("Signed Affidavit of Support (Form I-134) accompanied by sponsor's recent tax returns / Form 16.")

    # 3. Non-Immigrant Intent & Ties to Home Country (INA 214(b)) (Weight: 20)
    ties_score = 0
    ties_max = 20

    has_family_ties = data.get("has_dependent_family_in_home_country", True)
    owns_property = data.get("owns_property_or_business", False)
    has_career_plan = data.get("has_career_progression_plan", True)
    has_job_offer_or_leave = data.get("has_job_offer_or_leave", False)

    if has_family_ties:
        ties_score += 5
        checklist.append({"item": "Immediate Family Ties in Home Country", "status": "Verified", "category": "Home Ties"})
    if owns_property:
        ties_score += 5
        checklist.append({"item": "Documented Immovable Property / Assets in Home Country", "status": "Verified", "category": "Home Ties"})
        strengths.append("Possesses documented domestic assets/real estate tying applicant to country of origin.")
    if has_career_plan:
        ties_score += 5
        checklist.append({"item": "Articulated Post-Study Career Trajectory in Home Country", "status": "Verified", "category": "Home Ties"})
        strengths.append("Clear domestic career plan demonstrating non-immigrant intent under INA 214(b).")
    if has_job_offer_or_leave:
        ties_score += 5
        checklist.append({"item": "Sabbatical / Re-employment Agreement", "status": "Verified", "category": "Home Ties"})

    if ties_score < 10:
        recommendations.append("Prepare a concise, convincing explanation of why your US degree is essential for career advancement in your home country to overcome the statutory immigrant intent presumption under Section 214(b).")

    # 4. Academic Credibility & Study Plan (Weight: 15)
    acad_score = 0
    acad_max = 15

    has_english = data.get("has_english_test", True)
    has_transcripts = data.get("has_academic_transcripts", True)
    has_study_gap = data.get("has_study_gap", False)
    gap_justified = data.get("study_gap_justified", True)

    if has_english:
        acad_score += 5
        checklist.append({"item": "English Language Proficiency (TOEFL / IELTS / Duolingo / Waiver)", "status": "Verified", "category": "Academic"})
    else:
        checklist.append({"item": "English Language Test Report", "status": "Missing", "category": "Academic"})
        missing_docs.append("Standardized English test scorecard or university waiver letter.")

    if has_transcripts:
        acad_score += 5
        checklist.append({"item": "Official Academic Transcripts & Degree Certificates", "status": "Verified", "category": "Academic"})
    else:
        checklist.append({"item": "Official Transcripts", "status": "Missing", "category": "Academic"})
        missing_docs.append("Certified official transcripts from all previously attended institutions.")

    if not has_study_gap or (has_study_gap and gap_justified):
        acad_score += 5
        checklist.append({"item": "Study History Continuity / Gap Justification", "status": "Verified", "category": "Academic"})
    else:
        checklist.append({"item": "Study Gap Documentation", "status": "Action Required", "category": "Academic"})
        missing_docs.append("Documentation (employment experience letters, certificates) explaining educational gaps.")
        recommendations.append("Be prepared to explain any gap years with factual work experience or preparation records.")

    total_score = doc_score + fin_score + ties_score + acad_score

    # Determine readiness tier
    if total_score >= 85:
        level = "High Readiness (Interview Ready)"
        color = "green"
    elif total_score >= 65:
        level = "Moderate Readiness (Minor Gaps to Close)"
        color = "orange"
    else:
        level = "Low Readiness (Substantial Compliance Gaps)"
        color = "red"

    return {
        "country": "USA",
        "visa_category": "F-1 Academic Student Visa",
        "readiness_score": total_score,
        "max_score": 100,
        "readiness_level": level,
        "indicator_color": color,
        "category_scores": {
            "Documentation": round((doc_score / doc_max) * 100, 1),
            "Financial Capability": round((fin_score / fin_max) * 100, 1),
            "Home Ties (INA 214b)": round((ties_score / ties_max) * 100, 1),
            "Academic Credibility": round((acad_score / acad_max) * 100, 1)
        },
        "checklist": checklist,
        "missing_documents": missing_docs,
        "strengths": strengths,
        "recommendations": recommendations,
        "legal_basis": "U.S. Immigration and Nationality Act (INA) §§ 101(a)(15)(F) & 214(b)"
    }


def evaluate_usa_b1b2(data: dict) -> dict:
    checklist = []
    missing_docs = []
    strengths = []
    recommendations = []

    # 1. Application & Documentation (Weight: 25)
    doc_score = 0
    doc_max = 25

    ds160_completed = data.get("ds160_submitted", False)
    if ds160_completed:
        doc_score += 15
        checklist.append({"item": "DS-160 Nonimmigrant Visa Confirmation Page", "status": "Verified", "category": "Documentation"})
    else:
        checklist.append({"item": "DS-160 Nonimmigrant Visa Confirmation", "status": "Pending", "category": "Documentation"})
        missing_docs.append("DS-160 Online Confirmation Sheet.")

    passport_valid = data.get("passport_valid_6m", True)
    if passport_valid:
        doc_score += 10
        checklist.append({"item": "Passport (Valid 6+ months)", "status": "Verified", "category": "Documentation"})
    else:
        checklist.append({"item": "Passport Validity Check", "status": "Deficient", "category": "Documentation"})
        missing_docs.append("Passport valid for at least 6 months beyond intended stay.")

    # 2. Employment Stability & Home Country Ties (INA 214(b)) (Weight: 35)
    ties_score = 0
    ties_max = 35

    emp_status = data.get("employment_status", "Employed")
    years_job = float(data.get("years_at_current_job", 3.0))
    has_leave_letter = data.get("has_approved_leave_letter", False)
    owns_property = data.get("owns_property_or_business", False)
    has_family_ties = data.get("has_dependent_family_in_home_country", True)

    if emp_status in ["Employed", "Business Owner"]:
        ties_score += 15
        checklist.append({"item": f"Verifiable Employment / Business ({years_job:.1f} yrs)", "status": "Verified", "category": "Home Ties"})
        strengths.append(f"Stable employment status: {emp_status} with continuous track record.")
    elif emp_status == "Student":
        ties_score += 10
        checklist.append({"item": "Current University Enrollment in Home Country", "status": "Verified", "category": "Home Ties"})
    else:
        checklist.append({"item": "Employment Proof", "status": "Deficient", "category": "Home Ties"})
        recommendations.append("Unemployed applicants encounter heavy scrutiny under INA 214(b); provide documented proof of family financial security or pension.")

    if has_leave_letter:
        ties_score += 10
        checklist.append({"item": "Approved Leave Letter / No-Objection Certificate (NOC)", "status": "Verified", "category": "Home Ties"})
        strengths.append("Employer has formally sanctioned leave with confirmed resumption date.")
    else:
        checklist.append({"item": "Employer Leave Letter / NOC", "status": "Missing", "category": "Home Ties"})
        missing_docs.append("Formal NOC / approved leave letter on company letterhead.")

    if owns_property or has_family_ties:
        ties_score += 10
        checklist.append({"item": "Property Deeds / Dependent Family in Home Country", "status": "Verified", "category": "Home Ties"})
        strengths.append("Verifiable social and physical assets in country of residence.")

    # 3. Financial Solvency for Trip (Weight: 25)
    fin_score = 0
    fin_max = 25

    trip_days = int(data.get("trip_duration_days", 14))
    funds_usd = float(data.get("travel_funds_usd", 6000))
    estimated_cost = trip_days * 200 + 1500

    if funds_usd >= estimated_cost * 1.5:
        fin_score += 25
        checklist.append({"item": f"Bank Statements (${funds_usd:,.0f} vs ${estimated_cost:,.0f} est. cost)", "status": "Verified", "category": "Finances"})
        strengths.append(f"Substantial liquid funds exceeding 150% of estimated trip expenditure.")
    elif funds_usd >= estimated_cost:
        fin_score += 18
        checklist.append({"item": f"Bank Statements (${funds_usd:,.0f} funds)", "status": "Satisfactory", "category": "Finances"})
    else:
        fin_score += 5
        checklist.append({"item": "Bank Statements", "status": "Low Funds", "category": "Finances"})
        missing_docs.append(f"Insufficient funds: Holding ${funds_usd:,.0f} vs ${estimated_cost:,.0f} estimated travel costs.")

    # 4. Travel History & Purpose Clarity (Weight: 15)
    travel_score = 0
    travel_max = 15

    has_itinerary = data.get("has_travel_itinerary", True)
    has_past_travel = data.get("has_previous_international_travel", False)
    has_refusals = data.get("has_prior_visa_refusals", False)

    if has_itinerary:
        travel_score += 8
        checklist.append({"item": "Day-by-Day Travel Plan & Hotel Bookings", "status": "Verified", "category": "Travel Intent"})
    else:
        checklist.append({"item": "Travel Itinerary", "status": "Missing", "category": "Travel Intent"})
        missing_docs.append("Structured day-by-day travel itinerary with accommodation plans.")

    if has_past_travel:
        travel_score += 7
        checklist.append({"item": "Past International Travel Compliance", "status": "Verified", "category": "Travel Intent"})
        strengths.append("Established history of international travel without visa violations.")
    else:
        checklist.append({"item": "International Travel Record", "status": "First-Time Traveler", "category": "Travel Intent"})

    if has_refusals:
        travel_score = max(0, travel_score - 5)
        recommendations.append("Disclose prior visa refusals fully on Form DS-160 and be prepared to articulate what circumstances have improved since the previous decision.")

    total_score = doc_score + ties_score + fin_score + travel_score

    if total_score >= 80:
        level = "High Readiness"
        color = "green"
    elif total_score >= 60:
        level = "Moderate Readiness"
        color = "orange"
    else:
        level = "Low Readiness (Substantial 214(b) Risk)"
        color = "red"

    return {
        "country": "USA",
        "visa_category": "B-1/B-2 Tourist & Visitor Visa",
        "readiness_score": total_score,
        "max_score": 100,
        "readiness_level": level,
        "indicator_color": color,
        "category_scores": {
            "Documentation": round((doc_score / doc_max) * 100, 1),
            "Home Ties (INA 214b)": round((ties_score / ties_max) * 100, 1),
            "Financial Solvency": round((fin_score / fin_max) * 100, 1),
            "Travel Intent & History": round((travel_score / travel_max) * 100, 1)
        },
        "checklist": checklist,
        "missing_documents": missing_docs,
        "strengths": strengths,
        "recommendations": recommendations,
        "legal_basis": "U.S. Immigration and Nationality Act (INA) §§ 101(a)(15)(B) & 214(b)"
    }
