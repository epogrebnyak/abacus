from dataclasses import dataclass, field
from typing import Dict, List, Optional

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
class Line:
    text: str
    value: Optional[int]


@dataclass
class Ledger:
    """Ledger to record transactions in accounts."""

    accounts: Dict[str, Account]

    def enter(self, debit, credit, value):
        self.accounts[debit].debit(value)
        self.accounts[credit].credit(value)

    def process(self, e: Entry):
        self.enter(**e.__dict__)

    def balance(self, name):
        return self.accounts[name].balance()

    def get_line(self, name):
        return Line(name, self.balance(name))


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


def balance_lines(L, chart):
    from formatting import Line, fmt, make_formatter

    assets = [L.get_line(name) for name in chart.assets]
    left = ["Assets"] + fmt(assets)
    cap = [L.get_line(name) for name in chart.capital] + [
        Line("profit", profit(L, chart))
    ]
    liab = [L.get_line(name) for name in chart.liabilities]
    f = make_formatter(cap + liab)
    right = ["Capital"] + fmt(cap, f) + ["Liabilities"] + fmt(liab, f)
    return left, right
