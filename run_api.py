"""
Run API with proper imports
"""

import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import and run the API
from api.app import app

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Starting Job Queue API Server")
    print("=" * 60)
    print(f"📍 API URL: http://localhost:5000/api")
    print(f"📊 Dashboard: http://localhost:5000")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)