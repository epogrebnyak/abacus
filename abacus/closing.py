"""Closing accounts at period end"""

from typing import List, Type

from .accounting_types import (
    AccountName,
    ClosingEntry,
    CloseTempContraAccounts,
    ClosePermContraAccounts,
    CloseIncome,
    CloseExpense,
    CloseISA,
)
from .accounts import (
    Asset,
    Capital,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RetainedEarnings,
    Unique,
    get_contra_account_type,
)
from .ledger import Ledger, expenses, income, subset_by_class

__all__ = ["close"]  # type: ignore


def contra_accounts_closing_entries(
    ledger: Ledger, regular_cls: Type, constructor_class: ClosingEntry
):
    cls = get_contra_account_type(regular_cls)
    return [
        account.transfer_balance(account_name, account.link, constructor_class)
        for account_name, account in subset_by_class(ledger, cls).items()
    ]


def closing_entries_for_temporary_contra_accounts(
    ledger,
) -> List[CloseTempContraAccounts]:
    def f(t):
        return contra_accounts_closing_entries(ledger, t, CloseTempContraAccounts)

    return f(Income) + f(Expense)


def closing_entries_for_permanent_contra_accounts(
    ledger,
) -> List[ClosePermContraAccounts]:
    def f(t):
        return contra_accounts_closing_entries(ledger, t, ClosePermContraAccounts)

    return f(Asset) + f(Capital) + f(Liability)


def find_account_name(ledger: Ledger, cls: Type[Unique]) -> AccountName:
    """In ledger there should be just one of IncomeSummaryAccount and one of RetainedEarnings,
    this is a helper function to find out these account names.
    """
    account_names = list(subset_by_class(ledger, cls).keys())
    if len(account_names) == 1:
        return account_names[0]
    raise ValueError(cls)


def closing_entries_income_and_expense_to_isa(
    ledger,
) -> List[CloseIncome | CloseExpense]:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    a = [
        account.transfer_balance(name, isa, CloseExpense)
        for name, account in expenses(ledger).items()
    ]
    b = [
        account.transfer_balance(name, isa, CloseIncome)
        for name, account in income(ledger).items()
    ]
    return a + b


def closing_entry_isa_to_retained_earnings(
    ledger: Ledger,
) -> CloseISA:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    re = find_account_name(ledger, RetainedEarnings)
    return ledger[isa].transfer_balance(isa, re, CloseISA)


def closing_entries(ledger: Ledger) -> List[ClosingEntry]:
    es1 = closing_entries_for_temporary_contra_accounts(ledger)
    _dummy_ledger = ledger.process_entries(es1)
    # At this point we can issue IncomeStatement
    es2 = closing_entries_income_and_expense_to_isa(_dummy_ledger)
    _dummy_ledger = _dummy_ledger.process_entries(es2)
    es3 = closing_entry_isa_to_retained_earnings(_dummy_ledger)
    return es1 + es2 + [es3]


def close(ledger: Ledger) -> Ledger:
    """Close ledger to *retained_earnings_account_name*."""
    return ledger.process_entries(closing_entries(ledger))
