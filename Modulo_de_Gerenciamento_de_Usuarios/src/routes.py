from flask import Blueprint, request, jsonify, make_response
from .services import UserService

bp = Blueprint('routes', __name__)

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
        return make_response(jsonify({'error': str(e)}), 400)

@bp.route('/users/all', methods=['GET'])
def get_users():
    try:
        users = UserService.get_all()
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
