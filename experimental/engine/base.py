"""Baisc data types used across package."""

from dataclasses import dataclass
from typing import Tuple

AccountName = str
Amount = int  # Can be changed to Decimal


@dataclass
class Entry:
    """Pure accounting entry (without title, date, etc.)."""

    debit: AccountName
    credit: AccountName
    amount: Amount


class AbacusError(Exception):
    """Custom error class."""


def nonzero(self: dict) -> dict[AccountName, Amount]:
    return {k: v for k, v in self.items() if v}


def total(self: dict) -> Amount:
    return sum(self.values())


"""Pair of debit and credit account names."""
Pair = Tuple[AccountName, AccountName]


@dataclass
class NamedEntry:
    operation: str
    amount: Amount

    def to_entry(self, operation_dict: dict[str, Pair]) -> Entry:
        dr, cr = operation_dict[self.operation]
        return Entry(dr, cr, self.amount)


@dataclass
class MultipleEntry:
    debit_entries: list[tuple[AccountName, Amount]]
    credit_entries: list[tuple[AccountName, Amount]]

    def __post_inti__(self):
        if sum(a for (_, a) in self.debit_entries) != sum(
            a for (_, a) in self.credit_entries
        ):
            raise AbacusError(["Invalid multiple entry", self])

    def entries(self, null_account_name: AccountName):
        return [
            Entry(account_name, null_account_name, amount)
            for (account_name, amount) in self.debit_entries
        ] + [
            Entry(null_account_name, account_name, amount)
            for (account_name, amount) in self.credit_entries
        ]
