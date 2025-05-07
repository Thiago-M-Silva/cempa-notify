from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELO
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    alert = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(120), nullable=True)

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'alert': self.alert,
            'city': self.city
        }

# Inicializa o banco de dados com contexto da aplicação
with app.app_context():
    db.create_all()

# ROTAS

@app.route('/test', methods=['GET'])
def test_route():
    return make_response(jsonify({'message': 'test route'}), 200)

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        new_user = User(
            username=data['username'],
            email=data['email'],
            alert=data['alert'],
            city=data['city']
        )
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify(new_user.json()), 201)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': f'error creating user\n{str(e)}'}), 400)
    finally:
        db.session.close()

@app.route('/users/all', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return make_response(jsonify([user.json() for user in users]), 200)
    except Exception as e:
        return make_response(jsonify({'error': f'error getting users\n{str(e)}'}), 400)
    finally:
        db.session.close()

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted'}), 200)
        else:
            return make_response(jsonify({'error': 'user not found'}), 404)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': f'error deleting user\n{str(e)}'}), 400)
    finally:
        db.session.close()

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        data = request.get_json()
        user = User.query.filter_by(id=id).first()
        if user:
            user.username = data['username']
            user.email = data['email']
            user.alert = data['alert']
            user.city = data['city']
            db.session.commit()
            return make_response(jsonify(user.json()), 200)
        else:
            return make_response(jsonify({'error': 'user not found'}), 404)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': f'error updating user\n{str(e)}'}), 400)
    finally:
        db.session.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)