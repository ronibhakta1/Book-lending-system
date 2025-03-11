from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Hashed
    role = db.Column(db.String(20), nullable=False)  # 'librarian' or 'patron'
    loans = db.relationship('Loan', backref='user', lazy=True)  # Relationship to Loan

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    copies_owned = db.Column(db.Integer, default=1)
    copies_available = db.Column(db.Integer, default=1)
    loans = db.relationship('Loan', backref='book', lazy=True)  # Relationship to Loan

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Float, nullable=True)  # Hours

class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)