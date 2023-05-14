from copy import deepcopy


def empty_account():
    return ([], [])


def debit(account, amount):
    return (account[0] + [amount]), account[1]


def credit(account, amount):
    return account[0], (account[1] + [amount])


def process_entry(ledger, entry):
    dr, cr, amount = entry
    _ledger = deepcopy(ledger)
    _ledger[dr] = debit(ledger[dr], amount)
    _ledger[cr] = credit(ledger[cr], amount)
    return _ledger


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


def get_balances(chart, ledger):
    return {
        account_name: balance(chart, account_name, account)
        for account_name, account in ledger.items()
    }


def filter_balances(chart, balances, filter_func):
    return {
        account_name: balance
        for account_name, balance in balances.items()
        if filter_func(chart, account_name)
    }


def trial_balance_as_tuple(chart, ledger):
    trial_balance = get_balances(chart, ledger)
    return (
        filter_balances(chart, trial_balance, is_debit_account),
        filter_balances(chart, trial_balance, is_credit_account),
    )


def union(d1, d2):
    return {**d1, **d2}


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
    ("cash", "services", 870),
    ("payroll", "cash", 355),
    ("rent", "cash", 200),
    ("cash", "loan", 500),
    ("interest", "cash", 15),
]
for entry in entries:
    ledger_ = process_entry(ledger_, entry)
print(ledger_)
a, b = trial_balance_as_tuple(chart_, ledger_)
print(a)
print(sum_dict(a))
print(b)
print(sum_dict(b))
assert sum_dict(a) == sum_dict(b)
print(union(a, b))
# balance, pl


def pick(chart, ledger, keys):
    res = {}
    trial_balance = get_balances(chart, ledger)
    for key in keys:
        res[key] = {}
        for account_name in chart[key]:
            res[key][account_name] = trial_balance[account_name]
    return res


def income_statement(chart, ledger):
    res = pick(chart, ledger, ["income", "expenses"])
    res["profit"] = {"profit": sum_dict(res["income"]) - sum_dict(res["expenses"])}
    return res


def current_profit(chart, ledger):
    return income_statement(chart, ledger)["profit"]["profit"]


def close(chart, ledger, re):
    # this is a hack to produce quick view of balance
    # this a signle, not a double entry posting
    ledger[re] = credit(ledger[re], current_profit(chart, ledger))
    return ledger


def balance_sheet(chart, ledger):
    close(chart, ledger, "retained_earnings")
    return pick(chart, ledger, ["assets", "capital", "liabilities"])


inc = income_statement(chart_, ledger_)
bal = balance_sheet(chart_, ledger_)

from pprint import pprint

pprint(inc)
pprint(bal)


def to_line(s):
    return s.replace("_", " ").capitalize()


def to_number(x):
    return str(x).rjust(5, " ")


def print_statement(report, title=""):
    print()
    print(title)
    for key, xs in report.items():
        print(to_line(key).ljust(25, "."), to_number(sum_dict(xs)))
        for account_name, amount in xs.items():
            print(("  " + to_line(account_name)).ljust(25, "."), to_number(amount))


print_statement(inc, "Income statement")
print_statement(bal, "Balance sheet")
