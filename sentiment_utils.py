import re
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer



def load_finbert_pipeline():
    # Smaller general sentiment model instead of ProsusAI/finbert
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

def load_multilang_pipeline():
    # Smaller multilingual distilled model instead of nlptown/bert-base-multilingual-uncased-sentiment
    model_name = "distilbert-base-multilingual-cased"
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


def detect_language(text):
    if not text:
        return 'en'
    text = text.lower()
    af_words = {'die', 'en', 'vir', 'van', 'nie', 'jy', 'ek', 'ons'}
    if any(word in text.split() for word in af_words):
        return 'af'
    return 'en'

def preprocess_text(text, language):
    if not text:
        return ""
    text = re.sub(r"[^a-zA-Z0-9\s\$\%,\.!?]", "", text)
    return text.lower()

def calculate_sentiment(title, description, language=None):
    combined_text = f"{title}. {description}".strip()
    if not combined_text or len(combined_text.split()) < 3:
        return {'label': 'neutral', 'score': 0, 'note': 'insufficient text'}

    language = (language or detect_language(combined_text)).lower().strip()
    if language == 'english': language = 'en'
    elif language == 'afrikaans': language = 'af'

    try:
        text = preprocess_text(combined_text, language)
        if language == 'en':
            pipe = load_finbert_pipeline()
            result = pipe(text[:512], truncation=True)[0]
            label = result['label'].lower()
            score = result['score']
        elif language == 'af':
            pipe = load_multilang_pipeline()
            result = pipe(text[:512], truncation=True)[0]
            stars = int(result['label'].split()[0])
            if stars >= 4:
                label = 'positive'
            elif stars <= 2:
                label = 'negative'
            else:
                label = 'neutral'
            score = result['score']
        else:
            return {'label': 'neutral', 'score': 0, 'note': f'unsupported language: {language}'}

        return {
            'label': label,
            'score': score,
            'positive': score if label == 'positive' else 0,
            'neutral': score if label == 'neutral' else 0,
            'negative': score if label == 'negative' else 0
        }
    except Exception as e:
        return {'label': 'neutral', 'score': 0, 'error': str(e)}
