from pathlib import Path

import joblib
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


class FeatureNet(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.classifier = nn.Linear(32, num_classes)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return x


def safe_transform(encoder, values):
    classes_set = set(encoder.classes_)
    safe_values = [v if v in classes_set else encoder.classes_[0] for v in values]
    return encoder.transform(safe_values)


BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "media/dataset/public_emdat_project.csv", encoding="latin1")

target = "Disaster Type"
df = df.dropna(subset=[target])
counts = df[target].value_counts()
rare = counts[counts < 5].index
df[target] = df[target].replace(rare, "Other")

model_dir = BASE_DIR / "ml_models1"

numeric_cols = [
    "Total Deaths",
    "No. Injured",
    "Total Affected",
    "Total Damage ('000 US$)",
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

df[numeric_cols] = df[numeric_cols].fillna(0)
df[categorical_cols] = df[categorical_cols].fillna("Unknown")

scaler = joblib.load(model_dir / "scaler.pkl")
xgb_model = joblib.load(model_dir / "xgb_model.pkl")
target_encoder = joblib.load(model_dir / "target_encoder.pkl")
country_encoder = joblib.load(model_dir / "country_encoder.pkl")
iso_encoder = joblib.load(model_dir / "iso_encoder.pkl")
subtype_encoder = joblib.load(model_dir / "disaster subtype_encoder.pkl")

df["Country_enc"] = safe_transform(country_encoder, df["Country"])
df["ISO_enc"] = safe_transform(iso_encoder, df["ISO"])
df["Subtype_enc"] = safe_transform(subtype_encoder, df["Disaster Subtype"])

X = df[numeric_cols + ["Country_enc", "ISO_enc", "Subtype_enc"]].values
y = target_encoder.transform(df[target])

_, X_test, _, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

X_test_scaled = scaler.transform(X_test)

nn_model = FeatureNet(X_test_scaled.shape[1], num_classes=len(target_encoder.classes_))
nn_model.load_state_dict(torch.load(model_dir / "feature_nn.pt", map_location="cpu"))
nn_model.eval()

with torch.no_grad():
    nn_features = nn_model(torch.tensor(X_test_scaled, dtype=torch.float32)).numpy()

y_pred = xgb_model.predict(nn_features)

print("Accuracy", round(accuracy_score(y_test, y_pred) * 100, 2))
print("Precision", round(precision_score(y_test, y_pred, average="weighted") * 100, 2))
print("Recall", round(recall_score(y_test, y_pred, average="weighted") * 100, 2))
print("F1", round(f1_score(y_test, y_pred, average="weighted") * 100, 2))
