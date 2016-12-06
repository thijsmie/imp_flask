from collections import defaultdict


class TransactionSupplement:
    def __init__(self, transaction):
        self.grouptotals, self.subtotal, self.modtotals, self.total \
            = calculatetotals(transaction)
        self.details = {
            "_relation": transaction.relation.name,
            "_eventnumber": transaction.eventnumber,
            "_eventname": transaction.eventname,
            "_eventdate": transaction.eventdate.strftime("%Y-%m-%d"),
            "_eventcontact": transaction.eventcontact
            # (TODO) "_revision": transaction.revision
        }


def calculatetotals(transaction):
    grouptotals = defaultdict()
    subtotal = 0
    modtotals = defaultdict()
    total = 0

    for row in transaction.rows:
        subtotal += row.prevalue
        total += row.value
        grouptotals[row.product.group] += row.value

        for mod in row.includes_mods:
            modtotals[mod] += mod.apply(row.amount, row.prevalue)[1]

    grouptotals = [{'name': group, 'value': grouptotals[group]} for group in grouptotals]
    modtotals = [{'name': mod.name, 'tag': mod.tag, 'value': round(modtotals[mod])} for mod in modtotals]

    return grouptotals, subtotal, modtotals, total
