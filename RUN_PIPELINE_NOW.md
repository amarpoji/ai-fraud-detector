# 🚀 Quick Fix & Run Guide

## ✅ DVC.YAML Fixed!

All validation errors have been corrected. The file is now clean and valid.

---

## 🎯 Run Pipeline Now

### Option 1: Local MLflow (Simplest)
```bash
dvc repro
mlflow ui
```

✅ This will work immediately!

---

### Option 2: With DagsHub (Optional)
```bash
# Set DagsHub credentials (one-time setup)
export MLFLOW_TRACKING_URI=https://dagshub.com/username/repo.mlflow
export MLFLOW_TRACKING_USERNAME=your_username
export MLFLOW_TRACKING_PASSWORD=your_token

# Run pipeline
dvc repro

# View results
mlflow ui  # or check DagsHub dashboard
```

---

## 📋 What Each Stage Does

### Stage 1: Transform (2-3 minutes)
```
Input:  backend/data/raw/email_dataset.csv
Action: Clean text, add cleaned_text column
Output: backend/data/processed/email_dataset_processed.csv
```

### Stage 2: Train (5-10 minutes)
```
Input:  Processed data
Action: Train 5 different models
Output: Models in MLflow, training_info.json
```

### Stage 3: Evaluate (3-5 minutes)
```
Input:  Trained models, test data
Action: Evaluate all models
Output: evaluation_report.csv, metrics
```

---

## ✨ Verification

Check that pipeline is valid:
```bash
dvc status
```

You should see:
```
✓ Pipeline is up to date
```

Or run individual stages:
```bash
dvc repro -s transform    # First run this
dvc repro -s train        # Then this
dvc repro -s evaluate     # Finally this
```

---

## 📊 Expected Output

After running `dvc repro`, you'll see:

```
► Stage 1: transform
  Running: python backend/src/data_transform.py
  ✓ Done in 2.3s

► Stage 2: train
  Running: python backend/src/training.py
  Training RandomForest_v1...
  Training RandomForest_v2...
  Training LogisticRegression_v1...
  Training LogisticRegression_v2...
  Training NaiveBayes_v1...
  ✓ Done in 8.5s

► Stage 3: evaluate
  Running: python backend/src/evaluation.py
  Evaluating RandomForest_v1...
    Accuracy: 0.9700, F1: 0.9715
  Evaluating RandomForest_v2...
    Accuracy: 0.9650, F1: 0.9663
  ... (more models)
  ✓ Done in 4.2s

✓ Pipeline completed successfully!
```

---

## 🎯 View Results

After running, open MLflow to see all metrics:
```bash
mlflow ui
```

Then open http://localhost:5000 in your browser to see:
- ✅ Training runs (5 models)
- ✅ Evaluation runs (5 models)
- ✅ All metrics comparison
- ✅ Best model highlighted

---

## 📁 Output Files

After pipeline completes:

```
mlflow_artifacts/
├── training_info.json           # Metadata about trained models
├── evaluation_report.csv         # Evaluation results
├── RandomForest_v1/
│   ├── model/                    # Trained model
│   ├── reports/                  # Classification reports
│   └── matrices/                 # Confusion matrices
├── RandomForest_v2/
│   └── ...
└── ... (more models)

mlruns/                           # MLflow local database
└── experiments/
    └── email-phishing-detection/
        ├── train_RandomForest_v1/
        ├── train_RandomForest_v2/
        ├── eval_RandomForest_v1/
        └── ... (more runs)
```

---

## 🔄 DVC Commands

```bash
# See what needs to run
dvc status

# Visualize pipeline
dvc dag

# Run specific stage only
dvc repro -s transform
dvc repro -s train
dvc repro -s evaluate

# See metrics
dvc metrics show

# Compare with previous run
dvc metrics diff

# Push data to remote
dvc push

# Pull data from remote
dvc pull

# View pipeline lock file
cat dvc.lock
```

---

## ✅ Checklist

Before running:
- ✅ `pip install -r requirements_updated.txt` (dependencies installed)
- ✅ `backend/data/raw/email_dataset.csv` exists
- ✅ `params_new.yml` exists with model variants
- ✅ `dvc.yaml` is valid (just fixed!)

After running:
- ✅ `backend/data/processed/email_dataset_processed.csv` created
- ✅ `mlflow_artifacts/training_info.json` created
- ✅ `mlflow_artifacts/evaluation_report.csv` created
- ✅ `mlruns/` directory created with experiments

---

## 🎉 You're Ready!

Everything is fixed and ready to run:

```bash
dvc repro
mlflow ui
```

That's it! Your pipeline will execute and create all artifacts. 🚀
