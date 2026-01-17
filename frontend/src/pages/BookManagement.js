import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumb';

function BookManagement() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [books, setBooks] = useState([]);
    const [message, setMessage] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [editingBook, setEditingBook] = useState(null);
    const [formData, setFormData] = useState({
        title: '',
        author: '',
        subject: '',
        description: '',
        year: new Date().getFullYear(),
        quantity: 1
    });

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        } else {
            const parsedUser = JSON.parse(userData);
            if (parsedUser.role !== 'staff') {
                navigate('/dashboard');
            } else {
                setUser(parsedUser);
                fetchBooks();
            }
        }
    }, [navigate]);

    const fetchBooks = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/books');
            const data = await response.json();
            setBooks(data);
        } catch (error) {
            setMessage('Error fetching books');
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'year' || name === 'quantity' ? parseInt(value) : value
        }));
    };

    const handleAddBook = async (e) => {
        e.preventDefault();

        if (!formData.title || !formData.author || !formData.subject) {
            setMessage('Title, author, and subject are required');
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/books', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    staff_email: user.email,
                    ...formData
                })
            });

            const data = await response.json();

            if (response.ok) {
                setMessage('✅ Book added successfully');
                setFormData({
                    title: '',
                    author: '',
                    subject: '',
                    description: '',
                    year: new Date().getFullYear(),
                    quantity: 1
                });
                setShowForm(false);
                fetchBooks();
                setTimeout(() => setMessage(''), 3000);
            } else {
                setMessage(data.error || 'Error adding book');
            }
        } catch (error) {
            setMessage('Error adding book');
        }
    };

    const handleDeleteBook = async (bookId) => {
        if (!window.confirm('Are you sure you want to delete this book?')) return;

        try {
            const response = await fetch(`http://localhost:5000/api/books/${bookId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    staff_email: user.email
                })
            });

            const data = await response.json();

            if (response.ok) {
                setMessage('✅ Book deleted successfully');
                fetchBooks();
                setTimeout(() => setMessage(''), 3000);
            } else {
                setMessage(data.error || 'Error deleting book');
            }
        } catch (error) {
            setMessage('Error deleting book');
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/login');
    };

    return (
        <>
            <Breadcrumb pageTitle="Manage Books" />
            <div className="book-management-container">
                <div className="book-management-content">
                    <div className="management-header">
                        <h1>📖 Book Management</h1>
                        <button
                            onClick={() => {
                                setShowForm(!showForm);
                                setEditingBook(null);
                                setFormData({
                                    title: '',
                                    author: '',
                                    subject: '',
                                    description: '',
                                    year: new Date().getFullYear(),
                                    quantity: 1
                                });
                            }}
                            className="add-book-btn"
                        >
                            {showForm ? '✕ Cancel' : '+ Add New Book'}
                        </button>
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

                    {showForm && (
                        <form onSubmit={handleAddBook} className="add-book-form">
                            <h2>Add New Book</h2>
                            <div className="form-grid">
                                <div className="form-group">
                                    <label>Title *</label>
                                    <input
                                        type="text"
                                        name="title"
                                        value={formData.title}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Author *</label>
                                    <input
                                        type="text"
                                        name="author"
                                        value={formData.author}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Subject *</label>
                                    <input
                                        type="text"
                                        name="subject"
                                        value={formData.subject}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Year</label>
                                    <input
                                        type="number"
                                        name="year"
                                        value={formData.year}
                                        onChange={handleInputChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Quantity</label>
                                    <input
                                        type="number"
                                        name="quantity"
                                        min="1"
                                        value={formData.quantity}
                                        onChange={handleInputChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Description</label>
                                    <textarea
                                        name="description"
                                        value={formData.description}
                                        onChange={handleInputChange}
                                        rows="3"
                                    />
                                </div>
                            </div>
                            <button type="submit" className="submit-btn">Add Book</button>
                        </form>
                    )}

                    <div className="books-management-grid">
                        {books.length > 0 ? (
                            books.map(book => (
                                <div key={book.id} className="management-book-card">
                                    <div className="management-book-header">
                                        <h3>{book.title}</h3>
                                        <span className="book-id-badge">ID: {book.id}</span>
                                    </div>
                                    <div className="management-book-info">
                                        <p><strong>Author:</strong> {book.author}</p>
                                        <p><strong>Subject:</strong> {book.subject}</p>
                                        <p><strong>Year:</strong> {book.year}</p>
                                        <p><strong>Available:</strong> {book.available_count}/{book.total_count}</p>
                                    </div>
                                    <button
                                        onClick={() => handleDeleteBook(book.id)}
                                        className="delete-btn"
                                    >
                                        🗑️ Delete
                                    </button>
                                </div>
                            ))
                        ) : (
                            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '2rem' }}>
                                <p>No books in the system yet.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}

export default BookManagement;
