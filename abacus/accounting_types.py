"""
Classes for a minimal accounting framework.
"""

# pylint: disable=no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from collections import UserDict
from dataclasses import dataclass
from typing import List, Tuple

Amount = int
AccountName = str


__all__ = ["Entry", "RenameAccount", "Shortcodes"]


class Posting:
    pass


@dataclass
class Entry(Posting):
    """Accounting entry with amount and account names to be debited (dr)
    and credited (cr)."""

    dr: AccountName
    cr: AccountName
    amount: Amount


@dataclass
class RenameAccount(Posting):
    """Command to rename an account in ledger. `existing_name` will be dropped from a ledger,
    `new_name` will be present in ledger.
    """

    existing_name: AccountName
    new_name: AccountName


@dataclass
class NamedEntry:
    opcode: str
    amount: Amount


"""Pair of debit and credit account names."""
Pair = Tuple[AccountName, AccountName]


class Shortcodes(UserDict[str, Pair]):
    """A dictionary that holds names of typical entry templates (pairs).
    Methods allow to convert `NamedEntry("pay_capital", 1000)` to
    `Entry("cash", "capital", 1000)` for a single entry or a list of entries.
    """

    def make_entry(self, named_entry: NamedEntry) -> Entry:
        dr, cr = self[named_entry.opcode]
        return Entry(dr, cr, named_entry.amount)

    def make_entries(self, named_entries: List[NamedEntry]):
        return [self.make_entry(ne) for ne in named_entries]


@dataclass
class _Saldo:
    """Account name and balance.

    Note: 'saldo' is balance in Italian."""

    account_name: AccountName
    balance: Amount
