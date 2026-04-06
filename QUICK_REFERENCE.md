# 🎯 Quick Reference Guide - Refactored Pipeline

## 📊 Architecture at a Glance

```
BEFORE (Old)              AFTER (Refactored)
─────────────────         ──────────────────

train_pipeline.py    →    training.py (focused)
  ├─ Clean text           + evaluation.py
  ├─ Vectorize            + data_transform.py
  ├─ Train model
  ├─ Evaluate
  └─ Log to MLflow

train_multi.py       →    DVC Pipeline (dvc.yaml)
  ├─ Clean text           - transform stage
  ├─ Vectorize            - train stage
  ├─ Train multiple       - evaluate stage
  ├─ Evaluate all
  └─ Compare


ISSUE: Code duplication, mixed concerns
SOLUTION: Separate stages, reusable functions
```

---

## 🔄 Data Pipeline

```
raw/email_dataset.csv
        ↓
  data_transform.py
        ↓ [DVC tracks]
processed/email_dataset_processed.csv
        ↓
   training.py
        ↓ [MLflow tracks training]
   trained_models
        ↓
  evaluation.py
        ↓ [MLflow tracks evaluation]
   evaluation_report.csv
```

---

## 🚀 One-Minute Setup

```bash
# 1. Install
pip install -r requirements_updated.txt

# 2. Run (all 3 stages)
dvc repro

# 3. View
mlflow ui
```

Visit: http://localhost:5000

---

## 📁 File Map

| File | Purpose | Status |
|------|---------|--------|
| `backend/src/data_transform.py` | Data cleaning | ✅ Refactored |
| `backend/src/training.py` | Model training | ✅ NEW |
| `backend/src/evaluation.py` | Model evaluation | ✅ NEW |
| `dvc.yaml` | Pipeline definition | ✅ NEW |
| `requirements_updated.txt` | Dependencies | ✅ NEW |
| `params_new.yml` | Configuration | ⏸️ Existing |

---

## 🎯 What Each Script Does

### data_transform.py
```
Input:  raw/email_dataset.csv
Process: Clean text
Output: processed/email_dataset_processed.csv
        (with cleaned_text column)
```

### training.py
```
Input:  processed/email_dataset_processed.csv, params_new.yml
Process: Train models, log to MLflow
Output: trained_models, training_info.json
Track:  parameters, models, artifacts
```

### evaluation.py
```
Input:  trained_models, test_data
Process: Evaluate models, log to MLflow
Output: evaluation_report.csv, metrics
Track:  accuracy, precision, recall, f1, roc_auc
```

---

## 💻 Commands

### Run Everything
```bash
dvc repro
```

### Run One Stage
```bash
dvc repro -s transform    # Only clean data
dvc repro -s train        # Only train models
dvc repro -s evaluate     # Only evaluate models
```

### View Pipeline
```bash
dvc dag      # Show dependency graph
dvc status   # Show what needs to run
```

### Push to DagsHub
```bash
git push
dvc push
```

---

## 📊 DagsHub View

```
DagsHub Dashboard
├── Pipeline
│   ├── transform
│   ├── train
│   └── evaluate
├── Data
│   ├── raw/email_dataset.csv (v1, v2, v3...)
│   └── processed/...processed.csv (v1, v2, v3...)
├── MLflow Experiments
│   ├── Training runs
│   └── Evaluation runs
└── Metrics & Plots
```

---

## 🔗 DVC + MLflow + DagsHub

```
DVC handles:
├─ Data versioning
├─ Pipeline DAG
└─ Dependency tracking

MLflow handles:
├─ Model tracking
├─ Metrics logging
├─ Hyperparameters
└─ Artifacts

DagsHub shows:
├─ Everything from DVC
├─ Everything from MLflow
└─ Beautiful dashboard
```

---

## 📈 Key Metrics Tracked

### Training (training.py logs)
- Parameters (model_type, hyperparams)
- Model artifacts
- Vectorizer

### Evaluation (evaluation.py logs)
- accuracy
- precision
- recall
- f1_score
- roc_auc
- confusion_matrix
- classification_report

---

## 🎓 Learning Path

1. Read **REFACTORING_COMPLETE.md** (2 min)
2. Read **DVC_PIPELINE_GUIDE.md** (5 min)
3. Run `dvc repro` (5-10 min)
4. View MLflow UI (2 min)
5. Read **REFACTORED_ARCHITECTURE.md** (5 min)
6. Configure DagsHub (5 min)

---

## ✨ Benefits

| Before | After |
|--------|-------|
| Code duplication | No duplication |
| Mixed concerns | Clear separation |
| Hard to debug | Easy to debug |
| No pipeline | Clear DVC pipeline |
| Training + eval mixed | Separate MLflow runs |
| Hard to deploy | Production-ready |

---

## 🚨 Common Issues & Fixes

### "Module not found" error
```bash
# Fix: Export function in data_transform.py
# Use: from backend.src.data_transform import function
```

### "File not found" error
```bash
# Fix: Run transform first
dvc repro -s transform
```

### MLflow not showing metrics
```bash
# Fix: Run training
dvc repro -s train
```

---

## 📞 Quick Help

**Question**: Where's the cleaned data?  
**Answer**: `backend/data/processed/email_dataset_processed.csv`

**Question**: Where are trained models?  
**Answer**: MLflow artifacts + MLflow registry

**Question**: How to compare models?  
**Answer**: Run `mlflow ui` → Compare in dashboard

**Question**: How to push to DagsHub?  
**Answer**: See DVC_PIPELINE_GUIDE.md

---

## 🎉 You're Ready!

✅ Clean architecture  
✅ No code duplication  
✅ Clear pipeline  
✅ Production-ready  

Run this:
```bash
dvc repro && mlflow ui
```

Done! 🚀
