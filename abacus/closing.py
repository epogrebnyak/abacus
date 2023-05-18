"""Closing accounts at period end"""

from typing import List

from .accounting_types import AccountName, Entry, Posting, RenameAccount
from .accounts import Asset, Capital, Expense, Income, IncomeSummaryAccount, Liability
from .ledger import Ledger, expenses, income, subset_by_class

__all__ = []  # type: ignore


def closing_entries_for_contra_accounts(ledger: Ledger, peer_class):
    # find all contra accounts to close
    for peer_account_name, account in subset_by_class(ledger, peer_class).items():
        if n := account.netting:
            for contra_account_name in n.contra_accounts:
                entry = ledger[contra_account_name].transfer_balance(
                    contra_account_name, peer_account_name
                )
                yield entry
    # rename accounts
    for peer_account_name, account in subset_by_class(ledger, peer_class).items():
        if account.netting:
            yield RenameAccount(peer_account_name, account.netting.target_name)


def closing_entries_for_temporary_contra_accounts(ledger) -> List[Posting]:
    return [
        p
        for cls in (Income, Expense)
        for p in closing_entries_for_contra_accounts(ledger, cls)
    ]


def closing_entries_for_permanent_contra_accounts(ledger) -> List[Posting]:
    return [
        p
        for cls in (Asset, Capital, Liability)
        for p in closing_entries_for_contra_accounts(ledger, cls)
    ]


def find_account_name(ledger: Ledger, cls) -> AccountName:
    """In ledger there should be just one of IncomeSummaryAccount,
    this is a helper function to find it.
    """
    cs = list(subset_by_class(ledger, cls).keys())
    if len(cs) == 1:
        return cs[0]
    raise ValueError(cls)


def closing_entries_income_and_expense_to_isa(ledger) -> List[Entry]:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    es1 = [
        account.transfer_balance(name, isa) for name, account in income(ledger).items()
    ]

    es2 = [
        account.transfer_balance(name, isa)
        for name, account in expenses(ledger).items()
    ]
    return es1 + es2


def closing_entry_isa_to_retained_earnings(ledger, re) -> Entry:
    isa = find_account_name(ledger, IncomeSummaryAccount)
    return ledger[isa].transfer_balance(isa, re)


def closing_entries(
    ledger: Ledger, retained_earnings_account_name: AccountName
) -> List[Posting]:
    es1 = closing_entries_for_temporary_contra_accounts(ledger)
    _dummy_ledger = ledger.process_entries(es1)
    # at this point "sales" can be renamed tp "net_sales"
    es2 = closing_entries_income_and_expense_to_isa(_dummy_ledger)
    _dummy_ledger = _dummy_ledger.process_entries(es2)
    # at this pont we have profit value at isa
    es3 = [
        closing_entry_isa_to_retained_earnings(
            _dummy_ledger, retained_earnings_account_name
        )
    ]
    return es1 + es2 + es3  # type: ignore


def close(ledger: Ledger, retained_earnings_account_name: AccountName) -> Ledger:
    return ledger.process_entries(
        closing_entries(ledger, retained_earnings_account_name)
    )


def reports(ledger: Ledger, retained_earnings_account_name: AccountName):
    pass
