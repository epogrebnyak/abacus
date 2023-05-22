"""T-account classes:

- permanent accounts: `Asset`, `Capital`, and `Liability` 
- temporary accounts that are closed at period end: `Income` and `Expense`
- contra accounts: `ContraAsset`, `ContraExpense`, `ContraCapital`, 
  `ContraLiability`, and `ContraIncome` 
- income summary account: `IncomeSummaryAccount`
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type

from abacus import Entry

from .accounting_types import AccountName, Amount

__all__ = ["Account"]


@dataclass
class Netting:
    contra_accounts: List[str]
    target_name: str

    def safe_copy(self):
        return self


# > Using ABCs states the programmer’s intent clearly
# > and thus makes the code more communicative.
# https://dbader.org/blog/abstract-base-classes-in-python
# https://docs.python.org/3/library/abc.html
@dataclass
class Account(ABC):
    debits: List[Amount] = field(default_factory=list)
    credits: List[Amount] = field(default_factory=list)

    @abstractmethod
    def balance(self) -> Amount:
        """Return account balance."""

    @abstractmethod
    def transfer_balance(
        self, this_account: AccountName, other_account: AccountName
    ) -> Entry:
        """Create an entry that will move balance of *this_account*
        to *other_account*. Used when closing accounts. The resulting entry
        differs by debit and credit accounts."""

    def debit(self, amount: Amount):
        """Append *amount* to debit side of account."""
        self.debits.append(amount)

    def credit(self, amount: Amount):
        """Append *amount* to credit side of account."""
        self.credits.append(amount)

    def safe_copy(self):
        return self.__class__(self.debits.copy(), self.credits.copy())


@dataclass
class RegularAccount(Account):
    # Netting indicates which contra accounts must net out with this account.
    netting: Optional[Netting] = None

    def safe_copy(self):
        netting = self.netting.safe_copy() if self.netting else None
        return self.__class__(self.debits.copy(), self.credits.copy(), netting)


class DebitAccount(Account):
    def balance(self) -> Amount:
        return sum(self.debits) - sum(self.credits)

    def transfer_balance(
        self, this_account: AccountName, other_account: AccountName
    ) -> Entry:
        return Entry(cr=this_account, dr=other_account, amount=self.balance())


class CreditAccount(Account):
    def balance(self) -> Amount:
        return sum(self.credits) - sum(self.debits)

    def transfer_balance(
        self, this_account: AccountName, other_account: AccountName
    ) -> Entry:
        return Entry(dr=this_account, cr=other_account, amount=self.balance())


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
    """There sould be just one account of this class in any ledger."""

    pass


class IncomeSummaryAccount(CreditAccount, Unique):
    pass


class RetainedEarnings(Capital, Unique):
    pass


class ContraAccount(Account):
    pass


class ContraAsset(CreditAccount, ContraAccount):
    pass


class ContraExpense(CreditAccount, ContraAccount):
    pass


class ContraCapital(DebitAccount, ContraAccount):
    pass


class ContraLiability(DebitAccount, ContraAccount):
    pass


class ContraIncome(DebitAccount, ContraAccount):
    pass


def get_contra_account_type(cls: Type[RegularAccount]) -> Type[ContraAccount]:
    # without this long signature we get typing error for get_contra_account_type()
    mapping: Dict[Type[Account], Type[ContraAccount]] = dict(
        [
            (Asset, ContraAsset),
            (Expense, ContraExpense),
            (Capital, ContraCapital),
            (Liability, ContraLiability),
            (Income, ContraIncome),
        ]
    )
    return mapping[cls]
