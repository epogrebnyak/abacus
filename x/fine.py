from abc import ABC, abstractmethod
from collections import UserDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Type


class T(Enum):
    Asset = "asset"
    Liability = "liability"
    Capital = "capital"
    Income = "income"
    Expense = "expense"


@dataclass
class Regular:
    t: T


@dataclass
class Contra:
    t: T


@dataclass
class Account:
    name: str
    contra_accounts: list[str] = field(default_factory=list)

    @staticmethod
    def from_string(s) -> "Account":
        if isinstance(s, str):
            return Account(s, [])
        return s


Amount = int


@dataclass
class TAccount(ABC):
    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        self.debits.append(amount)

    def credit(self, amount: Amount):
        self.credits.append(amount)

    @abstractmethod
    def balance(self) -> Amount:
        ...


class DebitAccount(TAccount):
    def balance(self):
        return sum(self.debits) - sum(self.credits)


class CreditAccount(TAccount):
    def balance(self):
        return sum(self.credits) - sum(self.debits)


class RegularAccount:
    ...


class Asset(RegularAccount, DebitAccount):
    ...


class Capital(RegularAccount, CreditAccount):
    ...


class Liability(RegularAccount, CreditAccount):
    ...


class Income(RegularAccount, CreditAccount):
    ...


class Expense(RegularAccount, DebitAccount):
    ...


class ContraAccount:
    ...


class ContraAsset(ContraAccount, CreditAccount):
    ...


class ContraCapital(ContraAccount, DebitAccount):
    ...


class ContraLiability(ContraAccount, DebitAccount):
    ...


class ContraIncome(ContraAccount, DebitAccount):
    ...


class ContraExpense(ContraAccount, CreditAccount):
    ...


class TemporaryAccount:
    ...


class TemporaryCreditAccount(TemporaryAccount, CreditAccount):
    ...


class TemporaryDebitAccount(TemporaryAccount, DebitAccount):
    ...


@dataclass
class Temporary:
    t: Type[TAccount]


def taccount(t: Type[Contra | Regular | Temporary]) -> Type[TAccount]:
    match t:
        case Regular(T.Asset):
            return Asset
        case Regular(T.Capital):
            return Capital
        case Regular(T.Liability):
            return Liability
        case Regular(T.Income):
            return Income
        case Regular(T.Expense):
            return Expense
        case Contra(_):
            return contra(t)
        case Temporary(x):
            return x
        case _:
            raise ValueError(f"Invalid type: {t}")


def contra(t: Type[Contra]) -> Type[TAccount]:
    match t:
        case Contra(T.Asset):
            return ContraAsset
        case Contra(T.Capital):
            return ContraCapital
        case Contra(T.Liability):
            return ContraLiability
        case Contra(T.Income):
            return ContraIncome
        case Contra(T.Expense):
            return ContraExpense
        case _:
            raise ValueError(f"Invalid type: {t}")


@dataclass
class Chart:
    income_summary_account: str = "isa"
    retained_earnings_account: str = "re"
    null_account: str = "null"
    assets: list[str | Account] = field(default_factory=list)
    capital: list[str | Account] = field(default_factory=list)
    liabilities: list[str | Account] = field(default_factory=list)
    income: list[str | Account] = field(default_factory=list)
    expenses: list[str | Account] = field(default_factory=list)

    def __post_init__(self):
        self.validate()

    def validate(self):
        if len(self.to_dict()) != len(list(self.dict_items())):
            raise ValueError("Chart should not contain duplicate account names.")
        return self

    def to_dict(self):
        return dict(self.dict_items())

    def dict_items(self):
        yield from self.stream(self.assets, T.Asset)
        yield from self.stream(self.capital, T.Capital)
        yield self.retained_earnings_account, Regular(T.Capital)
        yield from self.stream(self.liabilities, T.Liability)
        yield from self.stream(self.income, T.Income)
        yield from self.stream(self.expenses, T.Expense)
        yield self.income_summary_account, Temporary(TemporaryCreditAccount)
        yield self.null_account, Temporary(TemporaryCreditAccount)

    def stream(self, xs, t):
        for x in xs:
            a = Account.from_string(x)
            yield a.name, Regular(t)
            for b in a.contra_accounts:
                yield b, Contra(t)

    def ledger(self):
        return Ledger({name: taccount(t)() for name, t in self.dict_items()})


class Ledger(UserDict[str, TAccount]):
    ...


chart = Chart(
    assets=["cash", "ar", "inventory"],
    capital=[Account("equity", contra_accounts=["ts"])],
    income=[Account("sales", contra_accounts=["refunds", "voids"])],
    liabilities=["ap", "dd"],
    expenses=["salaries"],
)


for a, b in chart.ledger().items():
    print(a, b)

# Next: entry, post and report
