# Validate Model Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Validation

## Overview

Comprehensive model validation including performance testing, fairness checks, and production readiness assessment.

## Command Usage

```bash
/databricks-mlops:validate-model --model-name <name> --version <version>
```

## Model Validation Script

```python
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import json

client = MlflowClient()

def validate_model_performance(
    model_uri: str,
    test_data,
    min_thresholds: dict
):
    """Validate model meets performance requirements"""

    # Load model
    model = mlflow.pyfunc.load_model(model_uri)

    # Predictions
    X_test = test_data.drop(columns=['target'])
    y_test = test_data['target']
    y_pred = model.predict(X_test)

    # Compute metrics
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1_score': f1_score(y_test, y_pred, average='weighted')
    }

    # Validate against thresholds
    validation_results = {}
    all_passed = True

    for metric_name, threshold in min_thresholds.items():
        actual_value = metrics.get(metric_name, 0)
        passed = actual_value >= threshold

        validation_results[metric_name] = {
            'actual': actual_value,
            'threshold': threshold,
            'passed': passed
        }

        if not passed:
            all_passed = False

    # Generate report
    print("\nModel Performance Validation")
    print("=" * 50)
    for metric, result in validation_results.items():
        status = "✓" if result['passed'] else "✗"
        print(f"{status} {metric}: {result['actual']:.4f} (threshold: {result['threshold']:.4f})")

    return all_passed, validation_results

def check_model_fairness(model_uri: str, test_data, sensitive_features: list):
    """Check model fairness across demographic groups"""

    model = mlflow.pyfunc.load_model(model_uri)

    X_test = test_data.drop(columns=['target'])
    y_test = test_data['target']
    y_pred = model.predict(X_test)

    fairness_metrics = {}

    for feature in sensitive_features:
        groups = test_data[feature].unique()
        group_metrics = {}

        for group in groups:
            mask = test_data[feature] == group
            group_y_test = y_test[mask]
            group_y_pred = y_pred[mask]

            from sklearn.metrics import accuracy_score
            group_accuracy = accuracy_score(group_y_test, group_y_pred)
            group_metrics[str(group)] = group_accuracy

        fairness_metrics[feature] = group_metrics

    print("\nFairness Analysis")
    print("=" * 50)
    for feature, groups in fairness_metrics.items():
        print(f"\n{feature}:")
        for group, accuracy in groups.items():
            print(f"  {group}: {accuracy:.4f}")

    return fairness_metrics

def validate_model_latency(model_uri: str, test_samples, max_latency_ms: float):
    """Validate model inference latency"""

    import time

    model = mlflow.pyfunc.load_model(model_uri)

    latencies = []
    for _ in range(100):
        start = time.time()
        model.predict(test_samples)
        latency = (time.time() - start) * 1000
        latencies.append(latency)

    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    p99_latency = np.percentile(latencies, 99)

    passed = p95_latency <= max_latency_ms

    print("\nLatency Validation")
    print("=" * 50)
    print(f"Average latency: {avg_latency:.2f} ms")
    print(f"P95 latency: {p95_latency:.2f} ms")
    print(f"P99 latency: {p99_latency:.2f} ms")
    print(f"Threshold: {max_latency_ms} ms")
    print(f"Status: {'✓ Passed' if passed else '✗ Failed'}")

    return passed, {
        'avg': avg_latency,
        'p95': p95_latency,
        'p99': p99_latency
    }

def validate_production_readiness(model_name: str, version: int):
    """Comprehensive production readiness check"""

    checks = []

    # 1. Model metadata completeness
    model_version = client.get_model_version(model_name, version)
    checks.append({
        'name': 'Model Description',
        'passed': model_version.description is not None and len(model_version.description) > 0
    })

    # 2. Model signature
    model_uri = f"models:/{model_name}/{version}"
    model = mlflow.pyfunc.load_model(model_uri)
    checks.append({
        'name': 'Model Signature',
        'passed': hasattr(model, 'metadata') and model.metadata.signature is not None
    })

    # 3. Model tags
    checks.append({
        'name': 'Required Tags',
        'passed': 'source_run_id' in model_version.tags
    })

    print("\nProduction Readiness Checklist")
    print("=" * 50)
    for check in checks:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']}")

    all_passed = all(check['passed'] for check in checks)
    return all_passed, checks

# Example usage
if __name__ == "__main__":
    MODEL_NAME = "main.ml_models.my_classifier"
    VERSION = 1

    # Load test data
    test_data = spark.table("main.ml_data.test_set").toPandas()

    # 1. Performance validation
    perf_passed, perf_results = validate_model_performance(
        model_uri=f"models:/{MODEL_NAME}/{VERSION}",
        test_data=test_data,
        min_thresholds={
            'accuracy': 0.85,
            'precision': 0.80,
            'recall': 0.80,
            'f1_score': 0.80
        }
    )

    # 2. Fairness check
    fairness = check_model_fairness(
        model_uri=f"models:/{MODEL_NAME}/{VERSION}",
        test_data=test_data,
        sensitive_features=['gender', 'age_group']
    )

    # 3. Latency validation
    latency_passed, latency_results = validate_model_latency(
        model_uri=f"models:/{MODEL_NAME}/{VERSION}",
        test_samples=test_data.head(10).drop(columns=['target']),
        max_latency_ms=100
    )

    # 4. Production readiness
    ready_passed, ready_checks = validate_production_readiness(MODEL_NAME, VERSION)

    # Overall validation
    all_passed = perf_passed and latency_passed and ready_passed

    if all_passed:
        print("\n✓ Model passed all validation checks")
    else:
        print("\n✗ Model failed validation")
```

## Validation Checklist

- [ ] Performance metrics meet thresholds
- [ ] Fairness across demographic groups
- [ ] Latency requirements satisfied
- [ ] Model metadata complete
- [ ] Input/output signature defined
- [ ] Error handling validated
- [ ] Edge cases tested
- [ ] Production readiness verified

## References

- [MLflow Model Evaluation](https://mlflow.org/docs/latest/models.html#model-evaluation)
