
## Key Features

- Email-based login (email/password)
- OTP verification for registration and password reset (6-digit; prints to terminal for development)
- Student self-registration with OTP verification
- Staff can register other staff members (no public registration)
- Role stored on user profile (student or staff)

---

## User Registration

### Student Registration (`/register`)
- Two-step: Registration → OTP verification
- Fields: Full name, email, password (min 6 chars)
- OTP is printed to the backend terminal for development

### Staff Accounts
Staff accounts are created by other staff members via the `/staff-management` page.

**Pre-registered Staff Account** (for initial access):
- Email: `staff@gmail.com`
- Password: `123456`
- Role: Staff

---

## Authentication Flows

### Login
1. Visit `/login`
2. Enter email and password
3. Backend validates credentials and returns user info (name, role)
4. User redirected to `/dashboard`

### Student Registration
1. Visit `/register`
2. Enter name, email, and password
3. Backend generates OTP (prints to terminal)
4. Enter OTP to verify and complete registration

### Forgot Password
1. Visit `/forgot-password`
2. Enter registered email
3. Backend generates OTP (prints to terminal)
4. Verify OTP and set new password

---

## API Endpoints

- `POST /api/register/student` — start student registration (generates OTP)
- `POST /api/verify-registration-otp` — verify OTP and create account
- `POST /api/login` — email/password login
- `POST /api/admin/register-staff` — staff creates new staff member (requires authentication)
- `POST /api/forgot-password` — request password-reset OTP
- `POST /api/verify-forgot-password-otp` — verify password-reset OTP
- `POST /api/reset-password` — set a new password after OTP verification

---

## Frontend Pages

- `/login` — login form (email & password)
- `/register` — student registration + OTP verification
- `/forgot-password` — password reset flow
- `/staff-management` — staff-only page to add new staff members
- `/dashboard` — user dashboard showing name, email, and role

---

## Running Locally

1. Start backend:

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

2. Start frontend:

```bash
cd frontend_react
npm install
npm start
```

OTPs print to the backend terminal for development testing.

---

## Testing Scenarios

- Register a student via `/register`; check backend terminal for OTP
- Complete OTP verification and log in via `/login` with student account
- Use `/forgot-password` to test password reset flow (OTP in terminal)
- Login as initial staff (`staff@gmail.com` / `123456`) and visit `/staff-management` to add other staff members
- New staff created by existing staff can login immediately without OTP

---

## Notes

- Passwords are stored hashed (SHA-256) for development
- In-memory storage is used; data resets on backend restart
- Staff can create other staff accounts without OTP (direct account creation)
- Students cannot access the staff management page


