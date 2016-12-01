from imp_flask.models.imps import Transaction, Relation, Product
from imp_flask.validators.validate import validate
import dateutil


class ShouldBeImpossibleException(Exception):
    pass
    
    
class NoSuchTransactionException(Exception):
    pass


def edittransaction(data):
    validate(data, "edittransaction")

    transaction = Transaction.query.get_or_404(data['index'])

    if "eventnotes" in data:
        transaction.eventnotes = data['eventnotes']
        
    if "eventdate" in data:
        eventdate = dateutil.parser.parse(data["eventdate"]).date()
        transaction.eventdate = eventdate
        
    if "eventname" in data:
        transaction.eventname = data['eventname']
        
    if "eventcontact" in data:
        transaction.eventcontact = data['eventcontact']

    for row in data['rows']:
        product = Product.query.get_or_404(row['product'])
        if row['type'] is 'gain':
            transaction.gain(product, row['amount'], row['value'])
        elif row['type'] is 'lose':
            transaction.loss(product, row['amount'])
        else:
            raise ShouldBeImpossibleException()

    return transaction
