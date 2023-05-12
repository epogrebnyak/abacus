def empty_account():
    return ([], [])


def debit(account, amount):
    return (account[0] + [amount]), account[1]


def credit(account, amount):
    return account[0], (account[1] + [amount])


def process_entry(ledger, entry):
    dr, cr, amount = entry
    ledger[dr] = debit(ledger[dr], amount)
    ledger[cr] = credit(ledger[cr], amount)


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
    if is_credit_account(chart, account_name):
        return sum(account[1]) - sum(account[0])


def make_ledger(chart):
    return {
        account_name: empty_account()
        for account_type in chart.keys()
        for account_name in chart[account_type]
    }


def trim_ledger(chart, ledger, filter_func):
    return {
        account_name: balance(chart, account_name, account)
        for account_name, account in ledger.items()
        if filter_func(chart, account_name)
    }


def debit_account_balances(chart, ledger):
    return trim_ledger(chart, ledger, is_debit_account)


def credit_account_balances(chart, ledger):
    return trim_ledger(chart, ledger, is_credit_account)


def trial_balance(chart, ledger):
    return debit_account_balances(chart, ledger), credit_account_balances(chart, ledger)


def sum_dict(d):
    return sum(d.values())


chart_ = {
    "assets": ["cash"],
    "capital": ["equity", "retained_earnings"],
    "income": ["services"],
    "expenses": ["payroll", "rent", "interest"],
    "liabilities": ["loan"],
}

ledger_ = make_ledger(chart_)
entries = [
    ("cash", "equity", 299),
    ("cash", "equity", 301),
    ("cash", "services", 1500),
    ("payroll", "cash", 355),
    ("rent", "cash", 200),
]
for entry in entries:
    process_entry(ledger_, entry)
print(ledger_)
a, b = trial_balance(chart_, ledger_)
print(a)
print(sum_dict(a))
print(b)
print(sum_dict(b))
assert sum_dict(a) == sum_dict(b)
# balance, pl

def pick(chart, ledger, keys):
    res = {}
    tb1, tb2 = trial_balance(chart, ledger)
    tb = {**tb1, **tb2}
    for key in keys:
        res[key] = {}
        for account_name in chart[key]:
            res[key][account_name] = tb[account_name]
    return res

def income_statement(chart, ledger):
    res = pick(chart, ledger, "income expenses".split())
    res["profit"] = sum_dict(res["income"]) - sum_dict(res["expenses"])
    return res

def current_profit(chart, ledger):
    return income_statement(chart, ledger)["profit"]

def close(chart, ledger, re):
    ledger[re] = current_profit(chart, ledger)
    return ledger

def balance_sheet(chart, ledger):
    close(chart, ledger, "retained_earnings")
    return pick(chart, ledger, "assets capital liabilities".split())

# Does not work
#print(income_statement(chart_, ledger_))
#print(balance_sheet(chart_, ledger_))
