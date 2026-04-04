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

@app.post("/analyze")
async def analyze(data: dict):
    # Mock data for now
    text = data.get("text", "")
    return {
        "score": 0.85,
        "label": "High Risk",
        "red_flags": ["urgent", "bit.ly/fake-link"],
        "reason": "This message uses urgent language and a suspicious short-link."
    }