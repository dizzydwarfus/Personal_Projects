from flask import Blueprint, request, redirect, url_for, render_template, jsonify
from flask_login import login_required, current_user
from app.models.expense import Expense
from app.models.categories import Category, SubCategory
from app import db
from urllib.parse import unquote

expenses = Blueprint('expenses', __name__)


@expenses.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        description = request.form.get('expenseDescription')
        category = request.form.get('expenseCategory')
        sub_category = request.form.get('expenseSubCategory')
        date = request.form.get('expenseDate')
        cost = request.form.get('expenseCost')

        new_expense = Expense(description=description, date_of_expense=date, category=category, sub_category=sub_category,
                              cost=cost, user_id=current_user.id)
        db.session.add(new_expense)
        db.session.commit()

        # Reload the page after adding the expense
        return redirect(url_for('main.dashboard'))


@expenses.route('/delete_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id == current_user.id:
        db.session.delete(expense)
        db.session.commit()

    # Reload the page after deleting the expense
    return redirect(url_for('main.dashboard'))


@expenses.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if request.method == 'POST':
        expense.description = request.form.get('expenseDescription')
        expense.category = request.form.get('expenseCategory')
        expense.sub_category = request.form.get('expenseSubCategory')
        expense.date_of_expense = request.form.get('expenseDate')
        expense.cost = request.form.get('expenseCost')
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('dashboard.html', expense=expense)


@expenses.route('/get_subcategories/<category>', methods=['GET'])
def get_subcategories(category):
    category = unquote(category)
    category_obj = Category.query.filter_by(name=category).first()
    print(category_obj)
    if category_obj:
        sub_categories = SubCategory.query.filter_by(
            category_id=category_obj.id).all()
        sub_categories_names = [sub_cat.name for sub_cat in sub_categories]
        print(sub_categories_names)
    else:
        sub_categories_names = []
    return jsonify(sub_categories_names)
