"""Chart of accounts."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .accounts import (
    Asset,
    Capital,
    RetainedEarnings,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    Netting,
    get_contra_account_type,
)
from .ledger import Ledger
from .accounting_types import RetainedEarningsAccount

__all__ = ["Chart"]


def split_equity(xs):
    strings = [x for x in xs if isinstance(x, str)]
    re_many = [x for x in xs if isinstance(x, RetainedEarningsAccount)]
    if len(re_many) != 1:
        raise TypeError("There must be exactly one RetainedEarningsAccount")
    return strings, re_many[0].retained_earnings_account_name


@dataclass
class Chart:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    equity: List[str | RetainedEarningsAccount]
    liabilities: List[str]
    income: List[str]
    contra_accounts: Dict[str, Tuple[List[str], str]] = field(default_factory=dict)
    income_summary_account: str = "_profit"

    def __post_init__(self):
        _, _ = split_equity(self.equity)

    def flat(self):
        capital, retained_earnings_account_name = split_equity(self.equity)
        return [
            (Asset, self.assets),
            (Expense, self.expenses),
            (Capital, capital),
            (RetainedEarnings, [retained_earnings_account_name]),
            (Liability, self.liabilities),
            (Income, self.income),
            (IncomeSummaryAccount, [self.income_summary_account]),
        ]

    def which(self, account_name):
        return [
            Class
            for Class, account_names in self.flat()
            if account_name in account_names
        ][0]

    # TODO: must check for duplicatre account keys

    def make_ledger(self) -> Ledger:
        ledger = make_regular_accounts(self)
        return add_contra_accounts(self, ledger)


def make_regular_accounts(chart: Chart):
    return Ledger(
        (account_name, cls())
        for cls, account_names in chart.flat()
        for account_name in account_names
    )


def add_contra_accounts(chart: Chart, ledger: Ledger) -> Ledger:
    for refers_to, (contra_accounts, target_account) in chart.contra_accounts.items():
        ledger[refers_to].netting = Netting(contra_accounts, target_account)  # type: ignore
        cls = get_contra_account_type(chart.which(refers_to))
        for contra_account_name in contra_accounts:
            ledger[contra_account_name] = cls()
    return ledger
