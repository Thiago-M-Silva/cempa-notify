from flask import Blueprint, render_template_string, request, jsonify, make_response
from .services import UserService, AlertService
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
    
#GET http://localhost:4000/usersByAlert?alert_type=temperature
@bp.route('/usersByAlert', methods=['GET'])
def get_users_by_alert():
    try:
        alert_type = request.args.get("alert_type")

        if not alert_type:
            return make_response(jsonify({'error': 'Missing alert_type parameter'}), 400)

        users = AlertService.get_users_by_alert_type(alert_type)

        if not users:
            return make_response(jsonify({'message': 'no users found'}), 404)

        return make_response(jsonify([user.json() for user in users]), 200)

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

# add alerta, para teste 
@bp.route("/alerts", methods=["POST"])
def create_alert():
    try:
        data = request.get_json()
        alert = AlertService.create_alert(data)

        if not alert:
            return jsonify({'error': 'Failed to create alert'}), 400

        return jsonify(alert.json()), 201

    except Exception as e:
        # db.session.rollback()
        return jsonify({'error': str(e)}), 400

