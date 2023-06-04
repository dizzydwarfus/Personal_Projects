function toggleAddExpense() {
    var bracket = document.querySelector('.add-expense-bracket');
    var content = document.querySelector('.add-expense-content');

    if (bracket.classList.contains('expanded')) {
        bracket.classList.remove('expanded');
        content.style.display = 'none';
    } else {
        bracket.classList.add('expanded');
        content.style.display = 'block';
    }
};

$(document).ready(function () {
    $('.edit-btn').on('click', function () {
        var id = $(this).data('id');
        var description = $(this).data('description');
        var category = $(this).data('category');
        var subcategory = $(this).data('subcategory');
        var date = $(this).data('date');
        var cost = $(this).data('cost');

        $('#editExpenseModal #expenseId').val(id);
        $('#editExpenseModal #expenseDescription').val(description);
        $('#editExpenseModal #expenseCategory').val(category);
        $('#editExpenseModal #expenseSubCategory').val(subcategory);
        $('#editExpenseModal #expenseDate').val(date);
        $('#editExpenseModal #expenseCost').val(cost);

        var actionUrl = '/edit_expense/' + id;
        $('#editExpenseModal form').attr('action', actionUrl);
    });
});
