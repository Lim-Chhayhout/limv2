from app import db
from utils.timezone import PhnomPenhTime

class Poster(db.Model):
    __tablename__ = 'tbl_poster'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(180), unique=True, nullable=False)
    description = db.Column(db.String(180), nullable=True)
    status = db.Column(db.Enum('Active', 'Inactive'), default='Active', nullable=False)
    created_at = db.Column(db.DateTime, default=PhnomPenhTime.now())
    updated_at = db.Column(db.DateTime, default=PhnomPenhTime.now(), onupdate=PhnomPenhTime.now)

