from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    status = Column(String, default="open")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sentiment = Column(String)
    category = Column(String, default="другое")
