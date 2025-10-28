"""
Database Manager - Handles all database operations
"""

from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker
from database.models import Base, JobModel
from workers.job import Job
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_url='sqlite:///jobs.db'):
        """Initialize database connection"""
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        print(f"✅ Database initialized: {db_url}")
    
    def save_job(self, job, queue_name='default', worker_id=None):
        """Save or update a job in database"""
        session = self.Session()
        try:
            # Check if job already exists
            job_model = session.query(JobModel).filter_by(id=job.id).first()
            
            if job_model:
                # Update existing job
                job_model.status = job.status
                job_model.retry_count = job.retry_count
                job_model.started_at = datetime.fromisoformat(job.started_at) if job.started_at else None
                job_model.completed_at = datetime.fromisoformat(job.completed_at) if job.completed_at else None
                job_model.result = json.dumps(job.result) if job.result else None
                job_model.error = job.error
                job_model.worker_id = worker_id
                
                # Calculate execution time
                if job_model.started_at and job_model.completed_at:
                    delta = job_model.completed_at - job_model.started_at
                    job_model.execution_time = delta.total_seconds()
            else:
                # Create new job
                job_model = JobModel(
                    id=job.id,
                    task_name=job.task_name,
                    task_data=json.dumps(job.task_data),
                    priority=job.priority,
                    max_retries=job.max_retries,
                    retry_count=job.retry_count,
                    status=job.status,
                    created_at=datetime.fromisoformat(job.created_at),
                    queue_name=queue_name,
                    worker_id=worker_id
                )
                session.add(job_model)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving job to database: {e}")
            return False
        finally:
            session.close()
    
    def get_job(self, job_id):
        """Get job by ID"""
        session = self.Session()
        try:
            job_model = session.query(JobModel).filter_by(id=job_id).first()
            return job_model.to_dict() if job_model else None
        finally:
            session.close()
    
    def get_all_jobs(self, limit=100):
        """Get all jobs"""
        session = self.Session()
        try:
            jobs = session.query(JobModel).order_by(desc(JobModel.created_at)).limit(limit).all()
            return [job.to_dict() for job in jobs]
        finally:
            session.close()
    
    def get_jobs_by_status(self, status, limit=100):
        """Get jobs by status"""
        session = self.Session()
        try:
            jobs = session.query(JobModel).filter_by(status=status).order_by(desc(JobModel.created_at)).limit(limit).all()
            return [job.to_dict() for job in jobs]
        finally:
            session.close()
    
    def get_job_stats(self):
        """Get job statistics"""
        session = self.Session()
        try:
            total_jobs = session.query(JobModel).count()
            pending_jobs = session.query(JobModel).filter_by(status='pending').count()
            processing_jobs = session.query(JobModel).filter_by(status='processing').count()
            completed_jobs = session.query(JobModel).filter_by(status='completed').count()
            failed_jobs = session.query(JobModel).filter_by(status='failed').count()
            
            # Average execution time
            avg_time = session.query(func.avg(JobModel.execution_time)).filter(
                JobModel.execution_time.isnot(None)
            ).scalar()
            
            return {
                'total': total_jobs,
                'pending': pending_jobs,
                'processing': processing_jobs,
                'completed': completed_jobs,
                'failed': failed_jobs,
                'avg_execution_time': round(avg_time, 2) if avg_time else 0
            }
        finally:
            session.close()
    
    def get_jobs_by_task(self, task_name, limit=50):
        """Get jobs by task name"""
        session = self.Session()
        try:
            jobs = session.query(JobModel).filter_by(task_name=task_name).order_by(desc(JobModel.created_at)).limit(limit).all()
            return [job.to_dict() for job in jobs]
        finally:
            session.close()
    
    def delete_job(self, job_id):
        """Delete a job"""
        session = self.Session()
        try:
            job = session.query(JobModel).filter_by(id=job_id).first()
            if job:
                session.delete(job)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ Error deleting job: {e}")
            return False
        finally:
            session.close()
    
    def clear_old_jobs(self, days=30):
        """Delete jobs older than specified days"""
        session = self.Session()
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted = session.query(JobModel).filter(
                JobModel.created_at < cutoff_date,
                JobModel.status.in_(['completed', 'failed'])
            ).delete()
            
            session.commit()
            print(f"🗑️  Deleted {deleted} old jobs")
            return deleted
        except Exception as e:
            session.rollback()
            print(f"❌ Error clearing old jobs: {e}")
            return 0
        finally:
            session.close()