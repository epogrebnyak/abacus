from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Type

from pydantic import BaseModel  # pylint: disable=import-error # type: ignore

AccountName = str
Amount = int


def permanent():
    return [
        Asset,
        ContraAsset,
        Capital,
        ContraCapital,
        Liability,
        ContraLiability,
        RetainedEarnings,
    ]


class Chart(BaseModel):
    assets: List[AccountName] = []
    expenses: List[AccountName] = []
    equity: List[AccountName] = []
    liabilities: List[AccountName] = []
    income: List[AccountName] = []
    retained_earnings_account: AccountName = "re"
    income_summary_account: AccountName = "current_profit"
    # maybe add null account for starting balances
    contra_accounts: Dict[AccountName, List[AccountName]] = {}

    @classmethod
    def mapping(cls):
        """Relate Chart class attributes to actual classes."""
        return dict(
            assets=(Asset, ContraAsset),
            expenses=(Expense, ContraExpense),
            equity=(Capital, ContraCapital),
            liabilities=(Liability, ContraLiability),
            income=(Income, ContraIncome),
        ).items()

    def account_names(self, cls: Type["RegularAccount"]) -> List[AccountName]:
        """Return account name list for regular account class *cls*."""
        reverse_dict = {
            Class.__name__: attribute for attribute, (Class, _) in self.mapping()
        }
        return getattr(self, reverse_dict[cls.__name__])

    def contra_account_pairs(self, cls: Type["RegularAccount"]):
        """Yield pairs of regular and contra account names for given account type *cls*.
        This action unpacks self.conta_accounts to a sequence of tuples, each tuple is
        a pair of account names."""
        for regular_account_name, contra_account_names in self.contra_accounts.items():
            if regular_account_name in self.account_names(cls):
                for contra_account_name in contra_account_names:
                    yield regular_account_name, contra_account_name


@dataclass
class Entry:
    """Pure accounting entry (without title, date, etc.)"""

    debit: AccountName
    credit: AccountName
    amount: Amount


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

    def credit(self, amount: Amount):
        """Append *amount* to credit side of the account."""
        self.credits.append(amount)

    def deep_copy(self):
        """Replicate this account as new data structure."""
        return self.__class__(self.debits.copy(), self.credits.copy())

    def condense(self):
        """Create a new account of the same type with only one value, the account balance."""
        cls = self.__class__
        balance = self.balance()
        match self:
            case DebitAccount(_, _):
                return cls([balance], [])
            case CreditAccount(_, _):
                return cls([], [balance])


class DebitAccount(TAccount):
    def balance(self) -> Amount:
        return sum(self.debits) - sum(self.credits)


class CreditAccount(TAccount):
    def balance(self) -> Amount:
        return sum(self.credits) - sum(self.debits)


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


class Transferable(TAccount):
    def transfer(self, my_name: AccountName, dest_name: AccountName) -> Entry:
        """Make entry to transfer balances from *t_account* of named *this* to *destination* account.
        The entry will differ depending on if *t_account* is debit or credit account."""
        amount = self.balance()
        match self:
            case DebitAccount(_, _):
                return Entry(dest_name, my_name, amount)
            case CreditAccount(_, _):
                return Entry(my_name, dest_name, amount)
            case _:
                raise TypeError


class IncomeSummaryAccount(CreditAccount, Unique, Transferable):
    pass


class RetainedEarnings(Capital, Unique):
    pass


class ContraAccount(Transferable):
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


assert Chart() == Chart(
    assets=[],
    expenses=[],
    equity=[],
    liabilities=[],
    income=[],
    retained_earnings_account="re",
    income_summary_account="current_profit",
    contra_accounts={},
)
