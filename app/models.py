from . import db
from datetime import datetime

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber = db.Column(db.String(20))
    email = db.Column(db.String(255))
    linkedId = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=True)
    linkPrecedence = db.Column(db.String(10), default="primary")  # "primary" or "secondary"
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletedAt = db.Column(db.DateTime, nullable=True)
