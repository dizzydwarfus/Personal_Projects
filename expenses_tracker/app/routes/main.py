from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.expense import Expense

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    # The 'GET' request case:
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user=current_user, expenses=expenses)
