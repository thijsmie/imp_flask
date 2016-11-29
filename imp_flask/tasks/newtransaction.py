from imp_flask.models.imps import Transaction, Relation, Product
from imp_flask.tasks.validate import validate


class ShouldBeImpossibleException(Exception):
    pass


def newtransaction(data):
    validate(data, "transaction")

    relation = Relation.query.get(data['relation'])
    transaction = Transaction(data['eventname'], data['eventdate'], data['eventcontact'], relation)

    if "eventnotes" in data:
        transaction.eventnotes = data['eventnotes']

    for row in data['rows']:
        product = Product.query.get(row['product'])
        if row['type'] is 'gain':
            transaction.gain(product, row['amount'], row['value'])
        elif row['type'] is 'loss':
            transaction.loss(product, row['amount'])
        else:
            raise ShouldBeImpossibleException()

    return transaction
