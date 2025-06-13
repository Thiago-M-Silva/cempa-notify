from flask import Blueprint, render_template_string, request, jsonify, make_response
from .services import UserService, AlertService
from .form import Form
import uuid

"""
Rotas de API para gerenciamento de usuários e alertas
form
    pagina principal, renderiza o formulario de cadastro de usuários

get_users_by_alert_and_city
    busca a lista de usuários filtrados por tipo de alerta e cidade
    parâmetros: alert_type (lista de tipos de alerta), city (lista de cidades)

create_user
    cria um novo usuário com os dados fornecidos
    deve-se enviar um body no seguinte formato:
        {
            "username": "nome do usuário",
            "email": "email do usuário",
            "cities": ["cidade1", "cidade2"],
            "alert_types": ["tipo1", "tipo2"]
        }

get_users
    busca todos os usuários cadastrados

delete_user
    deleta um usuário pelo UUID (string)
    
update_user
    atualiza os dados de um usuário pelo UUID (string)
"""

bp = Blueprint('routes', __name__)

@bp.route("/", methods=["GET"])
def form():
    return render_template_string(Form.form_html)
    
#GET http://localhost:4000/usersByAlert?alert_type=temperature
@bp.route('/usersByAlert', methods=['GET'])
def get_users_by_alert_and_city():
    try:
        # Pega parâmetros da query string
        alert_types = request.args.getlist("alert_type")
        cities = request.args.getlist("city")

        if not alert_types and not cities:
            return make_response(
                jsonify({'error': 'Necessário informar pelo menos um tipo de alerta ou cidade'}), 
                400
            )

        users = AlertService.get_users_by_alert_and_city(alert_types, cities)

        if not users:
            return make_response(
                jsonify({
                    'message': 'Nenhum usuário encontrado com os filtros informados',
                    'filters': {
                        'alert_types': alert_types,
                        'cities': cities
                    }
                }), 
                404
            )

        return make_response(jsonify({
            'total': len(users),
            'users': [user.json() for user in users]
        }), 200)

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

@bp.route('/users/delete/<string:id>', methods=['GET'])
def delete_user(id):
    try:
        success = UserService.delete(id)
        if success:
            return make_response(jsonify({'message': 'Usuario descastrado com sucesso.'}), 200)
        return make_response(jsonify({'error': 'Usuario não encontrado'}), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)

@bp.route('/users/<string:id>', methods=['PUT'])
def update_user(id):
    try:
        user = UserService.update(id, request.get_json())
        if user:
            return make_response(jsonify(user.json()), 200)
        return make_response(jsonify({'error': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)
