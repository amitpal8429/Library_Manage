from . import db
from flask_login import UserMixin

# Association table for Many-to-Many (Users ↔ Events)
user_events = db.Table('user_events',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='user')
    events = db.relationship('Event', secondary=user_events, backref='attendees')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    time = db.Column(db.String(50), nullable=False)  # or use DateTime
    capacity = db.Column(db.Integer, nullable=False)
    booked = db.Column(db.Integer, default=0)
