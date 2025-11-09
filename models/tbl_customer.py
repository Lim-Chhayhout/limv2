from app import db
from utils.timezone import PhnomPenhTime

class Customer(db.Model):
    __tablename__ = 'tbl_customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    telephone = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    social = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)

    orders = db.relationship('Order', backref='customer', lazy=True)
