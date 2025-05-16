from fastapi import FastAPI, Request
from pydantic import BaseModel
from sentiment_utils import load_finbert_pipeline, load_multilang_pipeline, calculate_sentiment

app = FastAPI()

# Preload models at startup
@app.on_event("startup")
def load_models():
    app.state.finbert = load_finbert_pipeline()
    app.state.multilang = load_multilang_pipeline()

class SentimentRequest(BaseModel):
    title: str
    description: str
    language: str = None  # Optional

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}

@app.post("/analyze")
def analyze_sentiment(req: SentimentRequest, request: Request):
    result = calculate_sentiment(
        req.title,
        req.description,
        req.language,
        request.app.state.finbert,
        request.app.state.multilang
    )
    return result
