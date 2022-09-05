from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Value = float


@dataclass
class Account:
    debits: List[Value] = field(default_factory=list)
    credits: List[Value] = field(default_factory=list)

    def debit(self, amount: Value):
        self.debits.append(amount)

    def credit(self, amount: Value):
        self.credits.append(amount)

    def balance(self):
        raise NotImplementedError


class DebitAccount(Account):
    def balance(self):
        return sum(self.debits) - sum(self.credits)


class CreditAccount(Account):
    def balance(self):
        return sum(self.credits) - sum(self.debits)


def debit_balance(account):
    return sum(account.debits) - sum(account.credits)


@dataclass
class Chart:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    equity: List[str]
    liabilities: List[str]
    income: List[str]

    @property
    def debit_account_names(self) -> List[str]:
        return self.assets + self.expenses

    def is_debit_account(self, account_name: str):
        return account_name in self.debit_account_names

    @property
    def credit_account_names(self) -> List[str]:
        return self.equity + self.liabilities + self.income

    def is_credit_account(self, account_name: str):
        return account_name in self.debit_account_names

    @property
    def account_names(self):
        return self.debit_account_names + self.credit_account_names


def equation(ch: Chart) -> str:
    return " ".join(
        [
            plus(ch.assets),
            "+",
            plus(ch.expenses),
            "=",
            plus(ch.equity),
            "+",
            plus(ch.liabilities),
            "+",
            plus(ch.income),
        ]
    )


def plus(xs: List[str]):
    return "(" + " + ".join(xs) + ")"


def is_debit_account(chart: Chart, account_name: str):
    return account_name in chart.debit_accounts


def is_credit_account(chart: Chart, account_name: str):
    return account_name in chart.credit_accounts


@dataclass
class Entry:
    value: Value
    debit: str
    credit: str
    description: str = ""


E = Entry


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

    def balance(self, account_name):
        return self.accounts[account_name].balance()


def make_ledger(chart: Chart) -> Ledger:
    accounts = dict()
    for name in chart.debit_account_names:
        accounts[name] = DebitAccount()
    for name in chart.credit_account_names:
        accounts[name] = CreditAccount()
    return Ledger(accounts)


def sum_of_balances(ledger, account_names):
    return sum(
        ledger.accounts[account_name].balance() for account_name in account_names
    )


def income(ledger, chart):
    return sum_of_balances(ledger, chart.income)


def expenses(ledger, chart):
    return sum_of_balances(ledger, chart.expenses)


def profit(ledger, chart):
    return income(ledger, chart) - expenses(ledger, chart)


def balances(ledger, chart):
    res = {}
    for name in chart.assets + chart.liabilities + chart.equity:
        res[name] = ledger.accounts[name].balance()
    res["profit"] = profit(ledger, chart)
    return res
