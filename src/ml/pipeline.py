from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET = "label"
DROP = ["label", "transaction_id", "timestamp", "customer_id", "merchant_id"]

def load_data(path="data/raw/transactions.csv"):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df.sort_values("timestamp").reset_index(drop=True)

def split_data(df):
    n = len(df)
    a, b = int(n * .70), int(n * .85)
    return df.iloc[:a].copy(), df.iloc[a:b].copy(), df.iloc[b:].copy()

def make_xy(df):
    X = df.drop(columns=DROP, errors="ignore")
    y = df[TARGET].astype(int)
    return X, y

def build_preprocessor(X):
    numeric = X.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical = X.select_dtypes(include=["object", "category"]).columns.tolist()
    return ColumnTransformer([
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ])

def build_models(X):
    pre = build_preprocessor(X)
    return {
        "logistic_regression": Pipeline([
            ("preprocessor", pre),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        ]),
        "random_forest": Pipeline([
            ("preprocessor", pre),
            ("model", RandomForestClassifier(
                n_estimators=250, max_depth=14, min_samples_leaf=3,
                class_weight="balanced_subsample", random_state=42, n_jobs=-1
            )),
        ]),
    }

def metrics_at_threshold(y, p, threshold, fp_cost=100, fn_cost=2500):
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    precision = precision_score(y, pred, zero_division=0)
    recall = recall_score(y, pred, zero_division=0)
    f1 = f1_score(y, pred, zero_division=0)
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    fnr = fn / (fn + tp) if (fn + tp) else 0.0
    cost = fp * fp_cost + fn * fn_cost
    return {
        "threshold": float(threshold), "precision": float(precision),
        "recall": float(recall), "f1": float(f1),
        "specificity": float(specificity), "false_positive_rate": float(fpr),
        "false_negative_rate": float(fnr), "true_negatives": int(tn),
        "false_positives": int(fp), "false_negatives": int(fn),
        "true_positives": int(tp), "false_positive_cost": int(fp * fp_cost),
        "false_negative_cost": int(fn * fn_cost), "total_cost": int(cost),
    }

def threshold_search(y, p, fp_cost=100, fn_cost=2500):
    rows = [metrics_at_threshold(y, p, t, fp_cost, fn_cost)
            for t in np.round(np.arange(.10, .91, .05), 2)]
    # Prefer minimum cost; break ties with higher recall.
    return sorted(rows, key=lambda r: (r["total_cost"], -r["recall"]))[0], rows

def save_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, default=str))

def train():
    df = load_data()
    train_df, val_df, test_df = split_data(df)
    X_train, y_train = make_xy(train_df)
    X_val, y_val = make_xy(val_df)
    X_test, y_test = make_xy(test_df)

    models = build_models(X_train)
    comparisons = {}
    best_name, best_pipe, best_threshold_info = None, None, None

    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        p_val = pipe.predict_proba(X_val)[:, 1]
        best, table = threshold_search(y_val, p_val)
        comparisons[name] = {
            "validation_best": best,
            "threshold_table": table,
            "validation_roc_auc": float(roc_auc_score(y_val, p_val)),
            "validation_pr_auc": float(average_precision_score(y_val, p_val)),
        }
        if best_name is None or best["total_cost"] < best_threshold_info["total_cost"]:
            best_name, best_pipe, best_threshold_info = name, pipe, best

    # Refit selected architecture on train+validation only; threshold remains validation-derived.
    train_val = pd.concat([train_df, val_df], ignore_index=True)
    X_tv, y_tv = make_xy(train_val)
    best_pipe.fit(X_tv, y_tv)

    Path("models").mkdir(exist_ok=True)
    joblib.dump(best_pipe, "models/fraudshield_pipeline.joblib")
    metadata = {
        "model_name": best_name,
        "model_version": "1.0",
        "dataset": "synthetic",
        "training_samples": len(train_df),
        "validation_samples": len(val_df),
        "held_out_test_samples": len(test_df),
        "fraud_rate_total": float(df.label.mean()),
        "selected_threshold": best_threshold_info["threshold"],
        "false_positive_cost": 100,
        "false_negative_cost": 2500,
        "validation_comparison": comparisons,
        "features": [c for c in X_train.columns],
    }
    save_json("models/model_metadata.json", metadata)
    print(f"Selected model: {best_name}")
    print(f"Validation-selected threshold: {best_threshold_info['threshold']}")
    print("Saved models/fraudshield_pipeline.joblib")
    print("Saved models/model_metadata.json")

def evaluate():
    df = load_data()
    train_df, val_df, test_df = split_data(df)
    pipe = joblib.load("models/fraudshield_pipeline.joblib")
    X_test, y_test = make_xy(test_df)
    p = pipe.predict_proba(X_test)[:, 1]
    meta = json.loads(Path("models/model_metadata.json").read_text())
    threshold = float(meta["selected_threshold"])
    m = metrics_at_threshold(y_test, p, threshold)
    m["roc_auc"] = float(roc_auc_score(y_test, p))
    m["pr_auc"] = float(average_precision_score(y_test, p))
    m["dataset"] = "synthetic"
    m["test_samples"] = len(test_df)
    m["test_fraud_rate"] = float(y_test.mean())
    save_json("models/evaluation.json", m)
    print(json.dumps(m, indent=2))

if __name__ == "__main__":
    train()
    evaluate()
