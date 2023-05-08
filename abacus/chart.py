"""Chart of accounts."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .accounts import (
    Asset,
    Capital,
    CreditAccount,
    CreditContraAccount,
    DebitAccount,
    DebitContraAccount,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    Netting,
)
from .ledger import Ledger


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

    def regular_attributes(self):
        return [p[0] for p in self.attribute_mapping]

    @property
    def attribute_mapping(self):
        return [
            ("assets", Asset),
            ("expenses", Expense),
            ("equity", Capital),
            ("liabilities", Liability),
            ("income", Income),
        ]

    def account_types(self):
        res = {}
        for attr, _cls in self.attribute_mapping:
            for account_name in getattr(self, attr):
                res[account_name] = _cls
        return res

    # TODO: must check for duplicatre account keys

    def make_ledger(self):
        return make_ledger(self)


def make_regular_accounts(chart: Chart):
    ledger = Ledger()
    account_types = chart.account_types()
    for attr in chart.regular_attributes():
        for account_name in getattr(chart, attr):
            ledger[account_name] = account_types[account_name]()
    return ledger


def make_ledger(chart: Chart) -> Ledger:
    account_types = chart.account_types()
    ledger = make_regular_accounts(chart)
    for nets_with, (contra_accounts, target_account) in chart.contra_accounts.items():
        for contra_account_name in contra_accounts:
            match account_types[nets_with]():
                case DebitAccount():
                    ledger[contra_account_name] = CreditContraAccount()
                    ledger[nets_with].netting = Netting(contra_accounts, target_account)
                case CreditAccount():
                    ledger[contra_account_name] = DebitContraAccount()
                    ledger[nets_with].netting = Netting(contra_accounts, target_account)
                case _:
                    raise TypeError
    ledger[chart.income_summary_account] = IncomeSummaryAccount()
    return ledger
