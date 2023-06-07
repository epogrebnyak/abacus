"""Journal of entries and general ledger."""

from collections import UserDict
from typing import List, Tuple, Type


from abacus.accounts import (
    Account,
    Asset,
    Capital,
    Expense,
    Income,
    Liability,
    Unique,
    OpenAccount,
)

from .accounting_types import AbacusError, AccountName, BaseEntry, Entry


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts."""

    @classmethod
    def from_stream(cls, stream: List[OpenAccount]):
        return Ledger((a.name, a.new()) for a in stream)

    def safe_copy(self) -> "Ledger":
        return Ledger((k, account.safe_copy()) for k, account in self.items())

    def find_account_name(self, cls: Type[Unique]) -> AccountName:
        return find_account_name(self, cls)

    def subset(self, cls):
        return subset_by_class(self, cls)

    def process_postings(self, postings: List["Posting"]) -> "Ledger":
        return process_postings(self, postings)


def subset_by_class(ledger, cls):
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


def assets(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Asset)


def expenses(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Expense)


def capital(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Capital)


def liabilities(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Liability)


def income(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Income)


AccountType = str


Posting = BaseEntry | Entry


def check_not_exists(ledger, account_name):
    if account_name in ledger.keys():
        raise AbacusError("Cannot open: account {account_name} already exists.")


def _process(ledger: Ledger, posting: Posting) -> Ledger:
    match posting:
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
