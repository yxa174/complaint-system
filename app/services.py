import requests
import openai
from .config import settings

def analyze_sentiment(text: str) -> str:
    url = "https://api.apilayer.com/sentiment/analysis"
    headers = {"apikey": settings.sentiment_api_key}
    response = requests.post(url, headers=headers, json={"text": text})
    response.raise_for_status()
    data = response.json()
    return data.get("sentiment", "unknown").lower()

def determine_category(text: str) -> str:
    openai.api_key = settings.openai_api_key
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Определи категорию жалобы. Варианты: техническая, оплата, другое. Ответ только одним словом."},
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    
    category = response.choices[0].message.content.lower()
    if category not in ["техническая", "оплата"]:
        category = "другое"
        
    return category
