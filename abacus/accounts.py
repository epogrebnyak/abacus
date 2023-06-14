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
from typing import List

from abacus.accounting_types import Amount
from abacus.closing_types import (
    CloseContraAsset,
    CloseContraCapital,
    CloseContraExpense,
    CloseContraIncome,
    CloseContraLiability,
    CloseExpense,
    CloseIncome,
    CloseISA,
    ClosingEntry,
)

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


class ClosableAccount:
    closing_entry_constructor = ClosingEntry


class ContraAccount(ClosableAccount):
    pass


class ContraAsset(CreditAccount, ContraAccount):
    closing_entry_constructor = CloseContraAsset


class ContraExpense(CreditAccount, ContraAccount):
    closing_entry_constructor = CloseContraExpense


class ContraCapital(DebitAccount, ContraAccount):
    closing_entry_constructor = CloseContraCapital


class ContraLiability(DebitAccount, ContraAccount):
    closing_entry_constructor = CloseContraLiability


class ContraIncome(DebitAccount, ContraAccount):
    closing_entry_constructor = CloseContraIncome


class RegularAccount:
    contra_account_constructor = ContraAccount


class Asset(DebitAccount, RegularAccount):
    contra_account_constructor = ContraAsset


class Expense(DebitAccount, RegularAccount, ClosableAccount):
    closing_entry_constructor = CloseExpense
    contra_account_constructor = ContraExpense


class Capital(CreditAccount, RegularAccount):
    contra_account_constructor = ContraCapital


class Liability(CreditAccount, RegularAccount):
    contra_account_constructor = ContraLiability


class Income(CreditAccount, RegularAccount, ClosableAccount):
    closing_entry_constructor = CloseIncome
    contra_account_constructor = ContraIncome


class Unique:
    """There should be just one account of this class in any ledger.
    `IncomeSummaryAccount` and `RetainedEarnings` are unique.
    """


class IncomeSummaryAccount(CreditAccount, Unique, ClosableAccount):
    closing_entry_constructor = CloseISA


class RetainedEarnings(Capital, Unique):
    pass


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
