# ⚡ Quick Start - Phishing Detection System

## 🎯 In 5 Minutes

### 1. **Install** (1 minute)
```bash
pip install -r requirements.txt
```

### 2. **Train** (10-20 minutes)
```bash
python backend/src/data_transform.py
python backend/src/training.py
python backend/src/evaluation.py
```

### 3. **View Results** (Optional)
```bash
mlflow ui
# Open http://localhost:5000
```

### 4. **Start Backend** (Terminal 1)
```bash
python -m uvicorn backend.src.app:app --reload
# API runs on http://localhost:8000
```

### 5. **Start Frontend** (Terminal 2)
```bash
streamlit run frontend/app.py
# UI runs on http://localhost:8501
```

### 6. **Analyze!**
- Go to http://localhost:8501
- Paste a message
- Click "Analyze"
- See risk score + red flags

---

## 📊 Key Files

| File | Purpose |
|------|---------|
| `backend/src/data_transform.py` | Data cleaning & preprocessing |
| `backend/src/training.py` | Train 15 models with CV & metrics |
| `backend/src/evaluation.py` | Evaluate models, comprehensive metrics |
| `backend/src/app.py` | FastAPI backend (inference API) |
| `frontend/app.py` | Streamlit UI for analysis |
| `params.yaml` | All configuration (models, TF-IDF, CV) |
| `dvc.yaml` | Pipeline definition |

---

## 🚀 Quick Commands

### ML Pipeline
```bash
# Run all stages
dvc repro

# Or step-by-step:
python backend/src/data_transform.py
python backend/src/training.py
python backend/src/evaluation.py
```

### Monitoring
```bash
# View metrics
mlflow ui                    # http://localhost:5000
dvc metrics show

# Check pipeline status
dvc status
dvc dag                      # Show pipeline DAG
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Analyze message
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":"Click here now!"}'

# List models
curl http://localhost:8000/models
```

---

## 📈 What to Expect

### Training Output
```
Training 15 model combinations:
- 3 TF-IDF variants × 5 models
- 5-fold cross-validation
- Comprehensive metrics per model

Expected time: 20-30 minutes
```

### API Response Example
```json
{
  "label": "Phishing",
  "risk_score": 87.5,
  "confidence": 0.875,
  "explanation": "⚠️ HIGH RISK: Strong phishing indicators",
  "red_flags": [
    {"category": "Urgent Language", "confidence": 0.95},
    {"category": "Suspicious Links", "confidence": 0.87}
  ]
}
```

### Risk Gauge
- 🟢 **0-33%**: Safe/Legitimate
- 🟠 **33-66%**: Suspicious
- 🔴 **66-100%**: Danger/Phishing

---

## ⚙️ Configuration (params.yaml)

**Change these to run experiments**:

```yaml
# Preprocessing variants
preprocessing:
  tfidf_variants:
    tfidf_v1: {max_features: 5000, ngram_range: [1, 2]}
    tfidf_v2: {max_features: 3000, ngram_range: [1, 3]}  # Try this!
    tfidf_v3: {max_features: 10000, ngram_range: [1, 2]}

# Model variants
model_variants:
  RandomForest_v1: {n_estimators: 100, max_depth: 15}
  LogisticRegression_v1: {C: 1.0}
  # Add new models here
```

**Change one at a time** to see what improves metrics!

---

## 🔄 Typical Workflow

### 1. **Baseline Run**
```bash
python backend/src/training.py
mlflow ui
# Note F1-scores in MLflow
```

### 2. **Experiment 1: Better Preprocessing**
```bash
# Modify clean_text() in data_transform.py
# Re-run:
python backend/src/data_transform.py
python backend/src/training.py
# Compare F1-scores in MLflow
```

### 3. **Experiment 2: TF-IDF Tuning**
```bash
# Add new tfidf variant in params.yaml
python backend/src/training.py
# Compare results
```

### 4. **Deploy Best Model**
```bash
# Best model automatically used by API
python -m uvicorn backend.src.app:app --reload
streamlit run frontend/app.py
```

---

## 🆘 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `No module named nltk` | Run `python -c "import nltk; nltk.download('punkt_tab')"` |
| API won't start | Check port 8000 is free: `python -m uvicorn backend.src.app:app --port 8001` |
| Can't connect to API | Make sure API is running: `python -m uvicorn backend.src.app:app --reload` |
| Models not found | Run training first: `python backend/src/training.py` |
| Frontend shows "API Error" | Check if backend is running on http://localhost:8000 |

---

## 📚 Learn More

- **Full Guide**: See `FULL_STACK_GUIDE.md`
- **ML Pipeline**: See `PIPELINE_ARCHITECTURE.md`
- **API Docs**: Visit http://localhost:8000/docs (when running)

---

## ✅ Success Checklist

- [ ] Installed all dependencies
- [ ] Ran data_transform.py
- [ ] Ran training.py (15 models trained)
- [ ] Ran evaluation.py (metrics logged)
- [ ] Opened MLflow UI, saw experiments
- [ ] Started FastAPI backend
- [ ] Started Streamlit frontend
- [ ] Analyzed test message in UI
- [ ] Got risk score + red flags
- [ ] Tried different models from sidebar

**Once all ✅, you're done!** 🎉

---

## 🎓 Understanding the System

### Data Flow
```
Raw Email → Clean Text → TF-IDF Vectorize → Model Predict
                                               ↓
                                          Risk Score
                                               ↓
                                          Red Flags
                                               ↓
                                          Explanation
```

### Metrics Explained
- **Precision**: Of predicted phishing, how many correct? (avoid false alarms)
- **Recall**: Of actual phishing, how many caught? (catch bad emails)
- **F1**: Balance both (usually best metric)
- **ROC-AUC**: Overall discrimination ability

### Why Cross-Validation?
- Tests model generalization (not just on test set)
- More reliable metrics
- Helps prevent overfitting

---

## 🚀 Next Steps

**To improve models:**
1. Modify params.yaml (one change at a time)
2. Re-run training.py
3. Compare F1-scores in MLflow
4. Keep changes that improve scores
5. Repeat

**Example improvements to try:**
- Better text preprocessing (modify clean_text)
- Different TF-IDF configurations
- Different model hyperparameters
- More training data

**Happy analyzing!** 🔍
