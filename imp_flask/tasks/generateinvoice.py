from imp_flask.core.latex import texenv
from imp_flask.tasks.maketransactionsupplement import TransactionSupplement
from imp_flask.config import strings


def generateinvoice(transaction, verbose=True):
    supplement = TransactionSupplement(transaction)
    if verbose:
        invoice = texenv.render_template('invoice_verbose.tex',
                                         strings=strings,
                                         total=supplement.total,
                                         subtotal=supplement.subtotal,
                                         grouptotals=supplement.grouptotals,
                                         modtotals=supplement.modtotals,
                                         details=supplement.details)
    else:
        invoice = texenv.render_template('invoice.tex',
                                         strings=strings,
                                         total=supplement.total,
                                         grouptotals=supplement.grouptotals,
                                         details=supplement.details)
    return invoice
