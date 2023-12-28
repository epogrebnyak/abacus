from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Type
from collections import UserDict


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

    def offset(self, name: str):
        return self.offset_many([name])

    def offset_many(self, names: list[str]):
        self.contra_accounts.extend(names)
        return self

    @staticmethod
    def from_string(s) -> "Account":
        if isinstance(s, str):
            return Account(s, [])
        return s


Amount = int


@dataclass
class TAccount:
    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)


class DebitAccount(TAccount):
    ...


class CreditAccount(TAccount):
    ...

class TemporaryAccount:...

class TemporaryCreditAccount(TemporaryAccount, CreditAccount):...

class TemporaryDebitAccount(TemporaryAccount, DebitAccount):...

@dataclass
class Temporary:
    t: Type[TAccount]


def reverse(t: Type[TAccount]) -> Type[TAccount]:
    match t():
        case DebitAccount():
            return CreditAccount
        case CreditAccount():
            return DebitAccount


def taccount(t):
    match t:
        case Regular(T.Asset):
            return DebitAccount
        case Regular(T.Capital):
            return CreditAccount
        case Regular(T.Liability):
            return CreditAccount
        case Regular(T.Income):
            return CreditAccount
        case Regular(T.Expense):
            return DebitAccount
        case Contra(y):
            return reverse(taccount(Regular(y)))
        case Temporary(x):
            return x
        case _:
            raise ValueError(f"Invalid type: {t}")

# TODO: will need ContraCapital, etc

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
        if len(self.to_dict()) != len(list(self.dict_items())):
            raise ValueError("Chart should not contain duplicate account names.")

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

for x, y in chart.to_dict().items():
    print(x, y)

for a, b in chart.ledger().items():
    print(a, b)

# Next: entry, post and report
