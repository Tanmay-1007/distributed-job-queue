"""
Database models for job persistence
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class JobModel(Base):
    """Database model for jobs"""
    __tablename__ = 'jobs'
    
    id = Column(String(36), primary_key=True)  # UUID
    task_name = Column(String(100), nullable=False)
    task_data = Column(Text, nullable=False)  # JSON string
    priority = Column(Integer, default=1)
    max_retries = Column(Integer, default=3)
    retry_count = Column(Integer, default=0)
    status = Column(String(20), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    result = Column(Text, nullable=True)  # JSON string
    error = Column(Text, nullable=True)
    
    # Performance metrics
    execution_time = Column(Float, nullable=True)  # in seconds
    worker_id = Column(String(50), nullable=True)
    queue_name = Column(String(50), default='default')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'task_name': self.task_name,
            'task_data': json.loads(self.task_data) if self.task_data else {},
            'priority': self.priority,
            'max_retries': self.max_retries,
            'retry_count': self.retry_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': json.loads(self.result) if self.result else None,
            'error': self.error,
            'execution_time': self.execution_time,
            'worker_id': self.worker_id,
            'queue_name': self.queue_name
        }
    
    def __repr__(self):
        return f"<Job(id={self.id}, task={self.task_name}, status={self.status})>"