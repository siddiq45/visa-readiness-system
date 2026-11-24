"""
engine.py
Unified rule assessment dispatcher for USA, Canada, and UK visa types.
"""

from .usa_rules import evaluate_usa_f1, evaluate_usa_b1b2
from .canada_rules import evaluate_canada_study, evaluate_canada_visitor
from .uk_rules import evaluate_uk_student, evaluate_uk_visitor


def evaluate_visa_readiness(country: str, category_type: str, form_data: dict) -> dict:
    """
    Evaluates rule-based compliance and readiness for:
    - USA: F1 Student, B1/B2 Tourist
    - Canada: Study Permit, Visitor Visa
    - UK: Student Visa, Standard Visitor Visa
    """
    c = country.upper()
    cat = category_type.lower()

    if "USA" in c or "UNITED STATES" in c:
        if "student" in cat or "f1" in cat or "f-1" in cat:
            return evaluate_usa_f1(form_data)
        else:
            return evaluate_usa_b1b2(form_data)

    elif "CANADA" in c:
        if "student" in cat or "study" in cat:
            return evaluate_canada_study(form_data)
        else:
            return evaluate_canada_visitor(form_data)

    elif "UK" in c or "UNITED KINGDOM" in c:
        if "student" in cat or "study" in cat:
            return evaluate_uk_student(form_data)
        else:
            return evaluate_uk_visitor(form_data)

    else:
        raise ValueError(f"Unsupported country: {country}. Supported countries are USA, Canada, and UK.")
