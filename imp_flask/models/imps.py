"""Holds all transaction and product data"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from imp_flask.models.helpers import Base, many_to_many
from imp_flask.tasks.rowapplymods import rowapplymods
from math import floor, ceil


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

    def lose(self, amount):
        if amount <= 0:
            raise IllegalProductAdaption("Incorrect call of function 'lose', amount cannot be zero/negative.")

        if amount > self.amount and not self.allow_negative:
            raise IllegalProductAdaption(str(self) + " would have negative stock.")

        if self.value_constant:
            dvalue = amount * self.value
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


class Transaction(Base):
    eventname = Column(String(80))
    eventnumber = Column(Integer)
    eventdate = Column(DateTime)
    eventcontact = Column(String(80))
    eventnotes = Column(Text)

    revision = Column(Integer)

    relation_id = Column(ForeignKey('relation.id'))
    rows = relationship('TransactionRow', backref='transaction', lazy='dynamic')

    def __init__(self, eventname, eventdate, eventcontact, relation):
        self.eventname = eventname
        self.eventdate = eventdate
        self.eventcontact = eventcontact
        self.eventnotes = ""
        self.relation = relation
        self.revision = 0
        previous = Transaction.query.filter_by(relation=self.relation, eventnumber=func.max(Transaction.eventnumber))
        if previous is None:
            self.eventnumber = 1
        else:
            self.eventnumber = previous.eventnumber + 1

    def lose(self, product, amount, mods):
        for row in self.rows:
            if row.product == product and row.includes_mods == mods:
                value = row.lose(amount)
                break
        else:
            value = TransactionRow(self, product, mods).lose(amount)

        return value

    def gain(self, product, amount, value, mods):
        for row in self.rows:
            if row.product == product and row.includes_mods == mods:
                value = row.gain(amount, value)
                break
        else:
            value = TransactionRow(self, product, mods).gain(amount, value)

        return value


class TransactionRow(Base):
    transaction_id = Column(ForeignKey('transaction.id'))

    product = relationship('Product', lazy='joined')
    product_id = Column(ForeignKey('product.id'))

    amount = Column(Integer)
    prevalue = Column(Integer)
    value = Column(Integer)

    includes_mods = many_to_many('includemods', 'TransactionRow', 'Mod')

    def __init__(self, transaction, product, mods):
        self.transaction = transaction
        transaction.rows.append(self)
        self.includes_mods = mods
        self.product = product
        self.value = 0
        self.amount = 0

    def lose(self, amount):  # selling more, buying less
        dvalue = self.product.lose(amount)
        self.prevalue -= dvalue
        self.amount -= amount
        rowapplymods(self)
        return dvalue

    def gain(self, amount, value):  # selling less, buying more
        self.amount += amount
        self.prevalue += value
        currvalue = self.value
        rowapplymods(self)
        self.product.gain(amount, self.value - currvalue)
        return value

    def delete(self):
        if self.value < 0:
            self.product.gain(-self.amount, -self.value)
        elif self.value > 0:
            self.product.change_amount(-self.amount)
            self.product.change_value(-self.value)
        elif self.amount != 0:
            self.product.change_amount(-self.amount)
        self.amount = 0
        self.value = 0


class Mod(Base):
    # nvalue = (ovalue + pre_add * amount)*multiplier + post_add * amount
    name = Column(String(64))
    tag = Column(String(16))
    pre_add = Column(Integer)
    multiplier = Column(Float)
    post_add = Column(Integer)
    included = Column(Boolean)
    rounding = Column(Enum('floor', 'ceil', 'round', 'none'))

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
        # scales with the multiplier.
        original_value = value - self.post_add * amount
        original_value /= self.multiplier

        # Rounding the wrong way when reversing operation yields best result.
        if self.rounding is 'floor':
            original_value = ceil(original_value)
        elif self.rounding is 'ceil':
            original_value = floor(original_value)
        elif self.rounding is 'round':
            original_value = round(original_value)

        original_value -= self.pre_add * amount
        delta_value = value - original_value
        return value, delta_value

    def apply_excluded(self, amount, value):
        nvalue = (value + self.pre_add * amount) * self.multiplier + self.post_add * amount
        if self.rounding is 'floor':
            nvalue = floor(nvalue)
        elif self.rounding is 'ceil':
            nvalue = ceil(nvalue)
        elif self.rounding is 'round':
            nvalue = round(nvalue)
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


class RecipePart(Base):
    product_id = Column(ForeignKey('product.id'))
    amount = Column(Integer)


class InputRecipe(Base):
    """"Make a special input that creates multiple products. Note: only one item may have variable cost."""
    input = Column(String(80))
    outputs = many_to_many('outputs', 'InputRecipe', 'RecipePart')


class OutputRecipe(Base):
    """"Make a special output that needs multiple products. Note: will do some ugly rounding."""
    output = Column(String(80))
    inputs = many_to_many('inputs', 'OutputRecipe', 'RecipePart')
