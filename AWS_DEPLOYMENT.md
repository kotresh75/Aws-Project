# AWS Cloud Deployment & Adoption Guide

This document outlines the steps to migrate the **Instant Library** application from a local development environment to a fully cloud-native architecture on AWS, as per the project vision.

---

## 1. Architecture Overview
The target architecture leverages AWS managed services for scalability, reliability, and security.

-   **Compute**: **Amazon EC2** (Elastic Cloud Compute) for hosting the Flask backend and React frontend.
-   **Database**: **Amazon DynamoDB** (NoSQL) replaces the in-memory Python dictionaries (`users_db`, `books_db`) for persistent storage.
-   **Notifications**: **Amazon SNS** (Simple Notification Service) replaces the file-based logging to send real emails to students and staff.
-   **Security**: **AWS IAM** (Identity and Access Management) manages permissions, replacing hardcoded credentials.

---

## 2. Service Adoption Steps

### A. Amazon DynamoDB (Database Migration)
*Goal: Move `users_db`, `books_db`, `book_requests_db` from memory to DynamoDB.*

#### 1. Create Tables
Go to AWS Console > DynamoDB > Create Table.
*   **Table: Users**
    *   Partition Key: `email` (String)
*   **Table: Books**
    *   Partition Key: `id` (Number)
*   **Table: Requests**
    *   Partition Key: `request_id` (Number)
    *   GSI (Global Secondary Index): `email-index` (Partition Key: `email`) for fast user lookup.

#### 2. Code Changes (`backend/app.py`)
1.  **Install SDK**: Add `boto3` to your environment (`pip install boto3`).
2.  **Initialize Client**:
    ```python
    import boto3
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    users_table = dynamodb.Table('Users')
    books_table = dynamodb.Table('Books')
    ```
3.  **Refactor CRUD Operations**:
    *   *Read*: Replace `users_db.get(email)` with `users_table.get_item(Key={'email': email})`.
    *   *Write*: Replace `users_db[email] = data` with `users_table.put_item(Item=data)`.
    *   *Scan*: Replace `books_db.values()` with `books_table.scan()['Items']`.

---

### B. Amazon SNS (Notifications)
*Goal: Replace local text logging with real email delivery.*

#### 1. Setup SNS
1.  Go to AWS Console > SNS > **Topics** > Create Topic > Standard.
    *   Name: `InstantLibraryNotifications`
2.  **Create Subscriptions**:
    *   Protocol: Email
    *   Endpoint: `staff@gmail.com` (and real student emails for testing).
    *   *Note*: Endpoints must confirm the subscription via the email received.

#### 2. Code Changes (`backend/app.py`)
1.  **Initialize Client**:
    ```python
    sns_client = boto3.client('sns', region_name='us-east-1')
    TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:InstantLibraryNotifications"
    ```
2.  **Modify `log_sns_notification` function**:
    ```python
    def log_sns_notification(topic, recipient, subject, message):
        try:
            # Publish to SNS Topic (Broadcasts to all subscribers, e.g., Staff)
            sns_client.publish(
                TopicArn=TOPIC_ARN,
                Message=message,
                Subject=subject
            )
            # For direct student emails, you might use SES or subscribe them dynamically to SNS.
            print(f"SNS Published: {subject}")
        except Exception as e:
            print(f"SNS Error: {e}")
    ```

---

### C. AWS IAM (Security)
*Goal: Grant EC2 permission to access DynamoDB and SNS without hardcoding keys.*

#### 1. Create IAM Role
1.  Go to AWS Console > IAM > **Roles** > Create Role.
2.  Trusted Entity: **AWS Service** > **EC2**.
3.  **Permissions Policies**:
    *   `AmazonDynamoDBFullAccess` (Or scope down to specific tables).
    *   `AmazonSNSFullAccess`.
4.  Name: `InstantLibraryEC2Role`.

#### 2. Attach to EC2
1.  When creating (or modifying) your EC2 instance, look for **IAM Instance Profile**.
2.  Select `InstantLibraryEC2Role`.
3.  *Code Change*: When using `boto3`, **DO NOT** pass `aws_access_key_id` or `secret_access_key`. Boto3 will automatically use the credentials from the attached IAM role.

---

### D. Amazon EC2 (Deployment)
*Goal: Host the application on a public server.*

#### 1. Launch Instance
1.  **OS**: Ubuntu Server 22.04 LTS or Amazon Linux 2023.
2.  **Instance Type**: t2.micro (Free Tier eligible).
3.  **Security Group**:
    *   Allow **SSH (22)** from your IP.
    *   Allow **HTTP (80)** and **Custom TCP (5000)** from Anywhere (0.0.0.0/0).

#### 2. Deployment Steps
1.  **SSH into EC2**: `ssh -i key.pem ubuntu@public-ip`
2.  **Install Dependencies**:
    ```bash
    sudo apt update
    sudo apt install python3-pip nodejs npm nginx
    ```
3.  **Clone Code**: Upload your project files.
4.  **Backend Setup**:
    ```bash
    cd backend
    pip3 install flask flask-cors boto3
    python3 app.py  # Use Gunicorn for production
    ```
5.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    npm run build
    # Serve 'build' folder using Nginx
    ```

---

## 3. Summary of Required Code Changes

| File | Component | Action |
| :--- | :--- | :--- |
| `backend/app.py` | **Imports** | Import `boto3` library. |
| `backend/app.py` | **Database** | Replace `dict` lookups with `dynamodb_table.get_item()` and `put_item()`. |
| `backend/app.py` | **Notifications** | Replace file write logic with `sns_client.publish()`. |
| `backend/app.py` | **Config** | Move configuration (Region, Table Names) to Environment Variables. |
| `frontend/src/` | **API URL** | Update `localhost:5000` to the public IP/DNS of the EC2 instance. |
