from . import db
import uuid

"""
Mapeamento de dados para o banco de dados usando SQLAlchemy.
AlertType e User são modelos que representam os tipos de alerta e usuários, respectivamente.

User
    - id: UUID único do usuário (armazenado como string).
    - username: Nome de usuário.
    - email: Email do usuário único.
    - alerts: Relação um-para-muitos com Alert, permitindo que um usuário tenha múltiplos alertas associados.

Alert
    - Tabela de associação para a relação um-para-muitos entre User e AlertType.
    - id: Identificador único do alerta.
    - user_id: Referência ao UUID do usuário (armazenado como string).
    - alert_type: Nome do tipo de alerta.
    - city: Cidade associada ao alerta.
"""

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    alerts = db.relationship('Alert', backref='user', cascade='all, delete-orphan')

    def json(self):
        return {
            'id': self.id,  # Already a string
            'username': self.username,
            'email': self.email,
            'alerts': [
                {
                    'city': alert.city,
                    'types': [alert.alert_type]
                } for alert in self.alerts
            ]
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)

    __table_args__ = (
        db.Index('idx_alert_type_city', 'alert_type', 'city'),
    )

    def json(self):
        return {
            'city': self.city,
            'type': self.alert_type
        }
