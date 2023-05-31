import json
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.constants import *
import datetime as dt
import os


class ExpensesTracker:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        if not os.path.isfile(self.filename) or os.stat(self.filename).st_size == 0:
            data = {"months": []}
            self.save_data(data)
            return data
        else:
            with open(self.filename) as file:
                return json.load(file)

    def save_data(self, data):
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)

    def add_monthly_expenses(self, month, expenses):
        for existing_month in self.data["months"]:
            if existing_month["month"] == month:
                existing_expenses = existing_month["expenses"]
                for expense in expenses:
                    category = expense["category"]
                    amount = expense["amount"]
                    for existing_expense in existing_expenses:
                        if existing_expense["category"] == category:
                            existing_expense["amount"] = amount
                            break
                    else:
                        existing_expenses.append(expense)
                break
        else:
            new_month_expenses = {
                "month": month,
                "expenses": expenses
            }
            self.data["months"].append(new_month_expenses)

        self.save_data(self.data)

    def delete_expense(self, month, category):
        for existing_month in self.data["months"]:
            if existing_month["month"] == month:
                existing_month["expenses"] = [
                    expense for expense in existing_month["expenses"] if expense["category"] != category]
                break

        self.save_data(self.data)

    def enter_expenses(self):
        # Create the main window
        window = ttk.Window(themename='superhero')
        window.title("Expenses Tracker")

        # Calculate the screen center
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_x = int((screen_width / 2) - (window.winfo_reqwidth() / 2))
        window_y = int((screen_height / 2) - (window.winfo_reqheight() / 2))

        # Position the window in the center of the screen
        window.geometry(f"+{window_x}+{window_y}")

        # Create label and date picker for month
        month_label = ttk.Labelframe(window, text="Month", labelanchor=N)
        month_label.pack(padx=5, pady=5)
        month_picker = DateEntry(month_label, dateformat="%Y-%m-%d")
        month_picker.pack(padx=5, pady=5)

        # Create label, entry, and frame for expenses
        expenses_label = ttk.Labelframe(
            window, text="Expenses", labelanchor=N)
        expenses_label.pack(padx=5, pady=5)

        expenses_frame = ttk.Frame(expenses_label)
        expenses_frame.pack(padx=5, pady=5)

        category_entries = []
        amount_entries = []

        def add_expense():
            expense_frame = ttk.Frame(expenses_frame)
            expense_frame.pack(padx=5, pady=5)

            category_label = ttk.Label(expense_frame, text="Category:")
            category_label.pack(side=LEFT, padx=5, pady=5)
            category_entry = ttk.Entry(expense_frame)
            category_entry.pack(side=LEFT, padx=5, pady=5)
            category_entries.append(category_entry)

            amount_label = ttk.Label(expense_frame, text="Amount:")
            amount_label.pack(side=LEFT, padx=5, pady=5)

            amount_var = tk.StringVar()
            amount_entry = ttk.Entry(expense_frame, textvariable=amount_var)
            amount_entry.pack(side=LEFT)
            amount_entries.append(amount_var)

            remove_button = ttk.Button(
                expense_frame, text="Remove", command=lambda frame=expense_frame: remove_expense(frame), style=DANGER)
            remove_button.pack(side=LEFT, padx=5, pady=5)

            def validate_amount(*args):
                value = amount_var.get()
                if value.startswith("€ "):
                    value = value[2:]
                try:
                    float(value)
                except ValueError:
                    amount_var.set("€ ")

            def update_amount_var(*args):
                value = amount_var.get()
                if not value.startswith("€ "):
                    try:
                        amount = float(value)
                        formatted_amount = "€ {:.2f}".format(amount)
                        amount_var.set(formatted_amount)
                    except ValueError:
                        pass

            amount_var.trace_add("write", validate_amount)
            amount_var.trace_add("write", update_amount_var)

        def remove_expense(frame):
            frame.destroy()

        add_expense()

        def save_expenses():
            date_get = dt.datetime.strptime(
                month_picker.entry.get(), "%Y-%m-%d"
            )
            month = dt.date.strftime(date_get, "%B %Y")
            expenses = []

            for i in range(len(category_entries)):
                category = category_entries[i].get().lower()
                amount_str = amount_entries[i].get()
                try:
                    amount = float(amount_str.split(" ")[1])
                    expenses.append({"category": category, "amount": amount})
                except ValueError:
                    Messagebox.show_info(
                        title="Expenses Tracker",
                        message=f"Invalid amount format for category: {category}. Please use format '€ <amount>'."
                    )
                    return

            self.add_monthly_expenses(month, expenses)
            Messagebox.show_info(
                title="Expenses Tracker",
                message="Expenses saved successfully!"
            )
            window.destroy()

        def delete_expenses():
            date_get = dt.datetime.strptime(
                month_picker.entry.get(), "%Y-%m-%d")
            month = dt.date.strftime(date_get, "%B %Y")
            category = category_entries[0].get() if category_entries else ""

            if month and category:
                self.delete_expense(month, category)
                Messagebox.show_info(title="Expenses Tracker",
                                     message="Expenses deleted successfully!")
            else:
                Messagebox.show_info(
                    title="Expenses Tracker", message="Please select a month and enter a category to delete expenses.")

        # Create buttons for adding, saving, and deleting expenses
        add_expense_button = ttk.Button(
            window, text="Add Expense", command=add_expense)
        add_expense_button.pack(side=LEFT, padx=5, pady=5)

        delete_expenses_button = ttk.Button(
            window, text="Delete Expenses", command=delete_expenses)
        delete_expenses_button.pack(side=LEFT, padx=5, pady=5)

        save_expenses_button = ttk.Button(
            window, text="Save Expenses", command=save_expenses)
        save_expenses_button.pack(side=BOTTOM, padx=5, pady=5)

        window.mainloop()

    # add total expenses for each month when selecting a month
    def get_total_expenses(self):
        total_expenses = 0
        for month in self.data["months"]:
            for expense in month["expenses"]:
                total_expenses += expense["amount"]
        return total_expenses

    # get number of expenses
    def get_number_of_expenses(self):
        number_of_expenses = 0
        for month in self.data["months"]:
            number_of_expenses += len(month["expenses"])
        return number_of_expenses

    # get average expenses per month
    def get_average_expenses(self):
        return self.get_total_expenses() / len(self.data["months"])


if __name__ == "__main__":
    tracker = ExpensesTracker('expenses.json')
    tracker.enter_expenses()

    print(f'Number of months: {len(tracker.data["months"])}')
    print(f'Number of expenses: {tracker.get_number_of_expenses()}')
    print(f'Current total expenses: € {tracker.get_total_expenses():.2f}')
    print(
        f'Average expenses per month: € {tracker.get_average_expenses():.2f}')

# TODO: add total expenses for each month when selecting a month
