"""Closing accounts at period end"""

from typing import List, Type

from abacus.accounting_types import (
    AbacusError,
    AccountName,
    CloseExpense,
    CloseIncome,
    CloseISA,
    ClosingEntry,
)
from abacus.accounts import (
    Asset,
    Capital,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RegularAccount,
    RetainedEarnings,
    Unique,
    get_contra_account_type,
)
from abacus.closing_types import CloseContra, get_closing_entry_type
from abacus.ledger import Ledger, expenses, income, subset_by_class

__all__ = ["close"]  # type: ignore


def closing_entries_contra_accounts(
    ledger: Ledger, regular_cls: Type[RegularAccount]
) -> List[CloseContra]:
    cls = get_contra_account_type(regular_cls)
    constructor = get_closing_entry_type(regular_cls)
    return [
        constructor(*account.transfer_balance_entry(account_name, account.link))
        for account_name, account in subset_by_class(ledger, cls).items()
    ]


def closing_entries_contra_income(ledger):
    return closing_entries_contra_accounts(ledger, Income)


def closing_entries_contra_expense(ledger):
    return closing_entries_contra_accounts(ledger, Expense)


def closing_entries_for_temporary_contra_accounts(ledger):
    return closing_entries_contra_income(ledger) + closing_entries_contra_expense(
        ledger
    )


def closing_entries_for_permanent_contra_accounts(
    ledger,
) -> List:
    def f(t):
        return closing_entries_contra_accounts(ledger, t)

    return f(Asset) + f(Capital) + f(Liability)


def find_account_name(ledger: Ledger, cls: Type[Unique]) -> AccountName:
    """In ledger there should be just one of IncomeSummaryAccount and one of RetainedEarnings,
    this is a helper function to find out these account names.
    """
    account_names = list(subset_by_class(ledger, cls).keys())
    if len(account_names) == 1:
        return account_names[0]
    raise AbacusError(f"{cls} must be unique in ledger")


def closing_entries_income_to_isa(ledger) -> List[CloseIncome]:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    return [
        CloseIncome(*account.transfer_balance_entry(name, isa))
        for name, account in income(ledger).items()
    ]


def closing_entries_expenses_to_isa(ledger) -> List[CloseExpense]:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    return [
        CloseExpense(*account.transfer_balance_entry(name, isa))
        for name, account in expenses(ledger).items()
    ]


def closing_entry_isa_to_retained_earnings(
    ledger: Ledger,
) -> CloseISA:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    re = find_account_name(ledger, RetainedEarnings)
    return CloseISA(*ledger[isa].transfer_balance_entry(isa, re))


def closing_entries(ledger: Ledger) -> List:
    es1 = closing_entries_for_temporary_contra_accounts(ledger)
    _dummy_ledger = ledger.process_entries(es1)
    # At this point we can issue IncomeStatement
    es2 = closing_entries_expenses_to_isa(_dummy_ledger)
    es3 = closing_entries_income_to_isa(_dummy_ledger)
    _dummy_ledger = _dummy_ledger.process_entries(es2 + es3)
    es4 = closing_entry_isa_to_retained_earnings(_dummy_ledger)
    return es1 + es2 + es3 + [es4]


def close(ledger: Ledger) -> Ledger:
    """Close ledger to *retained_earnings_account_name*."""
    return ledger.process_entries(closing_entries(ledger))
