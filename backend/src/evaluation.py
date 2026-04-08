import os
import yaml
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import sys
import json
from pathlib import Path
from datetime import datetime
import pickle
import warnings

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, classification_report,
                             roc_auc_score, roc_curve, matthews_corrcoef)

warnings.filterwarnings('ignore')


def load_config(config_path='params.yaml'):
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
    
    # Try to set experiment, but handle database schema errors gracefully
    try:
        mlflow_config = config.get('mlflow', {})
        experiment_name = mlflow_config.get('experiment_name', 'email-phishing-detection')
        mlflow.set_experiment(experiment_name)
    except Exception as e:
        if "out-of-date database schema" in str(e):
            print("\n❌ MLflow database is corrupted (out-of-date schema)")
            print("\n✓ FIX: Delete the corrupted database and retrain")
            print("  Windows: del mlflow.db")
            print("  Then run: python backend/src/training.py")
            sys.exit(1)
        else:
            raise


def load_test_data(processed_path, test_size=0.2, random_state=42):
    """Load test data with stratification."""
    print(f"\n📂 Loading test data from {processed_path}...")
    
    if not Path(processed_path).exists():
        print(f"❌ ERROR: Processed data not found at {processed_path}")
        sys.exit(1)
    
    df = pd.read_csv(processed_path)
    
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_text'],
        df['label'],
        test_size=test_size,
        random_state=random_state,
        stratify=df['label']
    )
    
    print(f"   Test set size: {len(X_test)}")
    print(f"   Class distribution: {np.bincount(y_test.values)}")
    
    return X_test, y_test


def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate model and return comprehensive metrics."""
    print(f"\n🔍 Evaluating {model_name}...")
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1_score': f1_score(y_test, y_pred, zero_division=0),
        'matthews_cc': matthews_corrcoef(y_test, y_pred)
    }
    
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
    
    clf_report = classification_report(y_test, y_pred)
    report_path = artifacts_dir / "classification_report.txt"
    with open(report_path, 'w') as f:
        f.write(clf_report)
    mlflow.log_artifact(str(report_path), artifact_path="evaluation/reports")
    
    cm = confusion_matrix(y_test, y_pred)
    cm_path = artifacts_dir / "confusion_matrix.txt"
    with open(cm_path, 'w') as f:
        f.write(str(cm))
    mlflow.log_artifact(str(cm_path), artifact_path="evaluation/matrices")
    
    print(f"   ✓ Evaluation artifacts logged")


def evaluate_single_model(run_id, model_name, tfidf_variant, config, X_test, y_test):
    """Evaluate a single model using its training run."""
    print(f"\n📊 Evaluating: {model_name}_{tfidf_variant}")
    
    with mlflow.start_run(run_name=f"eval_{model_name}_{tfidf_variant}") as eval_run:
        print(f"Evaluation Run ID: {eval_run.info.run_id[:8]}...")
        mlflow.log_param("training_run_id", run_id)
        
        try:
            # Load model from training run
            model_uri = f"runs:/{run_id}/model"
            model = mlflow.sklearn.load_model(model_uri)
            print(f"   ✓ Model loaded")
            
            # Load vectorizer from MLflow artifacts (CRITICAL)
            print(f"   📂 Loading vectorizer from training run {run_id[:8]}...")
            
            vectorizer_loaded = False
            try:
                # Try to download vectorizer artifact - download entire run directory
                artifact_path = mlflow.artifacts.download_artifacts(
                    artifact_uri=f"runs:/{run_id}/",
                    dst_path=None
                )
                
                # Search for vectorizer.pkl in artifacts
                vectorizer_file = None
                if os.path.exists(os.path.join(artifact_path, 'vectorizer.pkl')):
                    vectorizer_file = os.path.join(artifact_path, 'vectorizer.pkl')
                else:
                    # Recursive search in case it's in a subdirectory
                    for root, dirs, files in os.walk(artifact_path):
                        if 'vectorizer.pkl' in files:
                            vectorizer_file = os.path.join(root, 'vectorizer.pkl')
                            break
                
                if vectorizer_file and os.path.exists(vectorizer_file):
                    with open(vectorizer_file, 'rb') as f:
                        vectorizer = pickle.load(f)
                    print(f"   ✓ Vectorizer loaded successfully")
                    X_test_vec = vectorizer.transform(X_test)
                    print(f"   ✓ Vectorized with {tfidf_variant}: {X_test_vec.shape[1]} features")
                    vectorizer_loaded = True
                else:
                    print(f"   ⚠ Vectorizer.pkl not found in artifacts")
                    
            except Exception as e:
                print(f"   ⚠ Could not load from MLflow: {str(e)}")
            
            # Fallback: create new vectorizer if loading failed
            if not vectorizer_loaded:
                print(f"   Creating fallback vectorizer...")
                
                # Get TF-IDF config that matches training
                tfidf_config = config.get('preprocessing', {}).get('tfidf_variants', {}).get(
                    tfidf_variant,
                    {'max_features': 5000, 'ngram_range': [1, 2]}
                )
                
                max_feat = tfidf_config.get('max_features', 5000)
                ngram = tuple(tfidf_config.get('ngram_range', [1, 2]))
                
                vectorizer = TfidfVectorizer(
                    max_features=max_feat,
                    ngram_range=ngram,
                    lowercase=True,
                    stop_words='english'
                )
                X_test_vec = vectorizer.fit_transform(X_test)
                print(f"   ⚠ Fallback: {max_feat} max_features, {X_test_vec.shape[1]} actual features")
            
            # Evaluate
            metrics, y_pred = evaluate_model(model, X_test_vec, y_test, f"{model_name}_{tfidf_variant}")
            
            # Log metrics
            for metric_name, metric_value in metrics.items():
                if metric_value is not None:
                    mlflow.log_metric(f"eval_{metric_name}", metric_value)
            
            # Print results
            print(f"\n   📈 Results:")
            print(f"      Accuracy:     {metrics['accuracy']:.4f}")
            print(f"      Precision:    {metrics['precision']:.4f}")
            print(f"      Recall:       {metrics['recall']:.4f}")
            print(f"      F1-Score:     {metrics['f1_score']:.4f}")
            roc_auc_str = f"{metrics['roc_auc']:.4f}" if metrics['roc_auc'] else 'N/A'
            print(f"      ROC-AUC:      {roc_auc_str}")
            print(f"      Matthews CC:  {metrics['matthews_cc']:.4f}")
            
            try:
                y_pred_proba = model.predict_proba(X_test_vec)[:, 1]
            except:
                y_pred_proba = None
            
            log_evaluation_artifacts(y_test, y_pred, y_pred_proba, f"{model_name}_{tfidf_variant}")
            
            print(f"   ✓ Evaluation completed")
            
            return metrics
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Main evaluation pipeline."""
    print("\n" + "="*80)
    print("🚀 EMAIL PHISHING DETECTION - MODEL EVALUATION")
    print("="*80)
    
    config = load_config('params.yaml')
    
    data_config = config.get('data', {})
    processed_path = data_config.get('processed_path', 'backend/data/processed/email_dataset_processed.csv')
    
    if not Path(processed_path).is_absolute():
        processed_path = Path.cwd() / processed_path
    
    setup_mlflow(config)
    
    X_test, y_test = load_test_data(
        str(processed_path),
        test_size=config.get('preprocessing', {}).get('train_test_split', 0.2),
        random_state=config.get('preprocessing', {}).get('random_state', 42)
    )
    
    training_info_path = Path("mlflow_artifacts") / "training_info.json"
    
    if not training_info_path.exists():
        print(f"\n❌ ERROR: Training info not found. Please run training.py first.")
        sys.exit(1)
    
    with open(training_info_path, 'r') as f:
        training_info = json.load(f)
    
    print(f"\nFound {training_info['total_experiments']} trained models")
    
    evaluation_results = {}
    
    for result in training_info['results']:
        model_name = result['model_name']
        tfidf_variant = result['tfidf_variant']
        run_id = result['run_id']
        
        display_name = f"{model_name}_{tfidf_variant}"
        
        try:
            metrics = evaluate_single_model(run_id, model_name, tfidf_variant, config, X_test, y_test)
            if metrics:
                evaluation_results[display_name] = metrics
        except Exception as e:
            print(f"❌ Error evaluating {display_name}: {str(e)}")
    
    print(f"\n{'='*80}")
    print("📊 EVALUATION SUMMARY")
    print(f"{'='*80}")
    
    eval_df = pd.DataFrame(evaluation_results).T if evaluation_results else pd.DataFrame()
    if not eval_df.empty:
        print("\n" + eval_df.to_string())

    report_path = Path("mlflow_artifacts") / "evaluation_report.csv"
    eval_df.to_csv(report_path)
    print(f"\n✓ Evaluation report saved to {report_path}")
    
    print(f"\n{'='*80}")
    print(f"✓ Evaluation completed!")
    print(f"{'='*80}\n")
    
    return evaluation_results


if __name__ == '__main__':
    main()