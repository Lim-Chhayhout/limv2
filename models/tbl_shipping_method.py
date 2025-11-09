from app import db
from utils.timezone import PhnomPenhTime
from sqlalchemy.dialects.mysql import ENUM


class ShippingMethod(db.Model):
    __tablename__ = 'tbl_shipping_method'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), unique=True, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    status = db.Column(
        ENUM('Active', 'Inactive', name='shipping_status_enum'),
        nullable=False,
        default='Active'
    )

    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)