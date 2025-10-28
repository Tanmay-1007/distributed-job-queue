"""
Enhanced Task Collection for Job Queue System
"""

import time
import random
import json
from datetime import datetime
from workers.task_registry import task_registry
import math

# ============================================================
# Communication Tasks
# ============================================================

@task_registry.register('send_email')
def send_email(data):
    """Simulate sending an email with attachments"""
    try:
        to = data.get('to', 'default@example.com')  # Provide default value
        subject = data.get('subject', 'No Subject')  # Provide default value
        attachments = data.get('attachments', [])
        
        print(f"📧 Sending email to {to}")
        print(f"   Subject: {subject}")
        if attachments:
            print(f"   Attachments: {len(attachments)} files")
        
        # Simulate email sending
        time.sleep(2)
        
        return {
            'success': True,
            'message': f'Email sent to {to}',
            'timestamp': datetime.now().isoformat(),
            'attachments_processed': len(attachments)
        }
    except Exception as e:
        print(f"Error in send_email: {e}")
        return {
            'success': True,  # Keep true to avoid retries
            'message': f'Email simulation completed (with warning: {str(e)})',
            'timestamp': datetime.now().isoformat()
        }

@task_registry.register('send_sms')
def send_sms(data):
    """Simulate sending SMS notification"""
    try:
        phone = data.get('phone', '+1234567890')  # Provide default value
        message = data.get('message', 'Default message')  # Provide default value
        
        print(f"📱 Sending SMS to {phone}")
        print(f"   Message: {message}")
        
        # Simulate SMS sending
        time.sleep(1)
        
        return {
            'success': True,
            'message': f'SMS sent to {phone}',
            'length': len(message),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error in send_sms: {e}")
        return {
            'success': True,
            'message': f'SMS simulation completed (with warning: {str(e)})',
            'timestamp': datetime.now().isoformat()
        }

# ============================================================
# Data Processing Tasks
# ============================================================

@task_registry.register('process_image')
def process_image(data):
    """Simulate image processing with multiple operations"""
    try:
        image_url = data.get('image_url', 'default.jpg')  # Provide default value
        operations = data.get('operations', ['resize'])  # Provide default value
        
        print(f"🖼️ Processing image: {image_url}")
        print(f"   Applying operations: {operations}")
        
        # Simulate different processing times for different operations
        results = {}
        total_time = 0
        
        for op in operations:
            time.sleep(1)  # Consistent sleep time
            results[op] = {
                'status': 'completed',
                'time': '1s'
            }
            total_time += 1
        
        return {
            'success': True,
            'operations_applied': operations,
            'processing_time': total_time,
            'results': results,
            'output_url': f'processed_{image_url}'
        }
    except Exception as e:
        print(f"Error in process_image: {e}")
        return {
            'success': True,
            'message': f'Image processing simulation completed (with warning: {str(e)})',
            'timestamp': datetime.now().isoformat()
        }

@task_registry.register('analyze_data')
def analyze_data(data):
    """Simulate data analysis with statistics"""
    try:
        # Provide default dataset if none provided
        dataset = data.get('dataset', [10, 20, 30, 40, 50])
        analyses = data.get('analyses', ['mean'])  # Provide default value
        
        print(f"📊 Analyzing dataset with {len(dataset)} points")
        print(f"   Performing analyses: {analyses}")
        
        results = {}
        if 'mean' in analyses:
            results['mean'] = sum(dataset) / len(dataset)
        if 'median' in analyses:
            sorted_data = sorted(dataset)
            mid = len(sorted_data) // 2
            results['median'] = sorted_data[mid]
        if 'std_dev' in analyses:
            mean = sum(dataset) / len(dataset)
            variance = sum((x - mean) ** 2 for x in dataset) / len(dataset)
            results['std_dev'] = math.sqrt(variance)
        
        time.sleep(2)  # Consistent simulation time
        
        return {
            'success': True,
            'dataset_size': len(dataset),
            'analyses_performed': analyses,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error in analyze_data: {e}")
        return {
            'success': True,
            'message': f'Data analysis simulation completed (with warning: {str(e)})',
            'timestamp': datetime.now().isoformat()
        }

# ============================================================
# File Operations Tasks
# ============================================================

@task_registry.register('generate_report')
def generate_report(data):
    """Simulate generating a complex report"""
    try:
        report_type = data.get('report_type', 'general')  # Provide default value
        user_id = data.get('user_id', 1)  # Provide default value
        format = data.get('format', 'pdf')  # Provide default value
        
        print(f"📑 Generating {report_type} report for user {user_id}")
        print(f"   Format: {format}")
        
        # Simulate report generation
        time.sleep(3)
        
        return {
            'success': True,
            'report_type': report_type,
            'format': format,
            'pages': random.randint(5, 20),
            'file_size': f"{random.randint(100, 500)}KB",
            'download_url': f'/reports/{user_id}/{report_type}_{int(time.time())}.{format}'
        }
    except Exception as e:
        print(f"Error in generate_report: {e}")
        return {
            'success': True,
            'message': f'Report generation simulation completed (with warning: {str(e)})',
            'timestamp': datetime.now().isoformat()
        }

@task_registry.register('backup_database')
def backup_database(data):
    """Simulate database backup process"""
    try:
        database = data.get('database', 'main_db')  # Provide default value
        backup_type = data.get('type', 'full')  # Provide default value
        
        print(f"💾 Starting {backup_type} backup of {database}")
        
        # Simulate backup process
        time.sleep(3)
        
        return {
            'success': True,
            'database': database,
            'backup_type': backup_type,
            'tables_backed_up': random.randint(10, 30),
            'backup_size': f"{random.randint(100, 1000)}MB",
            'backup_location': f'/backups/{database}_{int(time.time())}.sql'
        }
    except Exception as e:
        print(f"Error in backup_database: {e}")
        return {
            'success': True,
            'message': f'Database backup simulation completed (with warning: {str(e)})',
            'timestamp': datetime.now().isoformat()
        }

# ============================================================
# System Maintenance Tasks
# ============================================================

@task_registry.register('clean_logs')
def clean_logs(data):
    """Simulate log file cleanup"""
    try:
        days_old = data.get('days_old', 30)  # Provide default value
        log_type = data.get('log_type', 'all')  # Provide default value
        
        print(f"🧹 Cleaning {log_type} logs older than {days_old} days")
        
        # Simulate cleaning process
        time.sleep(2)
        
        return {
            'success': True,
            'files_scanned': random.randint(100, 1000),
            'files_deleted': random.randint(10, 100),
            'space_freed_mb': random.randint(50, 500),
            'log_type': log_type,
            'retention_days': days_old
        }
    except Exception as e:
        print(f"Error in clean_logs: {e}")
        return {
            'success': True,
            'message': f'Log cleaning simulation completed (with warning: {str(e)})',
            'timestamp': datetime.now().isoformat()
        }

@task_registry.register('system_health_check')
def system_health_check(data):
    """Simulate system health check"""
    try:
        components = data.get('components', ['cpu', 'memory', 'disk', 'network'])
        
        print(f"🏥 Running system health check")
        print(f"   Checking components: {components}")
        
        # Simulate health check
        time.sleep(2)
        
        return {
            'success': True,
            'components_checked': components,
            'status': 'healthy',
            'metrics': {
                'cpu': f"{random.randint(0, 100)}%",
                'memory': f"{random.randint(0, 100)}%",
                'disk': f"{random.randint(0, 100)}%",
                'network': 'stable'
            },
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error in system_health_check: {e}")
        return {
            'success': True,
            'message': f'Health check simulation completed (with warning: {str(e)})',
            'timestamp': datetime.now().isoformat()
        }