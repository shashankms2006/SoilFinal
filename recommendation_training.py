"""
Standalone RandomForest crop recommendation training script.

This mirrors the Colab-style workflow requested by the user:

    !pip install scikit-learn --quiet
    <run this script to train/evaluate the model>

It supports both Google Colab (file upload) and local execution (reads
`Train Dataset.csv` from the working directory).  The script prints model
metrics for the train and test splits and persists `crop_rf_model.pkl`
and `crop_label_encoder.pkl`.  A helper `recommend_crops_ml` function is
available for querying the trained model.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

try:
    # Available only in Google Colab.
    from google.colab import files  # type: ignore
except Exception:  # pragma: no cover - local environments won't have this.
    files = None  # type: ignore


MODEL_PATH = Path("crop_rf_model.pkl")
ENCODER_PATH = Path("crop_label_encoder.pkl")
DEFAULT_DATASET = Path("Train Dataset.csv")
FEATURE_COLS = ["N", "P", "K", "pH", "rainfall", "temperature"]

rf_model: Optional[RandomForestClassifier] = None
label_encoder: Optional[LabelEncoder] = None


def _colab_upload() -> Optional[pd.DataFrame]:
    if files is None:
        return None
    print("📂 Please upload Train Dataset.csv")
    uploaded = files.upload()
    if not uploaded:
        raise RuntimeError("No file uploaded.")
    train_filename = list(uploaded.keys())[0]
    print("✅ Loaded:", train_filename)
    return pd.read_csv(train_filename)


def load_dataset(path: Path = DEFAULT_DATASET) -> pd.DataFrame:
    df = _colab_upload()
    if df is None:
        if not path.exists():
            raise FileNotFoundError(
                f"Training dataset not found at {path.resolve()} "
                "and no file uploaded via Colab."
            )
        print(f"📄 Loading dataset from {path.resolve()}")
        df = pd.read_csv(path)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    print("🔎 Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("Number of unique crops:", df["Crop"].nunique())
    print("Crops:", sorted(df["Crop"].unique()))
    return df


def train_and_evaluate(df: pd.DataFrame) -> Tuple[Dict, RandomForestClassifier, LabelEncoder]:
    X = df[FEATURE_COLS].values
    y = df["Crop"].values

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    print("Encoded classes:", le.classes_)
    print("Number of classes:", len(le.classes_))

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded,
    )

    print("Train size:", X_train.shape[0])
    print("Test size :", X_test.shape[0])

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    metrics: Dict[str, Dict] = {}
    for split_name, X_split, y_split in [
        ("train", X_train, y_train),
        ("test", X_test, y_test),
    ]:
        y_pred = model.predict(X_split)
        acc = accuracy_score(y_split, y_pred)
        report = classification_report(
            y_split,
            y_pred,
            target_names=le.classes_,
            zero_division=0,
        )
        print(f"\n✅ {split_name.title()} Accuracy: {acc * 100:.2f}%\n")
        print(f"📊 {split_name.title()} Classification Report:")
        print(report)
        metrics[split_name] = {
            "accuracy": acc,
            "classification_report": report,
        }

    joblib.dump(model, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)
    print("\n✅ Saved crop_rf_model.pkl and crop_label_encoder.pkl")

    return metrics, model, le


def recommend_crops_ml(
    N: float,
    P: float,
    K: float,
    pH: float,
    rainfall: float,
    temperature: float,
    top_k: int = 5,
) -> List[Dict[str, float | str]]:
    global rf_model, label_encoder
    if rf_model is None or label_encoder is None:
        if MODEL_PATH.exists() and ENCODER_PATH.exists():
            rf_model = joblib.load(MODEL_PATH)
            label_encoder = joblib.load(ENCODER_PATH)
        else:
            raise RuntimeError("Model not trained. Run this script to train first.")

    x_input = np.array([[N, P, K, pH, rainfall, temperature]])
    probs = rf_model.predict_proba(x_input)[0]
    top_indices = np.argsort(probs)[::-1][:top_k]
    top_crops = label_encoder.inverse_transform(top_indices)
    top_probs = probs[top_indices]

    results = []
    for crop, prob in zip(top_crops, top_probs):
        results.append({"crop": crop, "probability": float(prob)})
    return results


def main() -> None:
    df = load_dataset()
    metrics, model, le = train_and_evaluate(df)

    summary_path = Path("training_summary.json")
    summary_path.write_text(json.dumps(metrics, indent=2))
    print(f"\n📝 Saved training summary to {summary_path.resolve()}")

    # Cache trained artifacts for `recommend_crops_ml`.
    global rf_model, label_encoder
    rf_model = model
    label_encoder = le


if __name__ == "__main__":
    main()

