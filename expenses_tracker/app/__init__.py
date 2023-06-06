from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .sql_connector import CreateURL
from dotenv import dotenv_values
from ._constants import categories_dict

secrets = dotenv_values(".env")

db_conn_string = CreateURL(database=secrets['azure_sql_database'])
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = db_conn_string

    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        from app.models.expense import Expense
        from app.models.user import User
        from app.models.categories import Category, SubCategory
        # db.create_all()

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        print(db.session.query(Category).count())
        if db.session.query(Category).count() == 0:
            for category_name, sub_categories in categories_dict.items():
                category = Category(name=category_name)
                # print(category)
                db.session.add(category)
                # print(f'Added {category_name} to database')

                for sub_category_name in sub_categories:
                    sub_category = SubCategory(
                        name=sub_category_name, category=category)
                    # print(sub_category)
                    db.session.add(sub_category)
            db.session.commit()
    # blueprint for auth routes in our app
    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .routes.main import main as main_blueprint
    from .routes.expenses import expenses as expenses_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(expenses_blueprint)

    return app
