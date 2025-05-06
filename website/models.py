from flask_login import UserMixin
from website import db


# Structuring the database

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    reservations = db.relationship('Reservations', backref='user', lazy=True)


class Vehicles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration = db.Column(db.String(10), unique=True)
    type_vehicle = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    category = db.Column(db.String(100))
    transmission = db.Column(db.String(100))
    passengers_number = db.Column(db.Integer)
    image = db.Column(db.String(100))
    price_day = db.Column(db.Integer)
    fuel = db.Column(db.String(100))
    horsepower = db.Column(db.Integer)
    engine_displacement = db.Column(db.Integer)
    last_maintenance = db.Column(db.Date)
    next_maintenance = db.Column(db.Date)
    last_inspection = db.Column(db.Date)
    reserve_dates = db.Column(db.JSON, nullable=False, default=[])


class Reservations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    vehicle_model = db.Column(db.String(100))
    vehicle_price_day = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    total = db.Column(db.Integer)
    reservations_payment = db.relationship('Payments', backref='reservations', lazy=True)
    pay_confirmation = db.Column(db.Boolean)
    payment_receipt = db.Column(db.String(999))
    refund = db.Column(db.Boolean)
    vehicle = db.relationship('Vehicles', backref='reservations', lazy=True)


class Payments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'))
    entity = db.Column(db.Integer)
    reference = db.Column(db.Integer)
    amount = db.Column(db.Integer)




