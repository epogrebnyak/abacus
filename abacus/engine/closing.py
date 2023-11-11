"""Closing accounts at period end."""
from dataclasses import dataclass
from typing import List

from abacus.engine.accounts import Expense, Income
from abacus.engine.base import AccountName, Entry
from abacus.engine.better_chart import Chart
from abacus.engine.ledger import Ledger

__all__ = [
    "close_contra_income",
    "close_contra_expense",
    "make_closing_entries",
    "flush_permanent_accounts",
]


def flush_permanent_accounts(chart: Chart, ledger: Ledger) -> List[Entry]:
    """Make closing entries for permanent_accounts."""
    from abacus.engine.better_chart import AssetName, CapitalName, LiabilityName

    def f(name_class):
        return _flush(chart, ledger, name_class)

    return f(AssetName) + f(CapitalName) + f(LiabilityName)


@dataclass
class ClosingEntries:
    """Closing entries for accounts related to income and expenses."""

    closing_contra_income: List[Entry]
    closing_contra_expense: List[Entry]
    closing_income: List[Entry]
    closing_expense: List[Entry]
    closing_isa: Entry

    @property
    def closing_contra_accounts(self) -> List[Entry]:
        return self.closing_contra_income + self.closing_contra_expense

    @property
    def closing_income_expense_isa(self) -> List[Entry]:
        return self.closing_income + self.closing_expense + [self.closing_isa]

    def all(self):
        return self.closing_contra_accounts + self.closing_income_expense_isa


def make_closing_entries(chart: Chart, ledger: Ledger) -> ClosingEntries:
    """Create a data structure holding closing entries.

    Steps taken are the following:
    - close contra accounts to income and expense accounts
    - close income and expense accounts
    - close income summary account to retained earnings.
    """
    dummy_ledger = ledger.condense()
    a = close_contra_income(chart, dummy_ledger)
    b = close_contra_expense(chart, dummy_ledger)
    dummy_ledger.post_many(a + b)
    c = close_income_to_isa(chart.base_chart.income_summary_account, dummy_ledger)
    d = close_expenses_to_isa(chart.base_chart.income_summary_account, dummy_ledger)
    dummy_ledger.post_many(c + d)
    e = close_isa(
        isa=chart.base_chart.income_summary_account,
        re=chart.base_chart.retained_earnings_account,
        ledger=dummy_ledger,
    )
    return ClosingEntries(
        closing_contra_income=a,
        closing_contra_expense=b,
        closing_income=c,
        closing_expense=d,
        closing_isa=e,
    )


def _flush(chart: Chart, ledger: Ledger, name_class) -> List[Entry]:
    """Make a list of entries for transfering balances for accounts of a certain type.
    These entries are used to close contra accounts."""
    gen = chart.base_chart.yield_contra_account_pairs(name_class)
    return [
        ledger[contra_account].transfer(contra_account, regular_account)  # type: ignore
        for regular_account, contra_account in gen
    ]


def close_contra_income(chart: Chart, ledger: Ledger) -> List[Entry]:
    """Make entries for closing contra income accounts (eg discounts, refunds made to clients).
    Balance transfered from contra account to corresponding income account.
    The income accounts will hold net value after these entries are posted.
    """
    from abacus.engine.better_chart import IncomeName

    return _flush(chart, ledger, IncomeName)


def close_contra_expense(chart: Chart, ledger: Ledger) -> List[Entry]:
    """Make entries for closing contra expense accounts (eg discounts received).
    Balance transfered from contra account to corresponding expense account.
    The expense account will hold net value after these entries are posted.
    """
    from abacus.engine.better_chart import ExpenseName

    return _flush(chart, ledger, ExpenseName)


def close_income_to_isa(isa: AccountName, ledger: Ledger) -> List[Entry]:
    return [
        Entry(account_name, isa, t_account.balance())
        for account_name, t_account in ledger.subset(Income).items()
    ]


def close_expenses_to_isa(isa: AccountName, ledger: Ledger) -> List[Entry]:
    return [
        Entry(isa, account_name, t_account.balance())
        for account_name, t_account in ledger.subset(Expense).items()
    ]


def close_isa(isa: AccountName, re: AccountName, ledger: Ledger) -> Entry:
    """Make entry to close income summary account ("isa") and move its balance to retained earnings."""
    amount = ledger[isa].balance()
    return Entry(isa, re, amount)
