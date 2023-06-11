"""General ledger."""

from collections import UserDict
from typing import List, Tuple, Type

from abacus.accounting_types import AccountBalancesDict
from abacus.accounts import Account, Unique

from .accounting_types import (
    AbacusError,
    AccountName,
    BaseEntry,
    CreditEntry,
    DebitEntry,
    Entry,
    MultipleEntry,
)


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts and accounts can be referenced by name."""

    def safe_copy(self) -> "Ledger":
        return Ledger((k, account.safe_copy()) for k, account in self.items())

    def find_account_name(self, cls: Type[Unique]) -> AccountName:
        return find_account_name(self, cls)

    def subset(self, cls):
        return subset_by_class(self, cls)

    def balances(self):
        return balances(self)

    def process_postings(self, postings: List["Posting"]) -> "Ledger":
        return process_postings(self, postings)


def balances(ledger: Ledger) -> AccountBalancesDict:
    return AccountBalancesDict(
        {account_name: account.balance() for account_name, account in ledger.items()}
    )


def subset_by_class(ledger: Ledger, cls: Type):
    return Ledger(
        (account_name, account)
        for account_name, account in ledger.items()
        if isinstance(account, cls)
    )


def find_account_name(ledger: Ledger, cls: Type[Unique]) -> AccountName:
    """In ledger there should be just one of IncomeSummaryAccount and one of RetainedEarnings,
    this is a helper function to find out these account names.
    """
    account_names = list(subset_by_class(ledger, cls).keys())
    if len(account_names) == 1:
        return account_names[0]
    raise AbacusError(f"{cls} must be unique in ledger")


Posting = BaseEntry | Entry | MultipleEntry | DebitEntry | CreditEntry


def _process(ledger: Ledger, posting: Posting) -> Ledger:
    match posting:
        case MultipleEntry(_, _):
            for e in posting.entries():
                ledger = _process(ledger, e)
        case DebitEntry(dr, amount):
            ledger[dr].debits.append(amount)
        case CreditEntry(cr, amount):
            ledger[cr].credits.append(amount)
        case Entry(dr, cr, amount):
            ledger[dr].debits.append(amount)
            ledger[cr].credits.append(amount)
        case BaseEntry(dr, cr, amount, _):
            ledger[dr].debits.append(amount)
            ledger[cr].credits.append(amount)
        case _:
            raise AbacusError(f"{posting} type unknown.")
    return ledger


def safe_process_postings(
    ledger: Ledger, postings: List[Posting]
) -> Tuple[Ledger, List[Posting]]:
    _ledger = ledger.safe_copy()
    _failed = []
    for posting in postings:
        try:
            _ledger = _process(_ledger, posting)
        except KeyError:
            _failed.append(posting)
    return _ledger, _failed


def process_postings(ledger: Ledger, postings: List[Posting]) -> Ledger:
    ledger, _failed_entries = safe_process_postings(ledger, postings)
    if _failed_entries:
        raise AbacusError(_failed_entries)
    return ledger
