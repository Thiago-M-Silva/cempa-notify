from . import db

class AlertType(db.Model):
    __tablename__ = 'alert_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def json(self):
        return {
            'id': self.id,
            'name': self.name
        }

user_alerttype = db.Table(
    'user_alerttype',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('alert_type_id', db.Integer, db.ForeignKey('alert_types.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=True)
    alert_types = db.relationship('AlertType', secondary=user_alerttype, backref='users')

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'city': self.city,
            'alert_types': [alert.name for alert in self.alert_types]
        }
