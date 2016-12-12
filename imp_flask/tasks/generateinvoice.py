from imp_flask.core.latex import texenv
from imp_flask.tasks.maketransactionsupplement import TransactionSupplement


def generateinvoice(transaction, verbose=True):
    supplement = TransactionSupplement(transaction)
    if verbose:
        invoice = texenv.render_template('invoice_verbose.tex',
                                         total=supplement.total,
                                         subtotal=supplement.subtotal,
                                         grouptotals=supplement.grouptotals,
                                         modtotals=supplement.modtotals,
                                         details=supplement.details)
    else:
        invoice = texenv.render_template('invoice.tex',
                                         total=supplement.total,
                                         grouptotals=supplement.grouptotals,
                                         details=supplement.details)
    return invoice
