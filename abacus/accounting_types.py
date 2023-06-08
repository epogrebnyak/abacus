"""
Base classes for a minimal accounting framework.
"""

# pylint: disable=no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from pydantic.dataclasses import dataclass

Amount = int
AccountName = str

__all__ = ["Entry", "AbacusError"]


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

    def coerce(self, cls):
        """Change type of entry."""
        return cls(**self.__dict__)


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
class PostClose(BaseEntry):
    action: str = "post_close"
