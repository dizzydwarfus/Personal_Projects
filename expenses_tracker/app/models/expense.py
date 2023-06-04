from app import db
from sqlalchemy import Sequence


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100))
    category = db.Column(db.String(50))
    sub_category = db.Column(db.String(100))
    cost = db.Column(db.Float)
    date_of_expense = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
