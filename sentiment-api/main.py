from fastapi import FastAPI, Request
from pydantic import BaseModel
from sentiment_utils import calculate_sentiment

app = FastAPI()

class SentimentRequest(BaseModel):
    title: str
    description: str
    language: str = None  # Optional

@app.post("/analyze")
def analyze_sentiment(req: SentimentRequest):
    result = calculate_sentiment(req.title, req.description, req.language)
    return result
