from flask import Blueprint, render_template_string, request, jsonify, make_response
from .services import UserService
from .form import Form

bp = Blueprint('routes', __name__)

@bp.route("/", methods=["GET"])
def form():
    return render_template_string(Form.form_html)

@bp.route('/test', methods=['GET'])
def test_route():
    try:
        return make_response(jsonify({'message': 'test route'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

@bp.route('/users', methods=['POST'])
def create_user():
    try:
        user = UserService.create(request.get_json())
        return make_response(jsonify(user.json()), 201)
    except Exception as e:
        print(f"Error creating user: {e}")
        return make_response(jsonify({'Usuario já existe!'}), 400)

@bp.route('/users/all', methods=['GET'])
def get_users():
    try:
        users = UserService.get_all()
        
        if not users:
            return make_response(jsonify({'message': 'no users found'}), 404)
        
        return make_response(jsonify([u.json() for u in users]), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

@bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        success = UserService.delete(id)
        if success:
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({'error': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = UserService.update(id, request.get_json())
        if user:
            return make_response(jsonify(user.json()), 200)
        return make_response(jsonify({'error': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)
