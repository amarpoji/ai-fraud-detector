import os
import yaml
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
import sys
from pathlib import Path
import json
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB


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
    
    mlflow_config = config.get('mlflow', {})
    experiment_name = mlflow_config.get('experiment_name', 'email-phishing-detection')
    mlflow.set_experiment(experiment_name)
    print(f"✓ Experiment: {experiment_name}")


def load_processed_data(processed_path, test_size=0.2, random_state=42):
    """Load already transformed data."""
    print(f"\n📂 Loading processed data from {processed_path}...")
    
    if not Path(processed_path).exists():
        print(f"❌ ERROR: Processed data not found at {processed_path}")
        print(f"   Please run: python backend/src/data_transform.py")
        sys.exit(1)
    
    df = pd.read_csv(processed_path)
    
    print(f"   Loaded {len(df)} records")
    print(f"   Columns: {list(df.columns)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_text'],
        df['label'],
        test_size=test_size,
        random_state=random_state
    )
    
    print(f"   Training set size: {len(X_train)}")
    print(f"   Test set size: {len(X_test)}")
    
    return X_train, X_test, y_train, y_test


def vectorize_text(X_train, X_test, max_features=5000, ngram_range=(1, 2)):
    """Vectorize text using TF-IDF."""
    print(f"\n📈 Vectorizing Text (max_features={max_features}, ngram_range={ngram_range})...")
    
    vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=ngram_range)
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    
    print(f"   Training shape: {X_train_vectorized.shape}")
    print(f"   Test shape: {X_test_vectorized.shape}")
    
    return X_train_vectorized, X_test_vectorized, vectorizer


def train_model(model_type, X_train, y_train, **model_params):
    """Train model based on type."""
    print(f"\n🔄 Training {model_type}...")
    
    if model_type == 'RandomForest':
        model = RandomForestClassifier(**model_params)
    elif model_type == 'LogisticRegression':
        model = LogisticRegression(**model_params, max_iter=1000)
    elif model_type == 'SVM':
        model = SVC(**model_params, probability=True)
    elif model_type == 'NaiveBayes':
        model = MultinomialNB(**model_params)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model.fit(X_train, y_train)
    print(f"   ✓ Model trained successfully")
    
    return model


def log_training_artifacts(model, vectorizer, model_name):
    """Log training artifacts to MLflow."""
    artifacts_dir = Path("mlflow_artifacts") / model_name
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Save vectorizer
    vectorizer_path = artifacts_dir / "vectorizer.pkl"
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    mlflow.log_artifact(str(vectorizer_path), artifact_path="preprocessors")
    
    # Log model with signature
    sample_data = vectorizer.transform(["test email"])
    sample_output = model.predict(sample_data)
    signature = infer_signature(
        sample_data.toarray() if hasattr(sample_data, 'toarray') else sample_data,
        sample_output
    )
    
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        signature=signature,
        registered_model_name=f"{model_name}-model"
    )
    
    print(f"   ✓ Model and artifacts logged")


def train_single_model(model_name, model_config, X_train_vec, X_test_vec, y_train,vectorizer, config):
    """Train a single model."""
    print(f"\n{'='*80}")
    print(f"📊 TRAINING: {model_name}")
    print(f"{'='*80}")
    
    model_type = model_config.get('type', 'RandomForest')
    model_params = {k: v for k, v in model_config.items() if k != 'type'}
    
    with mlflow.start_run(run_name=f"train_{model_name}") as run:
        print(f"Run ID: {run.info.run_id}\n")
        
        # Log parameters
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("model_name", model_name)
        for param_name, param_value in model_params.items():
            mlflow.log_param(f"model_{param_name}", param_value)
        
        # Train
        model = train_model(model_type, X_train_vec, y_train, **model_params)
        
        # Log artifacts
        log_training_artifacts(model, vectorizer, model_name)  # vectorizer already logged separately
        
        print(f"\n✓ Training completed for {model_name}")
        
        return model, run.info.run_id


def main():
    """Main training pipeline."""
    print("\n" + "="*80)
    print("🚀 EMAIL PHISHING DETECTION - MODEL TRAINING")
    print("="*80)
    
    config = load_config('params.yaml')
    
    # Get data paths
    data_config = config.get('data', {})
    processed_path = data_config.get('processed_path', 'backend/data/processed/email_dataset_processed.csv')
    
    if not Path(processed_path).is_absolute():
        processed_path = Path.cwd() / processed_path
    
    # Get preprocessing config
    preprocess_config = config.get('preprocessing', {})
    test_size = preprocess_config.get('train_test_split', 0.2)
    max_features = preprocess_config.get('max_features', 5000)
    ngram_range = tuple(preprocess_config.get('ngram_range', [1, 2]))
    random_state = preprocess_config.get('random_state', 42)
    
    # Setup MLflow
    setup_mlflow(config)
    
    # Load processed data
    X_train, X_test, y_train, y_test = load_processed_data(
        str(processed_path),
        test_size=test_size,
        random_state=random_state
    )
    
    # Vectorize text
    X_train_vec, X_test_vec, vectorizer = vectorize_text(
        X_train, X_test,
        max_features=max_features,
        ngram_range=ngram_range
    )
    
    # Get model config
    model_variants = config.get('model_variants', {})
    
    if not model_variants:
        print("⚠️  No model variants found. Using default model config...")
        model_config = config.get('model', {})
        model_variants = {'default': model_config}
    
    training_results = {}
    
    # Train models
    for model_name, model_config in model_variants.items():
        try:
            model, run_id = train_single_model(
                model_name, model_config,
                X_train_vec, X_test_vec, y_train,vectorizer, config
            )
            training_results[model_name] = {
                'model': model,
                'vectorizer': vectorizer,
                'run_id': run_id
            }
        except Exception as e:
            print(f"❌ Error training {model_name}: {str(e)}")
    
    # Save training info for evaluation
    training_info_path = Path("mlflow_artifacts") / "training_info.json"
    training_info_path.parent.mkdir(exist_ok=True)
    
    with open(training_info_path, 'w') as f:
        json.dump({
            'models': list(training_results.keys()),
            'run_ids': {name: results['run_id'] for name, results in training_results.items()}
        }, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✓ Training completed!")
    print(f"{'='*80}\n")
    
    return training_results


if __name__ == '__main__':
    main()
