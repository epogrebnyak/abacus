"""Journal of entries and general ledger."""

from collections import UserDict
from typing import List, Tuple, Type

from pydantic.dataclasses import dataclass

from abacus.accounting_types import Amount
from abacus.accounts import Account, Asset, Capital, Expense, Income, Liability, Unique

from .accounting_types import AbacusError, AccountName, BaseEntry, Entry


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts."""

    def safe_copy(self) -> "Ledger":
        return Ledger((k, account.safe_copy()) for k, account in self.items())

    def process_entries(self, entries) -> "Ledger":
        return process_postings(self, entries)

    def process_entry(self, dr, cr, amount) -> "Ledger":
        return process_postings(self, [Entry(dr, cr, amount)])

    def close(self) -> "Ledger":
        """Close contraaccounts associated with income and expense accounts,
        aggregate profit or loss at income summary account
        and move balance of income summary account to retained earnings."""
        from .closing import close

        return close(self)

    def balances(self):
        from .reports import balances

        return balances(self)

    def _balance_sheet(self):
        from .reports import balance_sheet

        return balance_sheet(self)

    def find_account_name(self, cls: Type[Unique]) -> AccountName:
        return find_account_name(self, cls)


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


@dataclass
class OpenRegularAccount:
    """Command to open regular account in ledger."""

    name: AccountName
    type: AccountType
    balance: Amount


@dataclass
class OpenContraAccount:
    """Command to open contra account in ledger."""

    name: AccountName
    type: AccountType
    balance: Amount
    link: AccountName


Posting = OpenRegularAccount | OpenContraAccount | BaseEntry | Entry


def check_not_exists(ledger, account_name):
    if account_name in ledger.keys():
        raise AbacusError("Cannot open: account {account_name} already exists.")


def _process(ledger: Ledger, posting: Posting) -> Ledger:
    from abacus.accounts import get_class_constructor

    match posting:
        case OpenContraAccount(account_name, cls_string, amount, link):
            check_not_exists(ledger, account_name)
            cls = get_class_constructor(cls_string)
            ledger[account_name] = cls(link=link).start(amount)
        case OpenRegularAccount(account_name, cls_string, amount):
            check_not_exists(ledger, account_name)
            cls = get_class_constructor(cls_string)
            ledger[account_name] = cls().start(amount)
        case Entry(dr, cr, amount):
            ledger[dr].debits.append(amount)
            ledger[cr].credits.append(amount)
        case BaseEntry(dr, cr, amount, _):
            ledger[dr].debits.append(amount)
            ledger[cr].credits.append(amount)
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
