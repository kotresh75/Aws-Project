from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'dev_key_very_secret'  # For session/flash messages

import sqlite3
from datetime import datetime

DATABASE = 'library.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with conn:
        # Users Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                roll_no TEXT,
                semester TEXT,
                year TEXT
            )
        ''')
        
        # Books Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT,
                copies INTEGER DEFAULT 1
            )
        ''')
        
        # Requests Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                book_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                date TEXT NOT NULL,
                FOREIGN KEY (user_email) REFERENCES users (email),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')

        # Password Resets Table (OTP)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS password_resets (
                email TEXT NOT NULL,
                otp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES users (email)
            )
        ''')
        


    conn.close()

# Initialize DB on startup
if not os.path.exists(DATABASE):
    init_db()
elif os.environ.get("WERKZEUG_RUN_MAIN") == "true": 
    # Optional: Re-run init to ensure tables exist on reload, but avoid reseeding duplicates if checks are weak
    init_db()



# -------------------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------------------

@app.route('/')
def index():
    if 'user' in session:
        # Verify user exists in DB
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (session['user'],)).fetchone()
        db.close()
        
        if not user:
             session.clear()
             return render_template('index.html')
        return redirect(url_for('dashboard') if session.get('role') == 'student' else url_for('staff_dashboard'))
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/auth')
def auth():
    if 'user' in session:
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (session['user'],)).fetchone()
        db.close()
        
        if user:
             return redirect(url_for('dashboard') if session['role'] == 'student' else url_for('staff_dashboard'))
        else:
             session.clear()
    
    mode = request.args.get('mode', 'login')
    role = request.args.get('role', 'student') 
    return render_template('auth.html', mode=mode, role=role)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('role') != 'student':
        flash("Please login as a student to access the dashboard.", "warning")
        return redirect(url_for('auth', role='student'))
    return redirect(url_for('catalog'))

@app.route('/catalog')
def catalog():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    db = get_db()
    books = db.execute('SELECT * FROM books').fetchall()
    # Need requests to check if book is already pending
    my_requests = db.execute('SELECT * FROM requests WHERE user_email = ?', (session['user'],)).fetchall()
    db.close()
    
    return render_template('catalog.html', books=books, my_requests=my_requests)

    return render_template('catalog.html', books=books, my_requests=my_requests)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('auth'))
    
    db = get_db()
    if request.method == 'POST':
        # Password Change Logic
        current_pw = request.form.get('current_password')
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')
        
        user = db.execute('SELECT * FROM users WHERE email = ?', (session['user'],)).fetchone()
        
        if not check_password_hash(user['password'], current_pw):
            flash("Current password is incorrect.", "danger")
        elif new_pw != confirm_pw:
            flash("New passwords do not match.", "danger")
        else:
            hashed_pw = generate_password_hash(new_pw)
            db.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_pw, session['user']))
            db.commit()
            flash("Password updated successfully.", "success")
            
        db.close()
        return redirect(url_for('profile'))

    user = db.execute('SELECT * FROM users WHERE email = ?', (session['user'],)).fetchone()
    db.close()
    return render_template('profile.html', user=user)

@app.route('/my-requests')
def my_requests():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('index'))
    
    db = get_db()
    my_requests = db.execute('''
        SELECT r.*, b.title as book_title, b.author as book_author, b.cover_url as book_cover
        FROM requests r
        JOIN books b ON r.book_id = b.id
        WHERE r.user_email = ?
        ORDER BY r.id DESC
    ''', (session['user'],)).fetchall()
    db.close()

    return render_template('my_requests.html', my_requests=my_requests)

@app.route('/staff')
def staff_dashboard():
    if 'user' not in session or session.get('role') != 'staff':
        flash("Restricted access. Staff only.", "danger")
        return redirect(url_for('auth', role='staff'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (session['user'],)).fetchone()
    if not user:
        session.clear()
        db.close()
        flash("Session expired. Please login again.", "danger")
        return redirect(url_for('auth', mode='login', role='staff'))

    books = db.execute('SELECT * FROM books').fetchall()
    requests = db.execute('''
        SELECT r.*, b.title as book_title, b.cover_url as book_cover, u.email as user_email
        FROM requests r
        JOIN books b ON r.book_id = b.id
        JOIN users u ON r.user_email = u.email
        ORDER BY r.id DESC
    ''').fetchall()
    db.close()

    return render_template('staff_dashboard.html', user=user, books=books, requests=requests)

@app.route('/staff/books')
def manage_books():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    db = get_db()
    books = db.execute('SELECT * FROM books').fetchall()
    db.close()
    
    return render_template('manage_books.html', books=books)

@app.route('/staff/requests')
def manage_requests():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    db = get_db()
    requests = db.execute('''
        SELECT r.*, b.title as book_title, b.cover_url as book_cover, u.email as user_email
        FROM requests r
        JOIN books b ON r.book_id = b.id
        JOIN users u ON r.user_email = u.email
        ORDER BY r.id DESC
    ''').fetchall()
    db.close()
    
    return render_template('manage_requests.html', requests=requests)

@app.route('/staff/add_book', methods=['POST'])
def add_book():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    title = request.form.get('title')
    author = request.form.get('author')
    category = request.form.get('category')
    copies = int(request.form.get('copies', 1))
    isbn = request.form.get('isbn')
    cover_url = request.form.get('cover_url')

    db = get_db()
    db.execute('INSERT INTO books (title, author, category, copies, isbn, cover_url) VALUES (?, ?, ?, ?, ?, ?)', 
               (title, author, category, copies, isbn, cover_url))
    db.commit()
    db.close()

    flash(f"Book '{title}' added successfully.", "success")
    return redirect(url_for('staff_dashboard'))

@app.route('/staff/delete_book/<int:book_id>')
def delete_book(book_id):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    db = get_db()
    db.execute('DELETE FROM books WHERE id = ?', (book_id,))
    db.commit()
    db.close()

    flash("Book removed from inventory.", "info")
    return redirect(url_for('manage_books'))

@app.route('/staff/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    db = get_db()
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        category = request.form.get('category')
        copies = int(request.form.get('copies', 1))
        isbn = request.form.get('isbn')
        cover_url = request.form.get('cover_url')
        
        db.execute('''
            UPDATE books 
            SET title = ?, author = ?, category = ?, copies = ?, isbn = ?, cover_url = ?
            WHERE id = ?
        ''', (title, author, category, copies, isbn, cover_url, book_id))
        db.commit()
        db.close()
        flash("Book updated successfully.", "success")
        return redirect(url_for('manage_books'))
    
    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    db.close()
    return render_template('edit_book.html', book=book)

@app.route('/api/fetch_book_details')
def fetch_book_details():
    isbn = request.args.get('isbn')
    if not isbn:
        return jsonify({'error': 'ISBN required'}), 400
    
    # Strip hyphens/spaces for better matching
    clean_isbn = isbn.replace('-', '').replace(' ', '')
    
    result = {
        'title': '',
        'author': '',
        'category': '',
        'cover_url': ''
    }
    
    found_any = False

    try:
        import requests
        
        # 1. Try Google Books API
        try:
            url_google = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            response_google = requests.get(url_google, timeout=5)
            if response_google.status_code == 200:
                data_g = response_google.json()
                if data_g.get("totalItems", 0) > 0:
                    found_any = True
                    book_info = data_g['items'][0]['volumeInfo']
                    
                    result['title'] = book_info.get('title', '')
                    result['author'] = ", ".join(book_info.get('authors', []))
                    categories = book_info.get('categories', [])
                    result['category'] = categories[0] if categories else 'Other'
                    
                    image_links = book_info.get('imageLinks', {})
                    result['cover_url'] = image_links.get('thumbnail', '') or image_links.get('smallThumbnail', '')
        except Exception as e:
            print(f"Google API Error: {e}")

        # 2. Try OpenLibrary API (Enhance or Fallback)
        # Always try OpenLibrary if we are missing a cover or didn't find the book yet
        if not found_any or not result['cover_url']:
            try:
                # OpenLibrary Data API
                url_ol = f"https://openlibrary.org/api/books?bibkeys=ISBN:{clean_isbn}&format=json&jscmd=data"
                response_ol = requests.get(url_ol, timeout=5)
                
                if response_ol.status_code == 200:
                    data_ol = response_ol.json()
                    key = f"ISBN:{clean_isbn}"
                    
                    if key in data_ol:
                        book_ol = data_ol[key]
                        
                        # Fallback for core details if Google missed them
                        if not found_any:
                            found_any = True
                            result['title'] = book_ol.get('title', '')
                            authors = book_ol.get('authors', [])
                            result['author'] = ", ".join([a.get('name', '') for a in authors])
                            
                            # Map subjects to category (simple logic)
                            subjects = book_ol.get('subjects', [])
                            if subjects:
                                result['category'] = subjects[0].get('name', 'Other')
                            else:
                                result['category'] = 'Other'

                        # Specific check for Cover - OpenLibrary covers API is reliable
                        if not result['cover_url']:
                            if 'cover' in book_ol:
                                result['cover_url'] = book_ol['cover'].get('large', book_ol['cover'].get('medium', ''))
                            else:
                                # Try direct cover API constructing
                                # Check if cover exists by HEAD request or just assume it? 
                                # Better to rely on 'cover' key in data response.
                                pass

            except Exception as e:
                print(f"OpenLibrary API Error: {e}")

        # 3. Final Fallback: Construct OpenLibrary Cover URL Blindly
        if not result['cover_url']:
            try:
                # Check if a cover exists by trying to headcount it
                cover_try = f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-L.jpg"
                res_cover = requests.head(cover_try, timeout=3)
                # OpenLibrary returns a 1x1 pixel gif (approx 43 bytes) if not found, usually sent as image/gif
                # If found, it returns image/jpeg and larger size
                if res_cover.status_code == 200 and int(res_cover.headers.get('Content-Length', 0)) > 1000:
                     result['cover_url'] = cover_try
            except:
                pass

        if found_any:
            return jsonify(result)
        else:
             return jsonify({'error': 'Book not found in any database.'}), 404
             
    except Exception as e:
        print(f"Error fetching book: {e}")
        return jsonify({'error': 'Failed to fetch details'}), 500

# -------------------------------------------------------------------------
# NOTIFICATIONS (MOCK SNS)
# -------------------------------------------------------------------------
def send_notification(to_email, subject, body):
    """Simulates sending an email via AWS SNS/SES by printing to stderr."""
    import sys
    print("\n----------------------------------------------------------------", file=sys.stderr)
    print(f" [MOCK EMAIL] To: {to_email}", file=sys.stderr)
    print(f" [SUBJECT]    {subject}", file=sys.stderr)
    print(f" [BODY]       {body}", file=sys.stderr)
    print("----------------------------------------------------------------\n", file=sys.stderr, flush=True)

@app.route('/staff/request/<int:req_id>/<action>')
def handle_request(req_id, action):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    # Determine new status
    if action == 'return':
        new_status = 'returned'
    elif action == 'approve':
        new_status = 'approved'
    else:
        new_status = 'rejected'
    
    db = get_db()
    
    # Get current request details (to find book_id)
    req = db.execute('SELECT * FROM requests WHERE id = ?', (req_id,)).fetchone()
    if not req:
        db.close()
        flash("Request not found.", "danger")
        return redirect(url_for('manage_requests'))
    
    # Fetch book title for email
    book_title = db.execute('SELECT title FROM books WHERE id = ?', (req['book_id'],)).fetchone()['title']

    # Update status
    if new_status == 'approved':
        # Check stock before approving
        current_book = db.execute('SELECT * FROM books WHERE id = ?', (req['book_id'],)).fetchone()
        if current_book['copies'] < 1:
            db.close()
            flash("Cannot approve: Book is out of stock.", "danger")
            return redirect(url_for('manage_requests'))
            
        # Decrement stock
        db.execute('UPDATE books SET copies = copies - 1 WHERE id = ?', (req['book_id'],))
        flash("Request approved. Stock updated.", "success")
        send_notification(req['user_email'], f"Request Approved: {book_title}", 
                          f"Your request for '{book_title}' has been approved. Please pick it up from the library.")
        
    elif new_status == 'returned' and req['status'] == 'approved':
        # Increment stock
        db.execute('UPDATE books SET copies = copies + 1 WHERE id = ?', (req['book_id'],))
        flash("Book returned. Stock restored.", "info")
        send_notification(req['user_email'], f"Book Returned: {book_title}", 
                          f"You have successfully returned '{book_title}'. Thank you!")
        
    elif new_status == 'rejected':
        flash("Request rejected.", "warning")
        send_notification(req['user_email'], f"Request Rejected: {book_title}", 
                          f"Sorry, your request for '{book_title}' was rejected by the staff.")
    else:
        flash(f"Request marked as {new_status}.", "info")

    db.execute('UPDATE requests SET status = ? WHERE id = ?', (new_status, req_id))
    db.commit()
    db.close()
    
    db.close()
    
    return redirect(url_for('manage_requests'))

@app.route('/staff/students')
def manage_students():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    db = get_db()
    students = db.execute('SELECT * FROM users WHERE role = "student"').fetchall()
    db.close()
    return render_template('manage_students.html', students=students)

@app.route('/staff/delete_user/<string:email>')
def delete_user(email):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    db = get_db()
    db.execute('DELETE FROM users WHERE email = ?', (email,))
    db.commit()
    db.close()
    flash("Student removed.", "success")
    return redirect(url_for('manage_students'))

@app.route('/request_book/<int:book_id>')
def request_book(book_id):
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('auth', role='student'))
    
    db = get_db()
    
    # Check if already requested (pending)
    existing = db.execute('SELECT * FROM requests WHERE user_email = ? AND book_id = ? AND status IN ("pending", "waitlisted")', 
                          (session['user'], book_id)).fetchone()
    if existing:
        db.close()
        flash("You already have a pending request or waitlist for this book.", "warning")
        return redirect(url_for('dashboard'))
    
    # ALLOW Requests even if stock is 0 (Waitlist/Scenario 1 Compliance)
    # book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    # if not book or book['copies'] < 1:
    #     db.close()
    #     flash("Book is out of stock.", "danger")
    #     return redirect(url_for('dashboard'))

    # Create request
    from datetime import datetime
    
    # Determine status based on stock
    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    status = 'waitlisted' if book['copies'] < 1 else 'pending'
    
    db.execute('INSERT INTO requests (user_email, book_id, date, status) VALUES (?, ?, ?, ?)',
               (session['user'], book_id, datetime.now().strftime("%Y-%m-%d"), status))
    db.commit()
    
    # Fetch staff members for notification BEFORE closing DB
    staff_members = db.execute('SELECT email FROM users WHERE role = "staff"').fetchall()
    db.close()
    
    if status == 'pending':
        msg = "Request submitted!"
        send_notification(session['user'], f"Request Received: {book['title']}", 
                          f"We received your request for '{book['title']}'. status: Pending Approval.")
        
        # Notify ALL Staff
        for staff in staff_members:
            send_notification(staff['email'], f"New Request: {book['title']}",
                              f"Student {session['user']} has requested '{book['title']}'. Please review in dashboard.")
            
    else:
        msg = "Added to Waitlist!"
        send_notification(session['user'], f"Added to Waitlist: {book['title']}", 
                          f"'{book['title']}' is currently out of stock. You have been added to the waitlist.")
        
        # Notify ALL Staff
        for staff in staff_members:
            send_notification(staff['email'], f"New Waitlist Entry: {book['title']}",
                              f"Student {session['user']} joined the waitlist for '{book['title']}'.")
    
    flash(msg, "success")
    return redirect(url_for('dashboard'))

# -------------------------------------------------------------------------
# AI CHATBOT (GEMINI)
# -------------------------------------------------------------------------
import google.generativeai as genai

# Configure Gemini
GENAI_API_KEY = "AIzaSyC5HXAe98Ep-c7DGTYMQGvioKJEWzXsB88"
genai.configure(api_key=GENAI_API_KEY)
# Switch to 'gemini-flash-latest' for better quota
model = genai.GenerativeModel('gemini-flash-latest')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': "Please say something!"})

    # Context about the library
    context = """
    You are the intelligent assistant for the Greenfield University Instant Library System.
    System capabilities:
    - Students can search the Catalog and request books.
    - If a book is out of stock, they can join the Waitlist.
    - Staff manage requests (Approve, Reject, or Mark Returned).
    - Students get email notifications for all actions.
    - We use AWS (simulated) for scalability.
    
    Current User Session:
    Role: {}
    User: {}
    
    Answer the user's question concisely and helpfully.
    """.format(session.get('role', 'Guest'), session.get('user', 'Guest'))

    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{context}\nUser: {user_message}")
        return jsonify({'response': response.text})
    except Exception as e:
        import sys, traceback
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({'response': "Sorry, I'm having trouble connecting to my brain right now. "}), 500

# -------------------------------------------------------------------------
# API / ACTIONS
# -------------------------------------------------------------------------

@app.route('/api/stats')
def get_stats():
    db = get_db()
    available_books = db.execute('SELECT SUM(copies) FROM books').fetchone()[0] or 0
    total_students = db.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0] or 0
    pending_requests = db.execute("SELECT COUNT(*) FROM requests WHERE status = 'pending'").fetchone()[0] or 0
    db.close()

    stats = {
        'available_books': available_books,
        'total_students': total_students,
        'pending_requests': pending_requests
    }
    return jsonify(stats)

@app.route('/login', methods=['POST'])
def login_post():
    data = request.form
    mode = data.get('mode')
    
    if mode == 'register':
        return register_user(data)

    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    db.close()

    if not user:
        flash("Email not registered. Please register.", "danger")
        return redirect(url_for('auth', mode='login', role=role))
    
    if not check_password_hash(user['password'], password):
        flash("Password incorrect.", "danger")
        return redirect(url_for('auth', mode='login', role=role))
    
    if user['role'] != role:
        flash(f"Invalid role. This account is registered as {user['role']}.", "warning")
        return redirect(url_for('auth', mode='login', role=user['role']))

    session['user'] = email
    session['role'] = user['role']
    flash(f"Welcome back, {user['name']}!", "success")
    
    if user['role'] == 'staff':
        return redirect(url_for('staff_dashboard'))
    else:
        return redirect(url_for('dashboard'))

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
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if not user:
            db.close()
            flash("If that email exists, we sent a code.", "info") # Security best practice
            return redirect(url_for('verify_otp'))
            
        otp = generate_otp()
        # Delete old OTPs
        db.execute('DELETE FROM password_resets WHERE email = ?', (email,))
        # Save new OTP
        db.execute('INSERT INTO password_resets (email, otp) VALUES (?, ?)', (email, otp))
        db.commit()
        db.close()
        
        # MOCK SENDING - PRINT TO CONSOLE
        import sys
        print(f"\n==========================================", file=sys.stderr, flush=True)
        print(f" [MOCK SNS] OTP for {email}: {otp}", file=sys.stderr, flush=True)
        print(f"==========================================\n", file=sys.stderr, flush=True)
        
        session['reset_email'] = email # Temporarily store email for next step
        flash("OTP sent to your email (Check Console).", "info")
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
            
        db = get_db()
        record = db.execute('SELECT * FROM password_resets WHERE email = ? AND otp = ?', (email, otp)).fetchone()
        db.close()
        
        if record:
            session['otp_verified'] = True
            flash("OTP Verified. Set your new password.", "success")
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP. Try again.", "danger")
            
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
        db = get_db()
        db.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_pw, email))
        db.execute('DELETE FROM password_resets WHERE email = ?', (email,)) # Cleanup
        db.commit()
        db.close()
        
        session.pop('reset_email', None)
        session.pop('otp_verified', None)
        
        flash("Password reset successful. Please login.", "success")
        return redirect(url_for('auth', mode='login'))
        
    return render_template('reset_password.html')

def register_user(data):
    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirm_password')
    role = data.get('role')
    name = data.get('name')
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if user:
        db.close()
        flash("Email already registered. Please login.", "warning")
        return redirect(url_for('auth', mode='login', role=role))

    if password != confirm:
        db.close()
        flash("Passwords do not match.", "danger")
        return redirect(url_for('auth', mode='register', role=role))

    hashed_pw = generate_password_hash(password)
    
    if role == 'student':
        db.execute('INSERT INTO users (email, name, password, role, roll_no, semester, year) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                  (email, name, hashed_pw, role, data.get('roll_no'), data.get('semester'), data.get('year')))
    else:
        db.execute('INSERT INTO users (email, name, password, role) VALUES (?, ?, ?, ?)', 
                  (email, name, hashed_pw, role))
    
    db.commit()
    db.close()
    
    flash("Registration successful! Please login.", "success")
    return redirect(url_for('auth', mode='login', role=role))

if __name__ == '__main__':
    # Force reload v3 - Cover Fallback Added
    app.run(debug=True)
