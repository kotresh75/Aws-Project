# AWS Deployment Guide - Step-by-Step

**⚠️ CRITICAL: You MUST select "US East (N. Virginia) us-east-1" in the top-right corner of your AWS Console before starting. Your code is hardcoded to this region.**

Follow these steps in this exact order to deploy your application.

## Step 1: Launch EC2 Instance (Server)
1. Go to AWS Console → **EC2** → **Launch Instance**.
2. Name: `LibraryServer`.
3. OS Image (AMI): **Amazon Linux 2023**.
4. **Key Pair (Login Access)**:
   - Click **Create new key pair**.
   - Name: `LibraryKey`.
   - Click **Create key pair**.
   - *Select this new key in the dropdown.*
5. **Network Settings** → **Edit**:
   - **Add Security Group Rule**: Type `HTTP` → Source `Anywhere (0.0.0.0/0)`.
   - **Add Security Group Rule**: Type `Custom TCP` → Port `5000` → Source `Anywhere (0.0.0.0/0)`.
6. Click **Launch Instance**.

## Step 2: Create DynamoDB Tables (Database)
Go to **DynamoDB** → **Tables** → **Create Table** for each of the following:

| Table Name | Partition Key | Key Type |
| :--- | :--- | :--- |
| `InstantLibrary_Users` | `email` | String (S) |
| `InstantLibrary_Books` | `id` | String (S) |
| `InstantLibrary_Requests`| `id` | String (S) |
| `InstantLibrary_OTP` | `email` | String (S) |

**⚠️ Important for OTP Table:**
1. After creating `InstantLibrary_OTP`, click on it.
2. Go to **Additional Settings** → **Time to Live (TTL)**.
3. Turn **ON**.
4. Enter `ttl` as the attribute name.

## Step 3: Setup Request Notifications (SNS)
1. Go to **SNS** → **Topics** → **Create Topic** → **Standard**.
2. Name it: `InstantLibraryNotifications`.
3. Click Create. **COPY THE ARN** (starts with `arn:aws:sns...`).
4. Click **Create Subscription** → Protocol: **Email**.
5. Endpoint: Enter your email (e.g., `veerkotresh@gmail.com`).
6. **Check your Email Inbox** and click "Confirm Subscription".

### Role-Based Subscription Configuration
Configure subscriptions for your specific roles using the Filter Policies below:

| Role | Email | Filter Policy (JSON) | Behavior |
| :--- | :--- | :--- | :--- |
| **Admin** | `veerkotresh@gmail.com` | *(Leave Empty)* | **Receives Everything** (Broadcast). Login alerts, registrations, all user requests. |
| **Staff** | `mykotresh@gmail.com` | `{"recipient": ["mykotresh@gmail.com"]}` | Receives only messages addressed to them (e.g., Book Requests assigned to staff, their own OTPs). |
| **Student** | `kotreshoffical@gmail.com` | `{"recipient": ["kotreshoffical@gmail.com"]}` | Receives only their own interaction emails (Welcome, Request Updates, OTPs). |

> **To Add Filter Policy**: Select the Subscription ID → click **Edit** → expand **Subscription filter policy** → paste the JSON.

## Step 4: Create & Attach IAM Role (Permissions)
**Part A: Create Role**
1. Go to **IAM** → **Roles** → **Create role**.
2. Select **AWS Service** → **EC2** → **Next**.
3. Permissions: Select `AmazonDynamoDBFullAccess` and `AmazonSNSFullAccess`.
4. Name: `LibraryRole` → **Create role**.

**Part B: Attach to EC2**
1. Go to **EC2 Dashboard** → Select your Instance (`LibraryServer`).
2. Click **Actions** → **Security** → **Modify IAM role**.
3. Select `LibraryRole` → **Update IAM role**.

## Step 5: AWS Deployment (Connect & Run)
1. Select Instance → **Connect** → **EC2 Instance Connect** → Connect.
2. Run these commands:

```bash
# 1. Update & Install
sudo yum update -y
sudo yum install -y python3 python3-pip git

# 2. Download Code
git clone https://github.com/kotresh75/Aws-Project.git
cd Aws-Project

# 3. Install Requirements
pip install -r requirements_aws.txt

# 4. Configure App (Add SNS ARN & API Key)
nano app_aws.py

# --- NANO EDITOR STEPS ---
# 1. Use Arrow Keys to scroll down to line 18 (SNS_TOPIC_ARN).
# 2. Delete the empty quotes ''.
# 3. Paste your ARN inside quotes: 'arn:aws:sns:...' (Right-click to paste).
# 4. Scroll down to line 19 (GEMINI_API_KEY).
# 5. Paste your API Key inside quotes like: 'AIzaSy...'
# 6. Save & Exit:
#    - Press Ctrl + O (Write Out)
#    - Press Enter (Confirm File Name)
#    - Press Ctrl + X (Exit)
# -------------------------

# 5. Run Server
python3 app_aws.py
```

