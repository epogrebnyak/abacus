from dataclasses import dataclass, field
from typing import Dict, List

Value = int


@dataclass
class Account:
    debit_items: [Value] = field(default_factory=list)
    credit_items: [Value] = field(default_factory=list)

    def debit(self, x):
        self.debit_items.append(x)

    def credit(self, x):
        self.credit_items.append(x)


@dataclass
class DebitAccount(Account):
    def balance(self):
        return debit_balance(self)


class CreditAccount(Account):
    def balance(self):
        return -debit_balance(self)


def debit_balance(account):
    return sum(account.debit_items) - sum(account.credit_items)


@dataclass
class Chart:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    liabilities: List[str]
    capital: List[str]
    income: List[str]

    @property
    def account_names(self):
        return self.debit_accounts + self.credit_accounts

    @property
    def debit_accounts(self):
        return self.assets + self.expenses

    @property
    def credit_accounts(self):
        return self.liabilities + self.capital + self.income

    def is_debit_account(self, account_name: str):
        return account_name in self.debit_accounts

    def is_credit_account(self, account_name: str):
        return account_name in self.credit_accounts


@dataclass
class Entry:
    value: Value
    debit: str
    credit: str


E = Entry


@dataclass
class Ledger:
    """Ledger to record transactions in accounts."""

    accounts: Dict[str, Account]

    def enter(self, debit, credit, value):
        self.accounts[debit].debit(value)
        self.accounts[credit].credit(value)

    def process(self, e: Entry):
        self.enter(**e.__dict__)


def make_ledger(chart: Chart) -> Ledger:
    accounts = dict()
    for name in chart.debit_accounts:
        accounts[name] = DebitAccount()
    for name in chart.credit_accounts:
        accounts[name] = CreditAccount()
    return Ledger(accounts)


def profit(ledger, chart):
    income, expenses = 0, 0
    for name in chart.income:
        income += ledger.accounts[name].balance()
    for name in chart.expenses:
        expenses += ledger.accounts[name].balance()
    return income - expenses


def balances(ledger, chart):
    res = {}
    for name in chart.assets + chart.liabilities + chart.capital:
        res[name] = ledger.accounts[name].balance()
    res["profit"] = profit(ledger, chart)
    return res


def renamer(x):
    return x.replace("_", " ").capitalize()


def as_lines(xs, chart):
    longest = max([len(x) for x in chart.account_names])
    l_offset = min(20, 3 + longest)
    r_offest = 4

    def line(text, value):
        return "  " + text.ljust(l_offset, ".") + str(value).rjust(r_offest)

    bs = [line(renamer(x[0]), x[1]) for x in xs]
    return "\n".join(bs)


def nb(ledger, name):
    return (name, ledger.accounts[name].balance())


def str_assets(L, chart):
    xs = [nb(L, name) for name in chart.assets]
    return as_lines(xs, chart)


def str_cap(L, chart):
    xs = [nb(L, name) for name in chart.capital] + [("profit", profit(L, chart))]
    return as_lines(xs, chart)


def str_liab(L, chart):
    return as_lines([nb(L, name) for name in chart.liabilities], chart)


def print_balance(L, chart):
    print("Assets")
    print(str_assets(L, chart))
    print("Capital")
    print(str_cap(L, chart))
    print("Liabilities")
    print(str_liab(L, chart))
