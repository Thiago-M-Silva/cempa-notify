from .models import User
from .models import AlertType
from . import db

class UserService:
    # @staticmethod
    # def create(data):
    #     new_user = User(**data)
    #     db.session.add(new_user)
    #     db.session.commit()
    #     return new_user

    @staticmethod
    def create(data):
        try:
            alert_types_names = data.pop('alert_types', [])
            new_user = User(**data)
            
            # Busca ou cria tipos de alerta
            for alert_name in alert_types_names:
                alert_type = AlertType.query.filter_by(name=alert_name).first()
                if not alert_type:
                    alert_type = AlertType(name=alert_name)
                    db.session.add(alert_type)
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
    def get_users_by_alert_type(alert_type_name):
        try:
            alert_type = AlertType.query.filter_by(name=alert_type_name).first()
            if not alert_type:
                return []
            return alert_type.users
        except Exception as e:
            print(f"Error getting users by alert type: {e}")
            return []
