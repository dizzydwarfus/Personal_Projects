from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .sql_connector import CreateURL
from dotenv import dotenv_values

secrets = dotenv_values(".env")

db_conn_string = CreateURL(database='expense_tracker')
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = db_conn_string

    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        from .models.expense import Expense
        from .models.user import User
        db.create_all()

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .routes.main import main as main_blueprint
    from .routes.expenses import expenses as expenses_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(expenses_blueprint)

    return app
