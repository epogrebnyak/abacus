"""Account classes.

## Regular accounts (`RegularAccount`)

- Permanent accounts are `Asset`, `Capital` and `Liability`.
- `RetainedEarnings` is a subclass of `Capital` account. 
- Income summary account is `IncomeSummaryAccount`.
- There must be exactly one `RetainedEarnings` 
  and one `IncomeSummaryAccount` account in a ledger.
- Temporary accounts `Income` and `Expense` are closed at period end.
  Their balances are transferred to `IncomeSummaryAccount`.
  `IncomeSummaryAccount` balance is transferred to  `RetainedEarnings`.

## Contra accounts (`ContraAccount`)
  
- `ContraIncome` and `ContraExpense` are closed before closing of 
  `Income` and `Expense`.
- `ContraAsset`, `ContraCapital` and `ContraLiability` are permanent,
   they are passed to next period. These accounts are netted for 
   balance sheet presentation.
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


class DebitAccount(Account):
    def balance(self) -> Amount:
        return sum(self.debits) - sum(self.credits)

    def is_debit_account(self):
        return True

    def is_credit_account(self):
        return False


class CreditAccount(Account):
    def balance(self) -> Amount:
        return sum(self.credits) - sum(self.debits)

    def is_debit_account(self):
        return False

    def is_credit_account(self):
        return True


class RegularAccount:
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
    `IncomeSummaryAccount` and `RetainedEarnings` are unique.
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
    # signature added for mypy
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
    """Return class constructor (eg `Expense`) given a string name (`'Expense'`)."""
    return all_accounts_dict[class_name]


def new(class_name: str) -> Account:
    """Construct empty `Account` subclass."""
    return get_class_constructor(class_name)()


# FIXME: maybe OpenAccount not needed as Chart can directly create to Ledger
#        can have Journal.chart as very simple representation of accounts
#        and Journal.empty_ledger() as make_ledger(self.chart)
@dataclass
class OpenAccount:
    """Command to open account in ledger."""

    name: AccountName
    type: str

    def new(self):
        return get_class_constructor(self.type)([], [])
