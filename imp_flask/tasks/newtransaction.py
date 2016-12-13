from imp_flask.models.imps import Transaction, Relation, Product, Mod
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
        mods = []
        for mod_id in row['includes_mods']:
            mods.append(Mod.query.get(mod_id))
        if row['type'] is 'gain':
            transaction.gain(product, row['amount'], row['value'], mods)
        elif row['type'] is 'lose':
            transaction.loss(product, row['amount'], mods)
        else:
            raise ShouldBeImpossibleException()

    transaction.revision = 1

    return transaction
