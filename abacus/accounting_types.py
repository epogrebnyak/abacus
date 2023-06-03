"""
Base classes for a minimal accounting framework.
"""

# pylint: disable=no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name


from enum import Enum

from pydantic.dataclasses import dataclass

Amount = int
AccountName = str


__all__ = ["Entry", "OpenAccount", "Mark"]


class AbacusError(Exception):
    pass


@dataclass
class OpenAccount:
    """Command to open regular or contra account in ledger."""

    account_name: AccountName
    account_type: str
    starting_balance: Amount = 0
    link: AccountName | None = None


@dataclass
class Entry:
    """Double entry with amount, account names to be debited (dr)
    and account name to be credited (cr)."""

    dr: AccountName
    cr: AccountName
    amount: Amount


class Event(str, Enum):
    IssueIncomeStatement = "issue_income_statement"


@dataclass
class Mark:
    event: Event


Posting = Entry | Mark | OpenAccount
