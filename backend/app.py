from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import hashlib
import os
import random
import string

app = Flask(__name__)
CORS(app)

# In-memory storage (for local development only)
users_db = {}
book_requests_db = {}
otp_store = {}  # Store OTPs: {email: {otp: "123456", timestamp: datetime, verified: False, used_for: "registration/password_reset"}}
pending_registrations = {}  # Store pending registrations: {email: {data}}

books_db = {
    1: {"id": 1, "title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "subject": "Computer Science", "description": "A comprehensive guide to algorithms and data structures", "year": 2009, "available_count": 3, "total_count": 5},
    2: {"id": 2, "title": "Data Science Handbook", "author": "Jake VanderPlas", "subject": "Data Science", "description": "A practical guide to data science with Python", "year": 2016, "available_count": 2, "total_count": 3},
    3: {"id": 3, "title": "Web Development with Flask", "author": "Miguel Grinberg", "subject": "Web Development", "description": "Learn web development using Flask framework", "year": 2018, "available_count": 0, "total_count": 2},
    4: {"id": 4, "title": "Cloud Computing Basics", "author": "Tom Bowers", "subject": "Cloud Computing", "description": "Introduction to cloud computing and AWS", "year": 2020, "available_count": 4, "total_count": 4},
    5: {"id": 5, "title": "Database Design", "author": "C.J. Date", "subject": "Databases", "description": "Best practices in database design and normalization", "year": 2015, "available_count": 1, "total_count": 3},
    6: {"id": 6, "title": "Python Programming", "author": "Guido van Rossum", "subject": "Programming", "description": "Complete guide to Python programming language", "year": 2021, "available_count": 5, "total_count": 5},
    7: {"id": 7, "title": "Machine Learning Basics", "author": "Andrew Ng", "subject": "Machine Learning", "description": "Introduction to machine learning and AI", "year": 2019, "available_count": 2, "total_count": 4},
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
    print(f"\n{'='*60}")
    print(f"🔐 OTP for {email}: {otp}")
    print(f"{'='*60}\n")

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
            'role': 'student'
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
            'role': user['role']
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
        
        if not title or not author or not subject:
            return jsonify({'error': 'Title, author, and subject are required'}), 400
        
        new_book = {
            'id': next_book_id,
            'title': title,
            'author': author,
            'subject': subject,
            'description': description,
            'year': year,
            'available_count': quantity,
            'total_count': quantity
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
        if 'available_count' in data:
            book['available_count'] = int(data['available_count'])
        if 'total_count' in data:
            book['total_count'] = int(data['total_count'])
        
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

@app.route('/api/requests', methods=['POST'])
def create_request():
    """Create a book request"""
    global request_id_counter
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        book_id = data.get('book_id')
        roll_no = data.get('roll_no', '').strip()
        semester = data.get('semester', '')
        year = data.get('year', '')
        
        if not email or not book_id:
            return jsonify({'error': 'Email and book_id required'}), 400
        
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if book_id not in books_db:
            return jsonify({'error': 'Book not found'}), 404
        
        book = books_db[book_id]
        
        new_request = {
            'request_id': request_id_counter,
            'email': email,
            'book_id': book_id,
            'book_name': book['name'],
            'author': book['author'],
            'roll_no': roll_no,
            'semester': semester,
            'year': year,
            'status': 'pending',
            'requested_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        book_requests_db[request_id_counter] = new_request
        request_id_counter += 1
        
        return jsonify({'message': 'Book request created successfully', 'request': new_request}), 201
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
        
        book_requests_db[request_id]['status'] = status
        book_requests_db[request_id]['updated_at'] = datetime.now().isoformat()
        
        return jsonify({'message': 'Request updated', 'request': book_requests_db[request_id]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'Backend is running'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
