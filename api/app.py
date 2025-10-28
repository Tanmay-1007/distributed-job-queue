"""
REST API with WebSocket for real-time updates
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import sys
from api.app import app, socketio

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from workers.job import Job
from workers.queue_manager import QueueManager
from database.db_manager import DatabaseManager
import workers.tasks
from workers.task_registry import task_registry

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, 
                host='0.0.0.0', 
                port=port,
                allow_unsafe_werkzeug=True)  # Add this for production
    
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize managers
queue_manager = QueueManager()
db_manager = DatabaseManager()

# ============================================================
# WebSocket Events
# ============================================================

@socketio.on('connect')
def handle_connect():
    """Client connected to WebSocket"""
    print("✨ Client connected to WebSocket")
    # Send initial data
    emit_updates()

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected from WebSocket"""
    print("💔 Client disconnected from WebSocket")

def emit_updates():
    """Emit all updates to connected clients"""
    try:
        # Emit stats
        stats = db_manager.get_job_stats()
        socketio.emit('stats', {'stats': stats})

        # Emit queue status
        queues = {
            'high': queue_manager.get_queue_size('high'),
            'default': queue_manager.get_queue_size('default'),
            'low': queue_manager.get_queue_size('low')
        }
        socketio.emit('queues', {'queues': queues})

        # Emit recent jobs
        jobs = db_manager.get_all_jobs(limit=20)
        socketio.emit('jobs', {'jobs': jobs})
    except Exception as e:
        print(f"Error emitting updates: {e}")

# ============================================================
# Dashboard Routes
# ============================================================

@app.route('/')
def serve_dashboard():
    """Serve the dashboard HTML"""
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard')
    return send_from_directory(dashboard_path, 'index.html')

@app.route('/dashboard/<path:path>')
def serve_dashboard_files(path):
    """Serve dashboard static files"""
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard')
    return send_from_directory(dashboard_path, path)

# ============================================================
# API Info Routes
# ============================================================

@app.route('/api')
def api_info():
    """API information"""
    return jsonify({
        'message': 'Welcome to Job Queue API!',
        'status': 'running'
    })

# ============================================================
# Job Management Routes
# ============================================================

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs"""
    try:
        limit = int(request.args.get('limit', 100))
        jobs = db_manager.get_all_jobs(limit=limit)
        return jsonify({
            'success': True,
            'jobs': jobs
        })
    except Exception as e:
        print(f"Error getting jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new job"""
    try:
        data = request.get_json()
        job = Job(
            task_name=data['task_name'],
            task_data=data['task_data']
        )
        queue_name = data.get('queue', 'default')
        job_id = queue_manager.add_job(job, queue_name)
        
        # Emit updates to all clients
        emit_updates()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Job created!'
        })
    except Exception as e:
        print(f"Error creating job: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific job"""
    try:
        job = db_manager.get_job(job_id)
        if job:
            return jsonify({
                'success': True,
                'job': job
            })
        return jsonify({
            'success': False,
            'error': 'Job not found'
        }), 404
    except Exception as e:
        print(f"Error getting job: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/job-update', methods=['POST'])
def job_update():
    """Receive job updates from workers"""
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        status = data.get('status')
        
        if job_id and status:
            # Emit updates to all clients
            emit_updates()
            
            return jsonify({
                'success': True,
                'message': f'Job {job_id} status updated to {status}'
            })
    except Exception as e:
        print(f"Error handling job update: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================
# Queue Management Routes
# ============================================================

@app.route('/api/queues', methods=['GET'])
def get_queues():
    """Get queue status"""
    try:
        queues = {
            'high': queue_manager.get_queue_size('high'),
            'default': queue_manager.get_queue_size('default'),
            'low': queue_manager.get_queue_size('low')
        }
        return jsonify({
            'success': True,
            'queues': queues,
            'total': sum(queues.values())
        })
    except Exception as e:
        print(f"Error getting queue status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================
# Statistics Routes
# ============================================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get job statistics"""
    try:
        stats = db_manager.get_job_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================
# Task Management Routes
# ============================================================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get available tasks"""
    try:
        tasks = task_registry.list_tasks()
        return jsonify({
            'success': True,
            'tasks': tasks
        })
    except Exception as e:
        print(f"Error getting tasks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 'Not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 Starting Job Queue API Server with WebSocket")
    print("=" * 60)
    print(f"📍 API URL: http://localhost:5000/api")
    print(f"📊 Dashboard: http://localhost:5000")
    print(f"🔌 WebSocket: ws://localhost:5000")
    print("=" * 60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)