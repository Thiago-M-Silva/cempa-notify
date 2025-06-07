from flask import Blueprint, render_template_string, request, jsonify, make_response
from .services import UserService, AlertService
from .form import Form
from .models import AlertType

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
    
#GET http://localhost:4000/usersByAlert?alert_type=temperature
@bp.route('/usersByAlert', methods=['GET'])
def get_users_by_alert():
    try:
        alert_type = request.args.get("alert_type")

        if not alert_type:
            return make_response(jsonify({'error': 'Missing alert_type parameter'}), 400)

        alert_type_obj = AlertType.query.filter_by(name=alert_type).first()
        
        if not alert_type_obj:
            return make_response(jsonify({'message': f'Alert type "{alert_type}" not found'}), 404)

        users = alert_type_obj.users

        if not users:
            return make_response(jsonify({'message': f'No users found for alert type "{alert_type}"'}), 404)

        return make_response(jsonify([user.json() for user in users]), 200)

    except Exception as e:
        print(f"Error in get_users_by_alert: {str(e)}")  
        return make_response(jsonify({'error': str(e)}), 400)


@bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user = UserService.create(data)
        return make_response(jsonify(user.json()), 201)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

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
