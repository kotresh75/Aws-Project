# AWS Deployment Guide - Step-by-Step

Follow these steps exactly to deploy your application perfectly.

## Step 1: Create IAM Role (Permissions)
1. Go to AWS Console → Search **IAM** → **Roles**.
2. Click **Create role**.
3. Select **AWS Service** → Choose **EC2** → Click **Next**.
4. In Permissions, search for and select these two:
   - `AmazonDynamoDBFullAccess`
   - `AmazonSNSFullAccess`
5. Click **Next**, Name the role (e.g., `LibraryRole`), and click **Create role**.

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

## Step 4: Launch EC2 Instance (Server)
1. Go to **EC2** → **Launch Instance**.
2. Name: `LibraryServer`.
3. OS Image (AMI): **Amazon Linux 2023**.
4. Key Pair: Select your key (or create one).
5. **Network Settings** → **Edit**:
   - **Add Security Group Rule**: Type `HTTP` → Source `Anywhere (0.0.0.0/0)`.
   - **Add Security Group Rule**: Type `Custom TCP` → Port `5000` → Source `Anywhere (0.0.0.0/0)`.
6. Click **Launch Instance**.

## Step 5: Attach IAM Role
*Only if you didn't select it during launch:*
1. Go to **EC2 Dashboard** → Select your Instance.
2. Click **Actions** → **Security** → **Modify IAM role**.
3. Select the role you created in Step 1 (e.g., `LibraryRole`).
4. Click **Update IAM role**.

## Step 6: Connect & Deploy Application
1. Select Instance → **Connect** → **EC2 Instance Connect** → Connect.
2. Run these commands one by one:

```bash
# 1. Update System & Install Tools
sudo yum update -y
sudo yum install -y python3 python3-pip git

# 2. Download Code
git clone https://github.com/kotresh75/Aws-Project.git
cd Aws-Project/backend

# 3. Install Dependencies
pip install -r requirements_aws.txt

# 4. Configure App (Add SNS ARN & API Key)
nano AWS_app.py
# -> Use Arrow Keys to find SNS_TOPIC_ARN and GEMINI_API_KEY
# -> Delete the empty quotes and Paste your values
# -> Press Ctrl + X, then Y, then Enter to save

# 5. Run the Server
python3 AWS_app.py
```

3. **Success!**
   - Open your browser and go to: `http://YOUR_EC2_IP:5000`
   - App will auto-create default users (`staff@gmail.com` / `student@gmail.com`).