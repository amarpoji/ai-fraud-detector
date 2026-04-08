# 🔒 Email Phishing Detector - Full Stack App

**Beautiful React UI + Powerful ML Backend + Docker Containerization**

## What's New

✅ **React + Material-UI Frontend** (replaced Streamlit)
- Professional, responsive design
- Real-time risk gauge visualization
- Interactive model selection
- Red flag detection display
- API health monitoring

✅ **Docker Containerization**
- Backend: FastAPI + Python 3.11
- Frontend: React + Vite + Nginx
- MLflow UI for model tracking
- Easy deployment to cloud

✅ **Fully Integrated Stack**
- Frontend calls Backend API
- Nginx reverse proxy routing
- Docker Compose orchestration
- One-command deployment

## Quick Start (3 Steps)

### 1️⃣ Install Docker
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Mac: https://docs.docker.com/desktop/install/mac-install/
- Linux: https://docs.docker.com/engine/install/

### 2️⃣ Build & Run
```bash
cd ai-fraud-detector

# Build all containers
docker-compose build

# Start all services
docker-compose up -d
```

### 3️⃣ Open in Browser
- **UI**: http://localhost
- **API**: http://localhost:8000
- **MLflow**: http://localhost:5000

That's it! 🎉

## Architecture

```
┌─────────────────────────────────────────────┐
│       Browser (User)                        │
└────────────────────┬────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   Nginx Reverse Proxy      │
        │   (Port 80)                │
        ├────────────────────────────┤
        │ Frontend      │  API Proxy │
        │ (React/Vite) │  (to :8000)│
        └─────┬──────────────┬───────┘
              │              │
              ▼              ▼
        ┌──────────┐   ┌──────────────────┐
        │ React UI │   │ FastAPI Backend  │
        │Port :80  │   │ Port :8000       │
        └──────────┘   ├──────────────────┤
                       │ Load Model       │
                       │ (MLflow)         │
                       │ Run Prediction   │
                       │ Return Results   │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ MLflow UI        │
                       │ Port :5000       │
                       │ (Model Tracking) │
                       └──────────────────┘
```

## Features

### 🎨 Frontend (React + Material-UI)
- **Text Input**: Paste email/SMS content
- **Model Selection**: Choose from 15 trained models
- **Risk Gauge**: Visual representation (Low/Medium/High)
- **Prediction**: Phishing vs Legitimate
- **Red Flags**: Display detected phishing indicators
- **Explanations**: Human-readable risk analysis
- **API Status**: Connection indicator

### 🔧 Backend (FastAPI)
- **REST API**: `/analyze`, `/models`, `/health`
- **Model Loading**: MLflow integration
- **Vectorization**: TF-IDF text processing
- **Red Flag Detection**: 6 phishing categories
- **Risk Scoring**: 0-100 confidence scale

### 🐳 Docker Setup
- **Multi-container**: Frontend + Backend + MLflow
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx routing
- **Health Checks**: Automatic monitoring
- **Volume Mounts**: Data persistence

## File Structure

```
ai-fraud-detector/
├── frontend/                    # React + Vite app
│   ├── package.json            # Dependencies
│   ├── vite.config.js          # Build config
│   ├── index.html              # Entry HTML
│   ├── App.jsx                 # Main component
│   └── main.jsx                # React bootstrap
├── backend/
│   ├── src/
│   │   ├── app.py              # FastAPI server
│   │   ├── training.py         # Model training
│   │   └── evaluation.py        # Model evaluation
│   └── data/
│       ├── raw/                # Original data
│       └── processed/          # Transformed data
├── Dockerfile.backend          # Python image
├── Dockerfile.frontend         # Node image
├── docker-compose.yml          # Orchestration
├── nginx.conf                  # Reverse proxy
├── DOCKER_SETUP.md            # Docker guide
└── README.md                   # This file
```

## How It Works

### User Flow
```
1. User enters email text in UI
2. Selects ML model to use
3. Clicks "Analyze"
4. Frontend calls API: POST /analyze
5. Backend loads model from MLflow
6. Backend loads vectorizer for that model
7. Backend vectorizes text with TF-IDF
8. Backend runs prediction
9. Backend detects red flags
10. Backend calculates risk score (0-100)
11. Backend returns JSON response
12. Frontend displays gauge + results
13. User sees risk assessment
```

### API Request/Response

**Request:**
```json
POST /analyze
{
  "message": "Click here to confirm your account!",
  "model_name": "RandomForest_v1_tfidf_v1"
}
```

**Response:**
```json
{
  "label": "Phishing",
  "risk_score": 85.5,
  "confidence": 0.92,
  "explanation": "Urgent language + suspicious link + generic greeting",
  "red_flags": ["Urgent Language", "Suspicious Link", "Generic Greeting"]
}
```

## Commands

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop Services
```bash
docker-compose down
```

### Rebuild Images
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Access Container Shell
```bash
docker exec -it phishing_backend bash
docker exec -it phishing_frontend sh
```

### Test API
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Click here to verify your account",
    "model_name": "RandomForest_v1_tfidf_v1"
  }'
```

## Environment Variables

**In `docker-compose.yml`:**

Frontend:
```yaml
environment:
  - VITE_API_URL=http://localhost:8000
```

Backend:
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

## Troubleshooting

### Frontend shows "API Server not responding"
```bash
# Check if backend is running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Verify API is responding
curl http://localhost:8000/health
```

### Port already in use (Port 80)
```bash
# Find what's using port 80
lsof -i :80

# Or use different port in docker-compose.yml:
ports:
  - "3000:80"  # Access at localhost:3000
```

### Rebuild fails
```bash
# Clean everything and rebuild
docker-compose down -v
docker system prune -a --volumes
docker-compose build --no-cache
docker-compose up -d
```

### Models not loading
```bash
# Check if training_info.json exists
docker exec phishing_backend ls -la mlflow_artifacts/

# Check MLflow database
docker exec phishing_backend sqlite3 mlflow.db ".tables"
```

## Performance

| Operation | Time |
|-----------|------|
| Frontend build | 30-45s |
| Backend startup | 10-15s |
| API response | 50-200ms |
| Model prediction | 20-100ms |

## Security Notes

### Current Setup (Development)
- CORS enabled for all origins (`*`)
- API runs on localhost only
- SQLite database (not production-grade)
- No authentication required

### For Production
- [ ] Restrict CORS origins
- [ ] Add API authentication (JWT/OAuth)
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/SSL with Let's Encrypt
- [ ] Add rate limiting
- [ ] Hide error details in responses
- [ ] Use environment secrets management

## Next Steps

### Deploy to Cloud
- **AWS**: ECS + ECR + ALB
- **Google Cloud**: Cloud Run + Artifact Registry
- **Azure**: Container Instances + App Service
- **Heroku**: Container Registry (deprecated, use alternatives)

### Add Features
- [ ] User authentication
- [ ] Email attachment analysis
- [ ] Batch analysis (upload CSV)
- [ ] Model comparison dashboard
- [ ] Feedback loop for retraining
- [ ] Multi-language support
- [ ] Mobile app

### Production Checklist
- [ ] Configure HTTPS/SSL
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Add automated testing
- [ ] Configure monitoring (Prometheus, Grafana)
- [ ] Set up logging (ELK stack)
- [ ] Add API documentation (Swagger UI)
- [ ] Configure backup strategy
- [ ] Load testing & optimization

## Technology Stack

**Frontend**
- React 18
- Vite (build tool)
- Material-UI 5
- Axios (API calls)

**Backend**
- Python 3.11
- FastAPI
- Scikit-learn (ML models)
- MLflow (model tracking)
- Pandas, NumPy

**Infrastructure**
- Docker
- Nginx
- SQLite (with MLflow)

**MLOps**
- DVC (data versioning)
- DagsHub (experiment tracking)
- 15 trained models (5 × 3 TF-IDF variants)

## Model Performance

**Best Model**: NaiveBayes_v1_tfidf_v2
- Accuracy: 76%
- F1-Score: 0.82
- ROC-AUC: 0.85

**Available Models**:
```
RandomForest_v1_tfidf_v1    F1=0.75, ROC-AUC=0.81
RandomForest_v2_tfidf_v1    F1=0.74, ROC-AUC=0.80
LogisticRegression_v1_tfidf_v1  F1=0.76, ROC-AUC=0.83
LogisticRegression_v2_tfidf_v1  F1=0.75, ROC-AUC=0.82
NaiveBayes_v1_tfidf_v1      F1=0.76, ROC-AUC=0.84
[... and 10 more variants with tfidf_v2 & v3]
```

## Support & Documentation

- **Docker Setup**: See `DOCKER_SETUP.md`
- **API Documentation**: Visit http://localhost:8000/docs (Swagger UI)
- **MLflow Tracking**: Visit http://localhost:5000
- **Backend Code**: `backend/src/app.py`
- **Frontend Code**: `frontend/App.jsx`

## Contributing

To improve the system:
1. Train new models (update `backend/src/training.py`)
2. Test locally: `docker-compose up -d`
3. Evaluate results in MLflow UI
4. Update frontend if API changes
5. Test end-to-end

## License

MIT License - Feel free to use for research/commercial projects

---

**🚀 You're ready to go!**

```bash
docker-compose up -d
```

Open http://localhost and start detecting phishing! 🎯
