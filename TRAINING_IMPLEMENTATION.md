# Implementation Summary

## Created Scripts

### 1. **backend/src/data_transform.py**
- Loads raw email dataset from CSV
- Applies text cleaning pipeline:
  - Lowercase conversion
  - Punctuation/special character removal
  - Tokenization using NLTK
  - Stopword removal
- Saves cleaned data to processed directory
- Reads file paths from `params.yml`

### 2. **backend/src/train_pipeline.py**
Single model training script with MLflow integration:
- **Text Vectorization**: TF-IDF vectorizer (configurable max_features, ngram_range)
- **Data Split**: Configurable train/test split ratio
- **Model Training**: Supports RandomForest, LogisticRegression, SVM, NaiveBayes
- **MLflow Tracking**:
  - Logs all parameters
  - Logs metrics (accuracy, precision, recall, f1_score)
  - Logs model with inferred signature
  - Generates classification reports as artifacts
  - Supports DagsHub integration via MLFLOW_TRACKING_URI
- **Model Registry**: Can register model with signature for production

### 3. **backend/src/train_multi.py** ⭐ RECOMMENDED
Advanced multi-model training with automatic comparison:
- **Multiple Model Variants**: Train different models and hyperparameters in one run
- **Automatic Comparison**: Generates comparison table ranked by F1-score
- **Per-Model MLflow Runs**: Each model gets its own MLflow run
- **Model Signature Inference**: Uses `infer_signature` for production-ready models
- **Artifact Management**:
  - Classification reports per model
  - Comparison CSV with all metrics
  - Model serialization and versioning
- **DagsHub Support**: Full integration with remote tracking
- **Best Model Selection**: Automatically identifies best performing model

---

## Configuration Files

### params_new.yml
```yaml
data:
  raw_path: backend/data/raw/email_dataset.csv
  processed_path: backend/data/processed/email_dataset_processed.csv

model:
  type: RandomForest
  n_estimators: 100
  max_depth: 15
  random_state: 42
  n_jobs: -1

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
  RandomForest_v2:
    type: RandomForest
    n_estimators: 200
    max_depth: 20
  LogisticRegression_v1:
    type: LogisticRegression
    C: 1.0
  LogisticRegression_v2:
    type: LogisticRegression
    C: 0.1
  NaiveBayes_v1:
    type: NaiveBayes
    alpha: 1.0

mlflow:
  experiment_name: email-phishing-detection
  track_model_signature: true
  register_model: true
  model_registry_name: fraud-detector-model
```

---

## Key Features Implemented

### ✅ MLflow Integration
- Experiment tracking with configurable experiment names
- Parameter logging (model type, hyperparameters, preprocessing settings)
- Metrics logging (accuracy, precision, recall, f1_score)
- Artifact logging (models, reports, preprocessors)
- Model registry support with model signatures

### ✅ Model Signature Inference
- Uses `mlflow.models.infer_signature` to automatically capture input/output schema
- Enables type validation and model validation in production
- Creates reproducible and deployable models

### ✅ DagsHub Integration
- Supports remote tracking via MLFLOW_TRACKING_URI environment variable
- Authentication via MLFLOW_TRACKING_USERNAME and MLFLOW_TRACKING_PASSWORD
- Enables team collaboration and remote experiment tracking

### ✅ URL Parse Support
- Uses `urllib.parse.urlparse` to parse DagsHub tracking URIs
- Validates and processes remote tracking endpoints

### ✅ Model Comparison Framework
- Train multiple models with different hyperparameters
- Automatic metric comparison and ranking
- CSV export of comparison results
- Best model selection based on F1-score

### ✅ Configuration-Driven Training
- All parameters externalized to params_new.yml
- Easy hyperparameter tuning without code changes
- Support for multiple model configurations
- Per-preprocessing configuration settings

---

## Usage Examples

### Quick Start - Single Model
```bash
# Run data transformation
python backend/src/data_transform.py

# Train single model with MLflow
python backend/src/train_pipeline.py
```

### Model Comparison - Multiple Models
```bash
# Define variants in params_new.yml, then:
python backend/src/train_multi.py

# View results in console and mlflow_artifacts/model_comparison_*.csv
```

### With DagsHub Integration
```bash
# Set environment variables
export MLFLOW_TRACKING_URI=https://dagshub.com/amarpoji/ai-fraud-detector.mlflow
export MLFLOW_TRACKING_USERNAME=amarpoji
export MLFLOW_TRACKING_PASSWORD=8e787fb5482c3710e4ed71f803155c075a6f4948

# Run training
python backend/src/train_multi.py

# Results available on DagsHub dashboard
```

---

## Workflow for Model Selection

1. **Prepare Data**
   ```bash
   python backend/src/data_transform.py
   ```

2. **Define Experiments in `params_new.yml`**
   - Add different RandomForest configurations
   - Add LogisticRegression variants
   - Add other model types if needed

3. **Train and Compare**
   ```bash
   python backend/src/train_multi.py
   ```

4. **Review Results**
   - Console output shows comparison table
   - Best model highlighted by F1-score
   - CSV report saved to mlflow_artifacts/

5. **Deploy Best Model**
   - Model with highest F1-score selected
   - Model can be retrieved from MLflow registry
   - Model signature ensures consistent deployment

---

## Files Structure

```
backend/src/
├── data_transform.py      # Data preprocessing
├── train_pipeline.py      # Single model training
├── train_multi.py         # Multi-model comparison (RECOMMENDED)
├── README.md              # Detailed documentation
└── __init__.py           # Package initialization

Root:
├── params_new.yml         # Configuration with model variants
└── params.yml             # Original params file (can use either)

Output:
├── mlruns/                # Local MLflow runs
├── mlflow_artifacts/      # Generated artifacts
└── .mlflow/              # MLflow metadata
```

---

## Technologies Used

- **MLflow**: Experiment tracking, model registry, and deployment support
- **scikit-learn**: RandomForest, LogisticRegression, SVM, NaiveBayes models
- **NLTK**: Text preprocessing and cleaning
- **pandas**: Data manipulation and CSV handling
- **PyYAML**: Configuration file parsing
- **urllib.parse**: URL handling for DagsHub integration
- **pickle**: Model serialization for vectorizers

---

## Notes

- Train.py loads from params_new.yml which has model variants defined
- Each model variant trains in a separate MLflow run
- Results compared automatically and saved to CSV
- Model signatures enable consistent deployment
- DagsHub integration works through environment variables
- All artifacts logged for reproducibility and auditability

