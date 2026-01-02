# Run Hyperparameter Tuning Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Optimization

## Overview

Perform distributed hyperparameter optimization using Hyperopt with parallel trials on Databricks.

## Command Usage

```bash
/databricks-mlops:run-hyperparameter-tuning --model-type <type> --max-trials <n>
```

## Hyperparameter Tuning Script

```python
import mlflow
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK, SparkTrials
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

def create_search_space(model_type: str):
    """Define hyperparameter search space"""

    if model_type == "random_forest":
        return {
            'n_estimators': hp.quniform('n_estimators', 50, 500, 50),
            'max_depth': hp.quniform('max_depth', 3, 20, 1),
            'min_samples_split': hp.quniform('min_samples_split', 2, 20, 1),
            'min_samples_leaf': hp.quniform('min_samples_leaf', 1, 10, 1),
            'max_features': hp.choice('max_features', ['sqrt', 'log2'])
        }
    elif model_type == "xgboost":
        return {
            'max_depth': hp.quniform('max_depth', 3, 18, 1),
            'learning_rate': hp.loguniform('learning_rate', np.log(0.001), np.log(0.3)),
            'n_estimators': hp.quniform('n_estimators', 50, 500, 50),
            'subsample': hp.uniform('subsample', 0.5, 1.0),
            'colsample_bytree': hp.uniform('colsample_bytree', 0.5, 1.0)
        }

def objective_function(params, X_train, y_train, model_type: str):
    """Objective function for hyperparameter optimization"""

    # Convert hyperopt params to int where needed
    params['n_estimators'] = int(params['n_estimators'])
    params['max_depth'] = int(params['max_depth'])

    if model_type == "random_forest":
        params['min_samples_split'] = int(params['min_samples_split'])
        params['min_samples_leaf'] = int(params['min_samples_leaf'])

        model = RandomForestClassifier(**params, random_state=42)
    elif model_type == "xgboost":
        import xgboost as xgb
        model = xgb.XGBClassifier(**params, random_state=42)

    # Cross-validation score
    with mlflow.start_run(nested=True):
        mlflow.log_params(params)

        scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        mean_score = scores.mean()

        mlflow.log_metric("cv_accuracy", mean_score)
        mlflow.log_metric("cv_std", scores.std())

    # Hyperopt minimizes, so return negative score
    return {'loss': -mean_score, 'status': STATUS_OK}

def run_distributed_tuning(
    X_train, y_train,
    model_type: str,
    max_evals: int = 50,
    parallelism: int = 4
):
    """Run distributed hyperparameter tuning with Hyperopt"""

    mlflow.set_experiment(f"/ml-experiments/{model_type}_tuning")

    with mlflow.start_run(run_name=f"{model_type}_hyperopt"):
        # Define search space
        search_space = create_search_space(model_type)

        # Use SparkTrials for distributed execution
        spark_trials = SparkTrials(parallelism=parallelism)

        # Run optimization
        best_params = fmin(
            fn=lambda params: objective_function(params, X_train, y_train, model_type),
            space=search_space,
            algo=tpe.suggest,
            max_evals=max_evals,
            trials=spark_trials
        )

        # Log best parameters
        mlflow.log_params({f"best_{k}": v for k, v in best_params.items()})

        print(f"✓ Hyperparameter tuning completed")
        print(f"✓ Best parameters: {best_params}")

        return best_params

def train_best_model(X_train, y_train, X_test, y_test, best_params, model_type: str):
    """Train final model with best hyperparameters"""

    with mlflow.start_run(run_name=f"{model_type}_best_model"):
        mlflow.sklearn.autolog()

        if model_type == "random_forest":
            model = RandomForestClassifier(**best_params, random_state=42)
        elif model_type == "xgboost":
            import xgboost as xgb
            model = xgb.XGBClassifier(**best_params, random_state=42)

        model.fit(X_train, y_train)

        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)

        mlflow.log_metric("final_train_accuracy", train_score)
        mlflow.log_metric("final_test_accuracy", test_score)

        print(f"✓ Final model trained")
        print(f"  Train accuracy: {train_score:.4f}")
        print(f"  Test accuracy: {test_score:.4f}")

        return model

# Example usage
if __name__ == "__main__":
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

    # Generate sample data
    X, y = make_classification(n_samples=10000, n_features=20, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Run hyperparameter tuning
    best_params = run_distributed_tuning(
        X_train, y_train,
        model_type="random_forest",
        max_evals=50,
        parallelism=4
    )

    # Train final model
    model = train_best_model(X_train, y_train, X_test, y_test, best_params, "random_forest")
```

## Best Practices

1. **Search Space Design**
   - Use appropriate distributions
   - Set reasonable bounds
   - Include most impactful parameters

2. **Parallel Execution**
   - Use SparkTrials for distributed tuning
   - Match parallelism to cluster size
   - Monitor resource usage

3. **Evaluation Strategy**
   - Use cross-validation
   - Balance speed vs accuracy
   - Consider early stopping

## References

- [Hyperopt Documentation](http://hyperopt.github.io/hyperopt/)
- [Databricks Hyperparameter Tuning](https://docs.databricks.com/machine-learning/automl-hyperparam-tuning/index.html)
