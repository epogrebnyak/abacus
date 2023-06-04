"""
Base classes for a minimal accounting framework.
"""

# pylint: disable=no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name


from enum import Enum

from pydantic.dataclasses import dataclass

Amount = int
AccountName = str
AccountType = str

__all__ = ["Entry", "OpenAccount", "Mark"]


class AbacusError(Exception):
    pass


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


@dataclass
class Entry:
    """Double entry with amount, account names to be debited (dr)
    and account name to be credited (cr)."""

    dr: AccountName
    cr: AccountName
    amount: Amount


@dataclass
class BaseEntry(Entry):
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


class Event(str, Enum):
    IssueIncomeStatement = "issue_income_statement"


@dataclass
class Mark:
    event: Event

class ClosingEntry:
    pass

@dataclass
class CloseIncome(BaseEntry, ClosingEntry):
    action: str = "close_income"


@dataclass
class CloseExpense(BaseEntry, ClosingEntry):
    action: str = "close_expense"


@dataclass
class CloseISA(BaseEntry, ClosingEntry):
    action: str = "close_isa"


Posting = Entry | BaseEntry | Mark | OpenRegularAccount | OpenContraAccount
