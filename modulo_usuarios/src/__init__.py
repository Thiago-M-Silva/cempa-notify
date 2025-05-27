from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Definir o diretório para o arquivo SQLite
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(basedir, 'database', 'users.db')
    
    # Garantir que o diretório da base de dados existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Configurar SQLite como banco de dados padrão
    # Permitir sobrescrever pela variável de ambiente DB_URL
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
