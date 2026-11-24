"""
train.py
Trains a Scikit-learn classification pipeline on the genuine US Department of Labor
OFLC Visa dataset (EasyVisa) to predict visa certification probability.
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = "data/raw/EasyVisa.csv"
MODEL_PATH = "models/visa_model.joblib"
METADATA_PATH = "models/model_metadata.json"


def annualize_wage(df: pd.DataFrame) -> pd.Series:
    """Standardize wages across Hour/Week/Month/Year into an annual salary."""
    factors = {
        'Hour': 2080,
        'Week': 52,
        'Month': 12,
        'Year': 1
    }
    return df['prevailing_wage'] * df['unit_of_wage'].map(factors).fillna(1)


def load_and_preprocess_data(csv_path: str = DATA_PATH):
    df = pd.read_csv(csv_path)

    # Clean & engineer features
    df['annual_wage'] = annualize_wage(df)
    current_year = 2026
    df['company_age'] = (current_year - df['yr_of_estab']).clip(lower=0)

    # Binary target: Certified=1, Denied=0
    y = (df['case_status'] == 'Certified').astype(int)

    categorical_features = [
        'continent',
        'education_of_employee',
        'has_job_experience',
        'requires_job_training',
        'region_of_employment',
        'full_time_position'
    ]
    numeric_features = [
        'annual_wage',
        'no_of_employees',
        'company_age'
    ]

    X = df[categorical_features + numeric_features]
    return X, y, categorical_features, numeric_features


def train():
    print(f"Loading data from {DATA_PATH}...")
    X, y, cat_features, num_features = load_and_preprocess_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Training set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
        ]
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', model)
    ])

    print("Training Random Forest Classifier on genuine OFLC visa data...")
    pipeline.fit(X_train, y_train)

    # Evaluation
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)

    print("\n--- Model Evaluation Results ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=['Denied', 'Certified']))

    # Extract Feature Importances
    fitted_preprocessor = pipeline.named_steps['preprocessor']
    cat_encoder = fitted_preprocessor.named_transformers_['cat']
    encoded_cat_names = cat_encoder.get_feature_names_out(cat_features).tolist()
    all_feature_names = num_features + encoded_cat_names

    importances = pipeline.named_steps['classifier'].feature_importances_
    feat_importance_dict = dict(
        sorted(zip(all_feature_names, [round(float(v), 4) for v in importances]), key=lambda x: x[1], reverse=True)
    )

    # Save artifacts
    os.makedirs("models", exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    metadata = {
        "model_type": "RandomForestClassifier",
        "dataset_name": "US Department of Labor OFLC Visa Dataset (EasyVisa)",
        "training_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
        "features": {
            "categorical": cat_features,
            "numeric": num_features,
            "all_encoded": all_feature_names
        },
        "metrics": {
            "accuracy": round(float(acc), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(roc_auc), 4)
        },
        "top_feature_importances": dict(list(feat_importance_dict.items())[:10])
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to {METADATA_PATH}")

    return pipeline, metadata


if __name__ == "__main__":
    train()
