from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user
from app.models.expense import Expense
from app import db

expenses = Blueprint('expenses', __name__)


@expenses.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        description = request.form.get('expenseDescription')
        category = request.form.get('expenseCategory')
        date = request.form.get('expenseDate')
        cost = request.form.get('expenseCost')

        new_expense = Expense(description=description, date_of_expense=date, category=category,
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
