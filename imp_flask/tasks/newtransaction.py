from imp_flask.models.imps import Transaction, Relation, Product
from imp_flask.validators.validate import validate
import dateutil


class ShouldBeImpossibleException(Exception):
    pass


def newtransaction(data):
    validate(data, "newtransaction")
    
    eventdate = dateutil.parser.parse(data["eventdate"]).date()
    
    relation = Relation.query.get(data['relation'])
    transaction = Transaction(data['eventname'], eventdate, data['eventcontact'], relation)

    if "eventnotes" in data:
        transaction.eventnotes = data['eventnotes']

    for row in data['rows']:
        product = Product.query.get_or_404(row['product'])
        if row['type'] is 'gain':
            transaction.gain(product, row['amount'], row['value'])
        elif row['type'] is 'lose':
            transaction.loss(product, row['amount'])
        else:
            raise ShouldBeImpossibleException()

    return transaction
