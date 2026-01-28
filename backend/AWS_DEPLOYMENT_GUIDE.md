# AWS Deployment Commands

## Step 1: Launch EC2 Instance
```
AMI: Amazon Linux 2023
Instance Type: t2.micro
Security Group: Allow SSH (22), HTTP (80), TCP (5000)
```

## Step 2: Connect to EC2
```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

## Step 3: Install Dependencies
```bash
sudo yum update -y
sudo yum install python3 python3-pip git -y
```

## Step 4: Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/backend
```

## Step 5: Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_aws.txt
```

## Step 6: Configure AWS_app.py
```bash
nano AWS_app.py
```
Edit these values:
```python
AWS_REGION = 'us-east-1'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:InstantLibraryNotifications'
```

## Step 7: Attach IAM Role to EC2
```
AWS Console → IAM → Roles → Create Role
Use Case: EC2
Policies: AmazonDynamoDBFullAccess, AmazonSNSFullAccess
Attach to EC2 instance
```

## Step 8: Create SNS Topic
```
AWS Console → SNS → Topics → Create Topic → Standard
Name: InstantLibraryNotifications
Copy ARN → Paste in AWS_app.py
```

## Step 9: Add SNS Email Subscription
```
AWS Console → SNS → Your Topic → Create Subscription
Protocol: Email
Endpoint: your-staff@email.com
Confirm via email link
```

## Step 10: Run Application
```bash
# Development
python AWS_app.py

# Production
nohup gunicorn -w 4 -b 0.0.0.0:5000 AWS_app:app &
```

## Step 11: Test
```bash
curl http://localhost:5000/api/health
```

---

## Default Login Credentials
| Role | Email | Password |
|------|-------|----------|
| Staff | staff@gmail.com | 123456 |
| Student | student@gmail.com | 123456 |

*Note: These accounts are automatically created when you run the application for the first time.*

---

## DynamoDB Tables Setup (Manual)

Create these 5 tables in AWS Console → DynamoDB → Tables → Create Table

### Table 1: InstantLibrary_Users
```
Table Name: InstantLibrary_Users
Partition Key: email (String)
Settings: Default settings
```

### Table 2: InstantLibrary_Books
```
Table Name: InstantLibrary_Books
Partition Key: id (String)
Settings: Default settings
```

### Table 3: InstantLibrary_Requests
```
Table Name: InstantLibrary_Requests
Partition Key: request_id (String)
Settings: Default settings
```

### Table 4: InstantLibrary_Notifications
```
Table Name: InstantLibrary_Notifications
Partition Key: id (String)
Settings: Default settings
```

### Table 5: InstantLibrary_OTP
```
Table Name: InstantLibrary_OTP
Partition Key: email (String)
Settings: Default settings
```
After creating, enable TTL:
```
Select table → Additional settings → Time to live (TTL) → Turn on
TTL attribute: ttl
```

---

## Add Initial Staff Account (Skipped)

The application now **automatically creates the default staff and student accounts** when it starts up. You do effectively NOT need to add them manually anymore.

---

## SNS Setup Guide (Manual)

Follow these steps to configure AWS SNS for email notifications:

### Step 1: Create SNS Topic
```
1. Go to AWS Console → SNS → Topics
2. Click "Create topic"
3. Type: Standard
4. Name: InstantLibraryNotifications
5. Click "Create topic"
6. Copy the Topic ARN (e.g., arn:aws:sns:us-east-1:123456789:InstantLibraryNotifications)
7. Paste ARN in AWS_app.py → SNS_TOPIC_ARN
```

### Step 2: Add Email Subscriptions
Add each staff/admin email that should receive notifications:
```
1. Open your SNS Topic
2. Click "Create subscription"
3. Protocol: Email
4. Endpoint: staff-email@example.com
5. Click "Create subscription"
6. Check inbox → Click confirmation link
7. Repeat for each email address
```

### Step 3: Configure IAM Permissions
Ensure EC2 instance has permission to publish to SNS:
```
Option A - Attach policy to EC2 IAM Role:
  - Go to IAM → Roles → Select your EC2 role
  - Add permission: AmazonSNSFullAccess

Option B - Create custom policy:
  {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:InstantLibraryNotifications"
    }]
  }
```

### Step 4: Test SNS
```bash
# Test from EC2 instance
aws sns publish --topic-arn "YOUR_TOPIC_ARN" --message "Test notification" --subject "Test"
```
