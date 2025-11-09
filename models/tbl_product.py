from app import db
from utils.timezone import PhnomPenhTime
from sqlalchemy.dialects.mysql import ENUM

class ProductCategory(db.Model):
    __tablename__ = 'tbl_product_category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)

    products = db.relationship('Product', back_populates='category', lazy='dynamic', cascade="all, delete-orphan")


class Product(db.Model):
    __tablename__ = 'tbl_product'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('tbl_product_category.id'), nullable=False)
    status = db.Column(
        ENUM('Active', 'Pending', name='product_status_enum'),
        nullable=False,
        default='Active'
    )
    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)

    category = db.relationship('ProductCategory', back_populates='products')
    detail = db.relationship('ProductDetail', back_populates='product', uselist=False, cascade="all, delete-orphan")
    stock = db.relationship('ProductStock', back_populates='product', uselist=False, cascade="all, delete-orphan")


class ProductDetail(db.Model):
    __tablename__ = 'tbl_product_detail'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('tbl_product.id'), nullable=False, unique=True)
    brand = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(10, 2), nullable=True, default=0)
    condition = db.Column(
        ENUM('New', 'LikeNew', '2ndHand', name='product_condition_enum'),
        nullable=False,
        default='New'
    )
    description = db.Column(db.Text, nullable=True)
    review = db.Column(db.Text, nullable=True)
    image1 = db.Column(db.String(255), nullable=True)
    image2 = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)

    product = db.relationship('Product', back_populates='detail')


class ProductStock(db.Model):
    __tablename__ = 'tbl_product_stock'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('tbl_product.id'), nullable=False, unique=True)
    qty = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)

    product = db.relationship('Product', back_populates='stock')

