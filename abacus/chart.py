"""Chart of accounts."""

from pathlib import Path
from typing import Dict, List, Type

from pydantic import BaseModel  # type: ignore

from abacus.accounting_types import AbacusError, AccountName
from abacus.accounts import (
    Asset,
    Capital,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RetainedEarnings,
    get_contra_account_type,
)

__all__ = ["Chart"]


def empty_chart():
    return Chart(
        assets=[],
        expenses=[],
        equity=[],
        retained_earnings_account="",
        liabilities=[],
        income=[],
    )


def is_unique(xs):
    return len(set(xs)) == len(xs)


class Chart(BaseModel):
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    equity: List[str]
    retained_earnings_account: str
    liabilities: List[str]
    income: List[str]
    contra_accounts: Dict[str, List[str]] = {}
    income_summary_account: str = "_profit"

    def __init__(self, **kw):
        super().__init__(**kw)
        self.assert_unique_account_names()
        self.assert_contra_account_names_match_regular_accounts()

    def weak_validate(self):
        self.assert_unique_account_names()
        self.assert_contra_account_names_match_regular_accounts()
        return self

    def strong_validate(self):
        self.weak_validate()
        if not self.retained_earnings_account:
            raise AbacusError("Must set retained earnings attribute")
        return self

    def pprint(self):
        from pprint import pprint

        pprint(self.dict())
        return self

    @classmethod
    def empty(cls):
        return empty_chart()

    @classmethod
    def load(cls, path):
        return cls.parse_file(path)

    def save(self, path):
        Path(path).write_text(self.json(indent=2), encoding="utf-8")

    @property
    def input_names(self):
        return (
            [self.income_summary_account]
            + [self.retained_earnings_account]
            + self.assets
            + self.expenses
            + self.equity
            + self.liabilities
            + self.income
            + [name for names in self.contra_accounts.values() for name in names]
        )

    def assert_unique_account_names(self):
        if not is_unique(self.input_names):
            raise AbacusError("Account names must be unique")

    def assert_contra_account_names_match_regular_accounts(self):
        for account_name in self.contra_accounts.keys():
            if account_name not in self.input_names:
                raise AbacusError(f"{account_name} must be specified in chart")

    def _yield_regular_accounts(self):
        for account_name in self.assets:
            yield account_name, Asset
        for account_name in self.expenses:
            yield account_name, Expense
        for account_name in self.equity:
            yield account_name, Capital
        yield self.retained_earnings_account, RetainedEarnings
        for account_name in self.liabilities:
            yield account_name, Liability
        for account_name in self.income:
            yield account_name, Income
        yield self.income_summary_account, IncomeSummaryAccount

    def get_type(self, account_name: AccountName) -> Type:
        """Return account class for *account_name*."""
        return dict(self._yield_regular_accounts())[account_name]

    # def check_type(self, account_name: AccountName, cls: Type) -> bool:
    #     return isinstance(self.get_type(account_name)(), cls)

    # def is_debit_account(self, account_name: AccountName) -> bool:
    #     from abacus.accounts import DebitAccount

    #     return self.check_type(account_name, DebitAccount)

    # def is_credit_account(self, account_name: AccountName) -> bool:
    #     from abacus.accounts import CreditAccount

    #     return self.check_type(account_name, CreditAccount)

    def _yield_contra_accounts(self):
        for linked_account_name, contra_account_names in self.contra_accounts.items():
            cls = get_contra_account_type(self.get_type(linked_account_name))
            for contra_account in contra_account_names:
                yield contra_account, cls

    def yield_accounts(self):
        from itertools import chain

        a = self._yield_regular_accounts()
        b = self._yield_contra_accounts()
        return chain(a, b)

    @property
    def account_names(self) -> List[AccountName]:
        """List all account names in chart."""
        return [a[0] for a in self.yield_accounts()]

    def book(self, starting_balances: dict | None = None):
        from abacus.book import Book

        if starting_balances is None:
            starting_balances = {}
        return Book(chart=self, starting_balances=starting_balances)

    # def journal(self, starting_balances: dict | None = None):
    #     """Create a journal based on this chart."""
    #     if starting_balances is None:
    #         starting_balances = {}
    #     return make_journal(self, starting_balances)

    def ledger(self):
        """Create empty ledger based on this chart."""
        from abacus.ledger import Ledger

        return Ledger(
            (account_name, cls()) for account_name, cls in self.yield_accounts()
        )
