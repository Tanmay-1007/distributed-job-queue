import os
import sys

# Add your project directory to Python path
path = '/home/YOUR_PYTHONANYWHERE_USERNAME/distributed-job-queue'
if path not in sys.path:
    sys.path.append(path)

from api.app import app as application

# Debug info
print("Python path:", sys.path)
print("Working directory:", os.getcwd())