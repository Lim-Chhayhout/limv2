from app import db
from utils.timezone import PhnomPenhTime
from sqlalchemy.dialects.mysql import ENUM

class Order(db.Model):
    __tablename__ = 'tbl_order'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(80),unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('tbl_customer.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('tbl_payment_method.id'), nullable=False)
    shipping_id = db.Column(db.Integer, db.ForeignKey('tbl_shipping_method.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    order_status = db.Column(
        ENUM('Pending', 'Success', name='order_status_enum'),
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)

    order_details = db.relationship('OrderDetail', backref='order', lazy=True, cascade='all, delete-orphan')


class OrderDetail(db.Model):
    __tablename__ = 'tbl_order_detail'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('tbl_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('tbl_product.id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    pre_date = db.Column(db.DateTime, nullable=True)
    product_status = db.Column(
        ENUM('Place-ordered', 'Pre-ordered', name='product_status_enum'),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
