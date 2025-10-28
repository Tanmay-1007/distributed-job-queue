# Job Queue API Documentation

Base URL: `http://localhost:5000/api`

## Endpoints

### 1. Create Job
**POST** `/api/jobs`

Create and submit a new job to the queue.

**Request Body:**
```json
{
  "task_name": "send_email",
  "task_data": {
    "to": "user@example.com",
    "subject": "Hello World"
  },
  "priority": 1,
  "queue": "default",
  "max_retries": 3
}