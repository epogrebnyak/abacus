"""Chart of accounts."""

from typing import Dict, List, Type

from pydantic import BaseModel, root_validator  # type: ignore

from .accounting_types import AbacusError, AccountName
from .accounts import (
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


def is_unique(xs):
    return len(set(xs)) == len(xs)


def contra_account_names(values):
    return [
        contra_account
        for _, contra_accounts in values.get("contra_accounts", {}).items()
        for contra_account in contra_accounts
    ]


def regular_account_names(values):
    return (
        [values["income_summary_account"], values["retained_earnings_account"]]
        + values["assets"]
        + values["expenses"]
        + values["equity"]
        + values.get("liabilities", [])
        + values["income"]
    )


def all_args(values):
    return regular_account_names(values) + contra_account_names(values)


class Chart(BaseModel):
    """Chart of accounts."""

    assets: list[str]
    expenses: list[str]
    equity: list[str]
    retained_earnings_account: str
    liabilities: list[str] = []
    income: list[str]
    contra_accounts: Dict[str, List[str]] = {}
    income_summary_account: str = "_profit"

    @root_validator
    def account_names_should_be_unique(cls, values):
        if not is_unique(all_args(values)):
            raise AbacusError("Account names must be unique")
        return values

    @root_validator
    def contra_accounts_should_match_chart_of_accounts(cls, values):
        regular_account_names = all_args(values)
        for account_name in values.get("contra_accounts", {}).keys():
            if account_name not in regular_account_names:
                raise AbacusError(
                    [
                        regular_account_names,
                        f"{account_name} must be specified in chart",
                    ]
                )
        return values

    def _yield_regular_accounts(self):
        for a in self.assets:
            yield a, Asset
        for e in self.expenses:
            yield e, Expense
        for c in self.equity:
            yield c, Capital
        yield self.retained_earnings_account, RetainedEarnings
        for l in self.liabilities:
            yield l, Liability
        for i in self.income:
            yield i, Income
        yield self.income_summary_account, IncomeSummaryAccount

    def get_type(self, account_name: AccountName) -> Type:
        """Return account class for *account_name*."""
        return dict(self._yield_regular_accounts())[account_name]

    def _yield_contra_accounts(self):
        for account_name, contra_account_names in self.contra_accounts.items():
            cls = get_contra_account_type(self.get_type(account_name))
            for contra_account in contra_account_names:
                yield contra_account, cls, account_name

    def yield_accounts(self):
        from itertools import chain

        return chain(self._yield_regular_accounts(), self._yield_contra_accounts())

    @property
    def account_names(self) -> List[AccountName]:
        """List all account names in chart."""
        return [xs[0] for xs in self.yield_accounts()]

    def journal(self, **kwargs):
        from abacus.ledger import Journal

        def get_balance(account_name):
            return kwargs.get(account_name, 0)

        journal = Journal()
        for account_name, cls_string in self._yield_regular_accounts():
            journal.open_regular_account(
                account_name, cls_string, get_balance(account_name)
            )
        for account_name, cls_string, link in self._yield_contra_accounts():
            journal.open_contra_account(
                account_name, cls_string, get_balance(account_name), link
            )
        return journal

    def ledger(self):
        """Create empty ledger based on this chart."""
        from abacus.ledger import Ledger

        _gen1 = [
            (account_name, cls())
            for account_name, cls in self._yield_regular_accounts()
        ]
        _gen2 = [
            (account_name, cls(link=link))
            for account_name, cls, link in self._yield_contra_accounts()
        ]
        return Ledger(_gen1 + _gen2)
