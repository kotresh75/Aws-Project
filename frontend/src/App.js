import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';
import StaffManagement from './pages/StaffManagement';
import BookCatalog from './pages/BookCatalog';
import RequestHistory from './pages/RequestHistory';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import Notifications from './pages/Notifications';
import BookManagement from './pages/BookManagement';
import RequestManagement from './pages/RequestManagement';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route
                    path="/dashboard"
                    element={
                        <>
                            <Sidebar />
                            <div className="app-container">
                                <Dashboard />
                            </div>
                        </>
                    }
                />
                <Route
                    path="/staff-management"
                    element={
                        <>
                            <Sidebar />
                            <div className="app-container">
                                <StaffManagement />
                            </div>
                        </>
                    }
                />
                <Route
                    path="/catalog"
                    element={
                        <>
                            <Sidebar />
                            <div className="app-container">
                                <BookCatalog />
                            </div>
                        </>
                    }
                />
                <Route
                    path="/requests"
                    element={
                        <>
                            <Sidebar />
                            <div className="app-container">
                                <RequestHistory />
                            </div>
                        </>
                    }
                />
                <Route
                    path="/profile"
                    element={
                        <>
                            <Sidebar />
                            <div className="app-container">
                                <Profile />
                            </div>
                        </>
                    }
                />
                <Route
                    path="/settings"
                    element={
                        <>
                            <Sidebar />
                            <div className="app-container">
                                <Settings />
                            </div>
                        </>
                    }
                />
                <Route
                    path="/notifications"
                    element={
                        <>
                            <Sidebar />
                            <div className="app-container">
                                <Notifications />
                            </div>
                        </>
                    }
                />
                <Route
                    path="/book-management"
                    element={
                        <>
                            <Sidebar />
                            <div className="app-container">
                                <BookManagement />
                            </div>
                        </>
                    }
                />
                <Route
                    path="/request-management"
                    element={
                        <>
                            <Sidebar />
                            <div className="app-container">
                                <RequestManagement />
                            </div>
                        </>
                    }
                />
                <Route path="/" element={<Navigate to="/login" />} />
            </Routes>
        </Router>
    );
}

export default App;
