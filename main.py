import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import openai

# Загрузка переменных окружения
load_dotenv()

# Инициализация FastAPI
app = FastAPI()

# Настройка базы данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./complaints.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель для базы данных
class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    status = Column(String, default="open")
    timestamp = Column(DateTime, default=datetime.utcnow)
    sentiment = Column(String, default="unknown")
    category = Column(String, default="другое")

# Создание таблицы
Base.metadata.create_all(bind=engine)

# Модель для входящих данных
class ComplaintRequest(BaseModel):
    text: str

# Модель для ответа
class ComplaintResponse(BaseModel):
    id: int
    status: str
    sentiment: str
    category: Optional[str] = None

# Функция для анализа тональности
def analyze_sentiment(text: str) -> str:
    try:
        url = "https://api.apilayer.com/sentiment/analysis"
        headers = {"apikey": os.getenv("SENTIMENT_API_KEY")}
        response = requests.post(url, headers=headers, data=text.encode("utf-8"))
        response.raise_for_status()
        result = response.json()
        return result.get("sentiment", {}).get("type", "unknown").lower()
    except Exception:
        return "unknown"

# Функция для определения категории с помощью OpenAI
def determine_category(text: str) -> str:
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = f"""Определи категорию жалобы: "{text}". Варианты: техническая, оплата, другое. Ответ только одним словом."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        
        category = response.choices[0].message.content.strip().lower()
        if category not in ["техническая", "оплата"]:
            return "другое"
        return category
    except Exception:
        return "другое"

# API endpoint для создания жалобы
@app.post("/complaints/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(complaint: ComplaintRequest):
    db = SessionLocal()
    
    try:
        # Анализ тональности
        sentiment = analyze_sentiment(complaint.text)
        
        # Создание записи в базе данных
        db_complaint = Complaint(
            text=complaint.text,
            sentiment=sentiment,
            status="open"
        )
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        
        # Определение категории (асинхронно, чтобы не задерживать ответ)
        category = determine_category(complaint.text)
        db_complaint.category = category
        db.commit()
        db.refresh(db_complaint)
        
        return {
            "id": db_complaint.id,
            "status": db_complaint.status,
            "sentiment": db_complaint.sentiment,
            "category": db_complaint.category
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# API endpoint для получения списка открытых жалоб
@app.get("/complaints/open/")
async def get_open_complaints(hours: int = 1):
    db = SessionLocal()
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        complaints = db.query(Complaint).filter(
            Complaint.status == "open",
            Complaint.timestamp >= time_threshold
        ).all()
        
        return [
            {
                "id": c.id,
                "text": c.text,
                "status": c.status,
                "timestamp": c.timestamp.isoformat(),
                "sentiment": c.sentiment,
                "category": c.category
            }
            for c in complaints
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# API endpoint для обновления статуса жалобы
@app.patch("/complaints/{complaint_id}/")
async def update_complaint_status(complaint_id: int, status: str):
    if status not in ["open", "closed"]:
        raise HTTPException(status_code=400, detail="Status must be 'open' or 'closed'")
    
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        complaint.status = status
        db.commit()
        return {"message": "Status updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
