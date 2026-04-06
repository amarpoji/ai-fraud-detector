# 🏗️ Refactored Architecture Guide

## Overview

The pipeline has been refactored into **separate, modular stages** for better maintainability and clear tracking:

```
Raw Data
   ↓
data_transform.py (TRANSFORM)
   ↓
Cleaned Data
   ↓
training.py (TRAIN)
   ↓
Trained Models
   ↓
evaluation.py (EVALUATE)
   ↓
Evaluation Metrics & Reports
```

---

## 📂 File Organization

### Transform Stage
- **Script**: `backend/src/data_transform.py`
- **Responsibility**: Data loading and text cleaning
- **Exports**: 
  - `clean_text()` function - reusable across scripts
  - `get_data_paths()` - configuration reading
  - `transform_data()` - main transformation logic
- **Output**: Cleaned CSV with `cleaned_text` column

### Training Stage
- **Script**: `backend/src/training.py`
- **Responsibility**: Model training only
- **Imports**: 
  - Uses `data_transform.get_data_paths()`
  - Loads pre-transformed data
- **Process**:
  1. Load processed data
  2. Vectorize text (TF-IDF)
  3. Train model(s)
  4. Log to MLflow
  5. Save training metadata
- **Output**: MLflow artifacts + training_info.json

### Evaluation Stage
- **Script**: `backend/src/evaluation.py`
- **Responsibility**: Model evaluation only
- **Inputs**:
  - Pre-transformed test data
  - Training metadata (run IDs)
- **Process**:
  1. Load test data
  2. Load trained models from MLflow
  3. Evaluate each model
  4. Calculate comprehensive metrics
  5. Log evaluation results
- **Output**: Evaluation metrics + CSV reports

---

## 🔄 Data Flow

```
email_dataset.csv (raw)
    ↓
[data_transform.py]
    ↓
email_dataset_processed.csv (cleaned, with cleaned_text column)
    ↓
[training.py]
    │
    ├─ Vectorizes: cleaned_text → TF-IDF features
    ├─ Trains: multiple models in parallel
    ├─ Logs to MLflow: params, metrics, models
    └─ Saves: training_info.json (metadata)
    ↓
[evaluation.py]
    │
    ├─ Loads: models from MLflow
    ├─ Loads: test data (same as training split)
    ├─ Evaluates: accuracy, precision, recall, f1, roc_auc
    ├─ Logs to MLflow: evaluation metrics
    └─ Exports: CSV reports + confusion matrices
    ↓
mlflow_artifacts/
├── training_info.json
├── evaluation_report.csv
├── {model_name}/
│   ├── model/
│   ├── reports/
│   │   └── classification_report.txt
│   └── matrices/
│       └── confusion_matrix.txt
```

---

## 🎯 Key Improvements

### 1. **No Duplicate Functions**
```python
# Before: clean_text() duplicated in multiple files
# After: Defined once in data_transform.py, imported where needed

# In training.py or evaluation.py:
from backend.src.data_transform import clean_text
```

### 2. **Configuration Reuse**
```python
# Both training and evaluation use same config:
config = load_config('params_new.yml')

# Path handling centralized:
raw_path, processed_path = get_data_paths()
```

### 3. **Separation of Concerns**
```
data_transform.py  → Raw → Processed
training.py        → Training + MLflow logging
evaluation.py      → Evaluation + MLflow logging
```

### 4. **Use Pre-Transformed Data**
```python
# training.py and evaluation.py load from:
processed_path = 'backend/data/processed/email_dataset_processed.csv'

# Instead of re-cleaning in each script
```

### 5. **Modular MLflow Tracking**
```
Training Run:      Logs training parameters + model
├── model/
├── preprocessors/vectorizer.pkl
└── training_info.json

Evaluation Run:    Logs evaluation metrics + reports
├── evaluation/reports/
├── evaluation/matrices/
└── evaluation_report.csv
```

---

## 📊 DVC Pipeline Integration

### dvc.yaml Structure
```yaml
stages:
  transform:
    cmd: python backend/src/data_transform.py
    deps:
      - backend/data/raw/email_dataset.csv
      - backend/src/data_transform.py
    outs:
      - backend/data/processed/email_dataset_processed.csv

  train:
    cmd: python backend/src/training.py
    deps:
      - backend/data/processed/email_dataset_processed.csv
      - backend/src/training.py
    outs:
      - mlflow_artifacts/training_info.json

  evaluate:
    cmd: python backend/src/evaluation.py
    deps:
      - backend/data/processed/email_dataset_processed.csv
      - mlflow_artifacts/training_info.json
    outs:
      - mlflow_artifacts/evaluation_report.csv
```

### Pipeline Execution
```bash
# Full pipeline
dvc repro

# Stages run in order:
# 1. transform - only if raw data changes
# 2. train - only if processed data or config changes
# 3. evaluate - only if training or test data changes
```

---

## 📈 MLflow + DVC + DagsHub Integration

### What Gets Tracked Where

**DVC (dvc.yaml, dvc.lock)**:
- ✅ Data versions
- ✅ Pipeline dependencies
- ✅ Stage inputs/outputs
- ✅ Execution history

**MLflow**:
- ✅ Training parameters
- ✅ Training metrics
- ✅ Trained models
- ✅ Evaluation metrics
- ✅ Model artifacts

**DagsHub Dashboard**:
- ✅ Pipeline DAG visualization
- ✅ Experiment tracking (MLflow)
- ✅ Data versioning (DVC)
- ✅ Parameter tracking
- ✅ Metrics comparison
- ✅ Model registry

---

## 🔧 Usage Workflow

### Step 1: Transform Data
```bash
python backend/src/data_transform.py
# Or via DVC:
dvc repro -s transform
```

Output: `backend/data/processed/email_dataset_processed.csv`

### Step 2: Train Models
```bash
python backend/src/training.py
# Or via DVC:
dvc repro -s train
```

Output: Models in MLflow + `training_info.json`

### Step 3: Evaluate Models
```bash
python backend/src/evaluation.py
# Or via DVC:
dvc repro -s evaluate
```

Output: Evaluation metrics + CSV reports

### View Results
```bash
# Local MLflow
mlflow ui

# DagsHub MLflow (if configured)
# Visit DagsHub project page
```

---

## 🎓 Architecture Decisions

### Why Separate Training and Evaluation?

1. **Modularity**: Each stage has single responsibility
2. **Reusability**: Can run evaluation anytime without re-training
3. **Efficiency**: Can evaluate multiple models without re-training
4. **Tracking**: MLflow tracks training and evaluation separately
5. **Debugging**: Easier to debug individual stages

### Why Use Pre-Transformed Data?

1. **Performance**: Don't re-clean data unnecessarily
2. **Consistency**: Same data cleaning across runs
3. **Reproducibility**: Data transformation is tracked by DVC
4. **Storage**: Transformed data can be cached/versioned

### Why Centralize Functions?

1. **DRY Principle**: Don't repeat code
2. **Maintainability**: Single source of truth
3. **Consistency**: Same cleaning logic everywhere
4. **Testing**: Easier to unit test

---

## 📝 Code Examples

### Using clean_text from multiple scripts

**data_transform.py**:
```python
def clean_text(text):
    # Implementation here
    pass

def transform_data(input_path, output_path=None):
    df['cleaned_text'] = df['text'].apply(clean_text)
    return df
```

**training.py** (can import if needed):
```python
from backend.src.data_transform import clean_text, get_data_paths

# Load already-transformed data
processed_path = get_data_paths()[1]
df = pd.read_csv(processed_path)
# clean_text already applied, just use df['cleaned_text']
```

**evaluation.py**:
```python
from backend.src.data_transform import get_data_paths

# Load same data as training
processed_path = get_data_paths()[1]
df = pd.read_csv(processed_path)
# Use pre-cleaned data
```

---

## ✅ Benefits of Refactored Architecture

| Aspect | Before | After |
|--------|--------|-------|
| Code Duplication | High (clean_text in multiple files) | Low (defined once, imported) |
| Data Processing | Repeated in each script | Single transform stage |
| MLflow Tracking | Mixed in each script | Separate train and eval stages |
| Pipeline Clarity | Not explicit | Clear with dvc.yaml |
| DVC Integration | Missing | Full integration |
| Debugging | Difficult | Easy (modular stages) |
| Reusability | Low | High |
| Maintainability | Low | High |

---

## 🚀 Next Steps

1. ✅ Run `dvc repro` to execute full pipeline
2. ✅ Check DagsHub for visualization
3. ✅ View MLflow UI for metrics
4. ✅ Compare models in evaluation report
5. ✅ Deploy best model

