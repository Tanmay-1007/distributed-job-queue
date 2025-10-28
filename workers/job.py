import json
import uuid
from datetime import datetime
from enum import Enum

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class Job:
    def __init__(self, task_name, task_data, priority=1, max_retries=3):
        self.id = str(uuid.uuid4())  # Unique job ID
        self.task_name = task_name
        self.task_data = task_data
        self.priority = priority
        self.max_retries = max_retries
        self.retry_count = 0
        self.status = JobStatus.PENDING.value
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
    
    def to_dict(self):
        """Convert job to dictionary for storage"""
        return {
            'id': self.id,
            'task_name': self.task_name,
            'task_data': self.task_data,
            'priority': self.priority,
            'max_retries': self.max_retries,
            'retry_count': self.retry_count,
            'status': self.status,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'result': self.result,
            'error': self.error
        }
    
    def to_json(self):
        """Convert job to JSON string"""
        return json.dumps(self.to_dict())
    
    @staticmethod
    def from_json(json_string):
        """Create job object from JSON string"""
        data = json.loads(json_string)
        job = Job(
            task_name=data['task_name'],
            task_data=data['task_data'],
            priority=data['priority'],
            max_retries=data['max_retries']
        )
        job.id = data['id']
        job.retry_count = data['retry_count']
        job.status = data['status']
        job.created_at = data['created_at']
        job.started_at = data['started_at']
        job.completed_at = data['completed_at']
        job.result = data['result']
        job.error = data['error']
        return job
    
    def __repr__(self):
        return f"Job(id={self.id}, task={self.task_name}, status={self.status})"