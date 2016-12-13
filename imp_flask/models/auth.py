from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from imp_flask.models.helpers import Base


class User(Base):
    username = Column(String(80), unique=True)
    passhash = Column(String(255))
    email = Column(String(255))
    admin = Column(Boolean)

    relation_id = Column(ForeignKey('relation.id'))
    relation = relationship('Relation')

    pos_id = Column(ForeignKey('posinstance.id'))
    pos = relationship('PosInstance')

    def __init__(self):
        self.pos = None
        self.relation = None
        self.admin = False

    # Flask-Login required functionality

    token = Column(String(64), unique=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.token)
