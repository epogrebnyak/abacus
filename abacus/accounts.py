"""Account classes.

- Permanent accounts: `Asset`, `Capital` and `Liability`.
- `RetainedEarnings` is a subclass of `Capital` account. 
- Temporary accounts that are closed at period end: `Income` and `Expense`.
- Contra accounts: `ContraAsset`, `ContraExpense`, `ContraCapital`, 
  `ContraLiability`, and `ContraIncome`. 
- Income summary account: `IncomeSummaryAccount`.
- There must be exactly one `RetainedEarnings` and one `IncomeSummaryAccount` account in a ledger.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Type

from abacus.accounting_types import AccountName, Amount

__all__ = ["Account"]


# Experimental, cannot blend to Account, may remove
class SafeCopy(ABC):
    @abstractmethod
    def safe_copy(self):
        pass


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

    def debit(self, amount: Amount):
        """Append *amount* to debit side of account."""
        self.debits.append(amount)

    def credit(self, amount: Amount):
        """Append *amount* to credit side of account."""
        self.credits.append(amount)

    def safe_copy(self):
        return self.__class__(self.debits.copy(), self.credits.copy())


class RegularAccount:
    pass


class DebitAccount(Account):
    def balance(self) -> Amount:
        return sum(self.debits) - sum(self.credits)


class CreditAccount(Account):
    def balance(self) -> Amount:
        return sum(self.credits) - sum(self.debits)


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
    IncomeSummaryAccount and RetainedEarnings are unique.
    """


class IncomeSummaryAccount(CreditAccount, Unique):
    pass


class RetainedEarnings(Capital, Unique):
    pass


class ContraAccount:
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
    # long signature for mypy
    mapping: Dict[Type[RegularAccount], Type[ContraAccount]] = dict(
        [
            (Asset, ContraAsset),
            (Expense, ContraExpense),
            (Capital, ContraCapital),
            (Liability, ContraLiability),
            (Income, ContraIncome),
        ]
    )
    return mapping[cls]


all_account_classes = (
    Asset,
    ContraAsset,
    Expense,
    ContraExpense,
    Capital,
    ContraCapital,
    Liability,
    ContraLiability,
    Income,
    ContraIncome,
    IncomeSummaryAccount,
    RetainedEarnings,
)

all_accounts_dict = {cls.__name__: cls for cls in all_account_classes}


def get_class_constructor(class_name: str) -> Type:
    return all_accounts_dict[class_name]


@dataclass
class OpenAccount:
    """Command to open account in ledger."""

    name: AccountName
    type: str

    def new(self):
        return get_class_constructor(self.type)([], [])
