from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy() 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    email = db.Column(db.String(40),unique = True, nullable= False)
    password = db.Column(db.String(120), nullable=False )
    role = db.Column(db.String(20), default='user')
    created_time = db.Column(db.DateTime, default=datetime.utcnow)


class Parking_lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique = True, nullable = False)
    location = db.Column(db.String(50), nullable = False)
    address = db.Column(db.String(), nullable=False)
    pincode = db.Column(db.String(), nullable= False)
    price = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable = False)
    time = db.Column(db.DateTime, default=datetime.utcnow ,nullable = False)
    spots = db.relationship('Spots', backref='parking_lot', lazy=True,cascade='all, delete-orphan')

class Spots(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id',ondelete='CASCADE'), nullable = False)
    spot_number = db.Column(db.Integer,nullable=False)
    status = db.Column(db.String(), default = 'A', nullable = False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Reservations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('spots.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    cost = db.Column(db.Float, nullable=False)
