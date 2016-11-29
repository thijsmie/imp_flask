"""Holds all transaction and product data"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from imp_flask.models.helpers import Base, many_to_many


def sign(num):
    return -1 * (num < 0) + (num > 0)


# Convention: the sign of a number in the database 
# is always relative to the owner of this program
# So a negative amount and value is a sell (and denoted with 'lose')
# and a positive amount and value is a buy (and denoted with 'gain')
# From outside, you call 'lose' or 'gain' with a positive number always.

class IllegalProductAdaption(Exception):
    pass


class Product(Base):
    name = Column(String(80))
    amount = Column(Integer)
    value = Column(Integer)

    allow_negative = Column(Boolean)
    value_constant = Column(Boolean)
    hidden = Column(Boolean)

    losemods = many_to_many('losemods', 'Product', 'Mod')
    gainmods = many_to_many('gainmods', 'Product', 'Mod')

    group = Column(String(80))

    def __init__(self):
        pass

    def lose(self, amount, value=None):
        if amount <= 0:
            raise IllegalProductAdaption("Incorrect call of function 'lose', amount cannot be zero/negative.")

        if amount > self.amount and not self.allow_negative:
            raise IllegalProductAdaption(str(self) + " would have negative stock.")

        if self.value_constant:
            dvalue = amount * self.value
        elif value is not None:
            if value > self.value:
                raise IllegalProductAdaption(str(self) + "would have negative value.")
            dvalue = value
        else:
            dvalue = round(amount / self.amount * self.value)

        self.value -= dvalue
        self.amount -= amount
        return dvalue

    def gain(self, amount, value):
        if amount <= 0 or value < 0:
            raise IllegalProductAdaption("Incorrect call of function 'gain', amount cannot be zero/negative.")

        if self.value_constant:
            if value != amount * self.value:
                raise IllegalProductAdaption(str(self) + " has a constant price that is not matched.")
            self.amount += amount
        else:
            self.value += value
            self.amount += amount
        return value

    def change_value(self, dvalue):
        if self.value_constant:
            return self.value * self.amount
        if sign(self.value + dvalue) != sign(self.value) or self.value + dvalue == 0:
            raise IllegalRowAdaption("The value of " + str(self) + " would change sign.")
        self.value += dvalue
        return self.value

    def change_amount(self, damount):
        if sign(self.amount + damount) != sign(self.amount) or self.amount + damount == 0:
            if not (self.allow_negative and self.value_constant):
                raise IllegalRowAdaption("The value of " + str(self) + " would change sign.")
        self.amount += damount
        return self.amount


class Transaction(Base):
    eventname = Column(String(80))
    eventnumber = Column(Integer)
    eventdate = Column(DateTime)
    eventcontact = Column(String(80))
    eventnotes = Column(Text)

    relation_id = Column(ForeignKey('relation.id'))
    rows = relationship('TransactionRow', backref='transaction', lazy='dynamic')

    def __init__(self, eventname, eventdate, eventcontact, relation):
        self.eventname = eventname
        self.eventdate = eventdate
        self.eventcontact = eventcontact
        self.eventnotes = ""
        self.relation = relation
        previous = Transaction.query.filter_by(relation=self.relation, eventnumber=func.max(Transaction.eventnumber))
        if previous is None:
            self.eventnumber = 1
        else:
            self.eventnumber = previous.eventnumber + 1

    def lose(self, product, amount, value=None):
        for row in self.rows:
            if row.product == product:
                value = row.lose(amount, value)
                break
        else:
            value = TransactionRow(self, product).lose(amount, value)

        return value

    def gain(self, product, amount, value):
        for row in self.rows:
            if row.product == product:
                value = row.gain(amount, value)
                break
        else:
            value = TransactionRow(self, product).gain(amount, value)

        return value


class IllegalRowAdaption(Exception):
    pass


class TransactionRow(Base):
    transaction_id = Column(ForeignKey('transaction.id'))

    product = relationship('Product', lazy='joined')
    product_id = Column(ForeignKey('product.id'))

    amount = Column(Integer)
    prevalue = Column(Integer)
    value = Column(Integer)

    includes_mods = many_to_many('includemods', 'TransactionRow', 'Mod')

    def __init__(self, transaction, product):
        self.transaction = transaction
        transaction.rows.append(self)
        self.product = product
        self.value = 0
        self.amount = 0

    def lose(self, amount, value=None):  # selling more, buying less
        dvalue = self.product.lose(amount, value)
        self.value -= dvalue
        self.amount -= amount
        return dvalue

    def gain(self, amount, value):  # selling less, buying more
        self.amount += amount
        self.value += value
        self.product.gain(amount, value)
        return value

    def change_value(self, value):
        dvalue = self.value - value
        self.product.change_value(dvalue)
        self.value = value
        return dvalue

    def change_amount(self, amount):
        if sign(amount) != sign(self.amount) or amount == 0:
            raise IllegalRowAdaption("The amount of " + str(self) + " would change sign.")
        damount = self.amount - amount
        self.product.change_amount(damount)
        self.amount = amount
        return damount

    def delete(self):
        if self.value < 0:
            self.product.gain(-self.amount, -self.value)
        elif self.value > 0:
            self.product.change_amount(-self.amount)
            self.product.change_value(-self.value)
        elif self.amount != 0:
            self.product.change_amount(-self.amount)


class Mod(Base):
    # nvalue = (ovalue + pre_add * amount)*multiplier + post_add * amount
    name = Column(String)
    pre_add = Column(Integer)
    multiplier = Column(Float)
    post_add = Column(Integer)
    included = Column(Boolean)

    def __init__(self, name, pre_add, multiplier, post_add, included):
        self.name = name
        self.pre_add = pre_add
        self.multiplier = multiplier
        self.post_add = post_add
        self.included = included

    def apply(self, amount, value):
        if self.included:
            return self.apply_included(amount, value)
        else:
            return self.apply_excluded(amount, value)

    def apply_included(self, amount, value):
        # The mod is already included in the value, we would just like to know it's total
        # Note: this is inexact science, since value might be rounded, so the error
        # scales with the multiplier and possible decimals in post and pre-add
        original_value = value - self.post_add * amount
        original_value /= self.multiplier
        original_value -= self.pre_add * amount
        delta_value = value - original_value
        return value, delta_value

    def apply_excluded(self, amount, value):
        nvalue = (value + self.pre_add * amount) * self.multiplier + self.post_add * amount
        dvalue = nvalue - value
        return nvalue, dvalue


class Relation(Base):
    name = Column(String(80))
    budget = Column(Integer)
    email = Column(String(200))

    send_transaction = Column(Boolean)
    send_transaction_updates = Column(Boolean)
    send_budget_warnings = Column(Boolean)

    transactions = relationship('Transaction', backref='relation', lazy='dynamic')

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.budget = 0.
        self.send_transaction = True
        self.send_transaction_updates = True
        self.send_budget_warnings = True


class User(Base):
    username = Column(String(80))
    passhash = Column(String(256))
    admin = Column(Boolean)

    relation_id = Column('relation.id')
    relation = relationship('Relation', lazy='dynamic')
