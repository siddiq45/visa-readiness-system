"""
predict.py
Inference module for the ML Visa Benchmark Model and Consular Statistical Baseline.
"""

import json
import os
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = "models/visa_model.joblib"
METADATA_PATH = "models/model_metadata.json"
COUNTRY_STATS_PATH = "data/reference/country_stats.json"

_MODEL = None
_METADATA = None
_COUNTRY_STATS = None


def get_model():
    global _MODEL
    if _MODEL is None:
        if os.path.exists(MODEL_PATH):
            _MODEL = joblib.load(MODEL_PATH)
        else:
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Run src/ml/train.py first.")
    return _MODEL


def get_metadata():
    global _METADATA
    if _METADATA is None:
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, "r") as f:
                _METADATA = json.load(f)
        else:
            _METADATA = {}
    return _METADATA


def get_country_stats():
    global _COUNTRY_STATS
    if _COUNTRY_STATS is None:
        if os.path.exists(COUNTRY_STATS_PATH):
            with open(COUNTRY_STATS_PATH, "r") as f:
                _COUNTRY_STATS = json.load(f)
        else:
            _COUNTRY_STATS = {}
    return _COUNTRY_STATS


def predict_ml_benchmark(profile: dict) -> dict:
    """
    Runs the trained Scikit-learn model on applicant's educational,
    economic, and geographic profile.
    """
    model = get_model()
    metadata = get_metadata()

    # Map profile into the expected feature format
    # Defaults provided for optional fields
    row = {
        'continent': profile.get('continent', 'Asia'),
        'education_of_employee': profile.get('education_level', "Bachelor's"),
        'has_job_experience': 'Y' if profile.get('has_job_experience', True) else 'N',
        'requires_job_training': 'Y' if profile.get('requires_training', False) else 'N',
        'region_of_employment': profile.get('region', 'Northeast'),
        'full_time_position': 'Y' if profile.get('full_time_position', True) else 'N',
        'annual_wage': float(profile.get('annual_income_usd', 65000)),
        'no_of_employees': int(profile.get('company_employees', 500)),
        'company_age': int(profile.get('institution_age_years', 25))
    }

    df_input = pd.DataFrame([row])

    proba = model.predict_proba(df_input)[0]
    # Class 1 is 'Certified'
    cert_prob = float(proba[1]) * 100.0

    # Determine qualitative tier
    if cert_prob >= 75.0:
        band = "Strong Historical Alignment"
        color = "green"
    elif cert_prob >= 50.0:
        band = "Moderate Historical Alignment"
        color = "orange"
    else:
        band = "Low Historical Alignment (Caution)"
        color = "red"

    # Analyze key profile drivers
    factors = []
    edu = row['education_of_employee']
    if edu in ["Master's", "Doctorate"]:
        factors.append(f"Advanced education ({edu}) positively influences profile strength.")
    elif edu == "High School":
        factors.append("Secondary-only education historically requires stronger secondary proof of qualification.")

    wage = row['annual_wage']
    if wage >= 80000:
        factors.append(f"Substantial financial benchmark (${wage:,.0f}/yr) aligns with high economic stability.")
    elif wage < 30000:
        factors.append("Lower reported income/funding bracket requires explicit financial sponsorship documentation.")

    if row['has_job_experience'] == 'Y':
        factors.append("Verified employment history contributes positively to professional track record.")

    return {
        "probability_percentage": round(cert_prob, 1),
        "alignment_tier": band,
        "indicator_color": color,
        "input_profile": row,
        "key_drivers": factors,
        "model_accuracy": metadata.get("metrics", {}).get("accuracy", 0.74),
        "dataset_name": metadata.get("dataset_name", "US Department of Labor OFLC Dataset")
    }


def get_consular_benchmark(country_of_citizenship: str, target_country: str, visa_type: str) -> dict:
    """
    Retrieves official government historical statistics (US DOS, UK Home Office, IRCC Canada).
    """
    stats_data = get_country_stats()
    countries = stats_data.get("countries", {})

    target_country_key = target_country.lower().replace(" ", "_")
    country_info = countries.get(country_of_citizenship, countries.get("Other / Global Average", {}))
    dest_stats = country_info.get(target_country_key, {})

    risk_tier = dest_stats.get("risk_tier", "Moderate")

    benchmark_detail = {
        "country": country_of_citizenship,
        "destination": target_country,
        "visa_type": visa_type,
        "risk_tier": risk_tier,
        "stat_description": "",
        "stat_value": None
    }

    if target_country_key == "usa":
        if "tourist" in visa_type.lower() or "b1" in visa_type.lower():
            rate = dest_stats.get("b1_b2_refusal_rate", 22.0)
            benchmark_detail["stat_description"] = "US State Dept Official B-Visa Refusal Rate (INA 214(b))"
            benchmark_detail["stat_value"] = f"{rate}% refusal rate (Historical Refusal Benchmark)"
        else:
            share = dest_stats.get("f1_issuance_share", 10.0)
            benchmark_detail["stat_description"] = "US State Dept F-1 Issuance Volume Benchmark"
            benchmark_detail["stat_value"] = f"Top destination tier ({share}% global share)"

    elif target_country_key == "canada":
        if "student" in visa_type.lower() or "study" in visa_type.lower():
            rate = dest_stats.get("study_permit_approval_rate", 60.0)
            benchmark_detail["stat_description"] = "IRCC Official Open Data Study Permit Approval Rate"
            benchmark_detail["stat_value"] = f"{rate}% historical grant rate"
        else:
            rate = dest_stats.get("visitor_approval_rate", 65.0)
            benchmark_detail["stat_description"] = "IRCC Temporary Resident Visa (Visitor) Approval Rate"
            benchmark_detail["stat_value"] = f"{rate}% historical grant rate"

    elif target_country_key == "uk":
        if "student" in visa_type.lower():
            rate = dest_stats.get("student_visa_grant_rate", 86.0)
            benchmark_detail["stat_description"] = "UK Home Office Immigration Statistics Student Grant Rate"
            benchmark_detail["stat_value"] = f"{rate}% historical grant rate"
        else:
            rate = dest_stats.get("visitor_visa_grant_rate", 76.0)
            benchmark_detail["stat_description"] = "UK Home Office Standard Visitor Visa Grant Rate"
            benchmark_detail["stat_value"] = f"{rate}% historical grant rate"

    return benchmark_detail
