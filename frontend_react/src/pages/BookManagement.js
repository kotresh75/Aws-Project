import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function BookManagement() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [books, setBooks] = useState([]);
    const [filteredBooks, setFilteredBooks] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [message, setMessage] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [showCopiesModal, setShowCopiesModal] = useState(false);
    const [editingBook, setEditingBook] = useState(null);
    const [selectedBookCopies, setSelectedBookCopies] = useState([]);
    const [selectedBookTitle, setSelectedBookTitle] = useState('');
    const [formData, setFormData] = useState({ title: '', author: '', subject: '', description: '', year: new Date().getFullYear(), quantity: 1, pdf_url: '', isbn: '', cover_image: '' });

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) { navigate('/login'); }
        else {
            const parsedUser = JSON.parse(userData);
            if (parsedUser.role !== 'staff') { navigate('/dashboard'); }
            else { setUser(parsedUser); fetchBooks(); }
        }
    }, [navigate]);

    useEffect(() => {
        if (searchTerm) {
            const lower = searchTerm.toLowerCase();
            setFilteredBooks(books.filter(b => b.title.toLowerCase().includes(lower) || b.author.toLowerCase().includes(lower) || (b.isbn && b.isbn.includes(lower))));
        } else { setFilteredBooks(books); }
    }, [searchTerm, books]);

    const fetchBooks = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/books');
            const data = await response.json();
            setBooks(data);
            setFilteredBooks(data);
        } catch (error) { setMessage('Error fetching books'); }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: (name === 'year' || name === 'quantity') ? parseInt(value) || 0 : value }));
    };

    const handleFetchDetails = async () => {
        if (!formData.isbn) { setMessage('Please enter ISBN'); return; }

        const cleanIsbn = formData.isbn.replace(/[^0-9X]/gi, ''); // Sanitize ISBN
        setMessage('Fetching details from Google Books...');

        try {
            // 1. Try Google Books API
            const googleRes = await fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${cleanIsbn}`);
            const googleData = await googleRes.json();

            if (googleData.items && googleData.items.length > 0) {
                const info = googleData.items[0].volumeInfo;
                setFormData(prev => ({
                    ...prev,
                    title: info.title || prev.title,
                    author: info.authors ? info.authors.join(', ') : prev.author,
                    description: info.description || prev.description,
                    year: info.publishedDate ? parseInt(info.publishedDate.substring(0, 4)) : prev.year,
                    cover_image: info.imageLinks ? (info.imageLinks.thumbnail || info.imageLinks.smallThumbnail) : prev.cover_image,
                    subject: info.categories ? info.categories[0] : prev.subject
                }));
                setMessage('✅ Found via Google Books');
                setTimeout(() => setMessage(''), 3000);
                return;
            }

            // 2. Fallback to Open Library API
            setMessage('Trying Open Library...');
            const openLibRes = await fetch(`https://openlibrary.org/api/books?bibkeys=ISBN:${cleanIsbn}&format=json&jscmd=data`);
            const openLibData = await openLibRes.json();
            const key = `ISBN:${cleanIsbn}`;

            if (openLibData[key]) {
                const info = openLibData[key];
                setFormData(prev => ({
                    ...prev,
                    title: info.title || prev.title,
                    author: info.authors ? info.authors.map(a => a.name).join(', ') : prev.author,
                    description: info.description || prev.description,
                    year: info.publish_date ? parseInt(info.publish_date.match(/\d{4}/)) : prev.year,
                    cover_image: info.cover ? info.cover.large || info.cover.medium : prev.cover_image,
                    subject: info.subjects ? info.subjects[0].name : prev.subject
                }));
                setMessage('✅ Found via Open Library');
            } else {
                setMessage('❌ Book not found in any database');
            }
            setTimeout(() => setMessage(''), 3000);

        } catch (error) {
            console.error(error);
            setMessage('Error fetching details');
        }
    };

    const openModal = (book = null) => {
        if (book) {
            setEditingBook(book);
            setFormData({
                title: book.title, author: book.author, subject: book.subject, description: book.description || '',
                year: book.year, quantity: book.total_count, pdf_url: book.pdf_url || '', isbn: book.isbn || '', cover_image: book.cover_image || ''
            });
        } else {
            setEditingBook(null);
            setFormData({ title: '', author: '', subject: '', description: '', year: new Date().getFullYear(), quantity: 1, pdf_url: '', isbn: '', cover_image: '' });
        }
        setShowModal(true);
    };

    const handleViewCopies = (book) => { setSelectedBookCopies(book.copies || []); setSelectedBookTitle(book.title); setShowCopiesModal(true); };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const url = editingBook ? `http://localhost:5000/api/books/${editingBook.id}` : 'http://localhost:5000/api/books';
            const method = editingBook ? 'PUT' : 'POST';
            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    staff_email: user.email, ...formData,
                    available_count: editingBook ? (formData.quantity - (editingBook.total_count - editingBook.available_count)) : formData.quantity,
                    total_count: formData.quantity
                })
            });
            if (response.ok) {
                setMessage(editingBook ? '✅ Book updated' : '✅ Book added');
                setShowModal(false);
                fetchBooks();
                setTimeout(() => setMessage(''), 3000);
            } else { setMessage('Error saving book'); }
        } catch (error) { setMessage('Error saving book'); }
    };

    const handleDeleteBook = async (bookId) => {
        if (!window.confirm('Delete this book?')) return;
        try {
            const response = await fetch(`http://localhost:5000/api/books/${bookId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ staff_email: user.email })
            });
            if (response.ok) { setMessage('✅ Book deleted'); fetchBooks(); setTimeout(() => setMessage(''), 3000); }
            else { setMessage('Error deleting book'); }
        } catch (error) { setMessage('Error deleting book'); }
    };

    return (
        <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
            <div className="glass-card" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <h1 style={{ fontSize: '2rem', margin: 0, background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                        📚 Manage Library Catalog
                    </h1>
                    <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>Add, edit, and track book inventory</p>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <input type="text" placeholder="Search..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(0,0,0,0.1)', background: 'rgba(255,255,255,0.8)' }} />
                    <button onClick={() => openModal()} className="btn-primary">+ Add Book</button>
                </div>
            </div>

            {message && <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`} style={{ marginBottom: '1rem' }}>{message}</div>}

            <div className="glass-table-container">
                <table className="glass-table">
                    <thead>
                        <tr>
                            <th>Cover</th><th>Title</th><th>Author</th><th>Subject</th><th>Year</th><th>Stock</th><th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredBooks.map(book => (
                            <tr key={book.id}>
                                <td>{book.cover_image ? <img src={book.cover_image} alt="cover" style={{ width: '40px', height: '60px', objectFit: 'cover', borderRadius: '4px' }} /> : '📚'}</td>
                                <td>{book.title}</td>
                                <td>{book.author}</td>
                                <td><span className="badge badge-primary">{book.subject}</span></td>
                                <td>{book.year}</td>
                                <td>
                                    <span style={{ color: book.available_count === 0 ? 'var(--danger)' : 'var(--success)', fontWeight: 600 }}>{book.available_count}</span>
                                    <span style={{ color: 'var(--text-muted)' }}> / {book.total_count}</span>
                                </td>
                                <td>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                        <button onClick={() => handleViewCopies(book)} className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>Copies</button>
                                        <button onClick={() => openModal(book)} className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>✏️</button>
                                        <button onClick={() => handleDeleteBook(book.id)} className="btn-danger" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>🗑️</button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(5px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }} onClick={() => setShowModal(false)}>
                    <div className="glass-card" style={{ width: '90%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto', background: 'rgba(255,255,255,0.95)' }} onClick={e => e.stopPropagation()}>
                        <h2 style={{ marginBottom: '1.5rem' }}>{editingBook ? 'Edit Book' : 'Add New Book'}</h2>
                        <form onSubmit={handleSubmit}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                                <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '0.5rem' }}>
                                    <input type="text" name="isbn" value={formData.isbn} onChange={handleInputChange} placeholder="ISBN (optional)" style={{ flex: 1, padding: '0.75rem', borderRadius: '6px', border: '1px solid #ddd' }} />
                                    <button type="button" onClick={handleFetchDetails} className="btn-secondary">⬇ Fetch</button>
                                </div>
                                <div style={{ gridColumn: '1 / -1' }}><input type="text" name="title" value={formData.title} onChange={handleInputChange} placeholder="Title *" required style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #ddd' }} /></div>
                                <div><input type="text" name="author" value={formData.author} onChange={handleInputChange} placeholder="Author *" required style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #ddd' }} /></div>
                                <div><input type="text" name="subject" value={formData.subject} onChange={handleInputChange} placeholder="Subject *" required style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #ddd' }} /></div>
                                <div><input type="number" name="year" value={formData.year} onChange={handleInputChange} placeholder="Year" style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #ddd' }} /></div>
                                <div><input type="number" name="quantity" value={formData.quantity} onChange={handleInputChange} placeholder="Qty" min="1" style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #ddd' }} /></div>
                                <div style={{ gridColumn: '1 / -1' }}><input type="url" name="cover_image" value={formData.cover_image} onChange={handleInputChange} placeholder="Cover Image URL" style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #ddd' }} /></div>
                                <div style={{ gridColumn: '1 / -1' }}><textarea name="description" value={formData.description} onChange={handleInputChange} placeholder="Description" rows="3" style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #ddd' }} /></div>
                            </div>
                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                                <button type="submit" className="btn-primary" style={{ flex: 1 }}>Save</button>
                                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary" style={{ flex: 1 }}>Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {showCopiesModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(5px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }} onClick={() => setShowCopiesModal(false)}>
                    <div className="glass-card" style={{ width: '90%', maxWidth: '500px', background: 'rgba(255,255,255,0.95)' }} onClick={e => e.stopPropagation()}>
                        <h3 style={{ marginBottom: '1rem' }}>Copies: {selectedBookTitle}</h3>
                        <div style={{ maxHeight: '300px', overflowY: 'auto', background: '#f9fafb', padding: '1rem', borderRadius: '8px' }}>
                            {selectedBookCopies.length > 0 ? selectedBookCopies.map((copyId, idx) => (
                                <div key={idx} style={{ padding: '0.5rem', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between' }}>
                                    <code>{copyId}</code><span style={{ color: 'green' }}>Available</span>
                                </div>
                            )) : <p style={{ textAlign: 'center', color: '#999' }}>No individual copies tracked.</p>}
                        </div>
                        <button onClick={() => setShowCopiesModal(false)} className="btn-secondary" style={{ width: '100%', marginTop: '1rem' }}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default BookManagement;
