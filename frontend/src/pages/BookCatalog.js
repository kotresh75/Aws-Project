import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumb';

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

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        } else {
            setUser(JSON.parse(userData));
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

            // Extract unique subjects
            const uniqueSubjects = [...new Set(data.map(b => b.subject))];
            setSubjects(uniqueSubjects.sort());
        } catch (error) {
            setMessage('Error fetching books');
        }
    };

    const filterBooks = () => {
        let filtered = books;

        if (selectedSubject) {
            filtered = filtered.filter(book => book.subject === selectedSubject);
        }

        if (searchTerm) {
            const search = searchTerm.toLowerCase();
            filtered = filtered.filter(book =>
                book.title.toLowerCase().includes(search) ||
                book.author.toLowerCase().includes(search)
            );
        }

        setFilteredBooks(filtered);
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/login');
    };

    const handleRequestBook = async (book) => {
        if (!user) return;

        try {
            const response = await fetch('http://localhost:5000/api/requests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: user.email,
                    book_id: book.id
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
        <>
            <Breadcrumb pageTitle="Browse" />
            <div className="catalog-container">
                <div className="catalog-content">
                    <div className="catalog-header">
                        <h1>📖 Book Catalog</h1>
                        <p>Search and request books from our library collection</p>
                    </div>
                    {message && (
                        <div className="message" style={{
                            padding: '12px 16px',
                            marginBottom: '20px',
                            borderRadius: '8px',
                            backgroundColor: message.includes('Error') ? '#fee2e2' : '#dcfce7',
                            color: message.includes('Error') ? '#991b1b' : '#15803d',
                            textAlign: 'center'
                        }}>
                            {message}
                        </div>
                    )}

                    <div className="filters-section">
                        <div className="search-box">
                            <input
                                type="text"
                                placeholder="Search by title or author..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="search-input"
                            />
                        </div>

                        <select
                            value={selectedSubject}
                            onChange={(e) => setSelectedSubject(e.target.value)}
                            className="filter-select"
                        >
                            <option value="">All Subjects</option>
                            {subjects.map(subject => (
                                <option key={subject} value={subject}>{subject}</option>
                            ))}
                        </select>
                    </div>

                    <div className="results-info">
                        <p>Showing {filteredBooks.length} book(s)</p>
                    </div>

                    <div className="books-grid">
                        {filteredBooks.length > 0 ? (
                            filteredBooks.map(book => (
                                <div key={book.id} className="book-card">
                                    <div className="book-header">
                                        <h3>{book.title}</h3>
                                        <span className="book-id">ID: {book.id}</span>
                                    </div>

                                    <div className="book-details">
                                        <p><strong>Author:</strong> {book.author}</p>
                                        <p><strong>Subject:</strong> {book.subject}</p>
                                        <p><strong>Year:</strong> {book.year}</p>
                                        <p className="description"><strong>Description:</strong> {book.description}</p>
                                    </div>

                                    <div className="book-availability">
                                        <div className="availability-badge">
                                            <span className={book.available_count > 0 ? 'available' : 'unavailable'}>
                                                {book.available_count > 0 ? '✅ Available' : '❌ Not Available'}
                                            </span>
                                        </div>
                                        <span className="book-count">
                                            {book.available_count}/{book.total_count} copies
                                        </span>
                                    </div>

                                    <button
                                        onClick={() => {
                                            setSelectedBook(book);
                                            setShowRequestForm(true);
                                        }}
                                        className="request-btn"
                                        disabled={book.available_count <= 0}
                                    >
                                        {book.available_count > 0 ? '📝 Request Book' : '⏳ Unavailable'}
                                    </button>
                                </div>
                            ))
                        ) : (
                            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '2rem' }}>
                                <p style={{ fontSize: '1.1rem', color: '#6b7280' }}>No books found matching your search.</p>
                            </div>
                        )}
                    </div>
                </div>

                {showRequestForm && selectedBook && (
                    <div className="modal-overlay" onClick={() => setShowRequestForm(false)}>
                        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                            <h2>Request: {selectedBook.title}</h2>
                            <div className="modal-book-info">
                                <p><strong>Author:</strong> {selectedBook.author}</p>
                                <p><strong>Subject:</strong> {selectedBook.subject}</p>
                                <p><strong>Available:</strong> {selectedBook.available_count}/{selectedBook.total_count}</p>
                            </div>

                            <div className="modal-buttons">
                                <button
                                    onClick={() => handleRequestBook(selectedBook)}
                                    className="confirm-btn"
                                >
                                    ✓ Confirm Request
                                </button>
                                <button
                                    onClick={() => setShowRequestForm(false)}
                                    className="cancel-btn"
                                >
                                    ✗ Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}

export default BookCatalog;
