import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Layout from './components/Layout';
import Welcome from './pages/Welcome';
import RoleSelection from './pages/RoleSelection';
import StudentLogin from './pages/StudentLogin';
import StaffLogin from './pages/StaffLogin';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';
import ContactSupport from './pages/ContactSupport';
import NotFound from './pages/NotFound';
import Unauthorized from './pages/Unauthorized';
import ServerError from './pages/ServerError';
import Logout from './pages/Logout';
import Dashboard from './pages/Dashboard';
import StaffManagement from './pages/StaffManagement';
import StudentManagement from './pages/StudentManagement';
import BookCatalog from './pages/BookCatalog';
import RequestHistory from './pages/RequestHistory';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import Notifications from './pages/Notifications';
import BookManagement from './pages/BookManagement';
import RequestManagement from './pages/RequestManagement';
import About from './pages/About';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Welcome />} />
                <Route path="/login" element={<RoleSelection />} />
                <Route path="/student-login" element={<StudentLogin />} />
                <Route path="/staff-login" element={<StaffLogin />} />
                <Route path="/register" element={<Register />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/logout" element={<Logout />} />

                {/* Legal & Support */}
                <Route path="/privacy" element={<PrivacyPolicy />} />
                <Route path="/terms" element={<TermsOfService />} />
                <Route path="/support" element={<ContactSupport />} />

                {/* Error Pages */}
                <Route path="/unauthorized" element={<Unauthorized />} />
                <Route path="/server-error" element={<ServerError />} />

                {/* Protected Routes */}
                <Route element={<Layout />}>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/staff-management" element={<StaffManagement />} />
                    <Route path="/catalog" element={<BookCatalog />} />
                    <Route path="/requests" element={<RequestHistory />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/notifications" element={<Notifications />} />
                    <Route path="/book-management" element={<BookManagement />} />
                    <Route path="/request-management" element={<RequestManagement />} />
                    <Route path="/student-management" element={<StudentManagement />} />
                    <Route path="/about" element={<About />} />
                </Route>

                {/* 404 Catch-all - MUST be last */}
                <Route path="*" element={<NotFound />} />
            </Routes>
        </Router>
    );
}

export default App;
