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