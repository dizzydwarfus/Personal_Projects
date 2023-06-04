from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.expense import Expense
from app.models.categories import Category, SubCategory

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    # Retrieve expenses from the database
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(
        Expense.date_of_expense.desc()).all()

    # Group expenses by month and category
    expenses_by_month_category = {}
    for expense in expenses:
        month = expense.date_of_expense.strftime('%B %Y')
        category = expense.category
        if month not in expenses_by_month_category:
            expenses_by_month_category[month] = {}
        if category not in expenses_by_month_category[month]:
            expenses_by_month_category[month][category] = []
        expenses_by_month_category[month][category].append(expense)

    # Retrieve unique categories from the database
    unique_categories = Category.query.all()
    # print(unique_categories)
    unique_sub_categories = SubCategory.query.all()
    # print(unique_sub_categories)
    return render_template('dashboard.html', user=current_user, expenses=expenses, expenses_by_month_category=expenses_by_month_category, categories=unique_categories, sub_categories=unique_sub_categories)
