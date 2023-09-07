"""Classes to different types of accounts, all based on TAccount."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List
import re

from engine.base import AccountName, Amount, Entry


@dataclass
class TAccount(ABC):
    """Parent class for T-account with debits and credits."""

    debits: List[Amount] = field(default_factory=list)
    credits: List[Amount] = field(default_factory=list)

    @abstractmethod
    def balance(self) -> Amount:
        """Return account balance."""

    def debit(self, amount: Amount):
        """Append *amount* to debit side of the account."""
        self.debits.append(amount)
        return self

    def credit(self, amount: Amount):
        """Append *amount* to credit side of the account."""
        self.credits.append(amount)
        return self

    def deep_copy(self):
        """Replicate this account as new data structure."""
        return self.__class__(self.debits.copy(), self.credits.copy())

    def condense(self):
        """Create a new account of the same type with only one value as account balance."""
        return self.empty().topup(self.balance())

    def empty(self):
        """Create a new empty account of the same type."""
        return self.__class__()

    def topup(self, balance):
        """Add balance to a proper side of account."""
        match self:
            case DebitAccount(_, _):
                return self.debit(balance)
            case CreditAccount(_, _):
                return self.credit(balance)

    def split_on_caps(self) -> str:
        return " ".join(re.findall("[A-Z][^A-Z]*", self.__class__.__name__))


class DebitAccount(TAccount):
    def balance(self) -> Amount:
        return sum(self.debits) - sum(self.credits)


class CreditAccount(TAccount):
    def balance(self) -> Amount:
        return sum(self.credits) - sum(self.debits)


class Permanent:
    pass


class Temporary:
    pass


class RegularAccount(Permanent):
    pass


class Asset(DebitAccount, RegularAccount):
    pass


class Expense(DebitAccount, RegularAccount):
    pass


class Capital(CreditAccount, RegularAccount):
    pass


class Liability(CreditAccount, RegularAccount):
    pass


class Income(CreditAccount, RegularAccount):
    pass


class Unique:
    """There should be just one account of this class in any ledger.
    `IncomeSummaryAccount`,`RetainedEarnings` and `NullAccount` are unique.
    """


class Transferable(TAccount):
    def transfer(self, my_name: AccountName, dest_name: AccountName) -> Entry:
        """Make entry to transfer balances from account of named *my_name* to *dest_name* account.
        The entry will differ depending if *my_name* is debit or credit account."""
        amount = self.balance()
        match self:
            case DebitAccount(_, _):
                return Entry(dest_name, my_name, amount)
            case CreditAccount(_, _):
                return Entry(my_name, dest_name, amount)
            case _:
                raise TypeError


# Can equally be CreditAccount or DebitAccount, making it a ContraAccount
# keeps null at the bottom of trail balance, so it is less distracting.
class NullAccount(CreditAccount, Unique, Temporary):
    pass


class IncomeSummaryAccount(CreditAccount, Unique, Transferable, Temporary):
    pass


class RetainedEarnings(Capital, Unique):
    pass


class ContraAccount(Transferable):
    pass


class ContraAsset(CreditAccount, ContraAccount, Permanent):
    pass


class ContraExpense(CreditAccount, ContraAccount, Temporary):
    pass


class ContraCapital(DebitAccount, ContraAccount, Permanent):
    pass


class ContraLiability(DebitAccount, ContraAccount, Permanent):
    pass


class ContraIncome(DebitAccount, ContraAccount, Temporary):
    pass


def mapping():
    """Relate Chart class attributes (keys) to actual classes (values)."""
    return dict(
        assets=(Asset, ContraAsset),
        expenses=(Expense, ContraExpense),
        equity=(Capital, ContraCapital),
        liabilities=(Liability, ContraLiability),
        income=(Income, ContraIncome),
    ).items()
