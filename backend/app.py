from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import hashlib
import os
import random
import string
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# In-memory storage (for local development only)
users_db = {}
book_requests_db = {}
otp_store = {}  # Store OTPs: {email: {otp: "123456", timestamp: datetime, verified: False, used_for: "registration/password_reset"}}
pending_registrations = {}  # Store pending registrations: {email: {data}}
notifications_db = {} # Store notifications: {id: {id, recipient, message, type, read, timestamp}}
notification_id_counter = 1

books_db = {
    1: {
        "id": 1, 
        "title": "Introduction to Algorithms", 
        "author": "Thomas H. Cormen", 
        "subject": "Computer Science", 
        "description": "A comprehensive guide to algorithms and data structures", 
        "year": 2009, 
        "available_count": 3, 
        "total_count": 5, 
        "isbn": "978-0262033848",
        "cover_image": "https://m.media-amazon.com/images/I/41SNoh5ZhOL._SY264_BO1,204,203,200_QL40_ML2_.jpg",
        "copies": ["978-0262033848-001", "978-0262033848-002", "978-0262033848-003", "978-0262033848-004", "978-0262033848-005"],
        "pdf_url": "https://example.com/algorithms.pdf"
    },
    2: {
        "id": 2, 
        "title": "Data Science Handbook", 
        "author": "Jake VanderPlas", 
        "subject": "Data Science", 
        "description": "A practical guide to data science with Python", 
        "year": 2016, 
        "available_count": 2, 
        "total_count": 3,
        "isbn": "978-1491912058",
        "cover_image": "https://m.media-amazon.com/images/I/516C1yC59fL._SX218_BO1,204,203,200_QL40_ML2_.jpg",
        "copies": ["978-1491912058-001", "978-1491912058-002", "978-1491912058-003"]
    },
    3: {
        "id": 3, 
        "title": "Web Development with Flask", 
        "author": "Miguel Grinberg", 
        "subject": "Web Development", 
        "description": "Learn web development using Flask framework", 
        "year": 2018, 
        "available_count": 0, 
        "total_count": 2,
        "isbn": "978-1491991732",
        "cover_image": "https://m.media-amazon.com/images/I/41w8B3w-CPL._SX379_BO1,204,203,200_.jpg",
        "copies": ["978-1491991732-001", "978-1491991732-002"]
    },
    4: {
        "id": 4, 
        "title": "Cloud Computing Basics", 
        "author": "Tom Bowers", 
        "subject": "Cloud Computing", 
        "description": "Introduction to cloud computing and AWS", 
        "year": 2020, 
        "available_count": 4, 
        "total_count": 4,
        "isbn": "978-1234567890",
        "cover_image": "https://m.media-amazon.com/images/I/41-s7S+wFPL._SY346_.jpg",
        "copies": ["978-1234567890-001", "978-1234567890-002", "978-1234567890-003", "978-1234567890-004"]
    },
    5: {
        "id": 5, 
        "title": "Database Design", 
        "author": "C.J. Date", 
        "subject": "Databases", 
        "description": "Best practices in database design and normalization", 
        "year": 2015, 
        "available_count": 1, 
        "total_count": 3,
        "isbn": "978-0321295359",
        "cover_image": "https://m.media-amazon.com/images/I/41+7+G+k06L._SL500_.jpg",
        "copies": ["978-0321295359-001", "978-0321295359-002", "978-0321295359-003"]
    },
    6: {
        "id": 6, 
        "title": "Python Programming", 
        "author": "Guido van Rossum", 
        "subject": "Programming", 
        "description": "Complete guide to Python programming language", 
        "year": 2021, 
        "available_count": 5, 
        "total_count": 5,
        "isbn": "978-0321200000",
        "cover_image": "https://m.media-amazon.com/images/I/41oGkQd3T3L._SX385_BO1,204,203,200_.jpg",
        "copies": ["978-0321200000-001", "978-0321200000-002", "978-0321200000-003", "978-0321200000-004", "978-0321200000-005"]
    },
    7: {
        "id": 7, 
        "title": "Machine Learning Basics", 
        "author": "Andrew Ng", 
        "subject": "Machine Learning", 
        "description": "Introduction to machine learning and AI", 
        "year": 2019, 
        "available_count": 2, 
        "total_count": 4,
        "isbn": "978-0321300000",
        "cover_image": "https://m.media-amazon.com/images/I/51w+S6u0VLL._SX379_BO1,204,203,200_.jpg",
        "copies": ["978-0321300000-001", "978-0321300000-002", "978-0321300000-003", "978-0321300000-004"]
    },
}

next_book_id = 8

request_id_counter = 1

def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password"""
    return hash_password(password) == hashed

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def print_otp_to_terminal(email, otp):
    """Print OTP to terminal (for development only)"""
    # Generate formatted HTML just for show/logging
    html_body = f"""
    <p>Your One-Time Password (OTP) for registration/verification is:</p>
    <div style="background: #EEF2FF; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
        <span style="font-size: 32px; font-weight: 800; color: #4F46E5; letter-spacing: 4px;">{otp}</span>
    </div>
    <p>This OTP is valid for 10 minutes. Do not share it with anyone.</p>
    """
    html_content = generate_email_html("Verification OTP", html_body, action_text="Verify Account", action_url="#")
    
    print(f"\n{'='*60}")
    print(f"🔐 SIMULATED EMAIL TO: {email}")
    print(f"SUBJECT: Verification OTP")
    print(f"CONTENT: {otp}")
    print(f"HTML PREDVIEW GENERATED (See sns_logs.txt for full output)")
    print(f"{'='*60}\n")
    
    # Also log to file for "viewing"
    with open("sns_logs.txt", "a", encoding='utf-8') as f:
        f.write(f"\n[OTP ENTRY]\n{html_content}\n{'-'*60}\n")

def user_exists_by_email(email):
    """Check if user exists by email"""
    for user in users_db.values():
        if user['email'] == email:
            return True
    return False

def get_user_by_email(email):
    """Get user by email"""
    for user_id, user in users_db.items():
        if user['email'] == email:
            return user
    return None

# Pre-register staff account for initial access (staff@gmail.com / 123456)
users_db['staff@gmail.com'] = {
    'email': 'staff@gmail.com',
    'password': hash_password('123456'),
    'name': 'Staff Member',
    'role': 'staff',
    'verified': True,
    'created_at': datetime.now().isoformat()
}

# Pre-register student account for initial access (student@gmail.com / 123456)
users_db['student@gmail.com'] = {
    'email': 'student@gmail.com',
    'password': hash_password('123456'),
    'name': 'Student Member',
    'role': 'student',
    'roll_no': 'S101',
    'semester': '1',
    'year': '1',
    'verified': True,
    'created_at': datetime.now().isoformat()
}

# ==================== AUTHENTICATION ROUTES ====================

# Student Registration
@app.route('/api/register/student', methods=['POST'])
def register_student():
    """Register a new student"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # New fields for student details
        roll_no = data.get('roll_no', '').strip()
        semester = data.get('semester', '').strip()
        year = data.get('year', '').strip()
        
        # Validation
        if not email or not password or not name:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if user_exists_by_email(email):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Generate OTP
        otp = generate_otp()
        print_otp_to_terminal(email, otp)
        
        # Store OTP and pending registration
        otp_store[email] = {
            'otp': otp,
            'timestamp': datetime.now(),
            'verified': False,
            'used_for': 'registration'
        }
        
        pending_registrations[email] = {
            'email': email,
            'password': password,
            'name': name,
            'role': 'student',
            'roll_no': roll_no,
            'semester': semester,
            'year': year
        }
        
        return jsonify({
            'message': 'OTP sent to email. Please verify to complete registration.',
            'email': email
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Verify Registration OTP
@app.route('/api/verify-registration-otp', methods=['POST'])
def verify_registration_otp():
    """Verify OTP for registration"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP required'}), 400
        
        if email not in otp_store:
            return jsonify({'error': 'OTP not found. Please register again.'}), 400
        
        stored_otp_data = otp_store[email]
        
        # Check if OTP is expired (10 minutes)
        if (datetime.now() - stored_otp_data['timestamp']).seconds > 600:
            del otp_store[email]
            if email in pending_registrations:
                del pending_registrations[email]
            return jsonify({'error': 'OTP expired. Please register again.'}), 400
        
        if stored_otp_data['otp'] != otp:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        if email not in pending_registrations:
            return jsonify({'error': 'No pending registration found'}), 400
        
        # Create user account
        reg_data = pending_registrations[email]
        users_db[email] = {
            'email': email,
            'password': hash_password(reg_data['password']),
            'name': reg_data['name'],
            'role': reg_data['role'],
            'roll_no': reg_data.get('roll_no', ''),
            'semester': reg_data.get('semester', ''),
            'year': reg_data.get('year', ''),
            'verified': True,
            'created_at': datetime.now().isoformat()
        }
        
        # Cleanup
        del otp_store[email]
        del pending_registrations[email]
        
        return jsonify({
            'message': 'Registration completed successfully!',
            'email': email,
            'role': reg_data['role']
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Staff Register Other Staff
@app.route('/api/admin/register-staff', methods=['POST'])
def register_staff_by_staff():
    """Register a new staff member (requires caller to be staff)"""
    try:
        data = request.json
        caller_email = data.get('caller_email', '').strip().lower()
        new_email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # Validation
        if not caller_email or not new_email or not password or not name:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Verify caller is staff
        caller = get_user_by_email(caller_email)
        if not caller:
            return jsonify({'error': 'Caller not found'}), 401
        
        if caller['role'] != 'staff':
            return jsonify({'error': 'Only staff can register other staff'}), 403
        
        # Validate new staff account
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if user_exists_by_email(new_email):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create staff account directly (no OTP needed for staff-to-staff registration)
        users_db[new_email] = {
            'email': new_email,
            'password': hash_password(password),
            'name': name,
            'role': 'staff',
            'verified': True,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'message': 'Staff account created successfully',
            'email': new_email,
            'name': name,
            'role': 'staff'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Login with Email
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

# Update Profile logic
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
            
        # Update allowed fields
        if name:
            user['name'] = name
            
        if user['role'] == 'student':
            user['roll_no'] = data.get('roll_no', user.get('roll_no', ''))
            user['semester'] = data.get('semester', user.get('semester', ''))
            user['year'] = data.get('year', user.get('year', ''))
            
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                'roll_no': user.get('roll_no', ''),
                'semester': user.get('semester', ''),
                'year': user.get('year', '')
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Request Forgot Password OTP
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
            # Don't reveal if email exists (security best practice)
            return jsonify({'message': 'If email exists, OTP has been sent'}), 200
        
        # Generate OTP
        otp = generate_otp()
        print_otp_to_terminal(email, otp)
        
        otp_store[email] = {
            'otp': otp,
            'timestamp': datetime.now(),
            'verified': False,
            'used_for': 'password_reset'
        }
        
        return jsonify({'message': 'OTP sent to email'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Verify Forgot Password OTP
@app.route('/api/verify-forgot-password-otp', methods=['POST'])
def verify_forgot_password_otp():
    """Verify OTP for password reset"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP required'}), 400
        
        if email not in otp_store:
            return jsonify({'error': 'OTP not found. Please request again.'}), 400
        
        stored_otp_data = otp_store[email]
        
        # Check if OTP is expired (10 minutes)
        if (datetime.now() - stored_otp_data['timestamp']).seconds > 600:
            del otp_store[email]
            return jsonify({'error': 'OTP expired. Please request again.'}), 400
        
        if stored_otp_data['otp'] != otp:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        # Mark as verified but don't delete yet
        otp_store[email]['verified'] = True
        
        return jsonify({'message': 'OTP verified. You can now reset your password.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Reset Password
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
        
        if email not in otp_store or not otp_store[email]['verified']:
            return jsonify({'error': 'Please verify OTP first'}), 400
        
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user['password'] = hash_password(new_password)
        
        # Cleanup OTP
        del otp_store[email]
        
        return jsonify({'message': 'Password reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Change Password (Logged-in User)
@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Change password for logged-in user"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        current_password = data.get('currentPassword', '')
        new_password = data.get('newPassword', '')
        
        if not email or not current_password or not new_password:
            return jsonify({'error': 'Email, current password, and new password required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not verify_password(current_password, user['password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        user['password'] = hash_password(new_password)
        
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== BOOK ROUTES ====================

@app.route('/api/books', methods=['GET'])
def get_books():
    """Get all books with search and filter"""
    try:
        subject = request.args.get('subject', '').strip()
        search = request.args.get('search', '').strip().lower()
        
        books = list(books_db.values())
        
        if subject:
            books = [b for b in books if subject.lower() in b['subject'].lower()]
        
        if search:
            books = [b for b in books if search in b['title'].lower() or search in b['author'].lower()]
        
        return jsonify(books), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book"""
    try:
        if book_id not in books_db:
            return jsonify({'error': 'Book not found'}), 404
        
        return jsonify(books_db[book_id]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books', methods=['POST'])
def add_book():
    """Add a new book (staff only)"""
    global next_book_id
    try:
        data = request.json
        staff_email = data.get('staff_email', '').strip().lower()
        
        # Verify staff user
        user = get_user_by_email(staff_email)
        if not user or user['role'] != 'staff':
            return jsonify({'error': 'Unauthorized. Only staff can add books'}), 403
        
        title = data.get('title', '').strip()
        author = data.get('author', '').strip()
        subject = data.get('subject', '').strip()
        description = data.get('description', '').strip()
        year = data.get('year', datetime.now().year)
        quantity = int(data.get('quantity', 1))
        isbn = data.get('isbn', '').strip()
        
        if not title or not author or not subject:
            return jsonify({'error': 'Title, author, and subject are required'}), 400
        
        # Generate copies
        copies = []
        base_id = isbn if isbn else f"BK{next_book_id}"
        for i in range(1, quantity + 1):
            copies.append(f"{base_id}-{str(i).zfill(3)}")

        new_book = {
            'id': next_book_id,
            'title': title,
            'author': author,
            'subject': subject,
            'description': description,
            'year': year,
            'available_count': quantity,
            'total_count': quantity,
            'pdf_url': data.get('pdf_url', ''),
            'isbn': isbn,
            'cover_image': data.get('cover_image', ''),
            'copies': copies
        }
        
        books_db[next_book_id] = new_book
        next_book_id += 1
        
        return jsonify({'message': 'Book added successfully', 'book': new_book}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update book details (staff only)"""
    try:
        if book_id not in books_db:
            return jsonify({'error': 'Book not found'}), 404
        
        data = request.json
        staff_email = data.get('staff_email', '').strip().lower()
        
        # Verify staff user
        user = get_user_by_email(staff_email)
        if not user or user['role'] != 'staff':
            return jsonify({'error': 'Unauthorized. Only staff can update books'}), 403
        
        book = books_db[book_id]
        
        if 'title' in data:
            book['title'] = data['title']
        if 'author' in data:
            book['author'] = data['author']
        if 'subject' in data:
            book['subject'] = data['subject']
        if 'description' in data:
            book['description'] = data['description']
        if 'year' in data:
            book['year'] = data['year']
        if 'pdf_url' in data:
            book['pdf_url'] = data['pdf_url']
        if 'isbn' in data:
            # If ISBN changes, we ideally regenerate copies? 
            # For simplicity, we keep existing IDs unless user manually resets?
            # Or we can just update the stored ISBN for reference.
            book['isbn'] = data['isbn']
        if 'cover_image' in data:
            book['cover_image'] = data['cover_image']
            
        # Update counts and copies logic
        if 'total_count' in data:
            new_total = int(data['total_count'])
            current_total = book['total_count']
            
            # Update available count relatively
            diff = new_total - current_total
            book['available_count'] += diff
            book['total_count'] = new_total
            
            # Update copies list
            current_copies = book.get('copies', [])
            # In case copies wasn't initialized cleanly before
            if not current_copies:
                 # Generate from scratch if missing
                 base_id = book['isbn'] if book['isbn'] else f"BK{book_id}"
                 current_copies = [f"{base_id}-{str(i+1).zfill(3)}" for i in range(current_total)]

            if diff > 0:
                # Add new copies
                base_id = book['isbn'] if book['isbn'] else f"BK{book_id}"
                # Find maximum existing index to append correctly
                max_idx = 0
                for cp in current_copies:
                    try:
                        # try to parse suffix 
                        parts = cp.rsplit('-', 1)
                        if len(parts) == 2 and parts[1].isdigit():
                            idx = int(parts[1])
                            if idx > max_idx: max_idx = idx
                    except:
                        pass
                
                start_idx = max_idx + 1
                for i in range(diff):
                    current_copies.append(f"{base_id}-{str(start_idx + i).zfill(3)}")
            elif diff < 0:
                # Remove copies from the end (LIFO for reduction)
                # Ensure we don't go below zero
                remove_count = abs(diff)
                if remove_count < len(current_copies):
                    current_copies = current_copies[:-remove_count]
                else:
                    current_copies = []

            book['copies'] = current_copies

        return jsonify({'message': 'Book updated successfully', 'book': book}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book (staff only)"""
    try:
        if book_id not in books_db:
            return jsonify({'error': 'Book not found'}), 404
        
        data = request.json or {}
        staff_email = data.get('staff_email', '').strip().lower()
        
        # Verify staff user
        user = get_user_by_email(staff_email)
        if not user or user['role'] != 'staff':
            return jsonify({'error': 'Unauthorized. Only staff can delete books'}), 403
        
        del books_db[book_id]
        
        return jsonify({'message': 'Book deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== BOOK REQUEST ROUTES ====================

# ==================== SNS SIMULATION ====================
# ==================== NOTIFICATIONS LOGIC ====================
def create_notification(recipient, message, type='info'):
    """Create an in-app notification"""
    global notification_id_counter
    try:
        notification_id = notification_id_counter
        notification_id_counter += 1
        
        notifications_db[notification_id] = {
            'id': notification_id,
            'recipient': recipient,
            'message': message,
            'type': type,
            'read': False,
            'timestamp': datetime.now().isoformat()
        }
        return True
    except Exception as e:
        print(f"Failed to create notification: {e}")
        return False

def generate_email_html(subject, body_content, action_url=None, action_text=None):
    """Generate a beautiful Glassmorphic HTML email matching the app theme."""
    action_button = ""
    if action_url and action_text:
        action_button = f"""
            <a href="{action_url}" style="display:inline-block; background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); color:white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 20px;">
                {action_text}
            </a>
        """
    
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
                {action_button}
            </div>
            
            <!-- Footer -->
            <div style="background: #F9FAFB; padding: 20px; text-align: center; border-top: 1px solid #E5E7EB;">
                <p style="margin:0; color: #9CA3AF; font-size: 12px;">© {datetime.now().year} Greenfield University. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

# ==================== SNS SIMULATION ====================
def log_sns_notification(topic, recipient, subject, message):
    """Simulate sending an email via AWS SNS by logging to a file and creating in-app notification"""
    try:
        # Generate Styled HTML Content
        html_content = generate_email_html(subject, message)
        
        # File Logging (SNS Simulation)
        log_entry = f"""
{'='*60}
[SNS SIMULATION] - {datetime.now().isoformat()}
TOPIC: {topic}
TO:    {recipient}
SUBJ:  {subject}
BODY (Text): {message}
BODY (HTML Preview):
{html_content}
{'='*60}
"""
        with open("sns_logs.txt", "a", encoding='utf-8') as f:
            f.write(log_entry)
        print(f"📧 [Email Sent] To: {recipient} | Subject: {subject}") 
        
        # Create In-App Notification
        create_notification(recipient, f"{subject}: {message}", type='info')
        
    except Exception as e:
        print(f"Failed to log SNS notification: {e}")

# ==================== BOOK REQUEST ROUTES ====================

@app.route('/api/requests', methods=['POST'])
@app.route('/api/requests', methods=['POST'])
def create_request():
    """Create a book request"""
    """Create a new book request"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        book_id = data.get('book_id')
        
        # New: Collect student details for the request
        roll_no = data.get('roll_no', '')
        semester = data.get('semester', '')
        year = data.get('year', '')
        
        if not email or not book_id:
            return jsonify({'error': 'Email and Book ID required'}), 400
            
        # ... (Validation logic remains, assuming user and book exist checks are handled implicitly or by existing code)
        # We need to get user and book to populate other fields
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        book = next((b for b in books_db.values() if b['id'] == book_id), None) # Changed to .values() for dict
        if not book:
            return jsonify({'error': 'Book not found'}), 404
            
        # Check if already requested (pending)
        existing = next((r for r in book_requests_db.values() if r['email'] == email and r['book_id'] == book_id and r['status'] == 'pending'), None) # Changed to .values() for dict
        if existing:
            return jsonify({'error': 'You already have a pending request for this book'}), 400

        # Use request_id_counter as before, but ensure it's global and incremented
        global request_id_counter
        request_id = request_id_counter
        
        new_request = {
            'request_id': request_id,
            'email': email,
            'sender': user['name'],
            'book_id': book_id,
            'book_name': book['title'],
            'author': book['author'],
            'subject': book['subject'],
            'description': book.get('description', ''),
            'status': 'pending',
            'requested_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            # Store student details with the request snapshot
            'roll_no': roll_no or user.get('roll_no', ''),
            'semester': semester or user.get('semester', ''),
            'year': year or user.get('year', '')
        }
        
        book_requests_db[request_id] = new_request # Changed to dict assignment
        request_id_counter += 1 # Increment counter
        
        # Log notification
        log_sns_notification(
            topic="StudentNotification",
            recipient=email,
            subject=f"Request Received: {book['title']}",
            message=f"Dear {user['name']},\n\nYour request for '{book['title']}' has been received and is currently Pending.\n\nThank you,\nGreenfield Library"
        )
        
        # Notify Staff
        log_sns_notification(
            topic="StaffNotification",
            recipient="staff@gmail.com",
            subject=f"New Book Request: {book['title']}",
            message=f"Student {user['name']} has requested '{book['title']}'.\nRole No: {new_request['roll_no']}\nStatus: Pending"
        )
        
        return jsonify({'message': 'Request submitted successfully', 'request_id': request_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requests/<int:request_id>', methods=['GET'])
def get_request(request_id):
    """Get a specific request"""
    try:
        if request_id not in book_requests_db:
            return jsonify({'error': 'Request not found'}), 404
        
        return jsonify(book_requests_db[request_id]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-requests/<email>', methods=['GET'])
def get_user_requests(email):
    """Get all requests for a user"""
    try:
        email = email.strip().lower()
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_requests = [r for r in book_requests_db.values() if r['email'] == email]
        return jsonify(user_requests), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/all-requests', methods=['GET'])
def get_all_requests():
    """Get all requests (staff only)"""
    try:
        staff_email = request.args.get('staff_email', '').strip().lower()
        
        # Verify staff user
        user = get_user_by_email(staff_email)
        if not user or user['role'] != 'staff':
            return jsonify({'error': 'Unauthorized. Only staff can view all requests'}), 403
        
        all_requests = list(book_requests_db.values())
        return jsonify(all_requests), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/requests/<int:request_id>', methods=['PUT'])
def update_request(request_id):
    """Update request status"""
    try:
        if request_id not in book_requests_db:
            return jsonify({'error': 'Request not found'}), 404
        
        data = request.json
        status = data.get('status', '').strip()
        
        if status not in ['pending', 'approved', 'rejected', 'completed']:
            return jsonify({'error': 'Invalid status'}), 400
        
        req = book_requests_db[request_id]
        old_status = req['status']
        
        # [STOCK MANAGEMENT LOGIC]
        if old_status != status:
            book_id = req['book_id']
            # Find the book object (book_requests_db stores book_id as integer now? 
            # In create_request it comes from JSON so it might be int or str depending on frontend.
            # create_request stores: 'book_id': book_id.
            # books_db keys are integers.
            # Let's ensure we access it correctly.
            
            # Simple retrieval assuming book_id matches key type in books_db
            book = books_db.get(int(book_id))
            
            if book:
                # 1. Pending -> Approved (Take stock)
                if old_status == 'pending' and status == 'approved':
                    if book['available_count'] > 0:
                        book['available_count'] -= 1
                    else:
                        return jsonify({'error': 'Cannot approve: Book is out of stock'}), 400
                
                # 2. Approved -> Rejected OR Approved -> Completed (Return stock)
                elif old_status == 'approved' and (status == 'rejected' or status == 'completed'):
                    book['available_count'] += 1
                    # Capping at total_count shouldn't be strictly necessary if logic is sound, 
                    # but good for safety:
                    if book['available_count'] > book['total_count']:
                        book['available_count'] = book['total_count']

                # 3. Rejected/Completed -> Approved (Re-approve / Take stock)
                elif (old_status == 'rejected' or old_status == 'completed') and status == 'approved':
                    if book['available_count'] > 0:
                        book['available_count'] -= 1
                    else:
                        return jsonify({'error': 'Cannot approve: Book is out of stock'}), 400
                
                # 4. Pending -> Rejected (No stock change)
                # This case is implicitly handled by doing nothing.

        req['status'] = status
        req['updated_at'] = datetime.now().isoformat()
        
        # [SCENARIO 2] Notify Student on Status Change
        if old_status != status:
            log_sns_notification(
                topic="StudentNotification", 
                recipient=req['email'], 
                subject=f"Request Update: {req['book_name']}", 
                message=f"Your request for '{req['book_name']}' has been updated to: {status.upper()}."
            )
        
        return jsonify({'message': 'Request updated', 'request': req, 'book_available': book.get('available_count') if book else 'N/A'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'Backend is running'}), 200

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for a user"""
    try:
        email = request.args.get('email', '').strip().lower()
        if not email:
            return jsonify({'error': 'Email required'}), 400
            
        # Get notifications for this user
        user_notifs = [n for n in notifications_db.values() if n['recipient'] == email]
        
        # Sort by timestamp desc
        user_notifs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify(user_notifs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<int:notif_id>/read', methods=['PUT'])
def mark_notification_read(notif_id):
    """Mark notification as read"""
    try:
        if notif_id not in notifications_db:
            return jsonify({'error': 'Notification not found'}), 404
            
        notifications_db[notif_id]['read'] = True
        return jsonify({'message': 'Marked as read'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users or filter by role"""
    try:
        role = request.args.get('role')
        user_list = []
        
        for email, user in users_db.items():
            if role and user.get('role') != role:
                continue
                
            # exclude password
            safe_user = user.copy()
            if 'password' in safe_user:
                del safe_user['password']
            user_list.append(safe_user)
            
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<email>', methods=['DELETE'])
def delete_user(email):
    """Delete a user by email (staff only)"""
    try:
        staff_email = request.args.get('staff_email', '').strip().lower()
        # Verify requesting user is staff
        requester = get_user_by_email(staff_email)
        if not requester or requester['role'] != 'staff':
            return jsonify({'error': 'Unauthorized'}), 403

        email = email.lower()
        if email not in users_db:
            return jsonify({'error': 'User not found'}), 404
            
        if users_db[email]['role'] == 'staff':
             return jsonify({'error': 'Cannot delete staff accounts via this endpoint'}), 403

        del users_db[email]
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== CHATBOT ROUTES ====================

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.route('/api/chat', methods=['POST'])
def chat_bot():
    """Chat with AI Assistant"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
            
        if not GEMINI_API_KEY:
            return jsonify({'response': "I'm sorry, my AI brain is currently offline. (Missing API Key). Please ask the developer to set the GEMINI_API_KEY environment variable."}), 200

        # Create the model
        # Create the model
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Prepare book availability context
        book_list_text = "Here is the current library catalog:\n"
        for book_id, book in books_db.items():
            status = "Available" if book['available_count'] > 0 else "Out of stock"
            book_list_text += f"- {book['title']} by {book['author']} ({status}, {book['available_count']} copies left)\n"

        # System instruction context
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
