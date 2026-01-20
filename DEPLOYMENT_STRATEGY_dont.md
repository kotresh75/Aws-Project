# Greenfield University Instant Library - Deployment Masterplan
**Architecture Reference**: `The Overview.txt`

This document details the deployment strategy for the **Greenfield University Instant Library**. It aligns our "Hybrid Routing" (React + Flask) architecture with the specific AWS services designed to handle the university's resource management needs.

## 1. Cloud Architecture Overview

As per the project vision, we are deploying a **Scalable Cloud-Native Application**:

*   **Compute (Hosting)**: **Amazon EC2** (Ubuntu) running both the Frontend (React via Nginx) and Backend (Flask).
*   **Database (Storage)**: **Amazon DynamoDB** replaces local memory to efficiently store Student, Staff, and Book data.
*   **Notifications (Alerts)**: **Amazon SNS** manages real-time email alerts for book requests and availability.
*   **Security**: **AWS IAM** Roles allow the EC2 instance to talk to DynamoDB and SNS securely (Zero Access Keys).

---

## 2. Infrastructure Setup (AWS Console)

Before deploying code, ensure these "pillars" are active:

### A. Database (DynamoDB)
Create these tables in `us-east-1` (or your region):
*   **Users** (Partition Key: `email`)
*   **Books** (Partition Key: `id`)
*   **Requests** (Partition Key: `request_id`)

### B. Notifications (SNS)
*   Create Topic: `InstantLibraryNotifications`
*   Subscribe: Library Staff email (and verify/confirm subscription).
*   **Note ARN**: You will need the Topic ARN (e.g., `arn:aws:sns:us-east-1:123456789012:InstantLibraryNotifications`).

### C. Security (IAM)
*   Create Role: `InstantLibraryEC2Role`
*   Permissions: `AmazonDynamoDBFullAccess`, `AmazonSNSFullAccess`.
*   **Attach**: Go to EC2 Instance > Actions > Security > Modify IAM Role > Select `InstantLibraryEC2Role`.

---

## 3. Hybrid Routing Deployment (EC2 + Nginx)

This strategy uses **Hybrid Routing**: Nginx handles the traffic, ensuring instant page loads (Frontend) and secure data access (Backend).

### Step 1: Frontend Build (React)
On the EC2 instance:
```bash
cd f:/AWS Project/frontend  # (Adjust path to where you uploaded code)
npm install
npm run build
# Move build to web root
sudo mkdir -p /var/www/instant-library
sudo cp -r build/* /var/www/instant-library/
```

### Step 2: The "Golden" Nginx Configuration
This configuration solves the "404 Not Found" issue on refresh and proxies API requests.

**File**: `/etc/nginx/sites-available/default`

```nginx
server {
    listen 80;
    server_name _;

    root /var/www/instant-library;
    index index.html;

    # === FRONTEND (Hybrid Routing) ===
    # Serves React app. If route doesn't match a file, fallback to index.html.
    location / {
        try_files $uri $uri/ /index.html;
    }

    # === BACKEND (Flask API) ===
    # Forwards /api requests to the Python application running on port 5000.
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```
**Apply Changes**: `sudo systemctl restart nginx`

### Step 3: Backend Service (Flask)
The backend connects to DynamoDB and SNS automatically via the IAM Role.

```bash
cd f:/AWS Project/backend
pip3 install flask flask-cors boto3 gunicorn
# Run in background (Production Mode)
gunicorn -w 4 -b 127.0.0.1:5000 app:app --daemon
```

---

## 4. Verification Checklist

1.  **Frontend**: Visit EC2 Public IP. The "Welcome" page should load instantly.
2.  **Routing**: Click "Login" -> Refresh the page. You should stay on the Login page (No 404 Error).
3.  **Database**: Register a new student. Check DynamoDB "Users" table to see the new entry.
4.  **Notifications**: Request a book. Check the Staff email for the SNS notification.

This strategy ensures Greenfield University has a robust, professional, and scalable library system.
