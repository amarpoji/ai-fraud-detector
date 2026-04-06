# Quick Start Guide - Training Scripts

## 🚀 Quick Setup

### Prerequisites
```bash
pip install -r requirements.txt
```

### Step 1: Prepare Data
```bash
cd backend/src
python data_transform.py
```
✓ This cleans the raw email data and prepares it for training

### Step 2: Configure Models
Edit `params_new.yml` to define model variants you want to compare:
```yaml
model_variants:
  RandomForest_v1:
    type: RandomForest
    n_estimators: 100
    max_depth: 15
  
  LogisticRegression_v1:
    type: LogisticRegression
    C: 1.0
```

### Step 3: Train & Compare Models
```bash
python train_multi.py
```

✓ This will:
- Train all model variants
- Log metrics to MLflow
- Compare results and show best model
- Save comparison report to `mlflow_artifacts/`

### Step 4: View Results
```bash
mlflow ui
```
Then open `http://localhost:5000` to see all experiments and runs.

---

## 📊 Model Comparison Output

The script produces a comparison table:
```
Model                  accuracy  precision    recall  f1_score                           Run ID
RandomForest_v1         0.9700    0.9750   0.9680   0.9715  abc123...
LogisticRegression_v1   0.9450    0.9400   0.9500   0.9450  def456...
NaiveBayes_v1           0.8950    0.8900   0.9100   0.8990  ghi789...

🏆 Best Model (F1-Score): RandomForest_v1
   F1-Score: 0.9715
   Run ID: abc123...
```

---

## 🔧 Customization

### Try Different Models
```yaml
model_variants:
  RandomForest_v1:
    type: RandomForest
    n_estimators: 50
    max_depth: 10
  
  RandomForest_v2:
    type: RandomForest
    n_estimators: 200
    max_depth: 20
  
  LogisticRegression_v1:
    type: LogisticRegression
    C: 0.1
  
  LogisticRegression_v2:
    type: LogisticRegression
    C: 1.0
  
  SVM_v1:
    type: SVM
    kernel: rbf
    C: 1.0
  
  NaiveBayes_v1:
    type: NaiveBayes
    alpha: 1.0
```

### Adjust Preprocessing
```yaml
preprocessing:
  train_test_split: 0.2      # 80% train, 20% test
  max_features: 5000         # Max TF-IDF features
  ngram_range: [1, 2]        # Unigrams + Bigrams
  random_state: 42           # For reproducibility
```

### Change Data Paths
```yaml
data:
  raw_path: backend/data/raw/email_dataset.csv
  processed_path: backend/data/processed/email_dataset_processed.csv
```

---

## ☁️ Remote Tracking (DagsHub)

### Setup DagsHub Integration
```bash
# Get credentials from DagsHub dashboard
export MLFLOW_TRACKING_URI=https://dagshub.com/username/repo.mlflow
export MLFLOW_TRACKING_USERNAME=your_username
export MLFLOW_TRACKING_PASSWORD=your_token

# Run training
python train_multi.py
```

All experiments will be tracked on DagsHub!

---

## 📁 Output Files

After training, check:

**Console Output**
- Model comparison table
- Best model results
- Training progress

**mlflow_artifacts/**
- `model_comparison_YYYYMMDD_HHMMSS.csv` - Full comparison results
- `RandomForest_v1/` - Model-specific artifacts
  - `classification_report.txt`
  - `model/` - Serialized model
  - `preprocessors/` - Vectorizer

**mlruns/**
- Local MLflow database
- View with `mlflow ui`

---

## 🎯 Comparison Workflow

### Scenario 1: Find Best RandomForest Parameters
```yaml
model_variants:
  rf_small:
    type: RandomForest
    n_estimators: 50
    max_depth: 10
  
  rf_medium:
    type: RandomForest
    n_estimators: 100
    max_depth: 15
  
  rf_large:
    type: RandomForest
    n_estimators: 200
    max_depth: 20
```
Then run `train_multi.py` to find best depth and n_estimators.

### Scenario 2: Compare All Model Types
```yaml
model_variants:
  RandomForest:
    type: RandomForest
    n_estimators: 100
    max_depth: 15
  
  LogisticRegression:
    type: LogisticRegression
    C: 1.0
  
  NaiveBayes:
    type: NaiveBayes
    alpha: 1.0
```
Run to find which model type performs best.

### Scenario 3: Hyperparameter Tuning
```yaml
model_variants:
  lr_c_0_01:
    type: LogisticRegression
    C: 0.01
  
  lr_c_0_1:
    type: LogisticRegression
    C: 0.1
  
  lr_c_1:
    type: LogisticRegression
    C: 1.0
  
  lr_c_10:
    type: LogisticRegression
    C: 10.0
```
Run to find optimal C parameter.

---

## 📈 Metrics Explained

- **Accuracy**: (TP + TN) / Total - Overall correctness
- **Precision**: TP / (TP + FP) - Of predicted positives, how many correct
- **Recall**: TP / (TP + FN) - Of actual positives, how many caught
- **F1-Score**: Harmonic mean of precision and recall (best for imbalanced data)

For phishing detection, **F1-Score** is usually best metric since we care about both:
- Not missing phishing (high recall)
- Not flagging legitimate emails (high precision)

---

## ❓ Troubleshooting

**Error: Raw data file not found**
- Check data paths in params_new.yml
- Ensure `backend/data/raw/email_dataset.csv` exists

**NLTK data missing**
- Scripts auto-download required NLTK data
- Or run: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`

**MLflow not tracking**
- Check: `mlflow ui` opens on http://localhost:5000
- For DagsHub, verify MLFLOW_TRACKING_URI is set correctly

**Out of memory with large datasets**
- Reduce max_features in params_new.yml
- Reduce batch size / n_estimators

---

## 🎓 Next Steps

1. **Try different models** - Run with various model_variants
2. **Analyze results** - Check MLflow UI for detailed metrics
3. **Fine-tune winner** - Focus on best model and tune its parameters
4. **Deploy** - Use saved model for inference
5. **Monitor** - Track performance over time on MLflow

---

## 📚 More Information

- See `README.md` in backend/src for detailed documentation
- See `TRAINING_IMPLEMENTATION.md` for technical details
- MLflow docs: https://mlflow.org/docs/latest/
- scikit-learn docs: https://scikit-learn.org/
