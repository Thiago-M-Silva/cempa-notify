from .models import User
from .models import AlertType
from . import db

"""
Metodos de controle de usuários e alertas
create
    persiste um usuário e seus tipos de alerta no banco de dados.
    parametros: 
        data: dicionário com os dados do usuário, incluindo:
            - username: nome do usuário
            - email: email do usuário
            - alert_types: lista de tipos de alerta
            - cities: lista de cidades associadas aos tipos de alerta
    retorna: objeto User criado ou lança uma exceção em caso de erro

get_all
    busca todos os usuários cadastrados no banco de dados
    retorna: lista de objetos User ou uma lista vazia em caso de erro

delete
    deleta um usuário pelo ID
    parametros:
        user_id: ID do usuário a ser deletado
    retorna: True se o usuário foi deletado com sucesso, False caso contrário

update
    atualiza os dados de um usuário pelo ID
    parametros:
        user_id: ID do usuário a ser atualizado
        data: dicionário com os novos dados do usuário

get_users_by_alert_and_city
    busca a lista de usuários filtrados por tipo de alerta e cidade
    parâmetros: 
        alert_types: lista de tipos de alerta (opcional)
        cities: lista de cidades (opcional)
    retorna: lista de objetos User que correspondem aos filtros ou uma lista vazia em caso de erro
"""

class UserService:
    @staticmethod
    def create(data):
        try:
            alert_types_data = data.pop('alert_types', [])
            cities_data = data.pop('cities', [])
            new_user = User(**data)
            
            for alert_name in alert_types_data:
                alert_type = AlertType.query.filter_by(name=alert_name).first()
                
                if not alert_type:
                    alert_type = AlertType(
                        name=alert_name,
                        cities=','.join(cities_data)
                    )
                    db.session.add(alert_type)
                else:
                    existing_cities = set(alert_type.cities.split(',')) if alert_type.cities else set()
                    alert_type.cities = ','.join(cities_data)
            
                new_user.alert_types.append(alert_type)
    
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def get_all():
        try:
            return User.query.all()
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    
    @staticmethod
    def delete(user_id):
        try:
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    @staticmethod
    def update(user_id, data):
        try:
            user = User.query.get(user_id)
            if user:
                for key, value in data.items():
                    setattr(user, key, value)
                db.session.commit()
                return user
            return None
        except Exception as e:
            print(f"Error updating user: {e}")
            db.session.rollback()
            return None

class AlertService:
    @staticmethod
    def get_users_by_alert_and_city(alert_types=None, cities=None):
        try:
            query = User.query.join(User.alert_types)

            conditions = []

            if alert_types:
                conditions.append(AlertType.name.in_(alert_types))

            if cities:
                city_conditions = []
                for city in cities:
                    city_conditions.append(AlertType.cities.like(f'%{city}%'))
                if city_conditions:
                    conditions.append(db.or_(*city_conditions))

            if conditions:
                query = query.filter(db.and_(*conditions))

            query = query.distinct()

            users = query.all()
            return users

        except Exception as e:
            print(f"Error getting users by alert type and city: {e}")
            return []

