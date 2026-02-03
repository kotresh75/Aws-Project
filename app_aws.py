from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import json
from decimal import Decimal
import requests

app = Flask(__name__)
app.secret_key = 'never_mind_its_ok_lol'  
# ============================================
# AWS CONFIGURATION
# ============================================
AWS_REGION = 'us-east-1'
SNS_TOPIC_ARN = '' # To be filled during deployment
GEMINI_API_KEY = '' # To be filled during deployment
ADMIN_EMAIL = os.environ.get('LIBRARY_ADMIN_EMAIL', 'admin@library.com') # Configurable Admin Email

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sns_client = boto3.client('sns', region_name=AWS_REGION)

# DynamoDB Tables
users_table = dynamodb.Table('InstantLibrary_Users')
books_table = dynamodb.Table('InstantLibrary_Books')
requests_table = dynamodb.Table('InstantLibrary_Requests')
password_resets_table = dynamodb.Table('InstantLibrary_OTP') # Reusing existing name from old project if compatible

# AI Chatbot Setup
import google.generativeai as genai

def configure_genai():
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel('gemini-flash-latest')
    return None

model = configure_genai()

# -------------------------------------------------------------------------
# FORGOT PASSWORD (OTP)
# -------------------------------------------------------------------------
import random
import string

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        user = get_user(email)
        
        if not user:
            # Security best practice: Don't reveal if email exists, but for demo we might want to guide user?
            # Standard: Pretend functionality worked.
            flash("If that email exists, we sent a code.", "info")
            return redirect(url_for('verify_otp'))
            
        otp = generate_otp()
        
        # Save OTP to DynamoDB (Using 'password_resets_table' which maps to 'InstantLibrary_OTP')
        # We need to cleanup old OTPs first? DynamoDB TTL handles expiration automatically!
        # But we should overwrite or just add new item.
        # Key is 'email' so put_item overwrites by default.
        password_resets_table.put_item(Item={
            'email': email,
            'otp': otp,
            # TTL: 10 mins from now
            'ttl': int((datetime.now().timestamp()) + 600)
        })
        
        # Send Notification via SNS
        send_notification(email, "Password Reset OTP", f"Your OTP is: {otp}")
        
        session['reset_email'] = email # Temporarily store email for next step
        flash("OTP sent to your email (Check Console/Email).", "info")
        return redirect(url_for('verify_otp'))
        
    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form.get('otp')
        email = session.get('reset_email')
        
        if not email:
            flash("Session expired. Start over.", "danger")
            return redirect(url_for('forgot_password'))
            
        # Get OTP from DynamoDB
        resp = password_resets_table.get_item(Key={'email': email})
        record = convert_decimals(resp.get('Item'))
        
        if record and record.get('otp') == otp:
            session['otp_verified'] = True
            flash("OTP Verified. Set your new password.", "success")
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP or Expired.", "danger")
            
    return render_template('verify_otp.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('otp_verified'):
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        email = session.get('reset_email')
        
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('reset_password'))
            
        hashed_pw = generate_password_hash(password)
        
        # Update User Password
        users_table.update_item(
            Key={'email': email},
            UpdateExpression="set password=:p",
            ExpressionAttributeValues={':p': hashed_pw}
        )
        
        # Cleanup OTP
        password_resets_table.delete_item(Key={'email': email})
        
        # Notify Admin
        send_notification(ADMIN_EMAIL, f"Password Reset: {email}", 
                          f"Password for user {email} was successfully reset.")
        
        session.pop('reset_email', None)
        session.pop('otp_verified', None)
        
        flash("Password reset successful. Please login.", "success")
        return redirect(url_for('auth', mode='login'))
        
    return render_template('reset_password.html')

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types from DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def convert_decimals(obj):
    """Recursively convert Decimal to int/float"""
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

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

def send_notification(to_email, subject, body):
    """Send notification via AWS SNS"""
    if not SNS_TOPIC_ARN:
        print(f" [MOCK SNS] To: {to_email} | Subject: {subject}")
        return

    try:
        # Generate HTML Body
        html_body = generate_email_html(subject, body)
        
        # Structure for SNS: 'default' is raw text, 'email' is HTML (if supported by subscription settings)
        # or simplified:
        message = {
            "default": body,
            "email": html_body
        }
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject[:100],
            Message=json.dumps(message),
            MessageStructure='json',
            MessageAttributes={
                'recipient': {
                    'DataType': 'String',
                    'StringValue': to_email
                }
            }
        )
    except Exception as e:
        print(f"SNS Error: {e}")

# ==================== DYNAMODB HELPERS ====================

def get_user(email):
    try:
        resp = users_table.get_item(Key={'email': email})
        return convert_decimals(resp.get('Item'))
    except ClientError:
        return None

def create_user_db(user_data):
    users_table.put_item(Item=user_data)

def get_all_books_db():
    resp = books_table.scan()
    return convert_decimals(resp.get('Items', []))

def get_book_db(book_id):
    # Book ID is stored as String in DynamoDB usually, passing str(book_id)
    resp = books_table.get_item(Key={'id': str(book_id)})
    return convert_decimals(resp.get('Item'))

# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'user' in session:
        user = get_user(session['user'])
        if not user:
            session.clear()
            return render_template('index.html')
        return redirect(url_for('dashboard') if session.get('role') == 'student' else url_for('staff_dashboard'))
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if 'user' in session:
        return redirect(url_for('dashboard') if session['role'] == 'student' else url_for('staff_dashboard'))
    
    mode = request.args.get('mode', 'login')
    role = request.args.get('role', 'student') 
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'register':
            email = request.form.get('email').strip().lower()
            name = request.form.get('name')
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')
            role = request.form.get('role') # hidden input
            
            # Validation
            if password != confirm:
                flash("Passwords do not match.", "danger")
                return redirect(url_for('auth', mode='register', role=role))
            
            if get_user(email):
                flash("Email already registered. Please login.", "warning")
                return redirect(url_for('auth', mode='login', role=role))
            
            # Create User
            user_data = {
                'email': email,
                'name': name,
                'password': generate_password_hash(password),
                'role': role,
                'created_at': datetime.now().isoformat()
            }
            if role == 'student':
                user_data['roll_no'] = request.form.get('roll_no')
                user_data['semester'] = request.form.get('semester')
                user_data['year'] = request.form.get('year')
                
            create_user_db(user_data)
            
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('auth', mode='login', role=role))
            
        elif action == 'login':
            email = request.form.get('email').strip().lower()
            password = request.form.get('password')
            
            user = get_user(email)
            
            if user and check_password_hash(user['password'], password):
                session['user'] = user['email']
                session['role'] = user['role']
                session['name'] = user['name']
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('dashboard') if user['role'] == 'student' else url_for('staff_dashboard'))
            else:
                flash("Invalid email or password.", "danger")
                return redirect(url_for('auth', mode='login', role=role))
    
    return render_template('auth.html', mode=mode, role=role)

@app.route('/login', methods=['POST'])
def login_post():
    # This route is required because auth.html form action points to 'login_post'
    action = request.form.get('action')
    role = request.form.get('role', 'student')
    
    if action == 'register':
        email = request.form.get('email').strip().lower()
        name = request.form.get('name')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        # Validation
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('auth', mode='register', role=role))
        
        if get_user(email):
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for('auth', mode='login', role=role))
        
        # Create User
        user_data = {
            'email': email,
            'name': name,
            'password': generate_password_hash(password),
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        if role == 'student':
            user_data['roll_no'] = request.form.get('roll_no')
            user_data['semester'] = request.form.get('semester')
            user_data['year'] = request.form.get('year')
            
        create_user_db(user_data)
        
        send_notification(ADMIN_EMAIL, f"New Registration: {email}", 
                          f"New User Registered:<br>Name: {name}<br>Email: {email}<br>Role: {role}")
        
        # Welcome Notification for Student (Matches filter: 'recipient': email)
        send_notification(email, "Welcome to Instant Library", 
                          f"Hi {name},<br>Thanks for registering! You can now request books.")
        
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('auth', mode='login', role=role))
        
    else: # Login
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        
        user = get_user(email)
        
        if user and check_password_hash(user['password'], password):
            session['user'] = user['email']
            session['role'] = user['role']
            session['name'] = user['name']
            
            # Notify Admin
            send_notification(ADMIN_EMAIL, f"Login Alert: {email}", 
                              f"User {user['name']} ({email}) just logged in.")
            
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for('dashboard') if user['role'] == 'student' else url_for('staff_dashboard'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('auth', mode='login', role=role))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        current_pw = request.form.get('current_password')
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')
        
        user = get_user(session['user'])
        
        if not check_password_hash(user['password'], current_pw):
            flash("Current password is incorrect.", "danger")
        elif new_pw != confirm_pw:
            flash("New passwords do not match.", "danger")
        else:
            hashed_pw = generate_password_hash(new_pw)
            users_table.update_item(
                Key={'email': session['user']},
                UpdateExpression="set password=:p",
                ExpressionAttributeValues={':p': hashed_pw}
            )
            flash("Password updated successfully.", "success")
            return redirect(url_for('profile'))
            
    user = get_user(session['user'])
    return render_template('profile.html', user=user)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('auth', role='student'))
    return redirect(url_for('catalog'))

@app.route('/catalog')
def catalog():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    # 1. Fetch all books
    books = get_all_books_db()
    
    # 2. Fetch user requests to determine status
    # DynamoDB Scan for requests by this user
    response = requests_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_email').eq(session['user'])
    )
    my_requests = convert_decimals(response.get('Items', []))
    
    return render_template('catalog.html', books=books, my_requests=my_requests)

@app.route('/request_book/<book_id>') # Note: book_id is string in logic now mostly, but URL might pass int or string
def request_book(book_id):
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('auth', role='student'))
    
    book_id = str(book_id)
    
    # Check existing pending/waitlisted
    response = requests_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_email').eq(session['user']) & 
                         boto3.dynamodb.conditions.Attr('book_id').eq(book_id) &
                         boto3.dynamodb.conditions.Attr('status').is_in(['pending', 'waitlisted'])
    )
    if response.get('Count', 0) > 0:
        flash("You already have a pending request or waitlist for this book.", "warning")
        return redirect(url_for('dashboard'))
        
    # Get Book for Stock Check
    book = get_book_db(book_id)
    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('dashboard'))
    
    # Determine status
    status = 'waitlisted' if book.get('copies', 0) < 1 else 'pending'
    
    # Create Request
    import uuid
    req_id = str(uuid.uuid4())
    requests_table.put_item(Item={
        'id': req_id, # Using 'id' to match simple schema, old project used 'request_id' but new uses 'id' implies
        'user_email': session['user'],
        'book_id': book_id,
        'status': status,
        'date': datetime.now().strftime("%Y-%m-%d"),
        'formatted_date': datetime.now().strftime("%Y-%m-%d") # Extra for potential sorting
    })
    
    # Notifications
    if status == 'pending':
        msg_sub = f"Request Received: {book.get('title')}"
        msg_body = f"We received your request for '{book.get('title')}'. status: Pending Approval."
    else:
        msg_sub = f"Added to Waitlist: {book.get('title')}"
        msg_body = f"'{book.get('title')}' is currently out of stock. You have been added to the waitlist."
    
    send_notification(session['user'], msg_sub, msg_body)
    
    # Notify Staff
    # Scanning all users to find staff is inefficient but acceptable for demo
    staff_scan = users_table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('role').eq('staff'))
    for staff in staff_scan.get('Items', []):
         send_notification(staff['email'], f"New {'Request' if status=='pending' else 'Waitlist'}: {book.get('title')}", 
                           f"Student {session['user']} requests '{book.get('title')}'.")

    flash("Request submitted!" if status == 'pending' else "Added to Waitlist!", "success")
    return redirect(url_for('dashboard'))

@app.route('/my-requests')
def my_requests():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    # Fetch Requests
    resp = requests_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_email').eq(session['user'])
    )
    requests = convert_decimals(resp.get('Items', []))
    
    # Manual Join to get Book Details
    # Optimization: Fetch all books once into a dict
    all_books_resp = books_table.scan()
    all_books = {str(b['id']): b for b in convert_decimals(all_books_resp.get('Items', []))}
    
    # Enriched Requests
    enriched_requests = []
    for r in requests:
        b_id = str(r['book_id'])
        if b_id in all_books:
            r['book_title'] = all_books[b_id].get('title', 'Unknown')
            r['book_author'] = all_books[b_id].get('author', 'Unknown')
            r['book_cover'] = all_books[b_id].get('cover_url', '')
            enriched_requests.append(r)
    
    # Sort by ID (approximated by date or reverse list)
    enriched_requests.reverse()
    
    return render_template('my_requests.html', my_requests=enriched_requests)

@app.route('/staff')
def staff_dashboard():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('auth', role='staff'))
    
    user = get_user(session['user'])
    
    # Fetch all for simple dashboard stats
    books = get_all_books_db()
    req_resp = requests_table.scan()
    all_requests = convert_decimals(req_resp.get('Items', []))
    
    # We pass these to template, but template might expect enriched requests if it displays a table
    # For now, staff_dashboard handles overview. If it lists requests, we might need enrichment.
    # Looking at staff_dashboard.html, it DOES list requests. We need to enrich.
    
    users_scan = users_table.scan()
    all_users = {u['email']: u for u in convert_decimals(users_scan.get('Items', []))}
    books_map = {str(b['id']): b for b in books}
    
    enriched_requests = []
    for r in all_requests:
        b = books_map.get(str(r['book_id']), {})
        u = all_users.get(r['user_email'], {})
        r['book_title'] = b.get('title', 'Unknown')
        r['user_email'] = u.get('email', r['user_email'])
        r['book_cover'] = b.get('cover_url', '')
        enriched_requests.append(r)
    enriched_requests.reverse()
    
    return render_template('staff_dashboard.html', user=user, books=books, requests=enriched_requests)

@app.route('/staff/books')
def manage_books():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    books = get_all_books_db()
    return render_template('manage_books.html', books=books)

@app.route('/staff/requests')
def manage_requests():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    req_resp = requests_table.scan()
    all_requests = convert_decimals(req_resp.get('Items', []))
    
    books_resp = books_table.scan()
    books_map = {str(b['id']): b for b in convert_decimals(books_resp.get('Items', []))}
    
    enriched = []
    for r in all_requests:
        b = books_map.get(str(r['book_id']), {})
        r['book_title'] = b.get('title', 'Unknown')
        r['book_cover'] = b.get('cover_url', '')
        enriched.append(r)
    enriched.reverse()
    
    return render_template('manage_requests.html', requests=enriched)

@app.route('/staff/add_book', methods=['POST'])
def add_book():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    import uuid
    new_book = {
        'id': str(uuid.uuid4()), # UUID for DynamoDB
        'title': request.form.get('title'),
        'author': request.form.get('author'),
        'category': request.form.get('category'),
        'copies': int(request.form.get('copies', 1)),
        'isbn': request.form.get('isbn'),
        'cover_url': request.form.get('cover_url')
    }
    
    books_table.put_item(Item=new_book)
    flash(f"Book '{new_book['title']}' added successfully.", "success")
    return redirect(url_for('staff_dashboard'))

@app.route('/staff/delete_book/<book_id>')
def delete_book(book_id):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    books_table.delete_item(Key={'id': str(book_id)})
    flash("Book removed from inventory.", "info")
    return redirect(url_for('manage_books'))

@app.route('/staff/edit_book/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        books_table.update_item(
            Key={'id': str(book_id)},
            UpdateExpression="set title=:t, author=:a, category=:c, copies=:co, isbn=:i, cover_url=:url",
            ExpressionAttributeValues={
                ':t': request.form.get('title'),
                ':a': request.form.get('author'),
                ':c': request.form.get('category'),
                ':co': int(request.form.get('copies')),
                ':i': request.form.get('isbn'),
                ':url': request.form.get('cover_url'),
            }
        )
        flash("Book details updated.", "success")
        return redirect(url_for('manage_books'))
        
    book = get_book_db(book_id)
    return render_template('edit_book.html', book=book)

@app.route('/staff/request/<req_id>/<action>')
def handle_request(req_id, action):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))

    # Get Request
    resp = requests_table.get_item(Key={'id': str(req_id)})
    req = resp.get('Item')
    
    if not req:
        flash("Request not found.", "danger")
        return redirect(url_for('manage_requests'))
    
    book = get_book_db(req['book_id'])
    new_status = 'rejected'
    
    if action == 'return':
        new_status = 'returned'
    elif action == 'approve':
        new_status = 'approved'
    
    if new_status == 'approved':
        if book['copies'] < 1:
            flash("Cannot approve: Out of stock.", "danger")
            return redirect(url_for('manage_requests'))
        
        # Decrement Stock
        books_table.update_item(Key={'id': str(book['id'])}, UpdateExpression="set copies = copies - :val", ExpressionAttributeValues={':val': 1})
        send_notification(req['user_email'], f"Request Approved: {book['title']}", "Your request has been approved.")
        flash("Request approved.", "success")
        
    elif new_status == 'returned' and req['status'] == 'approved':
        # Increment Stock
        books_table.update_item(Key={'id': str(book['id'])}, UpdateExpression="set copies = copies + :val", ExpressionAttributeValues={':val': 1})
        send_notification(req['user_email'], f"Book Returned: {book['title']}", "Thank you for returning the book.")
        flash("Book returned.", "info")
        
    elif new_status == 'rejected':
        send_notification(req['user_email'], f"Request Rejected: {book['title']}", "Sorry, your request was rejected.")
        flash("Request rejected.", "warning")

    # Update Request Status
    requests_table.update_item(Key={'id': str(req_id)}, UpdateExpression="set #s = :s", ExpressionAttributeNames={'#s': 'status'}, ExpressionAttributeValues={':s': new_status})
    
    return redirect(url_for('manage_requests'))

@app.route('/staff/students')
def manage_students():
     if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
     
     resp = users_table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('role').eq('student'))
     students = convert_decimals(resp.get('Items', []))
     return render_template('manage_students.html', students=students)

@app.route('/staff/delete_user/<email>')
def delete_user(email):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    users_table.delete_item(Key={'email': email})
    flash("User deleted.", "success")
    return redirect(url_for('manage_students'))

@app.route('/api/fetch_book_details')
def fetch_book_details():
    isbn = request.args.get('isbn')
    if not isbn:
        return jsonify({'error': 'ISBN required'}), 400
    
    try:
        import requests
        # Query Google Books API
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url)
        data = response.json()
        
        result = {'title': '', 'author': '', 'category': '', 'cover_url': ''}
        found_any = False

        # 1. Google Books Strategy
        if data.get("totalItems", 0) > 0:
            found_any = True
            book_info = data['items'][0]['volumeInfo']
            result['title'] = book_info.get('title', '')
            result['author'] = ", ".join(book_info.get('authors', []))
            categories = book_info.get('categories', [])
            result['category'] = categories[0] if categories else 'Other'
            image_links = book_info.get('imageLinks', {})
            result['cover_url'] = image_links.get('thumbnail', '') or image_links.get('smallThumbnail', '')

        # 2. OpenLibrary Strategy (Fallback)
        clean_isbn = isbn.replace("-", "").strip()
        if not found_any or not result['title'] or not result['cover_url']:
            try:
                ol_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{clean_isbn}&jscmd=data&format=json"
                ol_resp = requests.get(ol_url)
                ol_data = ol_resp.json()
                key = f"ISBN:{clean_isbn}"
                
                if key in ol_data:
                    found_any = True
                    book_ol = ol_data[key]
                    if not result['title']:
                        result['title'] = book_ol.get('title', result['title'])
                    if not result['author']:
                        authors = book_ol.get('authors', [])
                        result['author'] = ", ".join([a['name'] for a in authors]) if authors else result['author']
                    
                    if not result['cover_url'] and 'cover' in book_ol:
                        result['cover_url'] = book_ol['cover'].get('large', book_ol['cover'].get('medium', ''))
            except Exception as e:
                print(f"OpenLibrary Error: {e}")

        # 3. Final Cover Fallback
        if not result['cover_url']:
             result['cover_url'] = f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-L.jpg"

        if found_any:
            return jsonify(result)
        else:
            return jsonify({'error': 'Book not found.'}), 404
            
    except Exception as e:
        print(f"Error fetching book: {e}")
        return jsonify({'error': 'Failed to fetch details'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    if not model:
        return jsonify({'response': "AI functionality is not configured (Missing API Key)."})
        
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': "Please say something!"})

    context = """
    You are the intelligent assistant for the Instant Library System.
    System capabilities:
    - Search Catalog and request books.
    - Join Waitlist for out-of-stock items.
    - Students get real-time email notifications.
    """
    
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{context}\nUser: {user_message}")
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'response': "I'm having trouble connecting to my brain right now."})

if __name__ == '__main__':
    # AWS usually runs via Gunicorn/WSGI, but for testing:
    app.run(host='0.0.0.0', port=5000)
