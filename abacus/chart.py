from itertools import chain
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel

from abacus.accounting_types import AbacusError, AccountName, Operation
from abacus.accounts import Account as TAccount
from abacus.accounts import IncomeSummaryAccount, RetainedEarnings, allocation


class Account(BaseModel):
    name: str
    cls: TAccount | None = None


def is_unique(xs):
    return len(set(xs)) == len(xs)


def assert_unique(xs):
    if not is_unique(xs):
        raise AbacusError("Account names must be unique")


class Chart(BaseModel):
    assets: List[str] = []
    expenses: List[str] = []
    equity: List[str] = []
    liabilities: List[str] = []
    income: List[str] = []

    @property
    def attributes(self):
        return list(allocation.keys())

    def account_names(self):
        return [
            account_name
            for attr in self.attributes
            for account_name in getattr(self, attr)
        ]

    def yield_accounts(self):
        for attr, classes in allocation.items():
            for account in getattr(self, attr):
                yield account, classes[0]

    def set_retained_earnings(self, account_name):
        if account_name in self.equity:
            self.equity.remove(account_name)
        assert_unique(self.account_names() + [account_name])
        return QualifiedChart(base=self, retained_earnings_account=account_name)


class QualifiedChart(BaseModel):
    base: Chart
    retained_earnings_account: str
    income_summary_account: str = "_profit"
    contra_accounts: Dict[str, List[str]] = {}
    names: Dict[AccountName, str] = {}
    operations: Dict[str, Operation] = {}

    def set_operation(
        self,
        name: str,
        debit: AccountName,
        credit: AccountName,
        text: str,
        requires: AccountName | None,
    ):
        self.operations[name] = Operation(
            debit=debit, credit=credit, description=text, requires=requires
        )
        return self

    def get_operation(self, op_name: str) -> Operation | None:
        return self.operations.get(op_name, None)

    def get_long_name(self, account_name) -> str:
        try:
            return self.names[account_name]
        except KeyError:
            return account_name.capitalize().replace("_", " ")

    def get_name(self, account_name) -> str:
        return f"{self.get_long_name(account_name)} <{account_name}>"

    @classmethod
    def empty(self):
        return QualifiedChart(base=Chart(), retained_earnings_account="")

    def save(self, path):
        Path(path).write_text(self.json(indent=2), encoding="utf-8")

    def set_name(self, account_name: AccountName, title: str):
        self.names[account_name] = title
        return self

    def account_names(self):
        return (
            self.base.account_names()
            + [n for n, _ in self.yield_contra_accounts()]
            + [self.retained_earnings_account, self.income_summary_account]
        )

    def set_retained_earnings(self, account_name):
        self.base = self.base.set_retained_earnings(account_name).base
        self.retained_earnings_account = account_name
        return self

    def _set_isa(self, account_name):
        # Would be rarely used, income_summary_account is a hidden name
        self.income_summary_account = account_name
        assert_unique(self.account_names())
        return self

    def _offset(self, account_name: str, contra_account_name: str):
        if account_name not in self.account_names():
            raise AbacusError(f"{account_name} must be specified in chart")
        try:
            self.contra_accounts[account_name].append(contra_account_name)
        except KeyError:
            self.contra_accounts[account_name] = [contra_account_name]
        assert_unique(self.account_names())
        return self

    def offset(self, account_name: str, contra_account: str | List[str]):
        if isinstance(contra_account, str):
            self._offset(account_name, contra_account)
        elif isinstance(contra_account, list):
            for contra_account_name in contra_account:
                self._offset(account_name, contra_account_name)
        return self

    def yield_contra_accounts(self):
        for attr, classes in allocation.items():
            account_names = getattr(self.base, attr)
            for nets_with, contra_account_names in self.contra_accounts.items():
                if nets_with in account_names:
                    for contra_account_name in contra_account_names:
                        yield contra_account_name, classes[1]

    def yield_accounts(self):
        more = iter(
            [
                (self.retained_earnings_account, RetainedEarnings),
                (self.income_summary_account, IncomeSummaryAccount),
            ]
        )
        return chain(self.base.yield_accounts(), more, self.yield_contra_accounts())

    def qualify(self) -> "QualifiedChart":
        assert_unique(self.account_names())
        if not self.retained_earnings_account:
            raise AbacusError(
                "Must set retained earnings account before creating ledger."
            )
        for account_name in self.contra_accounts.keys():
            if account_name not in self.account_names():
                raise AbacusError(
                    f"{account_name} used for contra accounts "
                    + "but not specified in chart."
                )
        return self

    def ledger(self):
        """Create empty ledger based on this chart."""
        from abacus.ledger import Ledger

        return Ledger(
            (account_name, cls()) for account_name, cls in self.yield_accounts()
        )

    def book(self, starting_balances: dict | None = None):
        from abacus.book import Book

        if starting_balances is None:
            starting_balances = {}
        return Book(chart=self.qualify(), starting_balances=starting_balances)
