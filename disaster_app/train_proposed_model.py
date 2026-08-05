from pathlib import Path
import random

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier

from disaster_app.nn_model import FeatureExtractor


SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "media/dataset/public_emdat_project.csv"
OUT_DIR = BASE_DIR / "ml_models2"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_transform(encoder, values):
    classes_set = set(encoder.classes_)
    safe_values = [v if v in classes_set else encoder.classes_[0] for v in values]
    return encoder.transform(safe_values)


def load_dataset():
    try:
        return pd.read_csv(CSV_PATH, encoding="utf-8")
    except Exception:
        return pd.read_csv(CSV_PATH, encoding="latin1")


def main():
    df = load_dataset()
    target_column = "Disaster Type"
    df = df.dropna(subset=[target_column]).copy()

    counts = df[target_column].value_counts()
    rare_classes = counts[counts < 10].index
    df[target_column] = df[target_column].replace(rare_classes, "Other")

    damage_col = "Total Damage ('000 US$)"
    if damage_col not in df.columns and "Total Damages ('000 US$)" in df.columns:
        damage_col = "Total Damages ('000 US$)"

    numeric_cols = [
        "Total Deaths",
        "No. Injured",
        "No. Affected",
        "Total Affected",
        damage_col,
        "CPI",
        "Magnitude",
        "Latitude",
        "Longitude",
        "Start Year",
        "End Year",
        "Start Month",
        "End Month",
    ]
    categorical_cols = ["Country", "ISO", "Disaster Subtype"]

    missing_numeric = [c for c in numeric_cols if c not in df.columns]
    missing_categorical = [c for c in categorical_cols if c not in df.columns]
    if missing_numeric or missing_categorical:
        raise ValueError(
            f"Missing expected columns. numeric={missing_numeric}, categorical={missing_categorical}"
        )

    df[numeric_cols] = df[numeric_cols].fillna(0)
    df[categorical_cols] = df[categorical_cols].fillna("Unknown")

    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(df[target_column])

    country_encoder = LabelEncoder()
    iso_encoder = LabelEncoder()
    subtype_encoder = LabelEncoder()
    df["Country_enc"] = country_encoder.fit_transform(df["Country"])
    df["ISO_enc"] = iso_encoder.fit_transform(df["ISO"])
    df["Subtype_enc"] = subtype_encoder.fit_transform(df["Disaster Subtype"])

    feature_cols = numeric_cols + ["Country_enc", "ISO_enc", "Subtype_enc"]
    X = df[feature_cols].values.astype(np.float32)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    input_dim = X_train_scaled.shape[1]
    num_classes = len(target_encoder.classes_)

    nn_model = FeatureExtractor(input_dim)
    classifier_head = nn.Linear(32, num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        list(nn_model.parameters()) + list(classifier_head.parameters()),
        lr=1e-3,
        weight_decay=1e-4,
    )

    X_train_t = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.long)
    X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)

    nn_model.train()
    classifier_head.train()
    for epoch in range(60):
        optimizer.zero_grad()
        feats = nn_model(X_train_t)
        logits = classifier_head(feats)
        loss = criterion(logits, y_train_t)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 20 == 0:
            print(f"Epoch {epoch+1}/60 - loss={loss.item():.4f}")

    nn_model.eval()
    with torch.no_grad():
        train_feats = nn_model(X_train_t).numpy()
        test_feats = nn_model(X_test_t).numpy()

    xgb_model = XGBClassifier(
        objective="multi:softmax",
        num_class=num_classes,
        n_estimators=600,
        max_depth=8,
        learning_rate=0.03,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=2,
        reg_lambda=1.0,
        reg_alpha=0.1,
        random_state=SEED,
        tree_method="hist",
        n_jobs=4,
    )
    xgb_model.fit(train_feats, y_train)
    y_pred = xgb_model.predict(test_feats)

    print("Accuracy:", round(accuracy_score(y_test, y_pred) * 100, 2))
    print("Precision:", round(precision_score(y_test, y_pred, average="weighted", zero_division=0) * 100, 2))
    print("Recall:", round(recall_score(y_test, y_pred, average="weighted", zero_division=0) * 100, 2))
    print("F1:", round(f1_score(y_test, y_pred, average="weighted", zero_division=0) * 100, 2))

    joblib.dump(scaler, OUT_DIR / "scaler.pkl")
    joblib.dump(xgb_model, OUT_DIR / "xgb_model.pkl")
    joblib.dump(target_encoder, OUT_DIR / "target_encoder.pkl")
    joblib.dump(country_encoder, OUT_DIR / "Country_encoder.pkl")
    joblib.dump(iso_encoder, OUT_DIR / "ISO_encoder.pkl")
    joblib.dump(subtype_encoder, OUT_DIR / "Disaster_Subtype_encoder.pkl")
    torch.save(nn_model.state_dict(), OUT_DIR / "feature_nn.pt")

    print(f"Saved proposed artifacts to: {OUT_DIR}")


if __name__ == "__main__":
    main()
