from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import os

"""
Creates and configures a Flask application instance for the user module.
- Initializes the Flask app.
- Sets up the database path and ensures the database directory exists.
- Configures SQLAlchemy with the database URI and disables modification tracking.
- Initializes the database extension.
- Registers the application's blueprint for routes.
- Creates all database tables within the application context.
- Prints the path to the initialized SQLite database.
Returns:
    Flask: The configured Flask application instance.
"""

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(basedir, 'database', 'users.db')

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL', f'sqlite:///{db_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    with app.app_context():
        from .models import User
        db.create_all()
        print(f"Banco de dados SQLite inicializado em: {db_path}")

    return app
