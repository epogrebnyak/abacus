"""Classes to different types of accounts, all based on TAccount.

Regular accounts (`RegularAccount`)

- Permanent accounts are `Asset`, `Capital` and `Liability`.
- `RetainedEarnings` is a subclass of `Capital` account. 
- Income summary account is `IncomeSummaryAccount`.
- There must be exactly one `RetainedEarnings` 
  and one `IncomeSummaryAccount` account in a ledger.
- Temporary accounts `Income` and `Expense` are closed at period end.
  Their balances are transferred to `IncomeSummaryAccount`.
  `IncomeSummaryAccount` balance is transferred to  `RetainedEarnings`.

Contra accounts (`ContraAccount`):
  
- `ContraIncome` and `ContraExpense` are closed before closing of 
  `Income` and `Expense`.
- `ContraAsset`, `ContraCapital` and `ContraLiability` are permanent,
   they are passed to next period. These accounts are netted for 
   balance sheet presentation.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Type

from abacus.engine.base import AbacusError, AccountName, Amount, Entry


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


class RegularAccountEnum(Enum):
    """Class for mapping account types to their names."""

    ASSET = "assets"
    LIABILITY = "liabilities"
    CAPITAL = "equity"
    INCOME = "income"
    EXPENSE = "expenses"

    def chart_attribute(self):
        # enum values are Chart attributes
        return self.value

    def singular(self):
        return self.name.lower()

    def qualified(self, account_name):
        return RegularName(self.name.lower(), account_name)

    @classmethod
    def from_flag(cls, string: str) -> "RegularAccountEnum":
        string = string.upper().strip()
        try:
            return RegularAccountEnum[string]
        except KeyError:
            raise AbacusError(f"Unknown account flag: {string}")

    @classmethod
    def from_class(cls, regular_cls: Type[RegularAccount]):
        return dict(
            asset=RegularAccountEnum.ASSET,
            liability=RegularAccountEnum.LIABILITY,
            capital=RegularAccountEnum.CAPITAL,
            income=RegularAccountEnum.INCOME,
            expense=RegularAccountEnum.EXPENSE,
        )[regular_cls.__name__.lower()]

    @classmethod
    def all(cls):
        return [item for item in RegularAccountEnum.__members__.values()]

    def cls(self):
        """Link account type enum to account class."""
        return dict(
            asset=Asset,
            liability=Liability,
            capital=Capital,
            income=Income,
            expense=Expense,
        )[self.name.lower()]

    def contra_class(self):
        """Link regular account type to its contra account type."""
        return dict(
            asset=ContraAsset,
            liability=ContraLiability,
            capital=ContraCapital,
            income=ContraIncome,
            expense=ContraExpense,
        )[self.name.lower()]


def regular_name(account_type, account_name):
    return f"{account_type.singular()}:{account_name}"


def contra_name(account_name, contra_account_name):
    return f"contra:{account_name}:{contra_account_name}"


def detect_prefix(prefix: str) -> RegularAccountEnum:
    prefix = prefix.lower()
    if prefix in ["asset", "assets"]:
        return RegularAccountEnum.ASSET
    elif prefix in ["liability", "liabilities"]:
        return RegularAccountEnum.LIABILITY
    elif prefix in ["capital", "equity"]:
        return RegularAccountEnum.CAPITAL
    elif prefix in ["expense", "expenses"]:
        return RegularAccountEnum.EXPENSE
    elif prefix in ["income"]:
        return RegularAccountEnum.INCOME
    else:
        raise AbacusError(f"Invalid account prefix: {prefix}")


@dataclass
class RegularName:
    account_name: str

    def qualified(self) -> str:
        return f"{self.klass.__name__.lower()}:{self.account_name}"  # type: ignore

    @classmethod
    def new(cls, prefix: str, account_name: str) -> "RegularName":
        prefix = prefix.lower()
        if prefix in ["asset", "assets"]:
            return AssetName(account_name)
        elif prefix in ["liability", "liabilities"]:
            return LiabilityName(account_name)
        elif prefix in ["capital", "equity"]:
            return CapitalName(account_name)
        elif prefix in ["expense", "expenses"]:
            return ExpenseName(account_name)
        elif prefix in ["income"]:
            return IncomeName(account_name)
        else:
            raise AbacusError(f"Invalid account prefix: {prefix}")


@dataclass
class AssetName(RegularName):
    klass: Type = Asset


class LiabilityName(RegularName):
    klass: Type = Liability


class CapitalName(RegularName):
    klass: Type = Capital


class IncomeName(RegularName):
    klass: Type = Income


class ExpenseName(RegularName):
    klass: Type = Expense


@dataclass
class ContraName:
    account_name: str
    contra_account_name: str

    def qualified(self) -> str:
        return f"contra:{self.account_name}:{self.contra_account_name}"


def extract(label: str):
    if ":" not in label:
        raise AbacusError(f"Not a label: {label}")
    parts = label.split(":")
    match len(parts):
        case 2:
            return RegularName.new(parts[0], parts[1])
        case 3:
            if parts[0] == "contra":
                return ContraName(account_name=parts[1], contra_account_name=parts[2])
            else:
                raise AbacusError(f"Wrong format for contra account name: {label}")
        case _:
            raise AbacusError(f"Too many colons (:) in account name: {label}")
