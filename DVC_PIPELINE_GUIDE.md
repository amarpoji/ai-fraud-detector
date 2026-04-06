# 🚀 DVC Pipeline Setup Guide

## Overview

This guide explains how to set up and use the DVC pipeline for the Email Phishing Detection system with clear visualization in DagsHub.

---

## 📋 DVC Pipeline Stages

The pipeline has **3 main stages**:

### 1. **Transform** (Data Transformation)
- **Script**: `backend/src/data_transform.py`
- **Input**: `backend/data/raw/email_dataset.csv`
- **Output**: `backend/data/processed/email_dataset_processed.csv`
- **Action**: Cleans and preprocesses text data
- **Tracking**: DVC tracks input/output files

### 2. **Train** (Model Training)
- **Script**: `backend/src/training.py`
- **Input**: Processed data from transform stage
- **Output**: Trained models, artifacts, training info
- **Action**: Trains multiple model variants
- **Tracking**: MLflow tracks metrics and parameters

### 3. **Evaluate** (Model Evaluation)
- **Script**: `backend/src/evaluation.py`
- **Input**: Test data, trained models
- **Output**: Evaluation metrics and reports
- **Action**: Evaluates all trained models
- **Tracking**: MLflow tracks evaluation metrics

---

## ⚙️ Quick Setup

### Step 1: Initialize DVC (if not done)
```bash
dvc init
dvc config core.autostage true
```

### Step 2: Configure DagsHub Remote
```bash
dvc remote add dagshub s3://your-bucket-name
dvc remote default dagshub
```

### Step 3: Run the Pipeline
```bash
dvc repro
```

This will:
1. Run `transform` stage
2. Run `train` stage (depends on transform)
3. Run `evaluate` stage (depends on train)

---

## 📊 DVC + DagsHub Visualization

### What You'll See in DagsHub

**Pipeline DAG (Directed Acyclic Graph)**:
```
transform.py
    ↓
 [processed data]
    ↓
training.py
    ↓
[trained models]
    ↓
evaluation.py
    ↓
[evaluation metrics]
```

**Version Control**:
- `dvc.lock` - Tracks pipeline execution and dependencies
- Data versioning automatically handled by DVC

**MLflow Integration**:
- Training metrics tracked in MLflow
- Evaluation metrics tracked in MLflow
- Can be viewed in DagsHub MLflow interface

---

## 🔗 Connect to DagsHub

### Step 1: Get DagsHub Credentials
1. Go to https://dagshub.com
2. Create account and repository
3. Get credentials from Settings

### Step 2: Configure DVC Remote
```bash
dvc remote add dagshub \
  s3://repo.dvc.dagshub.com/username/repo-name/storage \
  --default
```

### Step 3: Set Credentials
```bash
dvc remote modify dagshub access_key_id <YOUR_KEY>
dvc remote modify dagshub secret_access_key <YOUR_SECRET>
```

### Step 4: Push Pipeline
```bash
git add dvc.yaml dvc.lock
git commit -m "Add DVC pipeline"
git push

dvc push  # Push data to DagsHub
```

---

## 📁 File Structure

```
ai-fraud-detector/
├── dvc.yaml                    # Pipeline definition
├── dvc.lock                    # Pipeline lock (auto-generated)
├── .dvc/
│   ├── config                  # DVC configuration
│   └── .gitignore
├── backend/src/
│   ├── data_transform.py       # Transform stage
│   ├── training.py             # Train stage
│   └── evaluation.py           # Evaluate stage
├── backend/data/
│   ├── raw/
│   │   └── email_dataset.csv
│   └── processed/
│       └── email_dataset_processed.csv (tracked by DVC)
└── params_new.yml              # Configuration
```

---

## 🎯 Common Commands

### Run Full Pipeline
```bash
dvc repro
```

### Run Specific Stage
```bash
dvc repro -s transform  # Only run transform
dvc repro -s train      # Only run train
dvc repro -s evaluate   # Only run evaluate
```

### View Pipeline Status
```bash
dvc status
```

### View Pipeline DAG
```bash
dvc dag
```

Output:
```
 ╭─────────────────╮
 │   email_da.csv  │
 ╰────────┬────────╯
          │
     ┌────▼────┐
     │transform│
     └────┬────┘
          │
    ╭─────▼──────────────╮
    │processed_data.csv  │
    ╰─────┬──────────────╯
          │
      ┌───▼────┐
      │ train  │
      └───┬────┘
          │
     ╭────▼─────────╮
     │trained_model │
     ╰────┬─────────╯
          │
      ┌───▼───────┐
      │ evaluate  │
      └───────────┘
```

### Push Data to Remote
```bash
dvc push
```

### Pull Data from Remote
```bash
dvc pull
```

---

## 📊 DagsHub Dashboard Features

After pushing to DagsHub, you'll see:

### 1. **Pipeline Visualization**
- Visual DAG showing all stages
- Input/output files
- Dependencies between stages
- Execution time for each stage

### 2. **Data Versioning**
- Track processed data versions
- Version history
- Compare versions

### 3. **MLflow Metrics**
- Training metrics (accuracy, precision, recall, f1)
- Evaluation metrics
- Model comparison
- Hyperparameter tracking

### 4. **Experiments**
- Multiple experiment runs tracked
- Compare different runs
- Best model identification

### 5. **Collaboration**
- Share pipeline with team
- Version control
- Reproducibility

---

## 🔄 Workflow

### Development Workflow
```bash
# 1. Make changes to code
# 2. Run pipeline locally
dvc repro

# 3. Commit changes
git add dvc.yaml dvc.lock .gitignore
git commit -m "Update pipeline"

# 4. Push to DagsHub
git push
dvc push

# 5. View in DagsHub dashboard
```

### Iteration Workflow
```bash
# 1. Update params_new.yml
# 2. Run specific stage
dvc repro -s train

# 3. Check results
mlflow ui

# 4. If satisfied, run full pipeline
dvc repro

# 5. Commit and push
git add -A
git commit -m "Update model parameters"
git push && dvc push
```

---

## 🎓 Understanding dvc.yaml

### Stage Definition
```yaml
stages:
  transform:
    cmd: python backend/src/data_transform.py
    deps:                    # Input files that trigger re-run if changed
      - backend/data/raw/email_dataset.csv
      - backend/src/data_transform.py
    outs:                    # Output files tracked by DVC
      - backend/data/processed/email_dataset_processed.csv
    params:                  # Parameters tracked from YAML
      - data.raw_path
      - data.processed_path
```

### Parameters Tracking
DVC automatically tracks parameters from `params_new.yml`:
- Stage only re-runs if parameters change
- Parameter changes recorded in `dvc.lock`
- Visible in DagsHub dashboard

### Outputs Tracking
- `outs:` - Files tracked in DVC storage
- Changes to outputs trigger downstream stages
- Versions maintained automatically

---

## 📈 Visualize Pipeline Locally

### View DAG
```bash
dvc dag
```

### View Status
```bash
dvc status
```

### View Metrics
```bash
dvc metrics show
```

### View Parameters
```bash
dvc params show
```

---

## 🚨 Troubleshooting

### Pipeline Not Running
```bash
# Check status
dvc status

# Reproduce with verbose output
dvc repro -v

# Check for errors
dvc repro --force  # Force re-run
```

### Data Conflicts
```bash
# Pull latest data
dvc pull

# Check remote status
dvc remote status
```

### Parameters Not Updated
```bash
# Force re-run
dvc repro --force -s transform

# Clear cache
dvc cache clear

# Re-pull
dvc pull
```

---

## 🔐 Security

### DagsHub Credentials
Never commit credentials to git:
```bash
# Use environment variables
export DAGSHUB_USERNAME=your_username
export DAGSHUB_PASSWORD=your_token

# Or configure locally
dvc remote modify dagshub access_key_id your_key
```

### Git Ignore
DVC automatically updates `.gitignore` for:
- Large files
- Processed data
- Cache directory

---

## 📚 Integration with MLflow

DVC pipeline + MLflow provides:

1. **Data Lineage**: DVC tracks data versions
2. **Model Tracking**: MLflow tracks models and metrics
3. **Reproducibility**: Combination ensures full reproducibility
4. **Collaboration**: Share via DagsHub

### MLflow + DVC Flow
```
dvc.yaml defines pipeline
    ↓
Each stage runs scripts
    ↓
Scripts log to MLflow
    ↓
DVC tracks inputs/outputs
    ↓
DagsHub shows both
```

---

## 🎉 Next Steps

1. **Initialize**: `dvc init`
2. **Configure**: Set up DagsHub remote
3. **Run**: `dvc repro`
4. **Push**: `git push && dvc push`
5. **View**: Check DagsHub dashboard

---

## 📖 More Resources

- DVC Documentation: https://dvc.org/doc
- DagsHub: https://dagshub.com
- MLflow: https://mlflow.org
- Pipeline Tutorials: https://dvc.org/doc/start/pipeline

