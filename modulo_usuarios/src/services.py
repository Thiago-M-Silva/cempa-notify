from .models import User, Alert
from . import db
from sqlalchemy.orm import joinedload
import uuid

"""
Metodos de controle de usuários e alertas
create
    persiste um usuário e seus tipos de alerta no banco de dados.
    parametros: 
        data: dicionário com os dados do usuário, incluindo:
            - username: nome do usuário
            - email: email do usuário
            - alerts: lista de alertas
    retorna: objeto User criado ou lança uma exceção em caso de erro

get_all
    busca todos os usuários cadastrados no banco de dados
    retorna: lista de objetos User ou uma lista vazia em caso de erro

delete
    deleta um usuário pelo UUID (string)
    parametros:
        user_id: UUID do usuário a ser deletado (string)
    retorna: True se o usuário foi deletado com sucesso, False caso contrário

update
    atualiza os dados de um usuário pelo UUID (string)
    parametros:
        user_id: UUID do usuário a ser atualizado (string)
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
            alerts_data = data.pop('alerts', [])
            new_user = User(**data)
            for alert in alerts_data:
                city = alert['city']
                for alert_type in alert['types']:
                    user_alert = Alert(city=city, alert_type=alert_type)
                    new_user.alerts.append(user_alert)
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
    def get_user_by_email(email):
        """
        Busca um usuário pelo email.
        
        Args:
            email (str): Email do usuário a ser buscado
            
        Returns:
            User: Objeto do usuário encontrado ou None se não encontrado
        """
        try:
            return User.query.filter_by(email=email).first()
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None

    @staticmethod
    def delete(user_id):
        try:
            # Validate UUID format
            try:
                uuid.UUID(user_id)
            except ValueError:
                print(f"Invalid UUID format: {user_id}")
                return False
                
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
    def update_by_email(email, data):
        """
        Atualiza os alertas de um usuário pelo email.
        Mantém os dados do usuário inalterados, apenas atualiza os alertas.
        
        Args:
            email (str): Email do usuário a ser atualizado
            data (dict): Dicionário com os dados do usuário e alertas
                {
                    "username": str,
                    "email": str,
                    "alerts": [
                        {
                            "city": str,
                            "types": list[str]
                        }
                    ]
                }
            
        Returns:
            User: Objeto do usuário atualizado ou None em caso de erro
        """
        try:
            user = UserService.get_user_by_email(email)
            if not user:
                print(f"User not found with email: {email}")
                return None

            # Remove todos os alertas existentes
            Alert.query.filter_by(user_id=user.id).delete()
            
            # Cria novos alertas
            alerts_data = data.get('alerts', [])
            for alert in alerts_data:
                city = alert['city']
                for alert_type in alert['types']:
                    user_alert = Alert(city=city, alert_type=alert_type)
                    user.alerts.append(user_alert)
            
            db.session.commit()
            return user
        except Exception as e:
            print(f"Error updating user alerts: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def delete_by_email(email):
        try:
            user = UserService.get_user_by_email(email)
            if user:
                db.session.delete(user)
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting user by email: {e}")
            db.session.rollback()
            return False

class AlertService:
    @staticmethod
    def get_users_by_alert_and_city(alert_types=None, cities=None):
        try:
            query = User.query.join(User.alerts)
            if alert_types:
                query = query.filter(Alert.alert_type.in_(alert_types))
            if cities:
                query = query.filter(Alert.city.in_(cities))
            query = query.options(joinedload(User.alerts)).distinct()
            users = query.all()
            return users
        except Exception as e:
            print(f"Error getting users by alert type and city: {e}")
            return []

