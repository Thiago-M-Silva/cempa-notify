from .models import User
from .models import Alert
from . import db

class UserService:
    @staticmethod
    def create(data):
        new_user = User(**data)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def get_all():
        return User.query.all()
    
    @staticmethod
    def delete(user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update(user_id, data):
        user = User.query.get(user_id)
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            db.session.commit()
            return user
        return None

class AlertService:
    @staticmethod
    def get_users_by_alert_type(alert_type):
        alerts = Alert.query.filter_by(alert_type=alert_type).all()
        users = [alert.user for alert in alerts]
        return users

    #add alerta, para teste 
    @staticmethod
    def create_alert(data):
        if not data or not all(k in data for k in ("id_user", "alert_type")):
            return None

        alert = Alert(
            id_user=data["id_user"],
            alert_type=data["alert_type"],
            city=data.get("city")
        )

        db.session.add(alert)
        db.session.commit()
        return alert