"""
Base classes for a minimal accounting framework.
"""

from typing import Dict

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

__all__ = ["Entry", "AbacusError"]

Amount = int
AccountName = str
Netting = dict[AccountName, list[AccountName]]
Balances = Dict[AccountName, Amount]
AccountBalancesDict = Dict[AccountName, Amount]


class Operation(BaseModel):
    debit: AccountName
    credit: AccountName
    description: str = ""
    requires: AccountName | None = None


def total(dict_) -> Amount:
    return sum(dict_.values())


class AbacusError(Exception):
    pass


@dataclass
class SingleEntry:
    pass


@dataclass
class DebitEntry(SingleEntry):
    dr: AccountName
    amount: Amount


@dataclass
class CreditEntry(SingleEntry):
    cr: AccountName
    amount: Amount


def amount_sum(entries):
    return sum(e[1] for e in entries)


@dataclass
class MultipleEntry:
    debit_entries: list[tuple[AccountName, Amount]]
    credit_entries: list[tuple[AccountName, Amount]]

    def entries(self):
        for d in self.debit_entries:
            yield DebitEntry(*d)
        for c in self.credit_entries:
            yield CreditEntry(*c)

    def match_amounts(self):  # should be post-init method
        if amount_sum(self.debit_entries) != amount_sum(self.credit_entries):
            raise AbacusError(["Invalid multiple entry", self])


@dataclass
class Entry:
    """Double entry with amount, account names to be debited (dr)
    and account name to be credited (cr)."""

    dr: AccountName
    cr: AccountName
    amount: Amount


@dataclass
class ClosingEntry(Entry):
    pass


@dataclass
class BaseEntry(Entry):
    """Represent various types of entries and serializable."""

    action: str


@dataclass
class BusinessEntry(BaseEntry):
    action: str = "post"


@dataclass
class AdjustmentEntry(BaseEntry):
    action: str = "adjust"


@dataclass
class PostCloseEntry(BaseEntry):
    action: str = "after_close"
