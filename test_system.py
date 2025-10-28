"""
Test complete job queue system
"""
import requests
import time
import json

API_URL = 'http://localhost:5000/api'

def print_response(name, response):
    print(f"\n{'='*60}")
    print(f"📝 {name}")
    print(f"Status: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print('='*60)

def test_system():
    print("\n🚀 Testing Job Queue System\n")

    # Test 1: Submit Email Job
    email_job = {
        "task_name": "send_email",
        "task_data": {
            "to": "test@example.com",
            "subject": "Test Email"
        },
        "queue": "default"
    }
    
    print("📧 Submitting email job...")
    response = requests.post(f'{API_URL}/jobs', json=email_job)
    print_response("Email Job Submission", response)
    email_job_id = response.json().get('job_id')

    # Test 2: Submit Image Processing Job
    image_job = {
        "task_name": "process_image",
        "task_data": {
            "image_url": "test.jpg",
            "filters": ["resize", "compress"]
        },
        "queue": "high"
    }
    
    print("\n🖼️ Submitting image processing job...")
    response = requests.post(f'{API_URL}/jobs', json=image_job)
    print_response("Image Job Submission", response)
    image_job_id = response.json().get('job_id')

    # Test 3: Submit Report Generation Job
    report_job = {
        "task_name": "generate_report",
        "task_data": {
            "report_type": "monthly",
            "user_id": 123
        },
        "queue": "low"
    }
    
    print("\n📊 Submitting report generation job...")
    response = requests.post(f'{API_URL}/jobs', json=report_job)
    print_response("Report Job Submission", response)
    report_job_id = response.json().get('job_id')

    # Wait for jobs to be processed
    print("\n⏳ Waiting for jobs to be processed...")
    time.sleep(5)

    # Test 4: Check Job Statuses
    for job_id in [email_job_id, image_job_id, report_job_id]:
        response = requests.get(f'{API_URL}/jobs/{job_id}')
        print_response(f"Job Status {job_id[:8]}...", response)

    # Test 5: Get Queue Status
    response = requests.get(f'{API_URL}/queues')
    print_response("Queue Status", response)

    # Test 6: Get Statistics
    response = requests.get(f'{API_URL}/stats')
    print_response("System Statistics", response)

    print("\n✅ System test completed!")

if __name__ == "__main__":
    try:
        test_system()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API")
        print("Make sure the API server is running (python run_api.py)")
    except Exception as e:
        print(f"\n❌ Error: {e}")