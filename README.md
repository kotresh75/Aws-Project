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

### Simple Broadcast Configuration
Since this application uses a **Broadcast Model**, you (the Admin) will receive all notifications.

1.  **Skip Filter Policies**: You do NOT need to configure JSON filter policies.
2.  **Verify Subscription**: Ensure your email is 'Confirmed' in the SNS Console.
3.  **Result**: You will effectively act as the system monitor, receiving:
    -   Student Registrations & Requests
    -   Security Alerts (OTPs, Password Changes)
    -   Audit Logs (Book/User Deletions)

> **Note**: Students do not receive emails directly in this configuration. You can forward relevant emails if strictly necessary, but for this project scope, Admin visibility is the priority.

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

python3 app_aws.py
```

## Local Development (Mocked Environment)
Want to test without spending money on AWS? Use the local mock server!

**1. Install Mock Libs**
```bash
pip install flask boto3 moto requests google-generativeai
```

**2. Run Local Server**
```bash
python run_local.py
```
*   **Zero Config**: No AWS Keys required (uses `moto`).
*   **Clean Slate**: Starts with an empty database.
*   **AI**: Requires your `GEMINI_API_KEY` in `app_aws.py`.

**3. First Time Setup (Local)**
1.  Register a **Staff** user (e.g., `admin@test.com`).
2.  Login -> Dashboard -> Click **"Populate Catalog"**.
3.  Register a **Student** user to test requests.
