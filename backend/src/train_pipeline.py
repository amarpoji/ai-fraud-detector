import os
import yaml
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from urllib.parse import urlparse
import sys
from pathlib import Path

import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

# Download required NLTK data
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)


def load_config(config_path='params.yml'):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config or {}
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error loading config: {e}")
        return {}


def clean_text(text):
    """Clean text data."""
    text = text.lower()
    text = re.sub(r'[^\w\s:/.)]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words and len(token) > 1]
    return " ".join(tokens)


def load_and_prepare_data(data_path, test_size=0.2, random_state=42):
    """Load and prepare data for training."""
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    print(f"Loaded {len(df)} records")
    print(f"Columns: {list(df.columns)}")
    
    # Apply text cleaning
    print("Cleaning text data...")
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_text'],
        df['label'],
        test_size=test_size,
        random_state=random_state
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    return X_train, X_test, y_train, y_test, df


def vectorize_text(X_train, X_test, max_features=5000, ngram_range=(1, 2)):
    """Vectorize text using TF-IDF."""
    print(f"Vectorizing text with max_features={max_features}, ngram_range={ngram_range}...")
    
    vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=ngram_range)
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    
    print(f"Training set shape: {X_train_vectorized.shape}")
    print(f"Test set shape: {X_test_vectorized.shape}")
    
    return X_train_vectorized, X_test_vectorized, vectorizer


def train_model(model_type, X_train, y_train, **model_params):
    """Train model based on type."""
    print(f"Training {model_type} model with params: {model_params}")
    
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
    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate model and return metrics."""
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred)
    }
    
    return metrics, y_pred


def setup_mlflow_tracking():
    """Setup MLflow tracking with DagsHub."""
    # Set tracking URI from environment or use local
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
    
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
        print(f"MLflow tracking URI: {tracking_uri}")
    else:
        print("Using local MLflow tracking (set MLFLOW_TRACKING_URI for remote tracking)")
    
    # Set experiment
    experiment_name = "email-phishing-detection"
    mlflow.set_experiment(experiment_name)
    print(f"MLflow experiment: {experiment_name}")


def main():
    """Main training pipeline."""
    print("=" * 80)
    print("EMAIL PHISHING DETECTION - MODEL TRAINING PIPELINE")
    print("=" * 80)
    
    # Load configuration
    config = load_config('params.yml')
    
    # Get data paths
    data_config = config.get('data', {})
    raw_path = data_config.get('raw_path', 'backend/data/raw/email_dataset.csv')
    
    if not Path(raw_path).is_absolute():
        raw_path = Path.cwd() / raw_path
    
    if not Path(raw_path).exists():
        print(f"ERROR: Raw data file not found at {raw_path}")
        sys.exit(1)
    
    # Get preprocessing config
    preprocess_config = config.get('preprocessing', {})
    test_size = preprocess_config.get('train_test_split', 0.2)
    max_features = preprocess_config.get('max_features', 5000)
    ngram_range = tuple(preprocess_config.get('ngram_range', [1, 2]))
    random_state = preprocess_config.get('random_state', 42)
    
    # Get model config
    model_config = config.get('model', {})
    model_type = model_config.get('type', 'RandomForest')
    
    # Extract model parameters (all except 'type')
    model_params = {k: v for k, v in model_config.items() if k != 'type'}
    
    # Setup MLflow
    setup_mlflow_tracking()
    
    # Load and prepare data
    X_train, X_test, y_train, y_test, df = load_and_prepare_data(
        str(raw_path),
        test_size=test_size,
        random_state=random_state
    )
    
    # Vectorize text
    X_train_vec, X_test_vec, vectorizer = vectorize_text(
        X_train, X_test,
        max_features=max_features,
        ngram_range=ngram_range
    )
    
    # Start MLflow run
    with mlflow.start_run() as run:
        print(f"\nMLflow Run ID: {run.info.run_id}")
        
        # Log parameters
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("max_features", max_features)
        mlflow.log_param("ngram_range", str(ngram_range))
        mlflow.log_param("test_size", test_size)
        mlflow.log_param("random_state", random_state)
        
        for param_name, param_value in model_params.items():
            mlflow.log_param(f"model_{param_name}", param_value)
        
        # Train model
        model = train_model(model_type, X_train_vec, y_train, **model_params)
        
        # Evaluate model
        metrics, y_pred = evaluate_model(model, X_test_vec, y_test)
        
        # Log metrics
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)
        
        # Print metrics
        print("\n" + "=" * 80)
        print("MODEL EVALUATION RESULTS")
        print("=" * 80)
        print(f"Accuracy:  {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1-Score:  {metrics['f1_score']:.4f}")
        
        # Log confusion matrix and classification report
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:\n{cm}")
        
        clf_report = classification_report(y_test, y_pred)
        print(f"\nClassification Report:\n{clf_report}")
        
        # Log artifacts
        artifacts_dir = Path("mlflow_artifacts")
        artifacts_dir.mkdir(exist_ok=True)
        
        # Save classification report
        report_path = artifacts_dir / "classification_report.txt"
        with open(report_path, 'w') as f:
            f.write(clf_report)
        mlflow.log_artifact(str(report_path), artifact_path="reports")
        
        # Log model with signature
        sample_data = X_test_vec[:5].toarray() if hasattr(X_test_vec, 'toarray') else X_test_vec[:5]
        signature = infer_signature(sample_data, model.predict(X_test_vec[:5]))
        
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            signature=signature,
            registered_model_name="fraud-detector-model"
        )
        
        # Log vectorizer as artifact
        import pickle
        vectorizer_path = artifacts_dir / "vectorizer.pkl"
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
        mlflow.log_artifact(str(vectorizer_path), artifact_path="preprocessors")
        
        print(f"\n✓ Model and artifacts logged successfully!")
        print(f"✓ Run ID: {run.info.run_id}")
        
        # Print tracking UI URL
        tracking_uri = mlflow.get_tracking_uri()
        if tracking_uri and tracking_uri.startswith('http'):
            parsed_uri = urlparse(tracking_uri)
            print(f"\n📊 View experiment at: {tracking_uri}")
        
        return {
            'model': model,
            'vectorizer': vectorizer,
            'metrics': metrics,
            'run_id': run.info.run_id
        }


if __name__ == '__main__':
    main()
