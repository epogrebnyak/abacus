"""Closing accounts at period end"""

from dataclasses import field
from itertools import chain
from typing import List

from pydantic.dataclasses import dataclass

from abacus_depr.accounting_types import ClosingEntry, Netting
from abacus_depr.accounts import (
    Asset,
    Capital,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RetainedEarnings,
)
from abacus_depr.ledger import Ledger, LedgerWithNetting, transfer_balance

__all__ = ["make_closing_entries", "make_closing_entries_for_permanent_contra_accounts"]  # type: ignore


@dataclass
class ClosingEntries:
    contra_income: List[ClosingEntry] = field(default_factory=list)
    contra_expense: List[ClosingEntry] = field(default_factory=list)
    income: List[ClosingEntry] = field(default_factory=list)
    expense: List[ClosingEntry] = field(default_factory=list)
    isa: ClosingEntry | None = None

    def contra_expense_contra_income(self):
        return chain(self.contra_income, self.contra_expense)

    def all(self):
        return chain(
            self.contra_income,
            self.contra_expense,
            self.income,
            self.expense,
            [self.isa] if self.isa else [],
        )

    def __len__(self):
        return len(list(self.all()))


def make_closing_entries_for_permanent_contra_accounts(
    ledger: Ledger, netting: Netting
) -> List[ClosingEntry]:
    lwn = LedgerWithNetting(ledger, netting)

    def f(t):
        return lwn.contra_account_closing_entries(t)

    return f(Asset) + f(Capital) + f(Liability)


def make_closing_entries(ledger: Ledger, netting: Netting) -> ClosingEntries:
    lwn = LedgerWithNetting(ledger, netting)
    a = lwn.contra_account_closing_entries(Income)
    b = lwn.contra_account_closing_entries(Expense)
    _dummy_ledger = ledger.process_postings(list(a + b))
    c = close_income_to_isa(_dummy_ledger)
    d = close_expense_to_isa(_dummy_ledger)
    _dummy_ledger = _dummy_ledger.process_postings(list(c + d))
    e = closing_entry_isa_to_retained_earnings(_dummy_ledger)
    return ClosingEntries(contra_income=a, contra_expense=b, income=c, expense=d, isa=e)


def close_income_to_isa(ledger: Ledger) -> List[ClosingEntry]:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    return [
        transfer_balance(account, name, isa)
        for name, account in ledger.subset(Income).items()
    ]


def close_expense_to_isa(ledger: Ledger) -> List[ClosingEntry]:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    return [
        transfer_balance(account, name, isa)
        for name, account in ledger.subset(Expense).items()
    ]


def closing_entry_isa_to_retained_earnings(
    ledger: "Ledger",
) -> ClosingEntry:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    re = ledger.find_account_name(RetainedEarnings)
    return transfer_balance(ledger[isa], isa, re)
