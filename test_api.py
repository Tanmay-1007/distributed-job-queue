"""
Test the REST API endpoints
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000/api'

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📡 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

def test_api():
    print("\n" + "="*60)
    print("🧪 Testing Job Queue API")
    print("="*60)
    
    # 1. Health Check
    response = requests.get(f'{BASE_URL}/health')
    print_response("Health Check", response)
    
    # 2. Get Available Tasks
    response = requests.get(f'{BASE_URL}/tasks')
    print_response("Available Tasks", response)
    
    # 3. Create a Single Job
    job_data = {
        'task_name': 'send_email',
        'task_data': {
            'to': 'api-test@example.com',
            'subject': 'API Test Email'
        },
        'priority': 1,
        'queue': 'default'
    }
    response = requests.post(f'{BASE_URL}/jobs', json=job_data)
    print_response("Create Job", response)
    
    job_id = response.json().get('job_id')
    
    # 4. Get Job by ID
    if job_id:
        time.sleep(1)
        response = requests.get(f'{BASE_URL}/jobs/{job_id}')
        print_response(f"Get Job {job_id[:8]}...", response)
    
    # 5. Create Bulk Jobs
    bulk_data = {
        'jobs': [
            {
                'task_name': 'process_image',
                'task_data': {'image_url': 'image1.jpg', 'filters': ['resize']}
            },
            {
                'task_name': 'generate_report',
                'task_data': {'report_type': 'weekly', 'user_id': 123}
            }
        ],
        'queue': 'high'
    }
    response = requests.post(f'{BASE_URL}/jobs/bulk', json=bulk_data)
    print_response("Create Bulk Jobs", response)
    
    # 6. Get Queue Status
    response = requests.get(f'{BASE_URL}/queues')
    print_response("Queue Status", response)
    
    # 7. Get All Jobs
    response = requests.get(f'{BASE_URL}/jobs?limit=5')
    print_response("Get All Jobs (limit 5)", response)
    
    # 8. Get Jobs by Status
    response = requests.get(f'{BASE_URL}/jobs?status=pending&limit=5')
    print_response("Get Pending Jobs", response)
    
    # 9. Get Statistics
    response = requests.get(f'{BASE_URL}/stats')
    print_response("Statistics", response)
    
    print("\n" + "="*60)
    print("✅ API Test Completed!")
    print("="*60 + "\n")

if __name__ == '__main__':
    print("\n⚠️  Make sure API server is running!")
    print("   Run: python api/app.py")
    print("\nStarting tests in 3 seconds...\n")
    time.sleep(3)
    
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("   Please start the server first: python api/app.py\n")