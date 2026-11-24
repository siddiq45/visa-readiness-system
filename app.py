"""
app.py
Visa Readiness & Profile Assessment Platform
United States, Canada, and United Kingdom
Designed as a modern travel & immigration SaaS platform.
"""

import os
import tempfile
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "mpl_cache")

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.rules import evaluate_visa_readiness
from src.ml.predict import predict_ml_benchmark, get_consular_benchmark, get_metadata
from src.ui.charts import (
    plot_category_breakdown,
    plot_comparative_summary,
    plot_feature_importance_chart
)
from src.ui.questionnaires import (
    render_student_questionnaire,
    render_tourist_questionnaire
)
from src.utils.report_exporter import generate_markdown_report

# Page Configuration
st.set_page_config(
    page_title="Visa Readiness & Profile Assessment Platform",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium SaaS Light-Theme Custom CSS
st.markdown("""
<style>
    /* Global Base Reset & Typography */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #202938;
        background-color: #F5F7FA;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Top Brand Headers */
    .brand-title {
        font-size: 1.95rem;
        font-weight: 700;
        color: #17345C;
        letter-spacing: -0.5px;
        margin-bottom: 0.25rem;
    }
    .brand-subtitle {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.25rem;
    }

    /* Clean Notice Card */
    .notice-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #17345C;
        border-radius: 6px;
        padding: 14px 18px;
        color: #374151;
        font-size: 0.88rem;
        line-height: 1.5;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    .notice-card b {
        color: #17345C;
    }

    /* KPI Summary Card */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 18px 16px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        height: 100%;
    }
    .kpi-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #17345C;
        line-height: 1.1;
        margin-bottom: 8px;
    }
    .kpi-caption {
        font-size: 0.78rem;
        color: #6B7280;
        margin-top: 8px;
    }

    /* Badges with Strict High-Contrast */
    .pill-green {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }
    .pill-orange {
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }
    .pill-red {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }
    .pill-neutral {
        background-color: #F3F4F6;
        color: #374151;
        border: 1px solid #E5E7EB;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Informational Callout Box */
    .callout-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #0F8B8D;
        border-radius: 6px;
        padding: 14px 18px;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        font-size: 0.88rem;
        color: #374151;
        line-height: 1.5;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    .callout-card b {
        color: #17345C;
    }

    /* Checklist Item Box */
    .checklist-row {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.88rem;
        color: #202938;
    }

    /* Action & Recommendation Boxes */
    .alert-box-red {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 6px;
        padding: 12px 14px;
        color: #991B1B;
        font-size: 0.86rem;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    .alert-box-amber {
        background-color: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 6px;
        padding: 12px 14px;
        color: #92400E;
        font-size: 0.86rem;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    .alert-box-green {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 6px;
        padding: 12px 14px;
        color: #166534;
        font-size: 0.86rem;
        margin-bottom: 8px;
        line-height: 1.4;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    /* Clean Streamlit Buttons */
    button[kind="primary"] {
        background-color: #17345C !important;
        border-color: #17345C !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    button[kind="primary"]:hover {
        background-color: #122845 !important;
        border-color: #122845 !important;
    }

    /* Tab Headers */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #4B5563;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #17345C !important;
        border-bottom: 2px solid #17345C !important;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Top Header
    st.markdown('<div class="brand-title">Visa Readiness & Profile Assessment Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">Objective prerequisite auditing and historical approval benchmarks for the United States, Canada, and the United Kingdom</div>', unsafe_allow_html=True)

    # Clean Legal Disclaimer
    st.markdown("""
    <div class="notice-card">
        <b>Official Advisory:</b> Visa decisions are sovereign determinations made by government immigration officers under applicable national immigration laws 
        (U.S. INA 214(b), Canadian IRPA, and UK Immigration Rules). 
        <b>No software or consultancy can guarantee visa approval.</b> 
        This platform provides an independent <b>Prerequisite Readiness Check</b> against published statutory rules, combined with a 
        <b>Historical Profile Comparison</b> based strictly on verified open government records.
    </div>
    """, unsafe_allow_html=True)

    # Sidebar: Scope Selection
    st.sidebar.markdown("### Application Scope")

    country_selection = st.sidebar.selectbox(
        "Destination Country",
        ["United States", "Canada", "United Kingdom"],
        index=0
    )
    country_code = "USA" if "United States" in country_selection else ("Canada" if "Canada" in country_selection else "UK")

    visa_purpose = st.sidebar.radio(
        "Application Type",
        ["Student Visa (Higher Education)", "Visitor / Tourist Visa"]
    )
    is_student = "Student" in visa_purpose

    # Friendly Visa Category Names
    if country_code == "USA":
        visa_title = "F-1 Student Visa" if is_student else "B-1 / B-2 Visitor Visa"
        statute_label = "U.S. Immigration and Nationality Act (INA 214b)"
    elif country_code == "Canada":
        visa_title = "Study Permit" if is_student else "Visitor Visa (TRV)"
        statute_label = "Immigration and Refugee Protection Act (IRPA)"
    else:
        visa_title = "Student Visa (Points-Based System)" if is_student else "Standard Visitor Visa"
        statute_label = "UK Immigration Rules (Appendix Student / Visitor)"

    st.sidebar.markdown(f"**Selected Visa:** {visa_title}")
    st.sidebar.markdown(f"**Governing Rule:** *{statute_label}*")

    citizenship = st.sidebar.selectbox(
        "Country of Passport / Citizenship",
        ["India", "China", "Nigeria", "Philippines", "Brazil", "Other / Global Average"],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="font-size:0.82rem; color:#6B7280; line-height:1.4;">
        <b>Assessment Framework:</b><br/>
        • <b>Prerequisite Check:</b> Mandatory document and fund verification.<br/>
        • <b>Historical Match:</b> Machine learning model trained on US Department of Labor open data.
    </div>
    """, unsafe_allow_html=True)

    # Primary Navigation Tabs
    tab_questionnaire, tab_dashboard, tab_transparency, tab_guide = st.tabs([
        "Assessment Questionnaire",
        "Assessment Results",
        "Data & Model Transparency",
        "Immigration Guidelines"
    ])

    # TAB 1: QUESTIONNAIRE
    with tab_questionnaire:
        st.markdown(f"### {country_selection} — {visa_title} Questionnaire")
        st.caption("Please fill in your current details. Your answers will generate an instant readiness evaluation.")

        with st.form("visa_assessment_form"):
            if is_student:
                form_payload = render_student_questionnaire(country_code)
            else:
                form_payload = render_tourist_questionnaire(country_code)

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Generate Readiness Assessment", type="primary", use_container_width=True)

        if submitted:
            # 1. Execute Rules Engine
            category_key = "Student" if is_student else "Tourist"
            rule_result = evaluate_visa_readiness(country_code, category_key, form_payload)

            # 2. Execute ML Predictive Benchmark
            continent_map = {
                "India": "Asia", "China": "Asia", "Nigeria": "Africa",
                "Philippines": "Asia", "Brazil": "South America", "Other / Global Average": "Asia"
            }
            ml_input = {
                "continent": continent_map.get(citizenship, "Asia"),
                "education_level": form_payload.get("education_level", "Bachelor's"),
                "has_job_experience": True if form_payload.get("employment_status") in ["Employed", "Business Owner"] else False,
                "annual_income_usd": form_payload.get("annual_income_usd", 35000),
                "requires_training": False,
                "full_time_position": True if form_payload.get("employment_status") == "Employed" else False
            }
            ml_result = predict_ml_benchmark(ml_input)

            # 3. Retrieve Official Consular Baseline
            consular_stat = get_consular_benchmark(citizenship, country_code, visa_title)

            # Store in Session State
            st.session_state["assessment_result"] = {
                "rules": rule_result,
                "ml": ml_result,
                "consular": consular_stat,
                "country": country_code,
                "country_name": country_selection,
                "visa_name": visa_title,
                "citizenship": citizenship
            }

            st.success("Assessment complete. Please open the 'Assessment Results' tab to view your full readiness dashboard.")

    # TAB 2: ASSESSMENT RESULTS
    with tab_dashboard:
        if "assessment_result" not in st.session_state:
            st.info("Please complete the questionnaire in the **Assessment Questionnaire** tab and click **Generate Readiness Assessment**.")
        else:
            res = st.session_state["assessment_result"]
            rules = res["rules"]
            ml = res["ml"]
            cons = res["consular"]

            st.markdown(f"### Assessment Results: {res['visa_name']} ({res.get('country_name', res['country'])})")
            st.caption(f"Applicant Citizenship: **{res['citizenship']}** | Governing Rule: *{rules.get('legal_basis', 'N/A')}*")

            # KPI Summary Cards Row
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

            with kpi_col1:
                r_score = rules.get("readiness_score", 0)
                badge_class = "pill-green" if r_score >= 80 else ("pill-orange" if r_score >= 60 else "pill-red")
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Document & Eligibility Score</div>
                    <div class="kpi-value">{r_score}<span style="font-size:1.2rem; font-weight:600; color:#6B7280;">/100</span></div>
                    <span class="{badge_class}">{rules.get('readiness_level', '')}</span>
                    <div class="kpi-caption">Compliance with mandatory statutory requirements</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi_col2:
                ml_prob = ml.get("probability_percentage", 0.0)
                ml_badge = "pill-green" if ml_prob >= 75 else ("pill-orange" if ml_prob >= 50 else "pill-red")
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Historical Profile Match</div>
                    <div class="kpi-value">{ml_prob:.0f}<span style="font-size:1.2rem; font-weight:600; color:#6B7280;">%</span></div>
                    <span class="{ml_badge}">{ml.get('alignment_tier', '')}</span>
                    <div class="kpi-caption">Comparison against 25,480 government petition records</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi_col3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Official Country Benchmark</div>
                    <div class="kpi-value" style="font-size:1.6rem; margin-top:8px;">{cons.get('stat_value', 'N/A')}</div>
                    <span class="pill-neutral">Risk Category: {cons.get('risk_tier', 'Moderate')}</span>
                    <div class="kpi-caption">Source: {cons.get('stat_description', 'Official disclosures')}</div>
                </div>
                """, unsafe_allow_html=True)

            # Clear Explanation Banner
            st.markdown("""
            <div class="callout-card">
                <b>Understanding Your Two Scores:</b><br/>
                • <b>Document & Eligibility Score:</b> Checks whether you have every necessary document (such as Form I-20, CAS, PAL, approved leave certificate, or required bank balance). A score above 80 indicates that your paperwork is solid.<br/>
                • <b>Historical Profile Match:</b> Shows how closely your education, work background, and income bracket match successful profiles in past government records.
            </div>
            """, unsafe_allow_html=True)

            # High-Contrast Charts Row
            st.markdown("#### Performance Breakdown")
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.caption("**Readiness by Assessment Category**")
                cat_scores = rules.get("category_scores", {})
                if cat_scores:
                    fig_cat = plot_category_breakdown(cat_scores)
                    st.pyplot(fig_cat)

            with chart_col2:
                st.caption("**Score Comparison vs. Benchmark Average**")
                fig_comp = plot_comparative_summary(
                    readiness_score=rules.get("readiness_score", 0),
                    ml_probability=ml.get("probability_percentage", 0),
                    baseline_avg=75.0
                )
                st.pyplot(fig_comp)

            st.markdown("---")

            # Document Checklist & Recommendations
            doc_col1, doc_col2 = st.columns([1.1, 1.0])

            with doc_col1:
                st.markdown("#### Required Document Checklist")
                for item in rules.get("checklist", []):
                    status = item.get("status", "")
                    name = item.get("item", "")
                    cat = item.get("category", "")

                    if "Verified" in status or "Satisfactory" in status:
                        badge_html = f'<span class="pill-green">{status}</span>'
                    elif "Missing" in status or "Deficient" in status or "Critical" in status:
                        badge_html = f'<span class="pill-red">{status}</span>'
                    else:
                        badge_html = f'<span class="pill-orange">{status}</span>'

                    st.markdown(f"""
                    <div class="checklist-row">
                        <div>
                            <b>{name}</b><br/>
                            <span style="font-size:0.75rem; color:#6B7280;">Category: {cat}</span>
                        </div>
                        <div>{badge_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with doc_col2:
                st.markdown("#### Missing Information & Action Items")
                missing_items = rules.get("missing_documents", [])
                if missing_items:
                    for doc in missing_items:
                        st.markdown(f'<div class="alert-box-red"><b>Action Required:</b> {doc}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alert-box-green"><b>All Core Documents Complete:</b> You have verified all statutory prerequisites.</div>', unsafe_allow_html=True)

                st.markdown("#### Personalized Recommendations")
                recommendations = rules.get("recommendations", [])
                if recommendations:
                    for rec in recommendations:
                        st.markdown(f'<div class="alert-box-amber"><b>Recommendation:</b> {rec}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alert-box-green"><b>Ready for Submission:</b> Keep your original financial statements and documents organized for your appointment.</div>', unsafe_allow_html=True)

                if rules.get("strengths"):
                    st.markdown("#### Profile Strengths")
                    for st_item in rules.get("strengths"):
                        st.markdown(f'<div class="alert-box-green"><b>Strength:</b> {st_item}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Download Report
            markdown_report = generate_markdown_report(res)
            st.download_button(
                label="Download Full Assessment Report (.md)",
                data=markdown_report,
                file_name=f"Visa_Assessment_{res['country']}_{res['visa_name'].replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )

    # TAB 3: DATA & MODEL TRANSPARENCY
    with tab_transparency:
        st.markdown("### Machine Learning Model & Data Transparency")
        st.write("""
        This platform adheres to strict data ethics: **no training data or model results are fabricated**. 
        Because individual non-immigrant consular decisions are private records under government privacy laws, 
        our machine learning classifier is trained on the official public disclosure dataset from the 
        **United States Department of Labor Office of Foreign Labor Certification (OFLC)**.
        """)

        meta = get_metadata()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Training Cases", f"{meta.get('training_samples', 20384):,}")
        m2.metric("Testing Cases", f"{meta.get('test_samples', 5096):,}")
        m3.metric("Verified Model Accuracy", f"{meta.get('metrics', {}).get('accuracy', 0.7394)*100:.1f}%")
        m4.metric("Model ROC-AUC Score", f"{meta.get('metrics', {}).get('roc_auc', 0.7694):.3f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Primary Historical Predictors")
        st.caption("Feature importance weights from the trained Scikit-learn Random Forest model.")

        top_importances = meta.get("top_feature_importances", {})
        if top_importances:
            fig_fi = plot_feature_importance_chart(top_importances)
            st.pyplot(fig_fi)

        st.markdown("---")
        st.markdown("#### Official Historical Country Benchmark Rates")
        st.caption("Disclosed annual statistics published by the US State Department, UK Home Office, and IRCC Canada.")

        benchmark_table = pd.DataFrame([
            {"Country of Origin": "India", "USA B-1/B-2 Refusal Rate": "10.9%", "Canada Study Permit Approval": "62.0%", "UK Student Visa Grant Rate": "88.0%"},
            {"Country of Origin": "China", "USA B-1/B-2 Refusal Rate": "26.6%", "Canada Study Permit Approval": "84.0%", "UK Student Visa Grant Rate": "96.0%"},
            {"Country of Origin": "Nigeria", "USA B-1/B-2 Refusal Rate": "50.5%", "Canada Study Permit Approval": "35.0%", "UK Student Visa Grant Rate": "74.0%"},
            {"Country of Origin": "Philippines", "USA B-1/B-2 Refusal Rate": "24.3%", "Canada Study Permit Approval": "64.0%", "UK Student Visa Grant Rate": "89.0%"},
            {"Country of Origin": "Brazil", "USA B-1/B-2 Refusal Rate": "14.5%", "Canada Study Permit Approval": "85.0%", "UK Student Visa Grant Rate": "94.0%"},
            {"Country of Origin": "Global Average", "USA B-1/B-2 Refusal Rate": "22.0%", "Canada Study Permit Approval": "60.0%", "UK Student Visa Grant Rate": "86.0%"}
        ])
        st.dataframe(benchmark_table, use_container_width=True)

    # TAB 4: IMMIGRATION GUIDELINES
    with tab_guide:
        st.markdown("### Official Country Immigration Guidelines")
        st.caption("Key statutory standards explained in simple language.")

        st.markdown("""
        #### United States: INA Section 214(b) (Non-Immigrant Intent)
        * **What the law requires:** By law, U.S. consular officers must assume every applicant intends to stay permanently unless the applicant demonstrates strong reasons to return home.
        * **How to satisfy the requirement:**
          1. **Proof of Home Ties:** Show continuing family obligations, property deeds, or employment guarantees in your home country.
          2. **Clear Purpose:** For students, explain clearly how your chosen academic degree leads to career advancement back home.
          3. **Financial Solvency:** Show liquid, verifiable funds for Year 1 tuition and living costs stated on your Form I-20.

        ---

        #### Canada: IRPA & The 2024 Provincial Attestation Letter (PAL)
        * **What the law requires:** Study permits are governed by Section 30 of the Immigration and Refugee Protection Act (IRPA).
        * **Key Current Rules:**
          1. **Provincial Attestation Letter (PAL):** Most post-secondary students must have a valid PAL from the Canadian province where their school is located.
          2. **Living Cost Benchmark:** Students must show at least **CAD $20,635** for 12 months of living expenses, in addition to first-year tuition fees.
          3. **Temporary Intent (s.179b):** Applicants must satisfy the officer that they will depart Canada at the end of their authorized stay.

        ---

        #### United Kingdom: Points-Based Student Route & Visitor Rules
        * **Student Route (70 Points Required):**
          * **50 Points:** Valid Confirmation of Acceptance for Studies (CAS) from a licensed UK institution.
          * **10 Points:** English language proficiency (SELT B2 level).
          * **10 Points:** Financial maintenance funds (£1,334/month in London, £1,023/month outside London for 9 months) held for **at least 28 consecutive days**.
        * **Standard Visitor Route (Appendix V):**
          * Must show you are a genuine visitor who will leave the UK within 6 months.
          * Bank statements must demonstrate a consistent salary trail without sudden, unexplained deposits.
        """)


if __name__ == "__main__":
    main()
