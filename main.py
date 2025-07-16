from fastapi import FastAPI, HTTPException
import requests
import database
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()
database.init_db()

# Конфигурация API
SENTIMENT_API_URL = "https://api.apilayer.com/sentiment/analysis"
SENTIMENT_API_KEY = "8268c34838adaad2ac6cfe0f83baac33"  # Замените на реальный ключ

class Complaint(BaseModel):
    text: str

def analyze_sentiment(text: str):
    try:
        headers = {"apikey": SENTIMENT_API_KEY}
        response = requests.post(SENTIMENT_API_URL, headers=headers, data=text.encode('utf-8'))
        response.raise_for_status()
        return response.json().get("sentiment", "unknown").lower()
    except:
        return "unknown"

def categorize_complaint(text: str):
    text_lower = text.lower()
    if any(word in text_lower for word in ["sms", "код", "приложение", "техни"]):
        return "техническая"
    elif any(word in text_lower for word in ["оплат", "деньг", "счет", "цена"]):
        return "оплата"
    return "другое"

@app.post("/complaints/")
async def create_complaint(complaint: Complaint):
    try:
        sentiment = analyze_sentiment(complaint.text)
        category = categorize_complaint(complaint.text)
        
        complaint_id = database.save_complaint(
            text=complaint.text,
            sentiment=sentiment,
            category=category
        )
        
        return {
            "id": complaint_id,
            "status": "open",
            "sentiment": sentiment,
            "category": category
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/complaints/{complaint_id}")
async def read_complaint(complaint_id: int):
    complaint = database.get_complaint(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint
