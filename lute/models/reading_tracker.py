from lute.db import db
from datetime import datetime

class ReadingTracker(db.Model):
    __tablename__ = 'reading_tracking'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.BkID'), nullable=False)
    read_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)

    book = db.relationship('Book')

    def __init__(self, book, duration_seconds):
        self.book = book
        self.duration_seconds = duration_seconds
