from app import create_app, db
from app.models.categories import Category, SubCategory


def init_db():
    app = create_app()
    with app.app_context():
        categories_dict = {
            'Entertainment': ['Video/DVD', 'Games', 'Movies', 'Concerts', 'Sporting Events', 'Live Theater', 'Other'],
            'Food': ['Groceries', 'Dine Out', 'Other'],
            'Gifts/Donation': ['Birthday', 'Wedding', 'Charity', 'Other'],
            'Housing': ['Mortgage', 'Rent', 'Phone', 'Energy', 'Water', 'Gas', 'Cable', 'Waste Removal', 'Maintenance Repairs', 'Supplies', 'Other'],
            'Income': ['Investments', 'Salary', 'Allowance', 'Commission', 'Interest Payment', 'Government Payment', 'Gift', 'Payback'],
            'Insurance': ['Home', 'Health', 'Life', 'Car', 'Travel', 'Other'],
            'Legal Fees': ['Attorney', 'Alimony', 'Other'],
            'Loans': ['Personal', 'Credit Card', 'Student', 'Housing', 'Other'],
            'Personal': ['Medical Expenses', 'Personal Care', 'Clothing', 'Tech', 'Music', 'Sports', 'Other'],
            'Savings/Investments': ['Retirement', 'Investment', 'Emergency Fund', 'Other'],
            'Subscriptions': ['Phone', 'Entertainment', 'Fitness', 'Learning', 'Other'],
            'Taxes': ['Federal', 'State', 'Local', 'Income', 'Other'],
            'Transportation': ['Vehicle Payment', 'Public Transport', 'Licensing', 'Fuel', 'Maintenance', 'Other']
        }

        for category_name, sub_categories in categories_dict.items():
            category = Category(name=category_name)
            db.session.add(category)

            for sub_category_name in sub_categories:
                sub_category = SubCategory(
                    name=sub_category_name, category=category)
                db.session.add(sub_category)

        db.session.commit()


if __name__ == "__main__":
    init_db()
