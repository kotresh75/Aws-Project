import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function StudentManagement() {
    const navigate = useNavigate();
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [history, setHistory] = useState([]);
    const [showHistoryModal, setShowHistoryModal] = useState(false);
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    useEffect(() => {
        const fetchStudents = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/api/users?role=student');
                if (response.ok) { setStudents(await response.json()); }
            } catch (err) { console.error(err); } finally { setLoading(false); }
        };
        fetchStudents();
    }, []);

    const handleDelete = async (email) => {
        if (!window.confirm(`Are you sure you want to delete ${email}?`)) return;
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/users/${email}?staff_email=${user.email}`, { method: 'DELETE' });
            if (response.ok) { setStudents(students.filter(s => s.email !== email)); }
            else { alert('Failed to delete student'); }
        } catch (err) { alert('Error deleting student'); }
    };

    const handleViewHistory = async (student) => {
        setSelectedStudent(student);
        setShowHistoryModal(true);
        setHistory([]);
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/user-requests/${student.email}`);
            if (response.ok) setHistory(await response.json());
        } catch (err) { console.error(err); }
    };

    const filteredStudents = students.filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase()) || s.email.toLowerCase().includes(searchTerm.toLowerCase()));

    return (
        <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
            <div className="glass-card" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1 style={{ fontSize: '2rem', margin: 0, background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    🎓 Student Management
                </h1>
                <input
                    type="text"
                    placeholder="Search students..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(0,0,0,0.1)', background: 'rgba(255,255,255,0.8)', minWidth: '300px' }}
                />
            </div>

            <div className="glass-table-container">
                <table className="glass-table">
                    <thead>
                        <tr><th>Name</th><th>Email</th><th>Roll No</th><th>Year</th><th>Joined</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                        {loading ? <tr><td colSpan="6" style={{ textAlign: 'center' }}>Loading...</td></tr> :
                            filteredStudents.length > 0 ? filteredStudents.map((s, idx) => (
                                <tr key={idx}>
                                    <td>{s.name}</td>
                                    <td>{s.email}</td>
                                    <td>{s.roll_no || '-'}</td>
                                    <td>{s.year || '-'}</td>
                                    <td>{new Date(s.created_at).toLocaleDateString()}</td>
                                    <td>
                                        <button onClick={() => handleViewHistory(s)} className="btn-secondary" style={{ marginRight: '0.5rem', padding: '0.4rem 0.8rem' }}>📜 History</button>
                                        <button onClick={() => handleDelete(s.email)} className="btn-danger" style={{ padding: '0.4rem 0.8rem' }}>🗑️ Delete</button>
                                    </td>
                                </tr>
                            )) : <tr><td colSpan="6" style={{ textAlign: 'center' }}>No students found.</td></tr>}
                    </tbody>
                </table>
            </div>

            {showHistoryModal && selectedStudent && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(5px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }} onClick={() => setShowHistoryModal(false)}>
                    <div className="glass-card" style={{ width: '90%', maxWidth: '600px', maxHeight: '80vh', overflowY: 'auto', background: 'rgba(255,255,255,0.95)' }} onClick={e => e.stopPropagation()}>
                        <h2 style={{ marginBottom: '1rem' }}>History: {selectedStudent.name}</h2>
                        {history.length > 0 ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                {history.map(req => (
                                    <div key={req.request_id} style={{ padding: '1rem', background: '#f9fafb', borderRadius: '8px', border: '1px solid #eee' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                            <span style={{ fontWeight: 600 }}>{req.book_name}</span>
                                            <span className={`badge ${req.status === 'approved' ? 'badge-success' : 'badge-warning'}`}>{req.status}</span>
                                        </div>
                                        <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Requested: {new Date(req.requested_at).toLocaleDateString()}</div>
                                    </div>
                                ))}
                            </div>
                        ) : <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No history found.</p>}
                        <button onClick={() => setShowHistoryModal(false)} className="btn-secondary" style={{ width: '100%', marginTop: '1rem' }}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default StudentManagement;
