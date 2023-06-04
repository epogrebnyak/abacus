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
class Entry:
    """Double entry with amount, account names to be debited (dr)
    and account name to be credited (cr)."""

    dr: AccountName
    cr: AccountName
    amount: Amount


# not used
@dataclass
class Saldo:
    account_type: str
    balance: Amount


@dataclass
class BaseEntry(Entry):
    """Represent various types of entries and serialisable."""

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
