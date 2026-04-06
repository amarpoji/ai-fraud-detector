# Training Scripts Documentation

## Overview
This directory contains Python scripts for data transformation, model training, and comparison for the Email Phishing Detection system.

## Scripts

### 1. `data_transform.py`
Transforms raw email dataset by cleaning and preprocessing text data.

**Features:**
- Loads raw CSV data
- Applies text cleaning (lowercase, punctuation removal, tokenization, stopword removal)
- Saves processed data to CSV

**Usage:**
```bash
python backend/src/data_transform.py
```

**Configuration:**
Edit `params.yml` (or `params_new.yml`) to set data paths:
```yaml
data:
  raw_path: backend/data/raw/email_dataset.csv
  processed_path: backend/data/processed/email_dataset_processed.csv
```

---

### 2. `train_pipeline.py`
Single model training with MLflow tracking and model registry support.

**Features:**
- Loads and prepares data from params config
- Vectorizes text using TF-IDF
- Trains single model (RandomForest, LogisticRegression, SVM, NaiveBayes)
- Logs metrics and model artifacts to MLflow
- Registers model with signature using `infer_signature`
- Handles DagsHub integration via environment variables

**Usage:**
```bash
python backend/src/train_pipeline.py
```

**Configuration:**
```yaml
data:
  raw_path: backend/data/raw/email_dataset.csv

model:
  type: RandomForest
  n_estimators: 100
  max_depth: 15
  random_state: 42

preprocessing:
  train_test_split: 0.2
  max_features: 5000
  ngram_range: [1, 2]
```

---

### 3. `train_multi.py` (Recommended for Model Comparison)
Multi-model training with automatic comparison and ranking.

**Features:**
- Trains multiple model variants sequentially
- Compares models by F1-score and other metrics
- Generates comparison CSV report
- Individual MLflow runs for each model
- Model signature inference for production deployment
- DagsHub integration support

**Usage:**
```bash
python backend/src/train_multi.py
```

**Configuration:**
Edit `params_new.yml` to define model variants:
```yaml
model_variants:
  RandomForest_v1:
    type: RandomForest
    n_estimators: 100
    max_depth: 15
    random_state: 42
  
  LogisticRegression_v1:
    type: LogisticRegression
    C: 1.0
    random_state: 42
  
  NaiveBayes_v1:
    type: NaiveBayes
    alpha: 1.0
```

---

## MLflow Setup

### Local Tracking
By default, MLflow tracks locally in `./mlruns` directory.

View experiments:
```bash
mlflow ui
```
Then open `http://localhost:5000` in browser.

### Remote Tracking (DagsHub)
Set environment variable before running:
```bash
export MLFLOW_TRACKING_URI=https://dagshub.com/<username>/<repo>.mlflow
export MLFLOW_TRACKING_USERNAME=<username>
export MLFLOW_TRACKING_PASSWORD=<token>
```

Or on Windows:
```cmd
set MLFLOW_TRACKING_URI=https://dagshub.com/<username>/<repo>.mlflow
set MLFLOW_TRACKING_USERNAME=<username>
set MLFLOW_TRACKING_PASSWORD=<token>
```

Then run training scripts.

---

## Output Files

### Artifacts Generated:
- **mlflow_artifacts/** - Local artifact directory
  - `model/` - Trained scikit-learn model
  - `reports/` - Classification reports
  - `preprocessors/` - Vectorizer pickle file
  - `model_comparison_*.csv` - Comparison results

### MLflow Runs:
- Individual run folders in `./mlruns/`
- Each run contains parameters, metrics, and artifacts
- Model registry available for production deployment

---

## Model Types Supported

1. **RandomForest** - Ensemble method, good for text classification
   - Parameters: `n_estimators`, `max_depth`, `random_state`, `n_jobs`

2. **LogisticRegression** - Linear model, fast training
   - Parameters: `C`, `random_state`

3. **SVM** - Support Vector Machine
   - Parameters: `kernel`, `C`, `gamma`, `probability`

4. **NaiveBayes** - Probabilistic model
   - Parameters: `alpha`

---

## Model Comparison Workflow

1. **Edit `params_new.yml`** - Define multiple model variants
2. **Run `train_multi.py`** - Trains all models sequentially
3. **View results** - Check console output for comparison table
4. **Compare metrics** - Models ranked by F1-score
5. **Deploy best model** - Model with highest F1-score can be selected

---

## Example params_new.yml

```yaml
data:
  raw_path: backend/data/raw/email_dataset.csv
  processed_path: backend/data/processed/email_dataset_processed.csv

model:
  type: RandomForest
  n_estimators: 100
  max_depth: 15
  random_state: 42

preprocessing:
  train_test_split: 0.2
  max_features: 5000
  ngram_range: [1, 2]
  random_state: 42

model_variants:
  RandomForest_v1:
    type: RandomForest
    n_estimators: 100
    max_depth: 15
    random_state: 42
    n_jobs: -1
  
  RandomForest_v2:
    type: RandomForest
    n_estimators: 200
    max_depth: 20
    random_state: 42
    n_jobs: -1
  
  LogisticRegression_v1:
    type: LogisticRegression
    C: 1.0
    random_state: 42
  
  LogisticRegression_v2:
    type: LogisticRegression
    C: 0.1
    random_state: 42

mlflow:
  experiment_name: email-phishing-detection
  run_name_prefix: phishing-detector
  track_model_signature: true
  register_model: true
  model_registry_name: fraud-detector-model
```

---

## Features Used

- **MLflow**: Experiment tracking, parameter logging, metrics logging, model registry
- **infer_signature**: Automatic model input/output signature inference for deployment
- **urlparse**: URL parsing for DagsHub endpoint handling
- **YAML**: Configuration management
- **scikit-learn**: Text vectorization (TfidfVectorizer) and model training
- **NLTK**: Text cleaning and preprocessing
- **pandas**: Data handling and comparison reporting

---

## Tips for Best Results

1. **Try multiple models** - Use `train_multi.py` to find best model
2. **Tune hyperparameters** - Adjust parameters in `params_new.yml`
3. **Monitor MLflow UI** - Track experiments in real-time
4. **Compare metrics** - Focus on F1-score for imbalanced data
5. **Save preprocessor** - Vectorizer is saved as artifact for consistency
6. **Use DagsHub** - Enable remote tracking for team collaboration

