"""
Run worker process
"""

import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from workers.worker import Worker
import workers.tasks  # Import to register tasks

def main():
    print("\n" + "="*60)
    print("🚀 Starting Job Queue Worker")
    print("="*60)
    
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "worker-1"
    
    print(f"Worker ID: {worker_id}")
    print(f"Watching queues: high, default, low")
    print("="*60 + "\n")
    
    try:
        # Create and start worker
        worker = Worker(worker_id=worker_id)
        worker.start()
    except KeyboardInterrupt:
        print("\n⚠️ Shutting down worker...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise e

if __name__ == "__main__":
    main()