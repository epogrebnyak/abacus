from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Value = int  # can be Decimal


@dataclass
class Account:
    debits: List[Value] = field(default_factory=list)
    credits: List[Value] = field(default_factory=list)

    def debit(self, amount: Value):
        self.debits.append(amount)

    def credit(self, amount: Value):
        self.credits.append(amount)

    def balance(self):
        pass


@dataclass
class DebitAccount(Account):
    def balance(self):
        return sum(self.debits) - sum(self.credits)


class CreditAccount(Account):
    def balance(self):
        return sum(self.credits) - sum(self.debits)


def debit_balance(account):
    return sum(account.debits) - sum(account.credits)


def plus(xs):
    return "(" + " + ".join(xs) + ")"


@dataclass
class Chart:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    capital: List[str]
    liabilities: List[str]
    income: List[str]

    @property
    def equation(self) -> str:
        return (f"{plus(self.assets)} + {plus(self.expenses)} = "
                f"{plus(self.capital)} + {plus(self.liabilities)} + {plus(self.income)}")

    @property
    def debit_accounts(self):
        return self.assets + self.expenses

    def is_debit_account(self, account_name: str):
        return account_name in self.debit_accounts

    @property
    def credit_accounts(self):
        return self.capital + self.liabilities + self.income

    def is_credit_account(self, account_name: str):
        return account_name in self.credit_accounts

    @property
    def account_names(self):
        return self.debit_accounts + self.credit_accounts


@dataclass
class Entry:
    value: Value
    debit: str
    credit: str
    description: str = ""


E = Entry


def to_entry(textline: str):
    x, debit, credit = textline.split()
    return Entry(Value(x), debit.lower(), credit.lower())


@dataclass
class Ledger:
    """Ledger to record transactions in accounts."""

    accounts: Dict[str, Account]

    def enter(self, debit_account_name, credit_account_name, value):
        self.accounts[debit_account_name].debit(value)
        self.accounts[credit_account_name].credit(value)

    def process(self, e: Entry):
        self.enter(e.debit, e.credit, e.value)

    def process_all(self, es: List[Entry]):
        for e in es:
            self.process(e)

    def balance(self, name):
        return self.accounts[name].balance()


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


def balance_lines(
    book: Ledger, chart: Chart, names_dict: Dict[str, str] = {}
) -> Tuple[List[str], List[str]]:
    from abacus.formatting import Line, to_strings, make_formatter

    def rename(name):
        return names_dict.get(name, name)

    def lines(names):
        return [Line(rename(name), book.balance(name)) for name in names]

    cap = lines(chart.capital) + [Line("profit", profit(book, chart))]
    liab = lines(chart.liabilities)
    f = make_formatter(cap + liab)
    right = ["Capital"] + to_strings(cap, f) + ["Liabilities"] + to_strings(liab, f)
    left = ["Assets"] + to_strings(lines(chart.assets))
    return left, right


@dataclass
class Book:
    chart: Chart
    ledger: Ledger
    names: Dict[str, str]

    def balance_lines(self):
        return balance_lines(self.ledger, self.chart, self.names)

    def process_all(self, es: List[Entry]):
        self.ledger.process_all(es)

    @property
    def profit(self):
        return profit(self.ledger, self.chart)


def make_book(chart, names={}):
    return Book(chart, make_ledger(chart), names)
