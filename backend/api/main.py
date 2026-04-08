from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# VERY IMPORTANT: This allows his UI to talk to your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/models")
async def get_models():
    # Mock models for now
    return {"models": ["RandomForest_v1_tfidf_v1", "LogisticRegression_v1_tfidf_v1", "NaiveBayes_v1_tfidf_v1"]}

@app.post("/analyze")
async def analyze(data: dict):
    # Mock data for now
    message = data.get("message", "")
    model_name = data.get("model_name", "")
    
    # Mock prediction
    risk_score = 75.0  # Mock score
    label = "Phishing" if risk_score > 50 else "Legitimate"
    explanation = f"Analysis by {model_name}: This message shows suspicious patterns."
    red_flags = ["urgent language", "suspicious link"] if risk_score > 50 else []
    
    return {
        "risk_score": risk_score,
        "label": label,
        "explanation": explanation,
        "red_flags": red_flags
    }