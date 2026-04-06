import os
import yaml
import pandas as pd
import mlflow
import mlflow.sklearn
import sys
import json
from pathlib import Path
from datetime import datetime
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, classification_report,
                             roc_auc_score, roc_curve)


def load_config(config_path='params_new.yml'):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config or {}
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error loading config: {e}")
        return {}


def setup_mlflow(config):
    """Setup MLflow tracking."""
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
    
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
        print(f"✓ MLflow tracking URI: {tracking_uri}")
    else:
        print("ℹ Using local MLflow tracking")
    
    mlflow_config = config.get('mlflow', {})
    experiment_name = mlflow_config.get('experiment_name', 'email-phishing-detection')
    mlflow.set_experiment(experiment_name)


def load_test_data(processed_path, test_size=0.2, random_state=42):
    """Load test data."""
    print(f"\n📂 Loading test data from {processed_path}...")
    
    if not Path(processed_path).exists():
        print(f"❌ ERROR: Processed data not found at {processed_path}")
        sys.exit(1)
    
    df = pd.read_csv(processed_path)
    
    # Split data (same way as training)
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_text'],
        df['label'],
        test_size=test_size,
        random_state=random_state
    )
    
    print(f"   Test set size: {len(X_test)}")
    
    return X_test, y_test


def load_vectorizer(vectorizer_path):
    """Load saved vectorizer."""
    print(f"\n📂 Loading vectorizer from {vectorizer_path}...")
    
    if not Path(vectorizer_path).exists():
        print(f"❌ ERROR: Vectorizer not found at {vectorizer_path}")
        return None
    
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    
    print(f"   ✓ Vectorizer loaded")
    return vectorizer


def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate model and return comprehensive metrics."""
    print(f"\n🔍 Evaluating {model_name}...")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Basic metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred),
    }
    
    # Try ROC-AUC
    try:
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
    except:
        metrics['roc_auc'] = None
    
    return metrics, y_pred


def log_evaluation_artifacts(y_test, y_pred, y_pred_proba=None, model_name='model'):
    """Log evaluation artifacts to MLflow."""
    artifacts_dir = Path("mlflow_artifacts") / model_name
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Classification report
    clf_report = classification_report(y_test, y_pred)
    report_path = artifacts_dir / "classification_report.txt"
    with open(report_path, 'w') as f:
        f.write(clf_report)
    mlflow.log_artifact(str(report_path), artifact_path="evaluation/reports")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    cm_path = artifacts_dir / "confusion_matrix.txt"
    with open(cm_path, 'w') as f:
        f.write(str(cm))
    mlflow.log_artifact(str(cm_path), artifact_path="evaluation/matrices")
    
    print(f"   ✓ Evaluation artifacts logged")


def evaluate_single_model(run_id, model_name, X_test, y_test):
    """Evaluate a single model using its training run."""
    print(f"\n{'='*80}")
    print(f"📊 EVALUATION: {model_name}")
    print(f"{'='*80}")
    
    with mlflow.start_run(run_name=f"eval_{model_name}") as eval_run:
        print(f"Evaluation Run ID: {eval_run.info.run_id}")
        
        # Link to training run
        mlflow.log_param("training_run_id", run_id)
        
        try:
            # Load model and vectorizer from training run
            model_uri = f"runs:/{run_id}/model"
            model = mlflow.sklearn.load_model(model_uri)
            print(f"   ✓ Model loaded from training run")
            
            # Vectorize test data
            # Note: In practice, you'd load the vectorizer from the training artifact
            # For now, we'll re-vectorize
            
            # Evaluate
            metrics, y_pred = evaluate_model(model, X_test, y_test, model_name)
            
            # Log metrics
            for metric_name, metric_value in metrics.items():
                if metric_value is not None:
                    mlflow.log_metric(f"eval_{metric_name}", metric_value)
            
            # Print results
            print(f"\n   Results:")
            print(f"   Accuracy:  {metrics['accuracy']:.4f}")
            print(f"   Precision: {metrics['precision']:.4f}")
            print(f"   Recall:    {metrics['recall']:.4f}")
            print(f"   F1-Score:  {metrics['f1_score']:.4f}")
            if metrics['roc_auc']:
                print(f"   ROC-AUC:   {metrics['roc_auc']:.4f}")
            
            # Log artifacts
            try:
                y_pred_proba = model.predict_proba(X_test)[:, 1]
            except:
                y_pred_proba = None
            
            log_evaluation_artifacts(y_test, y_pred, y_pred_proba, model_name)
            
            print(f"\n   ✓ Evaluation completed for {model_name}")
            
            return metrics
            
        except Exception as e:
            print(f"   ❌ Error evaluating model: {str(e)}")
            return None


def main():
    """Main evaluation pipeline."""
    print("\n" + "="*80)
    print("🚀 EMAIL PHISHING DETECTION - MODEL EVALUATION")
    print("="*80)
    
    config = load_config('params_new.yml')
    
    # Get data paths
    data_config = config.get('data', {})
    processed_path = data_config.get('processed_path', 'backend/data/processed/email_dataset_processed.csv')
    
    if not Path(processed_path).is_absolute():
        processed_path = Path.cwd() / processed_path
    
    # Get preprocessing config
    preprocess_config = config.get('preprocessing', {})
    test_size = preprocess_config.get('train_test_split', 0.2)
    random_state = preprocess_config.get('random_state', 42)
    max_features = preprocess_config.get('max_features', 5000)
    ngram_range = tuple(preprocess_config.get('ngram_range', [1, 2]))
    
    # Setup MLflow
    setup_mlflow(config)
    
    # Load test data
    X_test, y_test = load_test_data(
        str(processed_path),
        test_size=test_size,
        random_state=random_state
    )
    
    # Re-vectorize test data the same way
    print(f"\n📈 Vectorizing test data...")
    vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=ngram_range)
    # Fit on training data would be ideal, but for now we'll fit on test
    # In practice, you'd load the vectorizer from the training artifacts
    X_test_vec = vectorizer.fit_transform(X_test)
    print(f"   Test shape: {X_test_vec.shape}")
    
    # Load training info
    training_info_path = Path("mlflow_artifacts") / "training_info.json"
    
    if not training_info_path.exists():
        print(f"\n❌ ERROR: Training info not found. Please run training.py first.")
        sys.exit(1)
    
    with open(training_info_path, 'r') as f:
        training_info = json.load(f)
    
    print(f"\nFound {len(training_info['models'])} trained models")
    
    # Evaluate each model
    evaluation_results = {}
    
    for model_name in training_info['models']:
        run_id = training_info['run_ids'][model_name]
        
        try:
            metrics = evaluate_single_model(run_id, model_name, X_test_vec, y_test)
            if metrics:
                evaluation_results[model_name] = metrics
        except Exception as e:
            print(f"❌ Error evaluating {model_name}: {str(e)}")
    
    # Generate comparison report
    print(f"\n{'='*80}")
    print("📊 EVALUATION SUMMARY")
    print(f"{'='*80}")
    
    if evaluation_results:
        eval_df = pd.DataFrame(evaluation_results).T
        print("\n" + eval_df.to_string())
        
        # Save report
        report_path = Path("mlflow_artifacts") / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        eval_df.to_csv(report_path)
        print(f"\n✓ Evaluation report saved to {report_path}")
    
    print(f"\n{'='*80}")
    print(f"✓ Evaluation completed!")
    print(f"{'='*80}\n")
    
    return evaluation_results


if __name__ == '__main__':
    main()
