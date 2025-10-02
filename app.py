from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:9456@localhost:5432/library_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default="student")

    transactions = db.relationship('Transaction', back_populates='user')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(100))
    copies = db.Column(db.Integer)
    available = db.Column(db.Integer)

    transactions = db.relationship('Transaction', back_populates='book')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    issue_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', back_populates='transactions')
    book = db.relationship('Book', back_populates='transactions')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first.", "warning")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Admin access required!", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password_raw = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for('register'))
        hashed = generate_password_hash(password_raw)
        user = User(name=name, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email'].strip().lower()
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['role'] = user.role
        session['user_name'] = user.name
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))
    flash("Invalid credentials!", "danger")
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    books = Book.query.all()
    if session['role'] == 'admin':
        transactions = Transaction.query.order_by(Transaction.issue_date.desc()).all()
    else:
        transactions = Transaction.query.filter_by(user_id=session['user_id']).order_by(Transaction.issue_date.desc()).all()
    return render_template('dashboard.html', books=books, transactions=transactions, role=session['role'])

@app.route('/books')
@login_required
def books_list():
    q = request.args.get('q', '').strip()
    if q:
        pattern = "%{}%".format(q)
        books = Book.query.filter(db.or_(Book.title.ilike(pattern), Book.author.ilike(pattern))).all()
    else:
        books = Book.query.all()
    return render_template('books.html', books=books, q=q)

@app.route('/authors')
@login_required
def authors():
    books = Book.query.all()
    author_books = {}
    for book in books:
        author_books.setdefault(book.author or "Unknown", []).append(book)
    return render_template('authors.html', author_books=author_books)

@app.route('/add_book', methods=['POST'])
@admin_required
def add_book():
    title = request.form['title'].strip()
    author = request.form['author'].strip()
    try:
        copies = int(request.form['copies'])
    except (ValueError, TypeError):
        copies = 1
    book = Book(title=title, author=author, copies=copies, available=copies)
    db.session.add(book)
    db.session.commit()
    flash("Book added successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/edit_book/<int:book_id>', methods=['GET','POST'])
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        title = request.form['title'].strip()
        author = request.form['author'].strip()
        try:
            copies = int(request.form['copies'])
        except (ValueError, TypeError):
            copies = book.copies
        # adjust available if copies change
        delta = copies - book.copies
        book.title = title
        book.author = author
        book.copies = copies
        book.available = max(0, book.available + delta)
        db.session.commit()
        flash("Book updated.", "success")
        return redirect(url_for('dashboard'))
    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    active = Transaction.query.filter_by(book_id=book.id, return_date=None).first()
    if active:
        flash("Cannot delete book while it is issued to someone.", "danger")
        return redirect(url_for('dashboard'))
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted.", "info")
    return redirect(url_for('dashboard'))

@app.route('/issue/<int:book_id>')
@login_required
def issue(book_id):
    book = Book.query.get_or_404(book_id)
    if book.available and book.available > 0:
        transaction = Transaction(user_id=session['user_id'], book_id=book.id)
        book.available -= 1
        db.session.add(transaction)
        db.session.commit()
        flash("Book issued successfully!", "success")
    else:
        flash("Book not available!", "danger")
    return redirect(url_for('dashboard'))

@app.route('/return/<int:transaction_id>')
@login_required
def return_book(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if session['role'] != 'admin' and transaction.user_id != session['user_id']:
        flash("You can't return someone else's book!", "danger")
        return redirect(url_for('dashboard'))
    if transaction.return_date:
        flash("Book already returned.", "info")
        return redirect(url_for('dashboard'))
    transaction.return_date = datetime.datetime.utcnow()
    book = Book.query.get(transaction.book_id)
    if book:
        book.available = (book.available or 0) + 1
    db.session.commit()
    flash("Book returned successfully!", "success")
    return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
