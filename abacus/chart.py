"""Chart of accounts."""

from typing import Dict, List, Type

from pydantic import BaseModel, root_validator  # type: ignore

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


def opening_entries_regular(chart, starting_balances):
    from abacus.ledger import OpenRegularAccount

    def get_balance(account_name):
        return starting_balances.get(account_name, 0)

    return [
        OpenRegularAccount(account_name, cls.__name__, get_balance(account_name))
        for account_name, cls in chart._yield_regular_accounts()
    ]


def opening_entries_contra(chart, starting_balances):
    from abacus.ledger import OpenContraAccount

    def get_balance(account_name):
        return starting_balances.get(account_name, 0)

    return [
        OpenContraAccount(account_name, cls.__name__, get_balance(account_name), link)
        for account_name, cls, link in chart._yield_contra_accounts()
    ]


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

    # FIXME: in pydantic 2.0 we can save some code with __post_init__()
    #        there will be no @root_validator with values and no helper functions.
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

    def check_type(self, account_name: AccountName, cls: Type) -> bool:
        return isinstance(self.get_type(account_name)(), cls)

    def is_debit_account(self, account_name: AccountName) -> bool:
        from abacus.accounts import DebitAccount

        return self.check_type(account_name, DebitAccount)

    def is_credit_account(self, account_name: AccountName) -> bool:
        from abacus.accounts import CreditAccount

        return self.check_type(account_name, CreditAccount)

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

    def yield_accounts_as_text(self):
        for account_name, cls in self.yield_accounts():
            yield account_name, cls.__name__

    @property
    def account_names(self) -> List[AccountName]:
        """List all account names in chart."""
        return [a[0] for a in self.yield_accounts()]

    def journal(self, starting_balances: dict | None = None):
        """Create a journal based on this chart."""
        if starting_balances is None:
            starting_balances = {}
        return make_journal(self, starting_balances)

    def ledger(self):
        """Create empty ledger based on this chart."""
        from abacus.ledger import Ledger

        return Ledger((a, b()) for a, b in self.yield_accounts())


def make_journal(chart, starting_balances: dict):
    from abacus.journal import Journal

    journal = Journal()
    journal.data.netting = chart.contra_accounts
    journal.data.accounts = list(chart.yield_accounts_as_text())
    journal.data.starting_balances = starting_balances
    return journal
