"""Chart of accounts."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .accounts import (Asset, Capital, Expense, Income, IncomeSummaryAccount,
                       Liability, Netting, get_contra_account_type)
from .ledger import Ledger


@dataclass
class Chart2:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    capital: List[str]
    liabilities: List[str]
    income: List[str]
    income_summary_account: str = "profit"

    def flat(self):
        for attr, cls in [
            ("assets", Asset),
            ("expenses", Expense),
            ("equity", Capital),
            ("liabilities", Liability),
            ("income", Income),
        ]:
            for account_name in getattr(self, attr):
                yield cls, account_name
        yield IncomeSummaryAccount, self.income_summary_account


@dataclass
class Chart:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    equity: List[str]
    liabilities: List[str]
    income: List[str]
    contra_accounts: Dict[str, Tuple[List[str], str]] = field(default_factory=dict)
    income_summary_account: str = "profit"

    def flat(self):
        return [
            (Asset, self.assets),
            (Expense, self.expenses),
            (Capital, self.equity),
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

    def make_ledger(self):
        return make_ledger(self)


def make_regular_accounts(chart: Chart):
    return Ledger(
        (account_name, C())
        for C, account_names in chart.flat()
        for account_name in account_names
    )


def add_contra_accounts(chart: Chart, ledger: Ledger) -> Ledger:
    for nets_with, (contra_accounts, target_account) in chart.contra_accounts.items():
        cls = get_contra_account_type(chart.which(nets_with))
        for contra_account_name in contra_accounts:
            ledger[contra_account_name] = cls()
            ledger[nets_with].netting = Netting(contra_accounts, target_account) #type: ignore
    return ledger


def make_ledger(chart: Chart) -> Ledger:
    ledger = make_regular_accounts(chart)
    return add_contra_accounts(chart, ledger)
