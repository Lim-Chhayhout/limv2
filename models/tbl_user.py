from app import db
from utils.timezone import PhnomPenhTime
from sqlalchemy.dialects.mysql import ENUM

class UserRole(db.Model):
    __tablename__ = 'tbl_user_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    status = db.Column(
        ENUM('Enable', 'Disable', name='role_status_enum'),
        nullable=False,
        default='Enable'
    )

    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)

    users = db.relationship('User', backref='user_role', lazy=True)


class User(db.Model):
    __tablename__ = 'tbl_user'
    id = db.Column(db.Integer, primary_key=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(80), nullable=False)
    telephone = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('tbl_user_role.id'), nullable=False)
    status = db.Column(
        ENUM('Enable', 'Disable', name='role_status_enum'),
        nullable=False,
        default='Enable'
    )
    token_version = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
