# 🐳 Docker Setup Guide

## Architecture

```
┌─────────────────────────────────────┐
│     React Frontend (Vite)           │
│   Material-UI Beautiful UI          │
│     Port: 80 (Nginx)                │
└─────────────┬───────────────────────┘
              │
       ┌──────▼──────┐
       │    Nginx    │
       │  Reverse    │
       │   Proxy     │
       └──────┬──────┘
              │
┌─────────────▼───────────────────────┐
│    FastAPI Backend (Python)         │
│   ML Model + MLflow Tracking        │
│     Port: 8000                      │
└─────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐      ┌──────▼────┐
│ MLflow │      │  SQLite   │
│   UI   │      │  Database │
│ :5000  │      │ (mlflow)  │
└────────┘      └───────────┘
```

## Prerequisites

- **Docker** (20.10+): https://docs.docker.com/get-docker/
- **Docker Compose** (2.0+): https://docs.docker.com/compose/install/
- Ports available: 80 (frontend), 8000 (API), 5000 (MLflow UI)

## Quick Start

### 1. Build Images

```bash
# Build both frontend and backend images
docker-compose build
```

**What it does:**
- Builds Python 3.11 image for FastAPI backend with all dependencies
- Builds Node.js 18 image for React + Vite, compiles to static files
- Creates Nginx image with reverse proxy configuration
- Creates MLflow UI image for monitoring

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services started:**
- **Frontend**: http://localhost (Nginx on port 80)
- **Backend API**: http://localhost:8000 (FastAPI)
- **MLflow UI**: http://localhost:5000 (Model tracking)

### 3. Verify Everything Works

```bash
# Check service status
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check frontend
curl http://localhost/health
```

## Directory Structure

```
ai-fraud-detector/
├── frontend/                    # React + Vite app
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── App.jsx                 # Main React component
│   └── main.jsx                # React entry point
├── backend/
│   └── src/
│       ├── app.py              # FastAPI app
│       ├── training.py         # Model training
│       └── evaluation.py        # Model evaluation
├── Dockerfile.backend          # Python FastAPI image
├── Dockerfile.frontend         # Node + React image
├── nginx.conf                  # Nginx reverse proxy
├── docker-compose.yml          # Orchestration
└── .dockerignore              # Ignore files in Docker build
```

## Configuration

### Environment Variables

**Frontend (.env):**
```
VITE_API_URL=http://localhost:8000
```

**Backend (.env):**
```
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

Edit in `docker-compose.yml` environment section.

### Ports

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 80 | Nginx (React UI) |
| Backend API | 8000 | FastAPI |
| MLflow UI | 5000 | Model tracking |

To change ports, edit `docker-compose.yml` ports section.

## Development Mode

### Hot Reload Frontend

Backend has hot reload enabled (`--reload` flag in docker-compose.yml).

To enable frontend hot reload:
```bash
# Run outside Docker for faster development
cd frontend
npm install
npm run dev
```

### Access Development Services

- Frontend (dev): http://localhost:5173
- Backend (dev): http://localhost:8000
- MLflow: http://localhost:5000

## Production Deployment

### Build for Production

```bash
# Build with production settings
docker-compose build --no-cache

# Start with production config
docker-compose up -d
```

### Security Checklist

- [ ] Change Nginx conf to disable server info header
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS with Let's Encrypt
- [ ] Add authentication to MLflow UI
- [ ] Set resource limits in docker-compose.yml

Add to service in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

## Troubleshooting

### Frontend not connecting to API

```bash
# Check if backend is running
docker-compose logs backend

# Verify API response
curl http://localhost:8000/health

# Check Nginx proxy config
docker exec phishing_frontend cat /etc/nginx/nginx.conf
```

### Database permission errors

```bash
# Fix permissions
docker exec phishing_backend chmod -R 777 /app/mlflow_artifacts
```

### Port already in use

```bash
# Find process using port
lsof -i :80
lsof -i :8000

# Kill process (on port 8000)
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Build fails

```bash
# Clean and rebuild
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Resource Usage

```bash
# CPU and memory
docker stats

# Container details
docker inspect phishing_backend
```

### Health Status

```bash
# Check health
docker-compose ps

# Detailed health
docker exec phishing_backend curl http://localhost:8000/health
docker exec phishing_frontend wget -O- http://localhost/health
```

## Data Persistence

All data is stored in volumes:
- `mlruns/`: MLflow run data
- `mlflow_artifacts/`: Model artifacts
- `backend/data/`: Raw and processed data

Delete volumes to reset:
```bash
docker-compose down -v
```

## API Integration

Frontend calls:
```
http://localhost/api/analyze
http://localhost/api/models
http://localhost/api/health
```

Nginx forwards to backend:
```
http://backend:8000/analyze
http://backend:8000/models
http://backend:8000/health
```

## Performance Tips

1. **Build locally first**: Test `npm run build` and `python -m pytest` before containerizing
2. **Use .dockerignore**: Reduces build context size
3. **Multi-stage builds**: Frontend uses builder stage (already optimized)
4. **Volume mounts**: Use for development, bind mounts for production
5. **Resource limits**: Set in docker-compose.yml to prevent runaway containers

## Common Commands

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Execute command in container
docker exec phishing_backend python -c "import sys; print(sys.version)"

# Access container shell
docker exec -it phishing_backend bash

# Remove all data and start fresh
docker-compose down -v && docker-compose up -d

# Test API
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":"test message", "model_name":"RandomForest_v1_tfidf_v1"}'
```

## Next Steps

1. ✅ Built React + Material-UI frontend
2. ✅ Created Docker setup with docker-compose
3. ✅ Configured Nginx reverse proxy
4. ✅ Added MLflow UI for monitoring
5. **TO DO**: 
   - Deploy to cloud (AWS, GCP, Azure)
   - Add authentication
   - Set up CI/CD pipeline
   - Configure HTTPS/SSL

## Support

- **Docker Issues**: https://docs.docker.com/config/containers/logging/
- **Frontend Issues**: Check `docker logs phishing_frontend`
- **Backend Issues**: Check `docker logs phishing_backend`
- **API Issues**: Test with `curl http://localhost:8000/health`

---

**You're ready to go!** 🚀

Run: `docker-compose up -d`

Then open: http://localhost
