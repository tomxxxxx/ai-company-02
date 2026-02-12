from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=False)
    channel_id = Column(String(50), nullable=False)
    channel_name = Column(String(100), nullable=True)
    user_id = Column(String(50), nullable=False)
    user_name = Column(String(100), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Task(id={self.id}, description='{self.description[:30]}...', completed={self.completed})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def mark_complete(self):
        self.completed = True
        self.completed_at = datetime.utcnow()