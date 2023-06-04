"""Closing accounts at period end"""

from typing import List, Type

from abacus.accounts import (
    Asset,
    Capital,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RegularAccount,
    RetainedEarnings,
    get_contra_account_type,
)
from abacus.closing_types import (
    CloseContra,
    CloseExpense,
    CloseIncome,
    CloseISA,
    get_closing_entry_type,
)
from abacus.ledger import Ledger

__all__ = ["closing_entries"]  # type: ignore


def closing_entries_contra_accounts(
    ledger: "Ledger", regular_cls: Type[RegularAccount]
) -> List[CloseContra]:
    from abacus.ledger import subset_by_class

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
    f = closing_entries_contra_income
    g = closing_entries_contra_expense
    return f(ledger) + g(ledger)


def closing_entries_for_permanent_contra_accounts(
    ledger,
) -> List:
    def f(t):
        return closing_entries_contra_accounts(ledger, t)

    return f(Asset) + f(Capital) + f(Liability)


def closing_entries_income_to_isa(ledger) -> List[CloseIncome]:
    from abacus.ledger import income

    isa = ledger.find_account_name(IncomeSummaryAccount)
    return [
        CloseIncome(*account.transfer_balance_entry(name, isa))
        for name, account in income(ledger).items()
    ]


def closing_entries_expenses_to_isa(ledger) -> List[CloseExpense]:
    from abacus.ledger import expenses

    isa = ledger.find_account_name(IncomeSummaryAccount)
    return [
        CloseExpense(*account.transfer_balance_entry(name, isa))
        for name, account in expenses(ledger).items()
    ]


def closing_entry_isa_to_retained_earnings(
    ledger: "Ledger",
) -> CloseISA:
    isa = ledger.find_account_name(IncomeSummaryAccount)
    re = ledger.find_account_name(RetainedEarnings)
    return CloseISA(*ledger[isa].transfer_balance_entry(isa, re))


def closing_entries(ledger: "Ledger") -> List:
    #     #     """Close contra accounts associated with income and expense accounts,
    #     #     aggregate profit or loss at income summary account
    #     #     and move balance of income summary account to retained earnings."""
    es1 = closing_entries_for_temporary_contra_accounts(ledger)
    _dummy_ledger = ledger.process_postings(es1)
    # At this point we can issue IncomeStatement
    es2 = closing_entries_expenses_to_isa(_dummy_ledger)
    es3 = closing_entries_income_to_isa(_dummy_ledger)
    _dummy_ledger = _dummy_ledger.process_postings(es2 + es3)  # type: ignore
    es4 = closing_entry_isa_to_retained_earnings(_dummy_ledger)
    return es1 + es2 + es3 + [es4]
