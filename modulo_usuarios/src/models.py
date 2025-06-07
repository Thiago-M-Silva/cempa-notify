from . import db

"""
Mapeamento de dados para o banco de dados usando SQLAlchemy.
AlertType e User são modelos que representam os tipos de alerta e usuários, respectivamente.

AlertType
    - id: Identificador único do tipo de alerta.
    - name: Nomes do tipo de alerta armazenadas como uma string separadas por vírgulas (ex: "Temperatura", "Humidade").
    - cities: Cidades associadas a este tipo de alerta, armazenadas como uma string separada por vírgulas (ex: "Goiania", "Rio_Verde").

User
    - id: Identificador único do usuário.
    - username: Nome de usuário.
    - email: Email do usuário único.
    - alert_types: Relação muitos-para-muitos com AlertType, permitindo que um usuário tenha múltiplos tipos de alerta associados.

user_alerttype
    - Tabela de associação para a relação muitos-para-muitos entre User e AlertType.
    - user_id: Referência ao ID do usuário.
    - alert_type_id: Referência ao ID do tipo de alerta.

"""


class AlertType(db.Model):
    __tablename__ = 'alert_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    cities = db.Column(db.String(500), nullable=True)  # Armazenará as cidades como string separada por vírgula

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'cities': self.cities.split(',') if self.cities else []
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
    alert_types = db.relationship('AlertType', secondary=user_alerttype, backref='users')

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'alerts': [{
                'type': alert.name,
                'cities': alert.cities.split(',') if alert.cities else []
            } for alert in self.alert_types]
        }
