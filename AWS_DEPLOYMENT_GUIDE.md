# AWS Deployment Guide - Greenfield University Instant Library

## Overview

This document outlines **all code changes required** to deploy the Instant Library system on AWS infrastructure as specified in the project overview.

> [!IMPORTANT]
> **Current State**: The application uses in-memory storage and console-based notifications.
> **Target State**: AWS EC2 hosting, DynamoDB database, SNS email notifications, IAM authentication, VPC security.

---

## Table of Contents

1. [AWS Services Required](#1-aws-services-required)
2. [Backend Code Changes](#2-backend-code-changes)
3. [Database Migration: DynamoDB](#3-database-migration-dynamodb)
4. [Notification System: AWS SNS](#4-notification-system-aws-sns)
5. [Security: AWS IAM](#5-security-aws-iam)
6. [Hosting: AWS EC2](#6-hosting-aws-ec2)
7. [Frontend Deployment](#7-frontend-deployment)
8. [Environment Configuration](#8-environment-configuration)
9. [Testing Checklist](#9-testing-checklist)

---

## 1. AWS Services Required

| Service | Purpose | Current Implementation |
|---------|---------|------------------------|
| **Amazon EC2** | Host Flask backend | Running locally on `localhost:5000` |
| **Amazon DynamoDB** | Store users, books, requests | In-memory Python dictionaries |
| **Amazon SNS** | Email notifications | `print()` statements to console |
| **AWS IAM** | Access control & permissions | None (open access) |
| **AWS VPC** | Network security | None |

---

## 2. Backend Code Changes

### 2.1 Required Dependencies

Add to `requirements.txt`:

```txt
Flask==2.3.3
flask-cors==4.0.0
boto3==1.34.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

### 2.2 Environment Variables

Create `.env` file (NOT committed to git):

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# DynamoDB Table Names
DYNAMODB_USERS_TABLE=instant-library-users
DYNAMODB_BOOKS_TABLE=instant-library-books
DYNAMODB_REQUESTS_TABLE=instant-library-requests
DYNAMODB_NOTIFICATIONS_TABLE=instant-library-notifications

# SNS Topic ARNs
SNS_STUDENT_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:StudentNotifications
SNS_STAFF_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:StaffNotifications

# Application
FLASK_ENV=production
SECRET_KEY=your_secure_secret_key
```

---

## 3. Database Migration: DynamoDB

### 3.1 Current Code to Replace

**File**: [backend/app.py](file:///F:/AWS%20Project/backend/app.py)

**Lines 13-19 (Remove in-memory storage)**:
```python
# REMOVE THIS:
users_db = {}
book_requests_db = {}
otp_store = {}
pending_registrations = {}
notifications_db = {}
notification_id_counter = 1
```

### 3.2 DynamoDB Tables Structure

#### Users Table
| Attribute | Type | Key |
|-----------|------|-----|
| email | String | Partition Key |
| password | String | - |
| name | String | - |
| role | String | - |
| roll_no | String | - |
| semester | String | - |
| year | String | - |
| verified | Boolean | - |
| created_at | String | - |

#### Books Table
| Attribute | Type | Key |
|-----------|------|-----|
| id | Number | Partition Key |
| title | String | - |
| author | String | - |
| subject | String | GSI |
| available_count | Number | - |
| total_count | Number | - |

#### Requests Table
| Attribute | Type | Key |
|-----------|------|-----|
| request_id | Number | Partition Key |
| email | String | GSI |
| book_id | Number | - |
| status | String | GSI |
| requested_at | String | - |

### 3.3 New Database Helper Module

**Create**: `backend/db/dynamodb.py`

```python
import boto3
import os
from botocore.exceptions import ClientError

class DynamoDBHelper:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.users_table = self.dynamodb.Table(os.getenv('DYNAMODB_USERS_TABLE'))
        self.books_table = self.dynamodb.Table(os.getenv('DYNAMODB_BOOKS_TABLE'))
        self.requests_table = self.dynamodb.Table(os.getenv('DYNAMODB_REQUESTS_TABLE'))
    
    # User operations
    def get_user(self, email):
        response = self.users_table.get_item(Key={'email': email})
        return response.get('Item')
    
    def create_user(self, user_data):
        self.users_table.put_item(Item=user_data)
    
    def update_user(self, email, updates):
        # Build update expression
        ...
    
    # Book operations
    def get_all_books(self):
        response = self.books_table.scan()
        return response.get('Items', [])
    
    def get_book(self, book_id):
        response = self.books_table.get_item(Key={'id': book_id})
        return response.get('Item')
    
    # Request operations
    def create_request(self, request_data):
        self.requests_table.put_item(Item=request_data)
    
    def get_user_requests(self, email):
        # Query using GSI
        ...
```

### 3.4 Code Changes in app.py

**Replace all dictionary operations**:

| Current Code | New Code |
|-------------|----------|
| `users_db[email] = {...}` | `db.create_user({...})` |
| `user = users_db.get(email)` | `user = db.get_user(email)` |
| `books_db.values()` | `db.get_all_books()` |
| `book_requests_db[id] = {...}` | `db.create_request({...})` |

---

## 4. Notification System: AWS SNS

### 4.1 Current Code to Replace

**File**: [backend/app.py](file:///F:/AWS%20Project/backend/app.py)

**Lines 756-779 (Replace print-based notifications)**:
```python
# REPLACE THIS:
def log_sns_notification(topic, recipient, subject, message):
    print(f"\n📧 SNS NOTIFICATION LOG")
    print(f"Topic: {topic}")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print(f"Message:\n{message}")
    print("-" * 40)
```

### 4.2 New SNS Helper Module

**Create**: `backend/notifications/sns.py`

```python
import boto3
import os

class SNSNotifier:
    def __init__(self):
        self.sns = boto3.client(
            'sns',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.student_topic = os.getenv('SNS_STUDENT_TOPIC_ARN')
        self.staff_topic = os.getenv('SNS_STAFF_TOPIC_ARN')
    
    def notify_student(self, email, subject, message):
        """Send notification to student via SNS"""
        self.sns.publish(
            TopicArn=self.student_topic,
            Message=message,
            Subject=subject,
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': email
                }
            }
        )
    
    def notify_staff(self, subject, message):
        """Send notification to all staff via SNS"""
        self.sns.publish(
            TopicArn=self.staff_topic,
            Message=message,
            Subject=subject
        )
```

### 4.3 AWS SNS Setup Required

1. Create SNS Topic: `StudentNotifications`
2. Create SNS Topic: `StaffNotifications`
3. Create email subscriptions for staff
4. Configure filter policies for student emails

---

## 5. Security: AWS IAM

### 5.1 IAM Policy for EC2 Instance

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/instant-library-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": [
                "arn:aws:sns:*:*:StudentNotifications",
                "arn:aws:sns:*:*:StaffNotifications"
            ]
        }
    ]
}
```

### 5.2 IAM Role for EC2

- Create IAM Role: `InstantLibraryEC2Role`
- Attach the policy above
- Assign role to EC2 instance

---

## 6. Hosting: AWS EC2

### 6.1 EC2 Instance Setup

| Setting | Value |
|---------|-------|
| AMI | Amazon Linux 2023 |
| Instance Type | t2.micro (free tier) |
| Security Group | Allow ports 22, 80, 443, 5000 |
| IAM Role | InstantLibraryEC2Role |

### 6.2 Security Group Rules

| Type | Port | Source |
|------|------|--------|
| SSH | 22 | Your IP |
| HTTP | 80 | 0.0.0.0/0 |
| HTTPS | 443 | 0.0.0.0/0 |
| Custom TCP | 5000 | 0.0.0.0/0 |

### 6.3 EC2 Setup Commands

```bash
# Update system
sudo yum update -y

# Install Python 3.9
sudo yum install python3.9 python3.9-pip -y

# Clone your repository
git clone https://github.com/your-repo/instant-library.git
cd instant-library/backend

# Install dependencies
pip3.9 install -r requirements.txt

# Run with Gunicorn (production)
gunicorn --bind 0.0.0.0:5000 app:app --workers 3
```

### 6.4 Systemd Service (Auto-start)

**Create**: `/etc/systemd/system/instant-library.service`

```ini
[Unit]
Description=Instant Library Flask App
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/instant-library/backend
ExecStart=/usr/bin/gunicorn --bind 0.0.0.0:5000 app:app --workers 3
Restart=always
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
```

---

## 7. Frontend Deployment

### 7.1 Update API Base URL

**File**: [frontend_only_html/js/app.js](file:///F:/AWS%20Project/frontend_only_html/js/app.js)

```javascript
// CHANGE THIS:
const API_BASE = 'http://127.0.0.1:5000/api';

// TO:
const API_BASE = 'https://your-ec2-public-ip/api';
// OR with domain:
const API_BASE = 'https://library.greenfield.edu/api';
```

### 7.2 Hosting Options

| Option | Description |
|--------|-------------|
| **S3 + CloudFront** | Static hosting with CDN (recommended) |
| **Same EC2** | Serve via Nginx alongside Flask |
| **Amplify** | AWS managed frontend hosting |

### 7.3 S3 Static Hosting Setup

```bash
# Create S3 bucket
aws s3 mb s3://greenfield-instant-library

# Upload frontend files
aws s3 sync frontend_only_html/ s3://greenfield-instant-library/ --acl public-read

# Enable static website hosting
aws s3 website s3://greenfield-instant-library/ --index-document index.html --error-document 404.html
```

---

## 8. Environment Configuration

### 8.1 Production app.py Changes

```python
# Add at top of app.py
from dotenv import load_dotenv
import os

load_dotenv()

# Change debug mode
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') != 'production'
    )
```

### 8.2 CORS Configuration for Production

```python
# Update CORS settings
CORS(app, origins=[
    'https://library.greenfield.edu',
    'https://your-cloudfront-domain.cloudfront.net'
])
```

---

## 9. Testing Checklist

### Pre-Deployment

- [ ] All DynamoDB tables created with correct schema
- [ ] SNS topics created and subscriptions confirmed
- [ ] IAM role attached to EC2 instance
- [ ] Security groups configured correctly
- [ ] Environment variables set on EC2

### Post-Deployment

- [ ] Health check endpoint responds: `GET /api/health`
- [ ] User registration works (DynamoDB write)
- [ ] Login works (DynamoDB read)
- [ ] Book catalog loads (DynamoDB scan)
- [ ] Book request creates notification (SNS publish)
- [ ] Email notifications received
- [ ] Frontend loads and connects to API

---

## Summary of Files to Modify

| File | Changes |
|------|---------|
| `backend/app.py` | Replace in-memory dicts with DynamoDB, replace print notifications with SNS |
| `backend/requirements.txt` | Add boto3, python-dotenv, gunicorn |
| `backend/.env` | Create with AWS credentials and config |
| `backend/db/dynamodb.py` | NEW - DynamoDB helper module |
| `backend/notifications/sns.py` | NEW - SNS notification module |
| `frontend_only_html/js/app.js` | Update API_BASE URL |

---

## Estimated Effort

| Task | Time Estimate |
|------|---------------|
| DynamoDB table creation | 1 hour |
| Backend code refactoring | 4-6 hours |
| SNS setup and integration | 2 hours |
| EC2 setup and deployment | 2 hours |
| Frontend deployment | 1 hour |
| Testing and debugging | 2-3 hours |
| **Total** | **12-15 hours** |
