import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function BookCatalog() {
    const navigate = useNavigate();
    const [books, setBooks] = useState([]);
    const [filteredBooks, setFilteredBooks] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedSubject, setSelectedSubject] = useState('');
    const [user, setUser] = useState(null);
    const [message, setMessage] = useState('');
    const [selectedBook, setSelectedBook] = useState(null);
    const [showRequestForm, setShowRequestForm] = useState(false);
    const [subjects, setSubjects] = useState([]);
    const [requestData, setRequestData] = useState({ roll_no: '', semester: '', year: '' });

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        } else {
            const parsedUser = JSON.parse(userData);
            setUser(parsedUser);
            setRequestData({
                roll_no: parsedUser.roll_no || '',
                semester: parsedUser.semester || '',
                year: parsedUser.year || ''
            });
        }
        fetchBooks();
    }, [navigate]);

    useEffect(() => {
        filterBooks();
    }, [books, searchTerm, selectedSubject]);

    const fetchBooks = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/books');
            const data = await response.json();
            setBooks(data);
            const uniqueSubjects = [...new Set(data.map(b => b.subject))];
            setSubjects(uniqueSubjects.sort());
        } catch (error) {
            setMessage('Error fetching books');
        }
    };

    const filterBooks = () => {
        let filtered = books;
        if (selectedSubject) filtered = filtered.filter(book => book.subject === selectedSubject);
        if (searchTerm) {
            const search = searchTerm.toLowerCase();
            filtered = filtered.filter(book =>
                book.title.toLowerCase().includes(search) ||
                book.author.toLowerCase().includes(search)
            );
        }
        setFilteredBooks(filtered);
    };

    const handleRequestBook = async (book) => {
        if (!user) return;
        if (user.role === 'student' && (!requestData.roll_no || !requestData.semester || !requestData.year)) {
            setMessage('Error: Please fill in all details (Roll No, Semester, Year)');
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/requests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: user.email,
                    book_id: book.id,
                    roll_no: requestData.roll_no,
                    semester: requestData.semester,
                    year: requestData.year
                })
            });
            const data = await response.json();
            if (response.ok) {
                setMessage(`✅ Request submitted for "${book.title}"`);
                setShowRequestForm(false);
                setSelectedBook(null);
                setTimeout(() => setMessage(''), 3000);
            } else {
                setMessage(data.error || 'Error submitting request');
            }
        } catch (error) {
            setMessage('Error submitting request');
        }
    };

    return (
        <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
            <div className="glass-card" style={{ marginBottom: '2rem', textAlign: 'center' }}>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    📖 Book Catalog
                </h1>
                <p style={{ color: 'var(--text-muted)' }}>Search and request books from our library collection</p>

                {message && (
                    <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`} style={{ marginTop: '1rem', display: 'inline-block' }}>
                        {message}
                    </div>
                )}

                <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
                    <input
                        type="text"
                        placeholder="Search by title or author..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{ padding: '0.75rem 1rem', borderRadius: '50px', border: '1px solid rgba(0,0,0,0.1)', background: 'rgba(255,255,255,0.8)', minWidth: '300px' }}
                    />
                    <select
                        value={selectedSubject}
                        onChange={(e) => setSelectedSubject(e.target.value)}
                        style={{ padding: '0.75rem 1rem', borderRadius: '50px', border: '1px solid rgba(0,0,0,0.1)', background: 'rgba(255,255,255,0.8)' }}
                    >
                        <option value="">All Subjects</option>
                        {subjects.map(subject => (
                            <option key={subject} value={subject}>{subject}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '2rem' }}>
                {filteredBooks.length > 0 ? (
                    filteredBooks.map(book => (
                        <div key={book.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', height: '100%', position: 'relative', overflow: 'hidden' }}>
                            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                                {book.cover_image && (
                                    <div style={{ flexShrink: 0, width: '80px', height: '120px', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
                                        <img src={book.cover_image} alt={book.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={(e) => { e.target.style.display = 'none'; }} />
                                    </div>
                                )}
                                <div style={{ flex: 1 }}>
                                    <h3 style={{ fontSize: '1.2rem', marginBottom: '0.25rem', color: 'var(--text-main)' }}>{book.title}</h3>
                                    <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem' }}>by {book.author}</p>
                                    <div style={{ marginTop: '0.5rem' }}>
                                        <span className={`badge ${book.available_count > 0 ? 'badge-success' : 'badge-danger'}`}>
                                            {book.available_count > 0 ? 'Available' : 'Out of Stock'}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: '1rem', flex: 1 }}>
                                <p><strong>Subject:</strong> {book.subject}</p>
                                <p><strong>Copies:</strong> {book.available_count} / {book.total_count}</p>
                            </div>

                            <button
                                onClick={() => { setSelectedBook(book); setShowRequestForm(true); }}
                                className={book.available_count > 0 ? "btn-primary" : "btn-warning"}
                                style={{
                                    width: '100%',
                                    background: book.available_count <= 0 ? 'linear-gradient(135deg, var(--warning), #d97706)' : undefined,
                                    color: 'white',
                                    border: 'none'
                                }}
                            >
                                {book.available_count > 0 ? 'Request Book' : 'Request Restock'}
                            </button>

                            {book.pdf_url && (
                                <button
                                    onClick={() => window.open(book.pdf_url, '_blank')}
                                    className="btn-secondary"
                                    style={{ width: '100%', marginTop: '0.5rem' }}
                                >
                                    Read PDF
                                </button>
                            )}
                        </div>
                    ))
                ) : (
                    <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                        No books found matching your criteria.
                    </div>
                )}
            </div>

            {showRequestForm && selectedBook && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(5px)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
                }} onClick={() => setShowRequestForm(false)}>
                    <div className="glass-card" style={{ width: '90%', maxWidth: '500px', background: 'rgba(255,255,255,0.95)' }} onClick={e => e.stopPropagation()}>
                        <h2 style={{ marginBottom: '1.5rem', color: 'var(--text-main)' }}>Request Book</h2>
                        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(0,0,0,0.03)', borderRadius: '8px' }}>
                            <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.1rem' }}>{selectedBook.title}</h3>
                            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Author: {selectedBook.author}</p>
                            {selectedBook.cover_image && (
                                <img
                                    src={selectedBook.cover_image}
                                    alt={selectedBook.title}
                                    style={{ width: '100px', height: '150px', objectFit: 'cover', borderRadius: '4px', marginTop: '1rem', display: 'block', marginLeft: 'auto', marginRight: 'auto' }}
                                    onError={(e) => e.target.style.display = 'none'}
                                />
                            )}
                        </div>

                        {user.role === 'student' && (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                                <div style={{ gridColumn: '1 / -1' }}>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Roll No</label>
                                    <input type="text" value={requestData.roll_no} onChange={(e) => setRequestData({ ...requestData, roll_no: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #ddd' }} />
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Semester</label>
                                    <input type="text" value={requestData.semester} onChange={(e) => setRequestData({ ...requestData, semester: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #ddd' }} />
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Year</label>
                                    <input type="text" value={requestData.year} onChange={(e) => setRequestData({ ...requestData, year: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #ddd' }} />
                                </div>
                            </div>
                        )}

                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <button onClick={() => handleRequestBook(selectedBook)} className="btn-primary" style={{ flex: 1 }}>Confirm</button>
                            <button onClick={() => setShowRequestForm(false)} className="btn-danger" style={{ flex: 1, background: 'transparent', color: 'var(--danger)', border: '1px solid var(--danger)' }}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default BookCatalog;
