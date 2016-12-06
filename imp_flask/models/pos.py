from imp_flask.models.helpers import Base, many_to_many
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class PosInstance(Base):
    name = Column(String(80))
    users = many_to_many('posusers', 'posinstance', 'user')


class PosSellable(Base):
    pos_id = Column(ForeignKey('posinstance.id'))
    pos = relationship('posinstance')
    product_id = Column(ForeignKey('product.id'))
    product = relationship('product')
    price = Column(Integer)


class PosSale(Base):
    pos_sellable_id = Column(ForeignKey('possellable.id'))
    pos_sellable = relationship('possellable')
    timeofsale = Column(DateTime)
    amount = Column(Integer)
