"""Closing accounts at period end"""

from typing import List, Type

from .accounting_types import AccountName, Entry, Posting, RenameAccount
from .accounts import (
    Asset,
    Capital,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RegularAccount,
    RetainedEarnings,
    Unique,
)
from .ledger import Ledger, expenses, income, subset_by_class

__all__ = ["close"]  # type: ignore


def closing_entries_for_contra_accounts(
    ledger: Ledger, classes: List[Type[RegularAccount]]
):
    # find all contra accounts to close related to *classes*
    # (where *cls* is a parent to contra account)
    gen = list(
        (name, account)
        for cls in classes
        for name, account in subset_by_class(ledger, cls).items()
        if account.netting
    )
    # first, close contra account balances
    for account_name, account in gen:
        for contra_account_name in account.netting.contra_accounts:
            yield ledger[contra_account_name].transfer_balance(
                contra_account_name, account_name
            )
    # second, rename parent accounts (eg 'sales' -> 'net_sales', cannot rename until first step is finished)
    for account_name, account in gen:
        yield RenameAccount(account_name, account.netting.target_name)


def closing_entries_for_temporary_contra_accounts(ledger) -> List[Posting]:
    return list(closing_entries_for_contra_accounts(ledger, classes=[Income, Expense]))


def closing_entries_for_permanent_contra_accounts(ledger) -> List[Posting]:
    return list(
        closing_entries_for_contra_accounts(ledger, classes=[Asset, Capital, Liability])
    )


def find_account_name(ledger: Ledger, cls: Type[Unique]) -> AccountName:
    """In ledger there should be just one of IncomeSummaryAccount and and one of RetainedEarnings,
    this is a helper function to these account names.
    """
    account_names = list(subset_by_class(ledger, cls).keys())
    if len(account_names) == 1:
        return account_names[0]
    raise ValueError(cls)


def closing_entries_income_and_expense_to_isa(ledger) -> List[Posting]:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    res: List[Posting] = []
    for filter_with in (income, expenses):
        for name, account in filter_with(ledger).items():
            res.append(account.transfer_balance(name, isa))
    return res


def closing_entry_isa_to_retained_earnings(ledger: Ledger) -> Entry:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    re = find_account_name(ledger, RetainedEarnings)
    return ledger[isa].transfer_balance(isa, re)


def closing_entries(ledger: Ledger) -> List[Posting]:
    es1 = closing_entries_for_temporary_contra_accounts(ledger)
    _dummy_ledger = ledger.process_entries(es1)
    es2 = closing_entries_income_and_expense_to_isa(_dummy_ledger)
    _dummy_ledger = _dummy_ledger.process_entries(es2)
    # at this point we have profit value at isa
    es3 = closing_entry_isa_to_retained_earnings(_dummy_ledger)
    return es1 + es2 + [es3]


def close(ledger: Ledger) -> Ledger:
    """Close ledger to *retained_earnings_account_name*."""
    return ledger.process_entries(closing_entries(ledger))
