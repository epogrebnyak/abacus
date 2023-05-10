def account():
    return ([], [])


def debit(account, amount):
    return (account[0] + [amount]), account[1]


def credit(account, amount):
    return account[0], (account[1] + [amount])


def process_entry(ledger, entry):
    dr, cr, amount = entry
    ledger[dr] = debit(ledger[dr], amount)
    ledger[cr] = credit(ledger[cr], amount)


chart = dict(
    assets=["cash"],
    capital=["equity", "retained_earnings"],
    income=["services"],
    expenses=["payroll", "rent", "interest"],
    liabilities=["loan"],
)


def subset(chart, account_types):
    return [account_name for key in account_types for account_name in chart[key]]


def debit_accounts(chart):
    return subset(chart, ["assets", "expenses"])


def credit_accounts(chart):
    return subset(chart, ["capital", "liabilities", "income"])


def is_debit_account(chart, account_name):
    return account_name in debit_accounts(chart)


def is_credit_account(chart, account_name):
    return account_name in credit_accounts(chart)


def balance(chart, account_name, account):
    if is_debit_account(chart, account_name):
        return sum(account[0]) - sum(account[1])
    elif is_credit_account(chart, account_name):
        return sum(account[1]) - sum(account[0])


def make_ledger(chart):
    return {
        account_name: account()
        for account_type in chart.keys()
        for account_name in chart[account_type]
    }


def debit_account_balances(chart, ledger):
    return {
        account_name: balance(chart, account_name, account)
        for account_name, account in ledger.items()
        if is_debit_account(chart, account_name)
    }


def credit_account_balances(chart, ledger):
    return {
        account_name: balance(chart, account_name, account)
        for account_name, account in ledger.items()
        if is_credit_account(chart, account_name)
    }


def trial_balance(chart, ledger):
    return debit_account_balances(chart, ledger), credit_account_balances(chart, ledger)


def sum_values(d):
    return sum(d.values())


ledger = make_ledger(chart)
entries = [("cash", "equity", 500)]
for entry in entries:
    process_entry(ledger, entry)
print(ledger)
print(trial_balance(chart, ledger))
