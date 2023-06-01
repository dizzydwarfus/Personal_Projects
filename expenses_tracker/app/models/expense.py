from . import db


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100))
    category = db.Column(db.String(50))
    cost = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
