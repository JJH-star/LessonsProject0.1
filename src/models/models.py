from sqlalchemy import Column, Integer, String, JSON, DateTime, LargeBinary, MetaData, ForeignKey
from datetime import datetime

from sqlalchemy.orm import relationship

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

    # Внешний ключ для связи с темой
    topic_id = Column(Integer, ForeignKey("topic.id"))

    # Связь "много к одному" с темой
    topic = relationship("Topic", back_populates="tasks")

class Topic(Base):
    __tablename__ = "topic"
    id = Column(Integer, primary_key=True, index=True)
    class_num = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(LargeBinary, nullable=False)
    # Связь "один ко многим" с задачами
    tasks = relationship("Task", back_populates="topic")