# Greenfield University Instant Library - Local Implementation

## 📚 Project Overview

A complete virtual library platform for Greenfield University BSC Computer Science department. Students can register, login, search books, request unavailable textbooks, and track request status. Library staff can manage book inventory and process student requests efficiently.

**Note:** This is a local implementation designed for development and testing. No AWS deployment is included.

---

## 🎯 Features Implemented

### ✅ Authentication System
- Email-based login (case-insensitive)
- Student self-registration with OTP verification
- Password reset with OTP verification
- Staff-only account creation by other staff members
- SHA-256 password hashing
- 6-digit OTP generation (printed to terminal for testing)
- Role-based access control (Student & Staff)

### ✅ Student Features
- **Book Catalog**: Search and filter books by title, author, or subject
- **Book Request**: Request available books with confirmation modal
- **Request History**: Track all requests with real-time status updates
  - Pending requests
  - Approved requests
  - Rejected requests
  - Completed requests
- **Profile Management**: Edit name and email, change password

### ✅ Staff Features
- **Book Management**: Add, view, and delete books
  - Set book title, author, subject, description, year, quantity
  - Track available vs. total copies
- **Request Management**: Review and process student requests
  - View all pending requests
  - Approve/Reject/Mark as Completed
  - Filter requests by status
- **Staff Management**: Add new staff members (staff-only)

### ✅ General Features
- Modern gradient-based UI design
- Responsive design (desktop, tablet, mobile)
- Real-time status updates
- In-app notification messages
- Smooth animations and transitions
- Comprehensive navbar with navigation
- Session management via localStorage

---

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- Node.js & npm

### Backend Setup

```bash
# Navigate to backend directory
cd "f:\AWS Project\backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd "f:\AWS Project\frontend"

# Install dependencies
npm install

# Start React development server
npm start
```

The frontend will open on `http://localhost:3000`

---

## 🧪 Testing Guide

### Demo Accounts

**Pre-registered Staff Account:**
- Email: `staff@gmail.com`
- Password: `123456`
- Role: Staff

**Pre-registered Student Account:**
- Email: `student@gmail.com`
- Password: `123456`
- Role: Student

### Workflow 1: Student Registration & Book Request

1. **Register as New Student**
   - Go to http://localhost:3000/register
   - Fill in: Name, Email, Password (min 6 chars)
   - Click "Register"
   - **Check backend terminal for OTP** (printed to console)
   - Enter OTP in verification step
   - Success → Redirected to login

2. **Login as Student**
   - Use your new credentials or student@gmail.com / 123456
   - Redirected to Dashboard

3. **Browse & Request Books**
   - Click "Book Catalog" in navbar
   - Search by title or author
   - Filter by subject (Computer Science, Data Science, etc.)
   - Click "📝 Request Book" on any available book
   - Confirm request in modal
   - Success message appears

4. **Check Request Status**
   - Click "Requests" in navbar
   - View all your requests with status badges
   - See request creation and update times
   - Stats at top show: Pending, Approved, Completed, Rejected

### Workflow 2: Staff Book Management

1. **Login as Staff**
   - Use staff@gmail.com / 123456
   - Dashboard shows staff-specific options

2. **Manage Books**
   - Click "Manage Books" on dashboard
   - Click "+ Add New Book" button
   - Fill in: Title, Author, Subject, Description (optional), Year, Quantity
   - Submit form
   - Success message appears
   - New book appears in grid below

3. **Delete Books**
   - In book grid, click "🗑️ Delete" on any book
   - Confirm deletion
   - Book removed from system

### Workflow 3: Staff Request Processing

1. **View All Requests**
   - Click "Manage Requests" on dashboard
   - View all student requests from all users

2. **Filter by Status**
   - Click filter tabs: All, Pending, Approved, Rejected, Completed
   - See count of requests in each status

3. **Process Pending Requests**
   - For each pending request, see:
     - Book name and author
     - Student email
     - Request timestamp
     - Action buttons
   - Click "✓ Approve" or "✕ Reject"
   - Success message shows

4. **Complete Approved Requests**
   - Filter to "Approved"
   - Click "✓ Mark Complete"
   - Request moves to "Completed" status

### Workflow 4: User Profile Management

1. **Access Profile**
   - Click "Profile" in navbar
   - See current: Name, Email, Role

2. **Edit Profile**
   - Click "✏️ Edit Profile"
   - Form appears with editable Name and Email
   - Role is read-only (cannot change)
   - Click "Save Changes"
   - Success message shows

3. **Change Password**
   - Click "🔐 Change Password" button
   - Enter: Current Password, New Password, Confirm Password
   - Validations: Min 6 chars, passwords must match
   - Click "Change Password"
   - Success message shows

---

## 📁 Project Structure

```
f:\AWS Project\
├── backend/
│   ├── app.py                    # Flask backend (API endpoints)
│   ├── requirements.txt          # Python dependencies
│   └── .gitignore               # Git ignore file
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.js          # Email/password login
│   │   │   ├── Register.js       # Student registration with OTP
│   │   │   ├── ForgotPassword.js # Password reset with OTP
│   │   │   ├── Dashboard.js      # Home page with role-based panels
│   │   │   ├── Profile.js        # User profile with edit/password change
│   │   │   ├── BookCatalog.js    # Search, filter, request books
│   │   │   ├── RequestHistory.js # Track request status
│   │   │   ├── BookManagement.js # Staff: add/delete books
│   │   │   ├── RequestManagement.js # Staff: approve/reject/complete requests
│   │   │   ├── StaffManagement.js # Staff: add new staff members
│   │   │   ├── Settings.js       # Placeholder: Account settings
│   │   │   └── Notifications.js  # Placeholder: Notification preferences
│   │   ├── App.js               # React router and main app
│   │   ├── App.css              # Complete styling (modern design)
│   │   └── index.js             # React entry point
│   ├── package.json             # Node dependencies
│   ├── .gitignore               # Git ignore file
│   └── public/
│       └── index.html           # HTML template
│
├── .gitignore                    # Root git ignore
├── PROJECT_STATUS.md             # Project documentation
├── The Overview.txt              # Project overview and requirements
└── README.md                     # This file
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/register/student` - Register new student
- `POST /api/verify-registration-otp` - Verify registration OTP
- `POST /api/login` - Email/password login
- `POST /api/forgot-password` - Request password reset
- `POST /api/verify-forgot-password-otp` - Verify password reset OTP
- `POST /api/reset-password` - Set new password
- `POST /api/change-password` - Change password (logged-in users)

### Books
- `GET /api/books` - List all books (with search/filter)
- `GET /api/books/<id>` - Get specific book details
- `POST /api/books` - Add new book (staff only)
- `PUT /api/books/<id>` - Update book (staff only)
- `DELETE /api/books/<id>` - Delete book (staff only)

### Book Requests
- `POST /api/requests` - Create book request (student)
- `GET /api/user-requests/<email>` - Get user's requests
- `GET /api/all-requests` - Get all requests (staff only)
- `PUT /api/requests/<id>` - Update request status (staff only)

### Staff Management
- `POST /api/admin/register-staff` - Add new staff member (staff only)

---

## 🎨 Design System

### Color Palette
- **Primary**: Indigo (#6366f1)
- **Secondary**: Pink (#ec4899)
- **Accent**: Teal (#14b8a6)
- **Success**: Green (#10b981)
- **Warning**: Amber (#f59e0b)
- **Danger**: Red (#ef4444)
- **Dark**: Charcoal (#1f2937)
- **Light**: Off-white (#f9fafb)

### Typography
- **Font**: Inter (system fallback)
- **H1**: 2.5rem, weight 600
- **H2**: 2rem, weight 600
- **H3**: 1.5rem, weight 600
- **Body**: 1rem, weight 400

### Components
- Gradient backgrounds (linear)
- Card layouts with shadows
- Smooth cubic-bezier transitions
- Glassmorphism effects (backdrop blur)
- Responsive grid layouts
- Mobile-first design approach

---

## 💾 Data Storage

### In-Memory Storage (Local Development)
- **users_db**: Stores user accounts and credentials
- **books_db**: Stores book inventory with availability
- **book_requests_db**: Stores student requests with status tracking
- **otp_store**: Stores temporary OTP codes (6-digit, 10-minute expiration)

**Note**: All data is reset when the backend restarts. For persistent storage, integrate a database.

---

## 🔐 Security Features

- SHA-256 password hashing
- OTP-based email verification
- Email case-insensitivity for logins
- Role-based access control
- Protected staff endpoints
- Session validation via localStorage

---

## 📝 Testing Checklist

- [x] Student registration flow
- [x] Email OTP verification
- [x] Student login
- [x] Staff login
- [x] Book catalog search & filter
- [x] Book request submission
- [x] Request status tracking
- [x] Staff book management (add/delete)
- [x] Staff request processing (approve/reject/complete)
- [x] Profile editing (name & email)
- [x] Password change flow
- [x] Logout functionality
- [x] Role-based navigation
- [x] Responsive design (desktop/tablet/mobile)

---

## 🚨 Known Limitations

1. **Notifications**: Uses console logs instead of AWS SNS (local alternative)
2. **Persistence**: Data resets on backend restart (use database for production)
3. **Email**: OTP printed to terminal instead of sent via email
4. **Authentication**: Uses localStorage (not JWT tokens)
5. **Deployment**: Not configured for AWS EC2 or cloud hosting

---

## 🔄 Future Enhancements

1. Database integration (DynamoDB, PostgreSQL, MongoDB)
2. AWS SNS for real email notifications
3. JWT token-based authentication
4. Email notifications via AWS SES
5. Book return tracking and due dates
6. Fine/penalty system
7. Book ratings and reviews
8. Admin dashboard with analytics
9. User activity logs
10. Integration with university authentication system

---

## 📞 Support

For issues or questions:
1. Check backend terminal for OTP when testing registration/password reset
2. Verify both backend and frontend servers are running
3. Clear browser cache if experiencing issues (Ctrl+Shift+Delete)
4. Check browser console for errors (F12)
5. Ensure ports 5000 (backend) and 3000 (frontend) are available

---

## 📄 Tech Stack

- **Backend**: Flask 2.3.0 | Python 3.x
- **Frontend**: React 18.2.0 | React Router 6.8.0
- **Styling**: CSS3 (no external libraries)
- **Storage**: In-Memory Dictionaries (local development only)
- **Deployment**: Local Testing Only

---

**Last Updated**: January 2026  
**Status**: Local Development Complete
