import os
import json
import boto3
import random
import string
import requests
from decimal import Decimal
from datetime import datetime
from botocore.exceptions import ClientError
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai

# =============================================================================
# CONFIGURATION
# =============================================================================
class Config:
    """Centralized Configuration for the Application"""
    SECRET_KEY = 'never_mind_its_ok_lol'
    AWS_REGION = 'us-east-1'
    
    # AWS Resources (DynamoDB Tables)
    TABLE_USERS = 'InstantLibrary_Users'
    TABLE_BOOKS = 'InstantLibrary_Books'
    TABLE_REQUESTS = 'InstantLibrary_Requests'
    TABLE_OTP = 'InstantLibrary_OTP'
    
    # External Services
    SNS_TOPIC_ARN = '' # PASTE YOUR SNS ARN HERE
    GEMINI_API_KEY = ''

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# =============================================================================
# AWS CLIENTS & SERVICES SETUP
# =============================================================================
try:
    dynamodb = boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    sns_client = boto3.client('sns', region_name=Config.AWS_REGION)
    
    # Table Resources
    users_table = dynamodb.Table(Config.TABLE_USERS)
    books_table = dynamodb.Table(Config.TABLE_BOOKS)
    requests_table = dynamodb.Table(Config.TABLE_REQUESTS)
    password_resets_table = dynamodb.Table(Config.TABLE_OTP)
except Exception as e:
    print(f"CRITICAL: Failed to connect to AWS Services. Error: {e}")

# AI Model Setup
model = None
if Config.GEMINI_API_KEY:
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest')
    except Exception as e:
        print(f"AI Setup Warning: {e}")

# =============================================================================
# UTILITIES & HELPER CLASSES
# =============================================================================
class Utils:
    @staticmethod
    def generate_otp():
        """Generates a 6-digit numeric OTP."""
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def convert_decimals(obj):
        """Recursively converts DynamoDB Decimal types to int/float for JSON serialization."""
        if isinstance(obj, list):
            return [Utils.convert_decimals(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: Utils.convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return obj

    @staticmethod
    def generate_email_html(subject, body_content):
        """Generates a styled HTML email template."""
        year = datetime.now().year
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0; padding:0; background-color: #f3f4f6; font-family: 'Inter', sans-serif;">
            <div style="max-width: 600px; margin: 40px auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%); padding: 32px 24px; text-align: center;">
                    <h1 style="margin:0; color:white; font-size: 24px; font-weight: 800;">Instant Library</h1>
                    <p style="margin:8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">Greenfield University</p>
                </div>
                <div style="padding: 32px 24px;">
                    <h2 style="margin-top:0; color: #111827; font-size: 20px;">{subject}</h2>
                    <div style="color: #4B5563; line-height: 1.6; font-size: 16px;">
                        {body_content}
                    </div>
                </div>
                <div style="background: #F9FAFB; padding: 20px; text-align: center; border-top: 1px solid #E5E7EB;">
                    <p style="margin:0; color: #9CA3AF; font-size: 12px;">© {year} Greenfield University. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

class NotificationService:
    @staticmethod
    def subscribe(email):
        """Subscribes a user's email to the SNS Topic."""
        if not Config.SNS_TOPIC_ARN:
             return

        try:
            sns_client.subscribe(
                TopicArn=Config.SNS_TOPIC_ARN,
                Protocol='email',
                Endpoint=email
            )
            print(f" [INFO] SNS Subscription Request sent to {email}")
        except Exception as e:
            print(f" [ERROR] SNS Subscribe Failed: {e}")


    @staticmethod
    def send(to_email, subject, body):
        """Sends an email notification via AWS SNS."""
        if not Config.SNS_TOPIC_ARN:
            print(f" [MOCK SNS] To: {to_email} | Subject: {subject}")
            return

        try:
            # SNS 'email' protocol sends raw text. HTML is not supported effectively.
            # We convert our body to plain text for readability.
            plain_text = body.replace('<br>', '\n').replace('<br/>', '\n')
            
            # Simple strip of other tags if any (basic approach)
            import re
            plain_text = re.sub('<[^<]+?>', '', plain_text)

            message = {"default": plain_text, "email": plain_text}
            
            sns_client.publish(
                TopicArn=Config.SNS_TOPIC_ARN,
                Subject=subject[:100],
                Message=json.dumps(message),
                MessageStructure='json'
            )
        except Exception as e:
            print(f"SNS Error: {e}")

class DatabaseService:
    @staticmethod
    def get_user(email):
        try:
            resp = users_table.get_item(Key={'email': email})
            return Utils.convert_decimals(resp.get('Item'))
        except ClientError:
            return None

    @staticmethod
    def create_user(user_data):
        users_table.put_item(Item=user_data)

    @staticmethod
    def get_all_books():
        resp = books_table.scan()
        return Utils.convert_decimals(resp.get('Items', []))

    @staticmethod
    def get_book(book_id):
        resp = books_table.get_item(Key={'id': str(book_id)})
        return Utils.convert_decimals(resp.get('Item'))

# =============================================================================
# PUBLIC ROUTES
# =============================================================================
@app.route('/')
def index():
    if 'user' in session:
        user = DatabaseService.get_user(session['user'])
        if not user:
            session.clear()
            return render_template('index.html')
        return redirect(url_for('dashboard') if session.get('role') == 'student' else url_for('staff_dashboard'))
    
    # Feature a book on the landing page
    trending_book = None
    try:
        # Scan limit to 50 efficient load
        response = books_table.scan(Limit=50)
        items = Utils.convert_decimals(response.get('Items', []))
        if items:
            trending_book = random.choice(items)
    except Exception:
        pass

    return render_template('index.html', trending_book=trending_book)

@app.route('/about')
def about():
    return render_template('about.html')

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if 'user' in session:
        return redirect(url_for('dashboard') if session['role'] == 'student' else url_for('staff_dashboard'))
    
    mode = request.args.get('mode', 'login')
    role = request.args.get('role', 'student') 
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'register':
            return handle_registration(request, role)
        elif action == 'login':
            return handle_login(request, role, mode)
    
    return render_template('auth.html', mode=mode, role=role)

@app.route('/login', methods=['POST'])
def login_post():
    # Helper route for form actions pointing to /login
    action = request.form.get('action')
    role = request.form.get('role', 'student')
    
    if action == 'register':
        return handle_registration(request, role)
    else:
        return handle_login(request, role, 'login')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = DatabaseService.get_user(email)
        
        if not user:
            flash("If that email exists, we sent a code.", "info")
            return redirect(url_for('verify_otp'))
            
        otp = Utils.generate_otp()
        password_resets_table.put_item(Item={
            'email': email,
            'otp': otp,
            'ttl': int((datetime.now().timestamp()) + 600)
        })
        
        NotificationService.send(email, "Security Alert: Password Reset OTP", f"Your OTP is: {otp}. It expires in 10 minutes.")
        session['reset_email'] = email
        flash("OTP sent to your email (Check Inbox).", "info")
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
            
        resp = password_resets_table.get_item(Key={'email': email})
        record = Utils.convert_decimals(resp.get('Item'))
        
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
        users_table.update_item(
            Key={'email': email},
            UpdateExpression="set password=:p",
            ExpressionAttributeValues={':p': hashed_pw}
        )
        password_resets_table.delete_item(Key={'email': email})
        
        NotificationService.send('Instant Library Alert', f"Audit: Password Reset", f"Password for user {email} was successfully reset via OTP.")
        NotificationService.send(email, "Security Alert: Password Changed", "Your password was successfully reset.")
        
        session.pop('reset_email', None)
        session.pop('otp_verified', None)
        
        flash("Password reset successful. Please login.", "success")
        return redirect(url_for('auth', mode='login'))
        
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

    return render_template('auth.html', mode=mode, role=role)

# Authentication Helper Functions
def handle_registration(req, role):
    email = req.form.get('email').strip().lower()
    name = req.form.get('name')
    password = req.form.get('password')
    confirm = req.form.get('confirm_password')
    
    if password != confirm:
        flash("Passwords do not match.", "danger")
        return redirect(url_for('auth', mode='register', role=role))
    
    if DatabaseService.get_user(email):
        flash("Email already registered. Please login.", "warning")
        return redirect(url_for('auth', mode='login', role=role))
    
    user_data = {
        'email': email,
        'name': name,
        'password': generate_password_hash(password),
        'role': role,
        'created_at': datetime.now().isoformat()
    }
    if role == 'student':
        user_data.update({
            'roll_no': req.form.get('roll_no'),
            'semester': req.form.get('semester'),
            'year': req.form.get('year')
        })
        
    DatabaseService.create_user(user_data)
    
    # Auto-subscribe triggers a "Confirm Subscription" email from AWS
    NotificationService.subscribe(email)

    NotificationService.send('Instant Library Alert', f"New Registration: {email}", 
                             f"Name: {name}<br>Email: {email}<br>Role: {role}")
    NotificationService.send(email, "Welcome to Instant Library", 
                             f"Hi {name},<br>Thanks for registering! You can now request books.")
    
    flash("Registration successful! Please login.", "success")
    return redirect(url_for('auth', mode='login', role=role))

def handle_login(req, role, mode):
    email = req.form.get('email').strip().lower()
    password = req.form.get('password')
    
    user = DatabaseService.get_user(email)
    
    if user and check_password_hash(user['password'], password):
        session['user'] = user['email']
        session['role'] = user['role']
        session['name'] = user['name']
        
        NotificationService.send('Instant Library Alert', f"Login Alert: {email}", 
                                 f"User {user['name']} ({email}) just logged in.")
        
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for('dashboard') if user['role'] == 'student' else url_for('staff_dashboard'))
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('auth', mode='login', role=role))

# =============================================================================
# STUDENT ROUTES
# =============================================================================
@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('auth', role='student'))
    return redirect(url_for('catalog'))

@app.route('/catalog')
def catalog():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    books = DatabaseService.get_all_books()
    response = requests_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_email').eq(session['user'])
    )
    my_requests = Utils.convert_decimals(response.get('Items', []))
    
    return render_template('catalog.html', books=books, my_requests=my_requests)

@app.route('/request_book/<book_id>')
def request_book(book_id):
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('auth', role='student'))
    
    book_id = str(book_id)
    
    # Check existing
    response = requests_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_email').eq(session['user']) & 
                         boto3.dynamodb.conditions.Attr('book_id').eq(book_id) &
                         boto3.dynamodb.conditions.Attr('status').is_in(['pending', 'waitlisted'])
    )
    if response.get('Count', 0) > 0:
        flash("You already have a pending request or waitlist for this book.", "warning")
        return redirect(url_for('dashboard'))
        
    book = DatabaseService.get_book(book_id)
    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('dashboard'))
    
    status = 'waitlisted' if book.get('copies', 0) < 1 else 'pending'
    
    import uuid
    requests_table.put_item(Item={
        'id': str(uuid.uuid4()),
        'user_email': session['user'],
        'book_id': book_id,
        'status': status,
        'date': datetime.now().strftime("%Y-%m-%d"),
        'formatted_date': datetime.now().strftime("%Y-%m-%d")
    })
    
    # Notifications
    msg_sub = f"Request Received: {book.get('title')}" if status == 'pending' else f"Added to Waitlist: {book.get('title')}"
    msg_body = f"Status: {status.title()}." if status == 'pending' else "You are on the waitlist."
    
    NotificationService.send(session['user'], msg_sub, msg_body)
    
    # Notify Staff (Inefficient Scan for demo)
    staff_scan = users_table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('role').eq('staff'))
    for staff in staff_scan.get('Items', []):
         NotificationService.send(staff['email'], f"New {status.title()}: {book.get('title')}", 
                                  f"Student {session['user']} requests '{book.get('title')}'.")

    flash("Request submitted!" if status == 'pending' else "Added to Waitlist!", "success")
    return redirect(url_for('dashboard'))

@app.route('/my-requests')
def my_requests():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    resp = requests_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('user_email').eq(session['user'])
    )
    requests_list = Utils.convert_decimals(resp.get('Items', []))
    
    all_books = {str(b['id']): b for b in DatabaseService.get_all_books()}
    
    enriched_requests = []
    for r in requests_list:
        b_id = str(r['book_id'])
        if b_id in all_books:
            r.update({
                'book_title': all_books[b_id].get('title', 'Unknown'),
                'book_author': all_books[b_id].get('author', 'Unknown'),
                'book_cover': all_books[b_id].get('cover_url', '')
            })
            enriched_requests.append(r)
    
    enriched_requests.reverse()
    return render_template('my_requests.html', my_requests=enriched_requests)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        current_pw = request.form.get('current_password')
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')
        
        user = DatabaseService.get_user(session['user'])
        
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
            # Notify User of Password Change
            NotificationService.send(session['user'], "Security Alert: Password Changed", 
                                     "Your password was just changed. If this wasn't you, please contact support immediately.")
            
            flash("Password updated successfully.", "success")
            return redirect(url_for('profile'))
            
    user = DatabaseService.get_user(session['user'])
    return render_template('profile.html', user=user)

# =============================================================================
# STAFF ROUTES
# =============================================================================
@app.route('/staff')
def staff_dashboard():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('auth', role='staff'))
    
    user = DatabaseService.get_user(session['user'])
    books = DatabaseService.get_all_books()
    
    req_resp = requests_table.scan()
    all_requests = Utils.convert_decimals(req_resp.get('Items', []))
    
    users_scan = users_table.scan()
    all_users = {u['email']: u for u in Utils.convert_decimals(users_scan.get('Items', []))}
    books_map = {str(b['id']): b for b in books}
    
    enriched_requests = []
    for r in all_requests:
        b = books_map.get(str(r['book_id']), {})
        u = all_users.get(r['user_email'], {})
        r.update({
            'book_title': b.get('title', 'Unknown'),
            'user_email': u.get('email', r['user_email']),
            'book_cover': b.get('cover_url', '')
        })
        enriched_requests.append(r)
    enriched_requests.reverse()
    
    return render_template('staff_dashboard.html', user=user, books=books, requests=enriched_requests)

@app.route('/staff/books')
def manage_books():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    books = DatabaseService.get_all_books()
    return render_template('manage_books.html', books=books)

@app.route('/staff/requests')
def manage_requests():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    req_resp = requests_table.scan()
    all_requests = Utils.convert_decimals(req_resp.get('Items', []))
    books = DatabaseService.get_all_books()
    books_map = {str(b['id']): b for b in books}
    
    enriched = []
    for r in all_requests:
        b = books_map.get(str(r['book_id']), {})
        r.update({'book_title': b.get('title', 'Unknown'), 'book_cover': b.get('cover_url', '')})
        enriched.append(r)
    enriched.reverse()
    
    return render_template('manage_requests.html', requests=enriched)

@app.route('/staff/add_book', methods=['POST'])
def add_book():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    import uuid
    new_book = {
        'id': str(uuid.uuid4()),
        'title': request.form.get('title'),
        'author': request.form.get('author'),
        'category': request.form.get('category'),
        'copies': int(request.form.get('copies', 1)),
        'isbn': request.form.get('isbn'),
        'cover_url': request.form.get('cover_url')
    }
    
    books_table.put_item(Item=new_book)
    
    # Notify Admin (Audit)
    NotificationService.send('Instant Library Alert', f"Audit: New Book Added", 
                             f"Book '{new_book['title']}' was added to inventory by {session['user']}.")

    flash(f"Book '{new_book['title']}' added successfully.", "success")
    return redirect(url_for('staff_dashboard'))

@app.route('/staff/delete_book/<book_id>')
def delete_book(book_id):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    books_table.delete_item(Key={'id': str(book_id)})
    
    # Notify Admin (Audit)
    NotificationService.send('Instant Library Alert', f"Audit: Book Deleted", 
                             f"Book ID {book_id} was deleted from inventory by {session['user']}.")

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
                ':t': request.form.get('title'), ':a': request.form.get('author'),
                ':c': request.form.get('category'), ':co': int(request.form.get('copies')),
                ':i': request.form.get('isbn'), ':url': request.form.get('cover_url'),
            }
        )
        flash("Book details updated.", "success")
        return redirect(url_for('manage_books'))
        
    book = DatabaseService.get_book(book_id)
    return render_template('edit_book.html', book=book)

@app.route('/staff/request/<req_id>/<action>')
def handle_request(req_id, action):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))

    resp = requests_table.get_item(Key={'id': str(req_id)})
    req = resp.get('Item')
    
    if not req:
        flash("Request not found.", "danger")
        return redirect(url_for('manage_requests'))
    
    book = DatabaseService.get_book(req['book_id'])
    new_status = 'rejected'
    
    if action == 'approve':
        if book['copies'] < 1:
            flash("Cannot approve: Out of stock.", "danger")
            return redirect(url_for('manage_requests'))
        
        books_table.update_item(Key={'id': str(book['id'])}, UpdateExpression="set copies = copies - :val", ExpressionAttributeValues={':val': 1})
        NotificationService.send(req['user_email'], f"Request Approved: {book['title']}", "Your request has been approved.")
        new_status = 'approved'
        flash("Request approved.", "success")
        
    elif action == 'return' and req['status'] == 'approved':
        books_table.update_item(Key={'id': str(book['id'])}, UpdateExpression="set copies = copies + :val", ExpressionAttributeValues={':val': 1})
        NotificationService.send(req['user_email'], f"Book Returned: {book['title']}", "Thank you for returning the book.")
        new_status = 'returned'
        flash("Book returned.", "info")
        
    elif action == 'reject': # implicitly handled by initialization but explicit check is better
        NotificationService.send(req['user_email'], f"Request Rejected: {book['title']}", "Sorry, your request was rejected.")
        new_status = 'rejected'
        flash("Request rejected.", "warning")

    requests_table.update_item(Key={'id': str(req_id)}, UpdateExpression="set #s = :s", 
                               ExpressionAttributeNames={'#s': 'status'}, ExpressionAttributeValues={':s': new_status})
    
    return redirect(url_for('manage_requests'))

@app.route('/staff/students')
def manage_students():
     if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
     
     resp = users_table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('role').eq('student'))
     students = Utils.convert_decimals(resp.get('Items', []))
     return render_template('manage_students.html', students=students)

@app.route('/staff/delete_user/<email>')
def delete_user(email):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    users_table.delete_item(Key={'email': email})
    
    # Notify Admin (Audit)
    NotificationService.send('', f"Audit: User Deleted", 
                             f"User {email} was deleted by {session['user']}.")

    flash("User deleted.", "success")
    return redirect(url_for('manage_students'))

# =============================================================================
# API ROUTES
# =============================================================================
@app.route('/api/fetch_book_details')
def fetch_book_details():
    isbn = request.args.get('isbn')
    if not isbn:
        return jsonify({'error': 'ISBN required'}), 400
    
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        data = requests.get(url).json()
        
        result = {'title': '', 'author': '', 'category': '', 'cover_url': ''}
        
        if data.get("totalItems", 0) > 0:
            info = data['items'][0]['volumeInfo']
            result['title'] = info.get('title', '')
            result['author'] = ", ".join(info.get('authors', []))
            result['category'] = info.get('categories', ['Other'])[0]
            imgs = info.get('imageLinks', {})
            result['cover_url'] = imgs.get('thumbnail') or imgs.get('smallThumbnail', '')
            
            return jsonify(result)
        
        # Fallback to OpenLibrary if needed (simplified for brevity given structure)
        clean_isbn = isbn.replace("-", "").strip()
        result['cover_url'] = f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-L.jpg"
        return jsonify(result) # Return what we have
        
    except Exception as e:
        print(f"Error fetching book: {e}")
        return jsonify({'error': 'Failed to fetch details'}), 500

@app.route('/api/analytics')
def analytics():
    """Provides JSON data for Staff Dashboard Charts"""
    if 'user' not in session or session.get('role') != 'staff':
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        # 1. Fetch Data
        books = Utils.convert_decimals(books_table.scan().get('Items', []))
        requests = Utils.convert_decimals(requests_table.scan().get('Items', []))
        all_books_map = {str(b['id']): b['title'] for b in books}
        
        # 2. Key Performance Indicators (KPIs)
        total_books = len(books)
        total_requests = len(requests)
        pending_requests = len([r for r in requests if r['status'] == 'pending'])
        low_stock = len([b for b in books if b['copies'] < 1])
        
        # 3. Chart 1: Most Popular Books (Request Count by Book Title)
        book_counts = {}
        for r in requests:
            b_id = str(r['book_id'])
            title = all_books_map.get(b_id, 'Unknown Book')
            book_counts[title] = book_counts.get(title, 0) + 1
            
        # Sort top 5
        sorted_books = sorted(book_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        popular_labels = [x[0] for x in sorted_books]
        popular_data = [x[1] for x in sorted_books]
        
        # 4. Chart 2: Request Status Distribution
        status_counts = {}
        for r in requests:
            s = r.get('status', 'Unknown').capitalize()
            status_counts[s] = status_counts.get(s, 0) + 1
            
        return jsonify({
            'total_books': total_books,
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'low_stock': low_stock,
            'popular_labels': popular_labels,
            'popular_data': popular_data,
            'status_labels': list(status_counts.keys()),
            'status_data': list(status_counts.values())
        })
        
    except Exception as e:
        print(f"Analytics Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations')
def recommendations():
    """Returns AI-powered book recommendations based on user history"""
    if 'user' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Fetch Catalog & User History
        all_books = Utils.convert_decimals(books_table.scan().get('Items', []))
        user_requests = Utils.convert_decimals(requests_table.scan().get('Items', []))
        
        # Filter for current user
        my_history = [r for r in user_requests if r['user_email'] == session['user']]
        
        # 1. Fallback Strategy (If no history or no API key)
        if not Config.GEMINI_API_KEY or not my_history:
            # Return 3 random books user hasn't requested yet
            requested_ids = {r['book_id'] for r in my_history}
            unread_books = [b for b in all_books if b['id'] not in requested_ids]
            recommendations = random.sample(unread_books, min(3, len(unread_books)))
            return jsonify({'source': 'random', 'books': recommendations})

        # 2. AI Strategy (Gemini)
        # Build Context
        all_books_map = {b['id']: f"{b['title']} by {b['author']}" for b in all_books}
        read_list = [all_books_map.get(r['book_id'], 'Unknown') for r in my_history]
        read_str = ", ".join(read_list[:10]) # Limit to last 10
        
        # Prompt
        prompt = f"""
        I have read these books: {read_str}.
        From the following library catalog, select 3 books I might like.
        Catalog: {json.dumps(all_books_map)}
        
        Return ONLY a JSON array of book IDs, like: ["id1", "id2", "id3"]
        """
        
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
            
            # Clean response (remove markdown code blocks)
            text = response.text.replace('```json', '').replace('```', '').strip()
            rec_ids = json.loads(text)
            
            recommendations = [b for b in all_books if b['id'] in rec_ids]
            return jsonify({'source': 'ai', 'books': recommendations})
            
        except Exception as ai_error:
            print(f"AI Error: {ai_error}")
            # Fallback to random if AI fails
            recommendations = random.sample(all_books, min(3, len(all_books)))
            return jsonify({'source': 'fallback', 'books': recommendations})

    except Exception as e:
        print(f"Rec Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/populate')
def populate_catalog():
    """Seeds the database with 500+ books from Open Library (Staff Only)"""
    if 'user' not in session or session.get('role') != 'staff':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Guard Check: Don't populate if we already have data
        existing_count = books_table.scan(Select='COUNT').get('Count', 0)
        if existing_count > 50:
            return jsonify({'success': True, 'count': 0, 'message': 'Catalog already populated.'})

        subjects = ['science_fiction', 'adventure', 'history', 'programming', 'biology']
        count = 0
        
        with books_table.batch_writer() as batch:
            for subject in subjects:
                try:
                    # Use Search API to get ISBNs (fields: title, author, isbn, cover, key)
                    url = f"https://openlibrary.org/search.json?subject={subject}&limit=100&fields=title,author_name,isbn,cover_i,key"
                    resp = requests.get(url, timeout=10).json()
                    
                    for doc in resp.get('docs', []):
                        try:
                            title = doc.get('title', 'Unknown Title')
                            author_name = doc.get('author_name', ['Unknown'])[0]
                            
                            # Get ISBN (first one found)
                            isbn_list = doc.get('isbn', [])
                            isbn = isbn_list[0] if isbn_list else "N/A"
                            
                            cover_id = doc.get('cover_i')
                            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
                            
                            batch.put_item(Item={
                                'id': f"ol_{doc['key'].split('/')[-1]}", 
                                'title': title[:100], 
                                'author': author_name,
                                'category': subject.replace('_', ' ').capitalize(),
                                'copies': random.randint(1, 10),
                                'cover_url': cover_url,
                                'isbn': isbn
                            })
                            count += 1
                        except:
                            continue
                except Exception as e:
                    print(f"Fetch Error ({subject}): {e}")
                    continue
        
        return jsonify({'success': True, 'count': count, 'message': f'Successfully seeded {count} books with ISBNs.'})

    except Exception as e:
        print(f"Populate Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    if not Config.GEMINI_API_KEY:
        return jsonify({'response': "AI functionality is not configured (Missing API Key)."})
        
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': "Please say something!"})

    # 1. RAG: Search Database for context
    db_context = ""
    try:
        # Simple keyword search strategy
        keywords = [w for w in user_message.split() if len(w) > 3]
        if keywords:
            # We can't efficiently search "OR" in scan easily without complexity, 
            # so we fetch a batch and filter in python for this MVP.
            # Production would use proper Search Index (ElasticSearch/OpenSearch)
            all_books = DatabaseService.get_all_books() # Warning: Scale limit, fine for demo (500 items)
            
            matches = []
            for book in all_books:
                # Check if any keyword matches title or author
                b_str = f"{book['title']} {book['author']} {book['category']}".lower()
                if any(k.lower() in b_str for k in keywords):
                    matches.append(f"- {book['title']} by {book['author']} ({book['copies']} copies) [Category: {book['category']}]")
            
            if matches:
                # Limit context to top 5 matches to save tokens
                db_context = "Here are some relevant books found in the library catalog:\n" + "\n".join(matches[:5])
            else:
                db_context = "I searched the catalog but didn't find specific matches for those terms."
    except Exception as e:
        print(f"RAG Error: {e}")
        db_context = "System Note: Database search unavailable."

    context = f"""
    You are the intelligent assistant for the Instant Library System.
    
    Current Catalog Context:
    {db_context}
    
    System capabilities:
    - Search Catalog and request books.
    - Join Waitlist for out-of-stock items.
    
    Instructions:
    - Use the Catalog Context to answer availability questions.
    - If a book is found in context, explicitly mention its copy count.
    - If not found, suggest they browse the full catalog.
    """
    
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Switch to generic latest alias (Safest for quotas)
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(f"{context}\nUser: {user_message}")
        return jsonify({'response': response.text})
    except Exception as e:
        print(f"!!! GEMINI ERROR: {e}")
        return jsonify({'response': f"I'm having trouble connecting to my brain right now. (Error: {str(e)[:50]}...)"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
