# Greenfield University Instant Library

**Instant Library** is a cloud-native virtual library platform designed for the BSC Computer Science department at Greenfield University. Facing a shortage of physical textbooks, this system allows students to search for books, check availability, and request resources online. It leverages AWS services to provide a scalable, reliable, and real-time solution for managing library resources.

## 🚀 Features

*   **User Roles**: Dedicated portals for **Students** and **Library Staff**.
*   **Book Catalog**: Searchable database of books with real-time availability status.
*   **Request System**: Students can request out-of-stock or new books.
*   **Smart Notifications**: Real-time email alerts via **AWS SNS** for:
    *   Registration & Login activities.
    *   New Book Requests (Staff alert).
    *   Request Status Updates (Student alert).
*   **Admin Dashboard**: Staff can manage books, view all requests, and process approvals/rejections.
*   **Secure Authentication**: Custom OTP-based email verification and secure password hashing.

## 🏗 Architecture

The application is built using a serverless-inspired architecture hosted on AWS:

*   **Frontend**: HTML, CSS, JavaScript (served via Flask).
*   **Backend**: Python Flask API.
*   **Database**: **Amazon DynamoDB** (NoSQL) for high-performance data storage of Users, Books, Requests, OTA, and Notifications.
*   **Hosting**: **Amazon EC2** instances for running the application server.
*   **Notifications**: **Amazon SNS** for reliable email delivery.
*   **Security**: **AWS IAM** for role-based access control.

## 🛠 Tech Stack

*   **Language**: Python 3.x
*   **Web Framework**: Flask
*   **Cloud Provider**: Amazon Web Services (AWS)
*   **AWS Services**: EC2, DynamoDB, SNS, IAM
*   **Frontend**: HTML5, CSS3, JavaScript

## 📦 Installation & Setup

### Prerequisites
*   Python 3.8+
*   AWS Account with access to Console
*   AWS Credentials configured locally (for local dev)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/instant-library.git
cd instant-library
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements_aws.txt
```

### 3. AWS Configuration
This application requires manual setup of AWS resources.
1.  **DynamoDB**: Create tables matching the names in `AWS_app.py` (e.g., `InstantLibrary_Users`, `InstantLibrary_Books`, etc.).
2.  **SNS**: Create a Topic, subscribe your admin email, and update the `SNS_TOPIC_ARN` in `AWS_app.py`.
3.  **Region**: Update `AWS_REGION` in `AWS_app.py` if not using `us-east-1`.

### 4. Run the Application
```bash
python AWS_app.py
```
The app will start at `http://localhost:5000`.

## 📝 Deployment to AWS EC2

Here is the quick command reference for deploying to Amazon Linux 2023:

### 1. Connect to your Instance
```bash
ssh -i "your-key.pem" ec2-user@your-ec2-public-ip
```

### 2. Install System Dependencies
```bash
sudo yum update -y
sudo yum install python3 python3-pip git -y
```

### 3. Clone & Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/instant-library.git
cd instant-library/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
pip install -r requirements_aws.txt
```

### 4. Configure Application
Edit the `AWS_app.py` file to add your AWS Region and SNS Topic ARN:
```bash
nano AWS_app.py
```

### 5. Run in Production
Use `gunicorn` to run the application in the background:
```bash
nohup gunicorn -w 4 -b 0.0.0.0:5000 AWS_app:app &
```

*For detailed troubleshooting and manual DynamoDB setup, see [AWS_DEPLOYMENT_GUIDE.md](backend/AWS_DEPLOYMENT_GUIDE.md)*

## 👥 Authors
*   **Greenfield University Cloud Solutions Dept.**

## 📄 License
This project is licensed under the MIT License.
