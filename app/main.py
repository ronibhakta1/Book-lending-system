from flask import Flask, jsonify, request
import jwt
import os
import json
from datetime import datetime, timedelta
from app import create_app, db  # Absolute import
from app.models import User, Book, Loan, Waitlist
from app.middleware import token_required, librarian_required
import bcrypt
from flask_cors import CORS

app = create_app()
CORS(app)
# Load global config
with open('/app/app/config.json', 'r') as f:
    config = json.load(f)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
        token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/api/dashboard')
# @token_required
def dashboard():
    total_loans = Loan.query.count()
    active_loans = Loan.query.filter_by(return_date=None).count()
    books_lent = Book.query.filter(Book.copies_available < Book.copies_owned).count()
    loans_per_title = {book.title: Loan.query.filter_by(book_id=book.id).count() for book in Book.query.all()}
    all_loans = [{'title': l.book.title, 'username': l.user.username, 'loan_date': l.loan_date.isoformat(),
                  'return_date': l.return_date.isoformat() if l.return_date else None,
                  'duration': ((l.return_date or datetime.utcnow()) - l.loan_date).total_seconds() / 3600 if l.return_date else None}
                 for l in Loan.query.all()]
    return jsonify({
        'total_loans': total_loans,
        'active_loans': active_loans,
        'books_lent': books_lent,
        'loans_per_title': loans_per_title,
        'all_loans': all_loans
    })


@app.route('/api/books/list')
@token_required
def list_books(current_user):
    books = [{'id': b.id, 'title': b.title, 'copies_owned': b.copies_owned, 'copies_available': b.copies_available}
             for b in Book.query.all()]
    return jsonify(books)


@app.route('/api/books/<int:book_id>', methods=['PUT'])
@librarian_required
def update_book(current_user, book_id):
    data = request.get_json()
    book = Book.query.get_or_404(book_id)
    book.copies_owned = data.get('copies_owned', book.copies_owned)
    book.copies_available = min(book.copies_available, book.copies_owned)
    db.session.commit()
    return jsonify({'message': 'Book updated'})


@app.route('/api/borrow/<int:book_id>', methods=['POST'])
@token_required
def borrow_book(current_user, book_id):
    book = Book.query.get_or_404(book_id)
    if book.copies_available > 0:
        loan = Loan(user_id=current_user.id, book_id=book_id)
        book.copies_available -= 1
        db.session.add(loan)
        db.session.commit()
        return jsonify({'message': 'Book borrowed'})
    return jsonify({'message': 'No copies available'}), 400


# The `@app.route('/api/return/<int:loan_id>', methods=['POST'])` decorator in the Flask application
# is defining a route for returning a borrowed book. It specifies that the endpoint
# `/api/return/<loan_id>` accepts POST requests. The `@token_required` decorator is used to ensure
# that the user making the request is authenticated and has a valid token.
@app.route('/api/return/<int:loan_id>', methods=['POST'])
@token_required
def return_book(current_user, loan_id):
    """
    This Python function returns a book that was previously loaned by a user.
    
    :param current_user: The `current_user` parameter in the `return_book` function likely represents
    the user who is currently logged in or performing the action of returning a book. This parameter is
    used to verify that the user attempting to return the book is the same user who borrowed it, as well
    as to check if the
    :param loan_id: The `loan_id` parameter in the `return_book` function is used to identify the
    specific loan that the user wants to return. It is typically a unique identifier for a loan record
    in the database. By passing the `loan_id` to this function, the system can retrieve the
    corresponding loan information
    :return: The function `return_book` is returning a JSON response with a message indicating whether
    the book was successfully returned or if there was an invalid loan. If the book is successfully
    returned, the message 'Book returned' is returned. If the loan is invalid (e.g., the loan does not
    belong to the current user or the book has already been returned), a message 'Invalid loan' is
    returned along
    """
    loan = Loan.query.get_or_404(loan_id)
    if loan.user_id != current_user.id or loan.return_date:
        return jsonify({'message': 'Invalid loan'}), 403
    loan.return_date = datetime.utcnow()
    loan.duration = (loan.return_date - loan.loan_date).total_seconds() / 3600
    book = Book.query.get(loan.book_id)
    book.copies_available += 1
    db.session.commit()
    return jsonify({'message': 'Book returned'})


@app.route('/api/config', methods=['GET', 'PUT'])
@librarian_required
def manage_config(current_user):
    global config
    if request.method == 'GET':
        return jsonify(config)
    elif request.method == 'PUT':
        config.update(request.get_json())
        with open('/app/app/config.json', 'w') as f:
            json.dump(config, f)
        return jsonify({'message': 'Config updated'})


def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            hashed = bcrypt.hashpw(
                'password123'.encode('utf-8'), bcrypt.gensalt())
            db.session.add_all([
                User(username='librarian1', password=hashed.decode(
                    'utf-8'), role='librarian'),
                User(username='patron1', password=hashed.decode(
                    'utf-8'), role='patron'),
                Book(title='Book 1', copies_owned=2),
                Book(title='Book 2', copies_owned=1)
            ])
            db.session.commit()
            
@app.route('/api/debug/db')
def debug_db():
    users = User.query.all()
    books = Book.query.all()
    loans = Loan.query.all()
    return jsonify({
        'users': [{'id': u.id, 'username': u.username, 'role': u.role} for u in users],
        'books': [{'id': b.id, 'title': b.title, 'copies_owned': b.copies_owned, 'copies_available': b.copies_available} for b in books],
        'loans': [{'id': l.id, 'user_id': l.user_id, 'book_id': l.book_id, 'loan_date': l.loan_date.isoformat(), 'return_date': l.return_date.isoformat() if l.return_date else None} for l in loans]
    })


if __name__ == '__main__':
    print("Starting Flask app on port 7001...")
    init_db()
    app.run(host='0.0.0.0', port=7001, debug=True)
