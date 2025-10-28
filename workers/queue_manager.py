import redis
from config import Config
from workers.job import Job, JobStatus
from database.db_manager import DatabaseManager

class QueueManager:
    def __init__(self):
        # Connect to Redis
        self.redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            decode_responses=True
        )
        
        # Connect to Database
        self.db = DatabaseManager()
        
        # Queue names based on priority
        self.queues = {
            'high': 'queue:high_priority',
            'default': 'queue:default',
            'low': 'queue:low_priority'
        }
        
        # Job storage (hash map in Redis)
        self.jobs_key = 'jobs'
    
    def add_job(self, job, queue_name='default'):
        """Add a job to the queue"""
        try:
            # Store job details in Redis hash
            self.redis_client.hset(
                self.jobs_key, 
                job.id, 
                job.to_json()
            )
            
            # Add job ID to the appropriate queue (list)
            queue_key = self.queues.get(queue_name, self.queues['default'])
            self.redis_client.rpush(queue_key, job.id)
            
            # Save to database
            self.db.save_job(job, queue_name)
            
            print(f"✅ Job {job.id} added to {queue_name} queue")
            return job.id
            
        except Exception as e:
            print(f"❌ Error adding job: {e}")
            return None
    
    def get_job(self, job_id):
        """Retrieve job details by ID"""
        job_json = self.redis_client.hget(self.jobs_key, job_id)
        if job_json:
            return Job.from_json(job_json)
        return None
    
    def update_job(self, job, worker_id=None):
        """Update job details in Redis and Database"""
        # Update Redis
        self.redis_client.hset(
            self.jobs_key,
            job.id,
            job.to_json()
        )
        
        # Update Database
        self.db.save_job(job, worker_id=worker_id)
    
    def get_next_job(self, queue_name='default'):
        """Get the next job from queue (FIFO)"""
        queue_key = self.queues.get(queue_name, self.queues['default'])
        
        # Pop job ID from left (FIFO - First In First Out)
        job_id = self.redis_client.lpop(queue_key)
        
        if job_id:
            return self.get_job(job_id)
        return None
    
    def get_queue_size(self, queue_name='default'):
        """Get number of jobs in queue"""
        queue_key = self.queues.get(queue_name, self.queues['default'])
        return self.redis_client.llen(queue_key)
    
    def get_all_jobs(self):
        """Get all jobs (for monitoring)"""
        job_ids = self.redis_client.hkeys(self.jobs_key)
        jobs = []
        for job_id in job_ids:
            job = self.get_job(job_id)
            if job:
                jobs.append(job)
        return jobs
    
    def get_job_stats(self):
        """Get job statistics from database"""
        return self.db.get_job_stats()
    
    def clear_queue(self, queue_name='default'):
        """Clear all jobs from a queue (for testing)"""
        queue_key = self.queues.get(queue_name, self.queues['default'])
        self.redis_client.delete(queue_key)
        print(f"🗑️  Cleared {queue_name} queue")
    
    def clear_all(self):
        """Clear everything (for testing)"""
        for queue in self.queues.values():
            self.redis_client.delete(queue)
        self.redis_client.delete(self.jobs_key)
        print("🗑️  Cleared all queues and jobs")