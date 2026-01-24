"""
Greenfield University Instant Library - AWS Deployment-Ready Application
=========================================================================
AWS Services Used:
1. EC2 - Hosting the Flask application
2. DynamoDB - Database (Users, Books, Requests, Notifications, OTP)
3. SNS - Email notifications to students and staff
4. IAM - Access management and security

Clone repository → Configure below → Run setup_dynamodb.py → Deploy
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import hashlib
import os
import random
import string
import uuid
import json
from decimal import Decimal

app = Flask(__name__, static_folder='../static', static_url_path='')
CORS(app)

# ============================================
# AWS CONFIGURATION - EDIT THESE VALUES
# ============================================

# AWS Region (e.g., us-east-1, ap-south-1)
AWS_REGION = 'us-east-1'

SNS_TOPIC_ARN = ''

# (Optional) Gemini API Key for AI Chatbot
GEMINI_API_KEY = 'AIzaSyApedFAAJOa5pCgkRLr0l6HIGNXfmxREgY'

# ============================================

# Initialize AWS clients
try:
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    sns_client = boto3.client('sns', region_name=AWS_REGION)
    
    # DynamoDB Tables
    # NOTE: Tables must be created manually in AWS Console without running any setup script
    users_table = dynamodb.Table('InstantLibrary_Users')
    books_table = dynamodb.Table('InstantLibrary_Books')
    requests_table = dynamodb.Table('InstantLibrary_Requests')
    notifications_table = dynamodb.Table('InstantLibrary_Notifications')
    otp_table = dynamodb.Table('InstantLibrary_OTP')
    
    print("✅ AWS services initialized successfully (Manual Table Setup Required)")
except Exception as e:
    print(f"⚠️ AWS initialization error: {e}")
    print("Running in fallback mode - ensure AWS credentials are configured")

# ==================== HELPER FUNCTIONS ====================

def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password"""
    return hash_password(password) == hashed

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def generate_unique_id():
    """Generate a unique ID"""
    return str(uuid.uuid4())[:8]

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types from DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def convert_decimals(obj):
    """Recursively convert Decimal to int/float for JSON serialization"""
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

# ==================== SNS NOTIFICATION SERVICE ====================

def send_sns_notification(recipient_email, subject, message):
    """Send notification via AWS SNS"""
    try:
        if not SNS_TOPIC_ARN:
            print(f"📧 [SNS Disabled] Would send to {recipient_email}: {subject}")
            return True
        
        # Format HTML email
        html_body = generate_email_html(subject, message)
        
        # Publish to SNS Topic
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject[:100],  # SNS subject limit is 100 chars
            Message=json.dumps({
                'default': message,
                'email': html_body
            }),
            MessageStructure='json',
            MessageAttributes={
                'recipient': {
                    'DataType': 'String',
                    'StringValue': recipient_email
                }
            }
        )
        
        print(f"📧 [SNS] Sent to {recipient_email}: {subject}")
        return True
        
    except ClientError as e:
        print(f"❌ SNS Error: {e}")
        return False

def generate_email_html(subject, body_content):
    """Generate styled HTML email matching the app theme"""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0; padding:0; background-color: #f3f4f6; font-family: 'Inter', sans-serif;">
        <div style="max-width: 600px; margin: 40px auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%); padding: 32px 24px; text-align: center;">
                <h1 style="margin:0; color:white; font-size: 24px; font-weight: 800;">Instant Library</h1>
                <p style="margin:8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">Greenfield University</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 32px 24px;">
                <h2 style="margin-top:0; color: #111827; font-size: 20px;">{subject}</h2>
                <div style="color: #4B5563; line-height: 1.6; font-size: 16px;">
                    {body_content}
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #F9FAFB; padding: 20px; text-align: center; border-top: 1px solid #E5E7EB;">
                <p style="margin:0; color: #9CA3AF; font-size: 12px;">© {datetime.now().year} Greenfield University. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

# ==================== DYNAMODB OPERATIONS ====================

# --- Users ---
def get_user_by_email(email):
    """Get user from DynamoDB by email"""
    try:
        response = users_table.get_item(Key={'email': email.lower()})
        return convert_decimals(response.get('Item'))
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return None

def create_user(user_data):
    """Create user in DynamoDB"""
    try:
        user_data['email'] = user_data['email'].lower()
        user_data['created_at'] = datetime.now().isoformat()
        users_table.put_item(Item=user_data)
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

def update_user(email, updates):
    """Update user in DynamoDB"""
    try:
        update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
        expr_attr_names = {f"#{k}": k for k in updates.keys()}
        expr_attr_values = {f":{k}": v for k, v in updates.items()}
        
        users_table.update_item(
            Key={'email': email.lower()},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values
        )
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

def delete_user_by_email(email):
    """Delete user from DynamoDB"""
    try:
        users_table.delete_item(Key={'email': email.lower()})
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

def list_all_users(role_filter=None):
    """List all users from DynamoDB"""
    try:
        if role_filter:
            response = users_table.scan(
                FilterExpression='#role = :role',
                ExpressionAttributeNames={'#role': 'role'},
                ExpressionAttributeValues={':role': role_filter}
            )
        else:
            response = users_table.scan()
        
        users = convert_decimals(response.get('Items', []))
        # Remove passwords from response
        for user in users:
            user.pop('password', None)
        return users
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return []

# --- OTP ---
def store_otp(email, otp, used_for, pending_data=None):
    """Store OTP in DynamoDB with TTL"""
    try:
        item = {
            'email': email.lower(),
            'otp': otp,
            'timestamp': datetime.now().isoformat(),
            'verified': False,
            'used_for': used_for,
            'ttl': int((datetime.now() + timedelta(minutes=10)).timestamp())
        }
        if pending_data:
            item['pending_data'] = pending_data
        otp_table.put_item(Item=item)
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

def get_otp(email):
    """Get OTP from DynamoDB"""
    try:
        response = otp_table.get_item(Key={'email': email.lower()})
        return convert_decimals(response.get('Item'))
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return None

def delete_otp(email):
    """Delete OTP from DynamoDB"""
    try:
        otp_table.delete_item(Key={'email': email.lower()})
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

def update_otp_verified(email):
    """Mark OTP as verified"""
    try:
        otp_table.update_item(
            Key={'email': email.lower()},
            UpdateExpression='SET verified = :v',
            ExpressionAttributeValues={':v': True}
        )
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

# --- Books ---
def get_all_books(subject_filter=None, search_term=None):
    """Get all books from DynamoDB with optional filters"""
    try:
        response = books_table.scan()
        books = convert_decimals(response.get('Items', []))
        
        if subject_filter:
            books = [b for b in books if subject_filter.lower() in b.get('subject', '').lower()]
        
        if search_term:
            search_lower = search_term.lower()
            books = [b for b in books if 
                     search_lower in b.get('title', '').lower() or 
                     search_lower in b.get('author', '').lower()]
        
        return books
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return []

def get_book_by_id(book_id):
    """Get book from DynamoDB by ID"""
    try:
        response = books_table.get_item(Key={'id': str(book_id)})
        return convert_decimals(response.get('Item'))
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return None

def create_book(book_data):
    """Create book in DynamoDB"""
    try:
        book_data['id'] = str(book_data.get('id', generate_unique_id()))
        book_data['created_at'] = datetime.now().isoformat()
        books_table.put_item(Item=book_data)
        return book_data
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return None

def update_book_in_db(book_id, updates):
    """Update book in DynamoDB"""
    try:
        update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
        expr_attr_names = {f"#{k}": k for k in updates.keys()}
        expr_attr_values = {f":{k}": v for k, v in updates.items()}
        
        books_table.update_item(
            Key={'id': str(book_id)},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values
        )
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

def delete_book_from_db(book_id):
    """Delete book from DynamoDB"""
    try:
        books_table.delete_item(Key={'id': str(book_id)})
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

# --- Book Requests ---
def create_book_request(request_data):
    """Create book request in DynamoDB"""
    try:
        request_data['request_id'] = generate_unique_id()
        request_data['requested_at'] = datetime.now().isoformat()
        request_data['updated_at'] = datetime.now().isoformat()
        requests_table.put_item(Item=request_data)
        return request_data
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return None

def get_request_by_id(request_id):
    """Get book request from DynamoDB"""
    try:
        response = requests_table.get_item(Key={'request_id': str(request_id)})
        return convert_decimals(response.get('Item'))
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return None

def get_requests_by_email(email):
    """Get all requests for a user"""
    try:
        response = requests_table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email.lower()}
        )
        return convert_decimals(response.get('Items', []))
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return []

def get_all_requests():
    """Get all book requests"""
    try:
        response = requests_table.scan()
        return convert_decimals(response.get('Items', []))
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return []

def update_request_status(request_id, status):
    """Update request status in DynamoDB"""
    try:
        requests_table.update_item(
            Key={'request_id': str(request_id)},
            UpdateExpression='SET #status = :status, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': status,
                ':updated_at': datetime.now().isoformat()
            }
        )
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

def check_pending_request_exists(email, book_id):
    """Check if user has pending request for a book"""
    try:
        response = requests_table.scan(
            FilterExpression='email = :email AND book_id = :book_id AND #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':email': email.lower(),
                ':book_id': str(book_id),
                ':status': 'pending'
            }
        )
        return len(response.get('Items', [])) > 0
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

# --- Notifications ---
def create_notification(recipient, message, notif_type='info'):
    """Create notification in DynamoDB"""
    try:
        notif_id = generate_unique_id()
        notifications_table.put_item(Item={
            'id': notif_id,
            'recipient': recipient.lower(),
            'message': message,
            'type': notif_type,
            'read': False,
            'timestamp': datetime.now().isoformat()
        })
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

def get_notifications_for_user(email):
    """Get notifications for a user"""
    try:
        response = notifications_table.scan(
            FilterExpression='recipient = :email',
            ExpressionAttributeValues={':email': email.lower()}
        )
        notifs = convert_decimals(response.get('Items', []))
        return sorted(notifs, key=lambda x: x.get('timestamp', ''), reverse=True)
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return []

def mark_notification_as_read(notif_id):
    """Mark notification as read"""
    try:
        notifications_table.update_item(
            Key={'id': notif_id},
            UpdateExpression='SET #read = :read',
            ExpressionAttributeNames={'#read': 'read'},
            ExpressionAttributeValues={':read': True}
        )
        return True
    except ClientError as e:
        print(f"DynamoDB Error: {e}")
        return False

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/register/student', methods=['POST'])
def register_student():
    """Register a new student"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        roll_no = data.get('roll_no', '').strip()
        semester = data.get('semester', '').strip()
        year = data.get('year', '').strip()
        
        # Validation
        if not email or not password or not name:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if get_user_by_email(email):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Generate and store OTP
        otp = generate_otp()
        pending_data = {
            'email': email,
            'password': password,
            'name': name,
            'role': 'student',
            'roll_no': roll_no,
            'semester': semester,
            'year': year
        }
        
        store_otp(email, otp, 'registration', pending_data)
        
        # Send OTP via SNS
        send_sns_notification(
            email,
            "Your Verification OTP",
            f"Your OTP for registration is: <strong>{otp}</strong><br><br>This OTP is valid for 10 minutes."
        )
        
        return jsonify({
            'message': 'OTP sent to email. Please verify to complete registration.',
            'email': email
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-registration-otp', methods=['POST'])
def verify_registration_otp():
    """Verify OTP for registration"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP required'}), 400
        
        stored_otp = get_otp(email)
        
        if not stored_otp:
            return jsonify({'error': 'OTP not found. Please register again.'}), 400
        
        # Check if OTP is expired (10 minutes)
        otp_time = datetime.fromisoformat(stored_otp['timestamp'])
        if (datetime.now() - otp_time).seconds > 600:
            delete_otp(email)
            return jsonify({'error': 'OTP expired. Please register again.'}), 400
        
        if stored_otp['otp'] != otp:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        pending_data = stored_otp.get('pending_data')
        if not pending_data:
            return jsonify({'error': 'No pending registration found'}), 400
        
        # Create user account
        user_data = {
            'email': email,
            'password': hash_password(pending_data['password']),
            'name': pending_data['name'],
            'role': pending_data['role'],
            'roll_no': pending_data.get('roll_no', ''),
            'semester': pending_data.get('semester', ''),
            'year': pending_data.get('year', ''),
            'verified': True
        }
        
        if create_user(user_data):
            delete_otp(email)
            
            # Notify Admin of new registration
            send_sns_notification(
                'admin@library.com',
                f"New Registration: {email}",
                f"New student registered:<br>Name: <strong>{pending_data['name']}</strong><br>Email: {email}<br>Role: {pending_data['role']}"
            )

            return jsonify({
                'message': 'Registration completed successfully!',
                'email': email,
                'role': pending_data['role']
            }), 201
        else:
            return jsonify({'error': 'Failed to create account'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/register-staff', methods=['POST'])
def register_staff_by_staff():
    """Register a new staff member (requires caller to be staff)"""
    try:
        data = request.json
        caller_email = data.get('caller_email', '').strip().lower()
        new_email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not caller_email or not new_email or not password or not name:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Verify caller is staff
        caller = get_user_by_email(caller_email)
        if not caller or caller.get('role') != 'staff':
            return jsonify({'error': 'Only staff can register other staff'}), 403
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if get_user_by_email(new_email):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create staff account directly
        user_data = {
            'email': new_email,
            'password': hash_password(password),
            'name': name,
            'role': 'staff',
            'verified': True
        }
        
        if create_user(user_data):
            # Notify Admin
            send_sns_notification(
                'admin@library.com',
                f"New Staff Added: {new_email}",
                f"New staff member added by {caller_email}:<br>Name: <strong>{name}</strong><br>Email: {new_email}"
            )

            return jsonify({
                'message': 'Staff account created successfully',
                'email': new_email,
                'name': name,
                'role': 'staff'
            }), 201
        else:
            return jsonify({'error': 'Failed to create account'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login with email and password"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not verify_password(password, user['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Send Login Notification
        send_sns_notification(
            'admin@library.com',
            f"Login Alert: {email}",
            f"User <strong>{user.get('name')}</strong> ({email}) logged in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        )

        return jsonify({
            'message': 'Login successful',
            'email': email,
            'name': user['name'],
            'role': user['role'],
            'roll_no': user.get('roll_no', ''),
            'semester': user.get('semester', ''),
            'year': user.get('year', '')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    """Update user profile"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        name = data.get('name', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        updates = {}
        if name:
            updates['name'] = name
        
        if user.get('role') == 'student':
            if 'roll_no' in data:
                updates['roll_no'] = data['roll_no']
            if 'semester' in data:
                updates['semester'] = data['semester']
            if 'year' in data:
                updates['year'] = data['year']
        
        if updates:
            update_user(email, updates)
        
        updated_user = get_user_by_email(email)
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'email': updated_user['email'],
                'name': updated_user.get('name', ''),
                'role': updated_user.get('role', ''),
                'roll_no': updated_user.get('roll_no', ''),
                'semester': updated_user.get('semester', ''),
                'year': updated_user.get('year', '')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset OTP"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = get_user_by_email(email)
        if not user:
            # Don't reveal if email exists
            return jsonify({'message': 'If email exists, OTP has been sent'}), 200
        
        otp = generate_otp()
        store_otp(email, otp, 'password_reset')
        
        send_sns_notification(
            email,
            "Password Reset OTP",
            f"Your OTP for password reset is: <strong>{otp}</strong><br><br>This OTP is valid for 10 minutes."
        )
        
        return jsonify({'message': 'OTP sent to email'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-forgot-password-otp', methods=['POST'])
def verify_forgot_password_otp():
    """Verify OTP for password reset"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP required'}), 400
        
        stored_otp = get_otp(email)
        if not stored_otp:
            return jsonify({'error': 'OTP not found. Please request again.'}), 400
        
        otp_time = datetime.fromisoformat(stored_otp['timestamp'])
        if (datetime.now() - otp_time).seconds > 600:
            delete_otp(email)
            return jsonify({'error': 'OTP expired. Please request again.'}), 400
        
        if stored_otp['otp'] != otp:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        update_otp_verified(email)
        return jsonify({'message': 'OTP verified. You can now reset your password.'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Reset password after OTP verification"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        new_password = data.get('new_password', '')
        
        if not email or not new_password:
            return jsonify({'error': 'Email and new password required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        stored_otp = get_otp(email)
        if not stored_otp or not stored_otp.get('verified'):
            return jsonify({'error': 'Please verify OTP first'}), 400
        
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        update_user(email, {'password': hash_password(new_password)})
        delete_otp(email)
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Change password for logged-in user"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        current_password = data.get('currentPassword', '')
        new_password = data.get('newPassword', '')
        
        if not email or not current_password or not new_password:
            return jsonify({'error': 'All fields required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not verify_password(current_password, user['password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        update_user(email, {'password': hash_password(new_password)})
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== BOOK ROUTES ====================

@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books with search and filter"""
    try:
        subject = request.args.get('subject', '').strip()
        search = request.args.get('search', '').strip()
        
        books = get_all_books(subject, search)
        return jsonify(books), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book"""
    try:
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        return jsonify(book), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books', methods=['POST'])
def add_book():
    """Add a new book (staff only)"""
    try:
        data = request.json
        staff_email = data.get('staff_email', '').strip().lower()
        
        user = get_user_by_email(staff_email)
        if not user or user.get('role') != 'staff':
            return jsonify({'error': 'Unauthorized. Only staff can add books'}), 403
        
        title = data.get('title', '').strip()
        author = data.get('author', '').strip()
        subject = data.get('subject', '').strip()
        
        if not title or not author or not subject:
            return jsonify({'error': 'Title, author, and subject are required'}), 400
        
        quantity = int(data.get('quantity', 1))
        isbn = data.get('isbn', '').strip()
        book_id = generate_unique_id()
        
        # Generate copy IDs
        copies = [f"{isbn or book_id}-{str(i).zfill(3)}" for i in range(1, quantity + 1)]
        
        book_data = {
            'id': book_id,
            'title': title,
            'author': author,
            'subject': subject,
            'description': data.get('description', '').strip(),
            'year': data.get('year', datetime.now().year),
            'available_count': quantity,
            'total_count': quantity,
            'pdf_url': data.get('pdf_url', ''),
            'isbn': isbn,
            'cover_image': data.get('cover_image', ''),
            'copies': copies
        }
        
        result = create_book(book_data)
        if result:
            return jsonify({'message': 'Book added successfully', 'book': result}), 201
        else:
            return jsonify({'error': 'Failed to add book'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """Update book details (staff only)"""
    try:
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        data = request.json
        staff_email = data.get('staff_email', '').strip().lower()
        
        user = get_user_by_email(staff_email)
        if not user or user.get('role') != 'staff':
            return jsonify({'error': 'Unauthorized. Only staff can update books'}), 403
        
        updates = {}
        for field in ['title', 'author', 'subject', 'description', 'year', 'pdf_url', 'isbn', 'cover_image']:
            if field in data:
                updates[field] = data[field]
        
        # Handle quantity changes
        if 'total_count' in data:
            new_total = int(data['total_count'])
            current_total = book.get('total_count', 0)
            diff = new_total - current_total
            
            updates['total_count'] = new_total
            updates['available_count'] = max(0, book.get('available_count', 0) + diff)
            
            # Update copies
            copies = book.get('copies', [])
            base_id = book.get('isbn') or book_id
            
            if diff > 0:
                max_idx = len(copies)
                for i in range(diff):
                    copies.append(f"{base_id}-{str(max_idx + i + 1).zfill(3)}")
            elif diff < 0:
                copies = copies[:max(0, len(copies) + diff)]
            
            updates['copies'] = copies
        
        if updates:
            update_book_in_db(book_id, updates)
        
        updated_book = get_book_by_id(book_id)
        return jsonify({'message': 'Book updated successfully', 'book': updated_book}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book (staff only)"""
    try:
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        data = request.json or {}
        staff_email = data.get('staff_email', '').strip().lower()
        
        user = get_user_by_email(staff_email)
        if not user or user.get('role') != 'staff':
            return jsonify({'error': 'Unauthorized. Only staff can delete books'}), 403
        
        delete_book_from_db(book_id)
        return jsonify({'message': 'Book deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== BOOK REQUEST ROUTES ====================

@app.route('/api/requests', methods=['POST'])
def create_request_route():
    """Create a book request"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        book_id = data.get('book_id')
        
        if not email or not book_id:
            return jsonify({'error': 'Email and Book ID required'}), 400
        
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check for existing pending request
        if check_pending_request_exists(email, book_id):
            return jsonify({'error': 'You already have a pending request for this book'}), 400
        
        request_data = {
            'email': email,
            'sender': user.get('name', ''),
            'book_id': str(book_id),
            'book_name': book.get('title', ''),
            'author': book.get('author', ''),
            'subject': book.get('subject', ''),
            'description': book.get('description', ''),
            'status': 'pending',
            'roll_no': data.get('roll_no', user.get('roll_no', '')),
            'semester': data.get('semester', user.get('semester', '')),
            'year': data.get('year', user.get('year', ''))
        }
        
        result = create_book_request(request_data)
        
        if result:
            # Notify student
            send_sns_notification(
                email,
                f"Request Received: {book.get('title')}",
                f"Dear {user.get('name')},<br><br>Your request for '<strong>{book.get('title')}</strong>' has been received and is currently <strong>Pending</strong>.<br><br>Thank you,<br>Greenfield Library"
            )
            create_notification(email, f"Request submitted for '{book.get('title')}'", 'info')
            
            # Notify staff (Admin)
            send_sns_notification(
                'admin@library.com',
                f"New Book Request: {book.get('title')}",
                f"Student <strong>{user.get('name')}</strong> has requested '<strong>{book.get('title')}</strong>'.<br>Roll No: {request_data.get('roll_no', 'N/A')}<br>Status: Pending"
            )
            create_notification('admin@library.com', f"New request from {user.get('name')} for '{book.get('title')}'", 'info')
            
            return jsonify({
                'message': 'Request submitted successfully',
                'request_id': result.get('request_id')
            }), 201
        else:
            return jsonify({'error': 'Failed to create request'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requests/<request_id>', methods=['GET'])
def get_request_route(request_id):
    """Get a specific request"""
    try:
        req = get_request_by_id(request_id)
        if not req:
            return jsonify({'error': 'Request not found'}), 404
        return jsonify(req), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-requests/<email>', methods=['GET'])
def get_user_requests_route(email):
    """Get all requests for a user"""
    try:
        email = email.strip().lower()
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        requests = get_requests_by_email(email)
        return jsonify(requests), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/all-requests', methods=['GET'])
def get_all_requests_route():
    """Get all requests (staff only)"""
    try:
        staff_email = request.args.get('staff_email', '').strip().lower()
        
        user = get_user_by_email(staff_email)
        if not user or user.get('role') != 'staff':
            return jsonify({'error': 'Unauthorized. Only staff can view all requests'}), 403
        
        all_requests = get_all_requests()
        return jsonify(all_requests), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requests/<request_id>', methods=['PUT'])
def update_request_route(request_id):
    """Update request status"""
    try:
        req = get_request_by_id(request_id)
        if not req:
            return jsonify({'error': 'Request not found'}), 404
        
        data = request.json
        status = data.get('status', '').strip()
        
        if status not in ['pending', 'approved', 'rejected', 'completed']:
            return jsonify({'error': 'Invalid status'}), 400
        
        old_status = req.get('status')
        book_id = req.get('book_id')
        book = get_book_by_id(book_id)
        
        # Stock management
        if book and old_status != status:
            available = book.get('available_count', 0)
            total = book.get('total_count', 0)
            
            if old_status == 'pending' and status == 'approved':
                if available > 0:
                    update_book_in_db(book_id, {'available_count': available - 1})
                else:
                    return jsonify({'error': 'Cannot approve: Book is out of stock'}), 400
            
            elif old_status == 'approved' and status in ['rejected', 'completed']:
                update_book_in_db(book_id, {'available_count': min(available + 1, total)})
            
            elif old_status in ['rejected', 'completed'] and status == 'approved':
                if available > 0:
                    update_book_in_db(book_id, {'available_count': available - 1})
                else:
                    return jsonify({'error': 'Cannot approve: Book is out of stock'}), 400
        
        update_request_status(request_id, status)
        
        # Notify student on status change
        if old_status != status:
            send_sns_notification(
                req.get('email'),
                f"Request Update: {req.get('book_name')}",
                f"Your request for '<strong>{req.get('book_name')}</strong>' has been updated to: <strong>{status.upper()}</strong>."
            )
            create_notification(
                req.get('email'),
                f"Request for '{req.get('book_name')}' is now {status.upper()}",
                'info'
            )
            
            # Notify Admin of status change
            send_sns_notification(
                'admin@library.com',
                f"Request Processed: {req.get('book_name')}",
                f"Request for '<strong>{req.get('book_name')}</strong>' was marked as <strong>{status.upper()}</strong>.<br>Student: {req.get('email')}"
            )
        
        updated_request = get_request_by_id(request_id)
        updated_book = get_book_by_id(book_id)
        
        return jsonify({
            'message': 'Request updated',
            'request': updated_request,
            'book_available': updated_book.get('available_count') if updated_book else 'N/A'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== NOTIFICATION ROUTES ====================

@app.route('/api/notifications', methods=['GET'])
def get_notifications_route():
    """Get notifications for a user"""
    try:
        email = request.args.get('email', '').strip().lower()
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        notifs = get_notifications_for_user(email)
        return jsonify(notifs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<notif_id>/read', methods=['PUT'])
def mark_notification_read_route(notif_id):
    """Mark notification as read"""
    try:
        mark_notification_as_read(notif_id)
        return jsonify({'message': 'Marked as read'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== USER MANAGEMENT ROUTES ====================

@app.route('/api/users', methods=['GET'])
def list_users_route():
    """List all users or filter by role"""
    try:
        role = request.args.get('role')
        users = list_all_users(role)
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<email>', methods=['DELETE'])
def delete_user_route(email):
    """Delete a user by email (staff only)"""
    try:
        staff_email = request.args.get('staff_email', '').strip().lower()
        
        requester = get_user_by_email(staff_email)
        if not requester or requester.get('role') != 'staff':
            return jsonify({'error': 'Unauthorized'}), 403
        
        email = email.lower()
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.get('role') == 'staff':
            return jsonify({'error': 'Cannot delete staff accounts via this endpoint'}), 403
        
        delete_user_by_email(email)
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== CHATBOT ROUTES ====================

@app.route('/api/chat', methods=['POST'])
def chat_bot():
    """Chat with AI Assistant"""
    try:
        import google.generativeai as genai
        
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not GEMINI_API_KEY:
            return jsonify({
                'response': "I'm sorry, my AI brain is currently offline. Please configure GEMINI_API_KEY in AWS_app.py."
            }), 200
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Get book catalog for context
        books = get_all_books()
        book_list_text = "Here is the current library catalog:\n"
        for book in books:
            status = "Available" if book.get('available_count', 0) > 0 else "Out of stock"
            book_list_text += f"- {book.get('title')} by {book.get('author')} ({status}, {book.get('available_count', 0)} copies left)\n"
        
        context = f"""
        You are a helpful library assistant for Greenfield University.
        You help students find books, understand library rules, and track their requests.
        Be polite, concise, and professional.
        
        {book_list_text}
        
        If a student asks for a book, check the list above. If it's not listed, say we don't have it.
        """
        
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{context}\nUser: {user_message}")
        
        return jsonify({'response': response.text}), 200
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'response': f"Error: {str(e)}"}), 200

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Test DynamoDB connection
        users_table.table_status
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 200

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def root():
    """Serve index page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve any static file"""
    return send_from_directory(app.static_folder, path)

@app.route('/login')
def login_page():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/register')
def register_page():
    return send_from_directory(app.static_folder, 'register.html')

@app.route('/dashboard')
def dashboard_page():
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/catalog')
def catalog_page():
    return send_from_directory(app.static_folder, 'catalog.html')

@app.route('/requests')
def requests_page():
    return send_from_directory(app.static_folder, 'requests.html')

@app.route('/profile')
def profile_page():
    return send_from_directory(app.static_folder, 'profile.html')

@app.route('/notifications')
def notifications_page():
    return send_from_directory(app.static_folder, 'notifications.html')

@app.route('/settings')
def settings_page():
    return send_from_directory(app.static_folder, 'settings.html')

@app.route('/support')
def support_page():
    return send_from_directory(app.static_folder, 'support.html')

@app.route('/about')
def about_page():
    return send_from_directory(app.static_folder, 'about.html')

@app.route('/terms')
def terms_page():
    return send_from_directory(app.static_folder, 'terms.html')

@app.route('/privacy')
def privacy_page():
    return send_from_directory(app.static_folder, 'privacy.html')

# Staff Pages
@app.route('/staff-login')
def staff_login_page():
    return send_from_directory(app.static_folder, 'staff-login.html')

@app.route('/book-management')
def book_management_page():
    return send_from_directory(app.static_folder, 'book-management.html')

@app.route('/request-management')
def request_management_page():
    return send_from_directory(app.static_folder, 'request-management.html')

@app.route('/staff-management')
def staff_management_page():
    return send_from_directory(app.static_folder, 'staff-management.html')

@app.route('/student-management')
def student_management_page():
    return send_from_directory(app.static_folder, 'student-management.html')

@app.route('/forgot-password')
def forgot_password_page():
    return send_from_directory(app.static_folder, 'forgot-password.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, '404.html'), 404

# ==================== APPLICATION ENTRY POINT ====================

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # For production (gunicorn)
    # Run with: gunicorn -w 4 -b 0.0.0.0:5000 AWS_app:app
    pass
