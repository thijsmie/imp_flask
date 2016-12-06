

def rowapplymods(transactionrow):
    value = transactionrow.prevalue
    for mod in transactionrow.includes_mods:
        value = mod.apply(transactionrow.amount, value)[0]
    transactionrow.value = value
