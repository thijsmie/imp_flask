from imp_flask.models.helpers import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship


class ConscriboModTotal(Base):
    mod_id = Column(ForeignKey('mod.id'))
    mod = relationship('mod')
    account_num = Column(Integer)


class ConscriboTransactionVersionControl(Base):
    transaction_id = Column(ForeignKey('transaction.id'))
    transaction = relationship('transaction')
    version_sent = Column(Integer)
    conscribo_reference = Column(String(10))
