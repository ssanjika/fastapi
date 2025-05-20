import re
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
# Fix cache issue
# Optionally set cache directory via environment variable
import os
os.environ["HF_HOME"] = "~/.cache/huggingface" 

try:
  

 # Or another writable path

    # Load FinBERT with explicit cache directory
    cache_dir = "./finbert_cache"  # Local directory for caching
    finbert_model = AutoModelForSequenceClassification.from_pretrained(
        "yiyanghkust/finbert-tone",
        cache_dir=cache_dir
    )

    finbert_tokenizer = AutoTokenizer.from_pretrained(
        "yiyanghkust/finbert-tone",
        cache_dir=cache_dir
    )

    finbert_pipeline = pipeline(
        "sentiment-analysis",
        model=finbert_model,
        tokenizer=finbert_tokenizer,
        device=0 if torch.cuda.is_available() else -1
    )

    
    # Load multilingual model
    multilang_model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
    multilang_tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
    multilang_pipeline = pipeline(
        "sentiment-analysis",
        model=multilang_model,
        tokenizer=multilang_tokenizer,
        device=0 if torch.cuda.is_available() else -1
    )
    
    print("Successfully loaded sentiment analysis models")
except Exception as e:
    print(f"Failed to load models: {str(e)}")
    raise

def detect_language(text):
    """Detect language and return ISO code: 'en' or 'af'."""
    if not text:
        return 'en'
    
    text = text.lower()
    
    # Afrikaans word markers
    af_words = {'die', 'en', 'vir', 'van', 'nie', 'jy', 'ek', 'ons'}
    if any(word in text.split() for word in af_words):
        return 'af'
    
    return 'en'  # Default to English



def preprocess_text(text, language):
    """More conservative preprocessing"""
    if not text:
        return ""
    
    # Preserve key punctuation that might indicate sentiment
    text = re.sub(r"[^a-zA-Z0-9\s\$\%,\.!?]", "", text)
    text = text.lower()
    
    # Keep all words for sentiment analysis
    return text

def calculate_sentiment(title, description, language=None):
    """Robust sentiment analysis with proper error reporting"""
    combined_text = f"{title}. {description}".strip()
    
    if not combined_text or len(combined_text.split()) < 3:
        return {'label': 'neutral', 'score': 0, 'note': 'insufficient text'}
    
   
    language = (language or detect_language(combined_text)).lower().strip()
    if language == 'english':
        language = 'en'
    elif language == 'afrikaans':
        language = 'af'

    
    try:
        # Preprocess while preserving sentiment indicators
        text = preprocess_text(combined_text, language)
        print(f"Analyzing text ({language}): {text[:200]}...")
        
        if language == 'en':
            # Ensure FinBERT is working
            result = finbert_pipeline(text[:512], truncation=True)[0]  # Truncate to model max length
            print(f"FinBERT raw result: {result}")
            
            # Map to our expected format
            label = result['label'].lower()
            score = result['score']
            
            return {
                'label': label,
                'score': score,
                'positive': score if label == 'positive' else 0,
                'neutral': score if label == 'neutral' else 0,
                'negative': score if label == 'negative' else 0
            }
            
        elif language == 'af':
            # Use multilingual model for Afrikaans
            result = multilang_pipeline(text[:512], truncation=True)[0]
            print(f"Multilingual raw result: {result}")
            
            # Map 5-star rating to sentiment
            stars = int(result['label'].split()[0])
            if stars >= 4:
                label = 'positive'
            elif stars <= 2:
                label = 'negative'
            else:
                label = 'neutral'
                
            return {
                'label': label,
                'score': result['score'],
                'positive': result['score'] if label == 'positive' else 0,
                'neutral': result['score'] if label == 'neutral' else 0,
                'negative': result['score'] if label == 'negative' else 0
            }
            
        else:
            return {'label': 'neutral', 'score': 0, 'note': f'unsupported language: {language}'}
            
    except Exception as e:
        print(f"Sentiment analysis error: {str(e)}")
        return {'label': 'neutral', 'score': 0, 'error': str(e)}
