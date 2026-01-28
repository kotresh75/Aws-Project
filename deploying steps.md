# AWS Deployment Guide - Step-by-Step

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
| `InstantLibrary_Requests`| `request_id` | String (S) |
| `InstantLibrary_Notifications` | `id` | String (S) |
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
cd Aws-Project/backend

# 3. Install Requirements
pip install -r requirements_aws.txt

# 4. Configure App (Add SNS ARN & API Key)
nano AWS_app.py
# -> Find SNS_TOPIC_ARN and paste your ARN from Step 3
# -> Find GEMINI_API_KEY and paste your Key
# -> Save: Ctrl+X, Y, Enter

# 5. Run Server
python3 AWS_app.py
```

3. **Open in Browser**: `http://YOUR_EC2_IP:5000`
   - App will auto-create default users (`staff@gmail.com` / `student@gmail.com`).
