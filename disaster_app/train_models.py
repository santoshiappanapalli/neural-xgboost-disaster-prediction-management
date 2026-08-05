import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier

# ------------------------------
# Paths
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / 'media/dataset/public_emdat_project.csv'
model_dir = BASE_DIR / 'ml_models'
model_dir.mkdir(parents=True, exist_ok=True)

# ------------------------------
# Load Dataset
# ------------------------------
df = pd.read_csv(csv_path, encoding='latin1')

# ------------------------------
# Target and Features
# ------------------------------
target_column = 'Disaster Type'

# Drop rows with missing target
df = df.dropna(subset=[target_column])

# Handle rare classes (less than 5 samples) by merging into 'Other'
counts = df[target_column].value_counts()
rare_classes = counts[counts < 5].index
df[target_column] = df[target_column].replace(rare_classes, 'Other')

# Numeric and categorical features
numeric_features = [
    'Start Year', 'Start Month', 'Start Day', 
    'Total Deaths', 'No. Injured', 'No. Affected', 
    'Total Affected', 'CPI'
]

categorical_features = [
    'Country', 'Disaster Subtype'  # Example categorical features
]

# Fill missing values
df[numeric_features] = df[numeric_features].fillna(0)
df[categorical_features] = df[categorical_features].fillna('Unknown')

X = df[numeric_features + categorical_features]
y = df[target_column]

# ------------------------------
# Encode Target
# ------------------------------
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)
joblib.dump(label_encoder, model_dir / 'label_encoder.pkl')

# ------------------------------
# Train-Test Split
# ------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ------------------------------
# Preprocessing: Scaling + Encoding
# ------------------------------
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ]
)

X_train = preprocessor.fit_transform(X_train)
X_test = preprocessor.transform(X_test)

# Save preprocessor
joblib.dump(preprocessor, model_dir / 'preprocessor.pkl')

# ------------------------------
# Models
# ------------------------------
models = {
    'svm': SVC(probability=True, random_state=42),
    'rf': RandomForestClassifier(random_state=42),
    'lr': LogisticRegression(max_iter=1000, random_state=42),
    'knn': KNeighborsClassifier(),
}

# ------------------------------
# Train and Save Models
# ------------------------------
for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    joblib.dump(model, model_dir / f'{name}_model.pkl')

print("✅ All models, preprocessor, and label encoder saved successfully.")
