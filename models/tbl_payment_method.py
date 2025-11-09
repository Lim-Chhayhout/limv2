from app import db
from utils.timezone import PhnomPenhTime
from sqlalchemy.dialects.mysql import ENUM

class PaymentMethod(db.Model):
    __tablename__ = 'tbl_payment_method'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80),unique=True, nullable=False)
    status = db.Column(
        ENUM('Active', 'Inactive', name='payment_status_enum'),
        nullable=False,
        default='Active'
    )

    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)