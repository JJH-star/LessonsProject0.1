from sqlalchemy import Column, Integer, String, JSON, DateTime, LargeBinary, MetaData
from datetime import datetime
from src.database import Base

metadata = Base.metadata

class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True)
    class_num = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    original_text = Column(LargeBinary, nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)