"""Baisc data types used across package."""

from dataclasses import dataclass

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


def nonzero(self):
    return {k: v for k, v in self.items() if v}


def total(self) -> Amount:
    return sum(self.values())
