"""General ledger."""

from collections import UserDict
from typing import List, Tuple, Type

from abacus.accounting_types import AccountBalancesDict, Netting
from abacus.closing_types import ClosingEntry
from abacus.accounts import Account, Unique, RegularAccount, CreditAccount, DebitAccount
from dataclasses import dataclass

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


@dataclass
class LedgerWithNetting:
    ledger: Ledger
    netting: Netting

    def contra_account_pairs(
        self, regular_cls: Type[RegularAccount]
    ) -> List[Tuple[AccountName, AccountName]]:
        """Yield link account and contra account name pairs.
        Linked account is of type *regular_cls*.
        """
        return [
            (linked_account_name, contra_account_name)
            for linked_account_name, contra_account_names in self.netting.items()
            for contra_account_name in contra_account_names
            if isinstance(self.ledger[linked_account_name], regular_cls)
        ]

    def contra_account_closing_entries(self, regular_cls: Type[RegularAccount]):
        return [
            transfer_balance(
                self.ledger[contra_account_name],
                contra_account_name,
                linked_account_name,
            )
            for linked_account_name, contra_account_name in self.contra_account_pairs(
                regular_cls
            )
        ]


def transfer_balance(
    account, from_: AccountName, to_: AccountName
) -> ClosingEntry:
    amount = account.balance()
    if account.is_debit_account():
        return ClosingEntry(dr=to_, cr=from_, amount=amount)
    elif account.is_credit_account():
        return ClosingEntry(dr=from_, cr=to_, amount=amount)
    raise TypeError(account)


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
