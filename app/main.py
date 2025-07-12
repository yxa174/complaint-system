from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, schemas, services
from .database import SessionLocal, engine
from .config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/complaints/", response_model=schemas.ComplaintResponse)
async def create_complaint(complaint: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    try:
        sentiment = services.analyze_sentiment(complaint.text)
    except Exception as e:
        sentiment = "unknown"
        
    db_complaint = models.Complaint(
        text=complaint.text,
        sentiment=sentiment
    )
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    
    try:
        category = services.determine_category(complaint.text)
        db_complaint.category = category
        db.commit()
        db.refresh(db_complaint)
    except Exception as e:
        pass
    
    return db_complaint
