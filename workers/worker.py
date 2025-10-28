"""
Worker for processing jobs
"""

import time
import signal
import sys
from datetime import datetime
import requests

# Local imports
from workers.queue_manager import QueueManager
from workers.job import Job, JobStatus
from workers.task_registry import task_registry

class Worker:
    def __init__(self, worker_id, queues=['high', 'default', 'low']):
        self.worker_id = worker_id
        self.queues = queues
        self.queue_manager = QueueManager()
        self.is_running = False
        
        # Add API URL for notifications
        self.api_url = "http://localhost:5000/api"
        
        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        print(f"\n🛑 Worker {self.worker_id} shutting down...")
        self.is_running = False
        sys.exit(0)

    def notify_job_update(self, job_id, status):
        """Notify API about job status change"""
        try:
            response = requests.post(f"{self.api_url}/job-update", json={
                'job_id': job_id,
                'status': status
            })
            if not response.ok:
                print(f"Failed to notify job update: {response.text}")
        except Exception as e:
            print(f"Failed to notify job update: {e}")

    def process_job(self, job):
        """Process a single job"""
        print(f"\n{'='*60}")
        print(f"🔧 Worker {self.worker_id} processing job: {job.id}")
        print(f"   Task: {job.task_name}")
        print(f"   Data: {job.task_data}")
        print(f"{'='*60}")
        
        # Update job status to processing
        job.status = JobStatus.PROCESSING.value
        job.started_at = datetime.now().isoformat()
        self.queue_manager.update_job(job, worker_id=self.worker_id)
        self.notify_job_update(job.id, 'processing')  # Add this
        
        try:
            # Get task function
            task_func = task_registry.get_task(job.task_name)
            if not task_func:
                raise Exception(f"Task '{job.task_name}' not found")
            
            # Execute task
            result = task_func(job.task_data)
            
            # Update job as completed
            job.status = JobStatus.COMPLETED.value
            job.completed_at = datetime.now().isoformat()
            job.result = result
            self.queue_manager.update_job(job, worker_id=self.worker_id)
            self.notify_job_update(job.id, 'completed')  # Add this
            
            print(f"✅ Job {job.id} completed successfully")
            print(f"   Result: {result}")
            
        except Exception as e:
            print(f"❌ Job {job.id} failed: {str(e)}")
            
            job.retry_count += 1
            job.error = str(e)
            
            if job.retry_count < job.max_retries:
                job.status = JobStatus.RETRYING.value
                self.queue_manager.update_job(job, worker_id=self.worker_id)
                self.notify_job_update(job.id, 'retrying')  # Add this
                
                # Re-add to queue
                self.queue_manager.add_job(job, 'default')
                print(f"🔄 Job {job.id} will be retried (attempt {job.retry_count}/{job.max_retries})")
            else:
                job.status = JobStatus.FAILED.value
                job.completed_at = datetime.now().isoformat()
                self.queue_manager.update_job(job, worker_id=self.worker_id)
                self.notify_job_update(job.id, 'failed')  # Add this
                print(f"💀 Job {job.id} failed permanently after {job.retry_count} attempts")

    def get_next_job(self):
        """Get next job from queues based on priority"""
        for queue_name in self.queues:
            job = self.queue_manager.get_next_job(queue_name)
            if job:
                return job
        return None

    def start(self, poll_interval=2):
        """Start the worker"""
        self.is_running = True
        
        print(f"\n{'='*60}")
        print(f"🚀 Worker {self.worker_id} started")
        print(f"   Watching queues: {self.queues}")
        print(f"   Poll interval: {poll_interval}s")
        print(f"{'='*60}\n")
        
        while self.is_running:
            try:
                # Try to get next job
                job = self.get_next_job()
                
                if job:
                    self.process_job(job)
                else:
                    # No jobs available, wait before checking again
                    print(f"💤 No jobs available. Waiting {poll_interval}s...")
                    time.sleep(poll_interval)
            except KeyboardInterrupt:
                self.shutdown()
            except Exception as e:
                print(f"❌ Error processing job: {e}")
                time.sleep(poll_interval)

    def start_once(self):
        """Process one job and exit (useful for testing)"""
        print(f"\n🚀 Worker {self.worker_id} checking for one job...")
        
        job = self.get_next_job()
        if job:
            self.process_job(job)
            return True
        else:
            print("💤 No jobs available")
            return False