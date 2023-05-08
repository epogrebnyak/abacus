# Next:
# close_contra_accounts(ledger, cls) - closes all contraccounts related to cls
# close_income(ledger) nets income-related contraccounts
# close_expense(ledger) nets expense-related contraccounts (maybe there are none)
# close_isa(ledger, retained_earnings_account_name) moves income and expense to isa
# and closes isa to retained earnings (this keeps track of entries in isa)
# income statement (net values) produced here
# close all other contra_accounts (depreciation)

from typing import List

from .accounting_types import AccountName, Entry
from .accounts import IncomeSummaryAccount
from .ledger import Ledger, expenses, income, process_entries, subset_by_class
from .reports import balances


def find_account_name(ledger: Ledger, cls) -> AccountName:
    """In ledger there should be just one of IncomeSummaryAccount,
    this is a helper function to find it.
    """
    cs = list(subset_by_class(ledger, cls).keys())
    if len(cs) == 1:
        return cs[0]
    raise ValueError(cls)


def closing_entries_for_income_accounts(ledger) -> List[Entry]:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    return [
        Entry(
            amount=amount,
            dr=account_name,
            cr=isa,
        )
        for account_name, amount in balances(income(ledger)).items()
    ]


def closing_entries_for_expense_accounts(ledger) -> List[Entry]:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    return [
        Entry(
            amount=amount,
            dr=isa,
            cr=account_name,
        )
        for account_name, amount in balances(expenses(ledger)).items()
    ]


def closing_entries(
    ledger: Ledger, retained_earnings_account_name: AccountName
) -> List[Entry]:
    # fmt: off
    entries = closing_entries_for_income_accounts(ledger) \
            + closing_entries_for_expense_accounts(ledger)
    # fmt: on

    # We actually process the closing to find out the profit.
    # Alternative is to use amount = current_profit(ledger).
    # process_entries() was altering ledger before proper
    # coping was introduced with .safe_copy() methods
    # in Legder and Account classes.
    _dummy_ledger = process_entries(ledger, entries)
    isa = find_account_name(ledger, IncomeSummaryAccount)
    amount = _dummy_ledger[isa].balance()

    return entries + [
        Entry(
            amount=amount,
            cr=retained_earnings_account_name,
            dr=isa,
        )
    ]


def close(ledger: Ledger, retained_earnings_account_name: AccountName) -> Ledger:
    entries = closing_entries(ledger, retained_earnings_account_name)
    return process_entries(ledger, entries)
