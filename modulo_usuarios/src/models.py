from . import db

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
    
class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(120), nullable=True)

    user = db.relationship('User', backref=db.backref('alerts', lazy=True))

    def json(self):
        return {
            'id': self.id,
            'id_user': self.id_user,
            'alert_type': self.alert_type,
            'city': self.city
        }
    