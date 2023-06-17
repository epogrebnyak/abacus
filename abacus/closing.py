"""Closing accounts at period end"""

from dataclasses import field
from itertools import chain
from typing import List, Type

from pydantic.dataclasses import dataclass

from abacus.accounting_types import AccountName, Netting
from abacus.accounts import (
    Account,
    Asset,
    Capital,
    ClosableAccount,
    CreditAccount,
    DebitAccount,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RetainedEarnings,
)
from abacus.closing_types import (
    CloseContraAsset,
    CloseContraCapital,
    CloseContraExpense,
    CloseContraIncome,
    CloseContraLiability,
    ClosingEntry,
)
from abacus.ledger import Ledger, LedgerWithNetting

__all__ = ["make_closing_entries", "make_closing_entries_for_permanent_contra_accounts"]  # type: ignore


@dataclass
class ClosingEntries:
    contra_income: List[ClosingEntry] = field(default_factory=list)
    contra_expense: List[ClosingEntry] = field(default_factory=list)
    income: List[ClosingEntry] = field(default_factory=list)
    expense: List[ClosingEntry] = field(default_factory=list)
    isa: ClosingEntry | None = None

    def ci_ce(self):
        return chain(self.contra_income, self.contra_expense)

    def all(self):
        return chain(
            self.contra_income,
            self.contra_expense,
            self.income,
            self.expense,
            [self.isa],
        )


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


def subset(ledger: Ledger, netting: Netting, regular_cls: Type):
    """Yield link account and contra account name pairs."""
    for linked_account_name, contra_account_names in netting.items():
        linked_account = ledger[linked_account_name]
        if isinstance(linked_account, regular_cls):
            for contra_account_name in contra_account_names:
                yield linked_account_name, contra_account_name


def close_contra_accounts(ledger: Ledger, netting: Netting, regular_cls: Type) -> List:
    return [
        transfer_entry(
            account=ledger[contra_account_name],
            from_=contra_account_name,
            to_=linked_account_name,
        )
        for linked_account_name, contra_account_name in subset(
            ledger, netting, regular_cls
        )
    ]


def transfer_entry(account: Account, from_: AccountName, to_: AccountName):
    amount = account.balance()
    if isinstance(account, ClosableAccount):
        cls = account.closing_entry_constructor
    else:
        raise TypeError(account)
    if isinstance(account, DebitAccount):
        return cls(dr=to_, cr=from_, amount=amount)
    elif isinstance(account, CreditAccount):
        return cls(dr=from_, cr=to_, amount=amount)
    raise TypeError(account)


def closing_entries_for_temporary_contra_accounts(
    ledger: Ledger, netting: Netting
) -> List[CloseContraExpense | CloseContraIncome]:
    def f(t):
        return close_contra_accounts(ledger, netting, t)

    return f(Income) + f(Expense)


def closing_entries_for_permanent_contra_accounts(
    ledger: Ledger, netting: Netting
) -> List[CloseContraAsset | CloseContraCapital | CloseContraLiability]:
    def f(t):
        return close_contra_accounts(ledger, netting, t)

    return f(Asset) + f(Capital) + f(Liability)


def close_income_to_isa(ledger: Ledger) -> List[ClosingEntry]:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    return [
        transfer_entry(account, name, isa)
        for name, account in ledger.subset(Income).items()
    ]


def close_expense_to_isa(ledger: Ledger) -> List[ClosingEntry]:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    return [
        transfer_entry(account, name, isa)
        for name, account in ledger.subset(Expense).items()
    ]


def closing_entry_isa_to_retained_earnings(
    ledger: "Ledger",
) -> ClosingEntry:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    re = ledger.find_account_name(RetainedEarnings)
    return transfer_entry(ledger[isa], isa, re)


def closing_entries(ledger: Ledger, netting: Netting) -> List:  # List[ClosingEntry]
    """Return a list of closing entries that will:
    - close contra accounts related to income and expense;
    - close income and expense accounts to income summary account;
    - close income summary account to retained earnings.
    """
    # Close contra accounts associated with income and expense accounts
    es1 = closing_entries_for_temporary_contra_accounts(ledger, netting)
    # We should run actual postings to get the proper state of
    # income and expense accoutns after closing of related contra accounts.
    # This operation can be optimised later, maybe we do not need to process
    # all ledger, just related parts of it.
    _dummy_ledger = ledger.process_postings(list(es1))

    # At this point we can issue IncomeStatement as income and expense accounts
    # do have netted values and ContrIncome and ContraExpense accounts have zero
    # balance.

    # Next.we aggregate profit or loss at income summary account
    es2 = close_income_to_isa(_dummy_ledger)
    es3 = close_expense_to_isa(_dummy_ledger)
    # We have to process these entries to get actual state of income summary account.
    # Again, we are ru-running whole ledger here - much room for optimisation!
    _dummy_ledger = _dummy_ledger.process_postings(list(es2 + es3))  # type: ignore
    # Move balance of income summary account to retained earnings
    es4 = closing_entry_isa_to_retained_earnings(_dummy_ledger)
    # return a list of closing entriesthat can be
    # saved or serilised and re-run on a ledger later.
    return es1 + es2 + es3 + [es4]
