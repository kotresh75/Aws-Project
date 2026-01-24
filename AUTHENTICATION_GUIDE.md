
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


---

## Deploying React Frontend to AWS EC2

### Step 1: Build the React App Locally
```bash
cd frontend_react
npm install
npm run build
```
This creates a `build/` folder with optimized production files.

### Step 2: Update API Base URL
Before building, update the API URL in your React app to point to your EC2 backend:
```javascript
// In src/config.js or wherever API URL is defined
const API_BASE_URL = 'http://your-ec2-public-ip:5000';
```

### Step 3: Transfer Build Files to EC2
```bash
# From your local machine
scp -i your-key.pem -r build/* ec2-user@your-ec2-ip:/home/ec2-user/frontend/
```

### Step 4: Install and Configure Nginx on EC2
```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Install Nginx
sudo yum install nginx -y

# Create directory for frontend
sudo mkdir -p /var/www/html

# Copy build files
sudo cp -r /home/ec2-user/frontend/* /var/www/html/

# Set permissions
sudo chown -R nginx:nginx /var/www/html
```

### Step 5: Configure Nginx
```bash
sudo nano /etc/nginx/nginx.conf
```
Replace server block with:
```nginx
server {
    listen 80;
    server_name your-ec2-public-ip;
    root /var/www/html;
    index index.html;

    # React Router support
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to Flask backend
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Step 6: Start Nginx
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 7: Open Security Group Ports
```
AWS Console → EC2 → Security Groups → Edit Inbound Rules
- Add HTTP (80) from 0.0.0.0/0
- Add Custom TCP (5000) from 0.0.0.0/0 (for API)
```

### Step 8: Access Your App
Open browser: `http://your-ec2-public-ip`

---

## Quick Deployment Checklist

| Step | Command/Action |
|------|----------------|
| Build React | `npm run build` |
| Transfer files | `scp -r build/* ec2-user@EC2_IP:/home/ec2-user/frontend/` |
| Install Nginx | `sudo yum install nginx -y` |
| Copy to www | `sudo cp -r frontend/* /var/www/html/` |
| Start Nginx | `sudo systemctl start nginx` |
| Open port 80 | AWS Console → Security Groups |