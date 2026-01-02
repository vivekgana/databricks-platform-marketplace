"""Drift Detection Example"""

from scipy.stats import ks_2samp
import pandas as pd
import mlflow

def detect_feature_drift(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
    features: list,
    threshold: float = 0.05
):
    """Detect feature drift using KS test"""

    drift_results = {}

    for feature in features:
        stat, p_value = ks_2samp(
            reference_df[feature],
            current_df[feature]
        )

        drift_detected = p_value < threshold

        drift_results[feature] = {
            "ks_statistic": stat,
            "p_value": p_value,
            "drift_detected": drift_detected
        }

        if drift_detected:
            print(f"⚠ Drift detected in {feature} (p={p_value:.4f})")

    # Log to MLflow
    with mlflow.start_run():
        mlflow.log_dict(drift_results, "drift_report.json")

    return drift_results
