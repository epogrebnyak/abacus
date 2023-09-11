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


"""Pair of debit and credit account names."""
Pair = Tuple[AccountName, AccountName]


@dataclass
class NamedEntry:
    operation: str
    amount: Amount

    def to_entry(self, operation_dict: dict[str, Pair]) -> Entry:
        dr, cr = operation_dict[self.operation]
        return Entry(dr, cr, self.amount)


def sum_second(xs):
    return sum(x for _, x in xs)


@dataclass
class MultipleEntry:
    debit_entries: list[tuple[AccountName, Amount]]
    credit_entries: list[tuple[AccountName, Amount]]

    def __post_init__(self):
        self.validate()

    def validate(self):
        if sum_second(self.debit_entries) != sum_second(self.credit_entries):
            raise AbacusError(["Invalid multiple entry", self])
        return self

    def entries(self, null_account_name: AccountName):
        return [
            Entry(account_name, null_account_name, amount)
            for (account_name, amount) in self.debit_entries
        ] + [
            Entry(null_account_name, account_name, amount)
            for (account_name, amount) in self.credit_entries
        ]
