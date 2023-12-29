from copy import deepcopy
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

    @abstractmethod
    def transfer_balance(self, my_name: str, dest_name: str) -> "Entry":
        ...


class DebitAccount(TAccount):
    def balance(self):
        return sum(self.debits) - sum(self.credits)

    def transfer_balance(self, my_name: str, dest_name: str) -> "Entry":
        return Entry(dest_name, my_name, self.balance())


class CreditAccount(TAccount):
    def balance(self):
        return sum(self.credits) - sum(self.debits)

    def transfer_balance(self, my_name: str, dest_name: str) -> "Entry":
        return Entry(my_name, dest_name, self.balance())


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


@dataclass
class Entry:
    debit: str
    credit: str
    amount: Amount


class AccountBalances(UserDict[str, Amount]):
    def nonzero(self):
        return {name: balance for name, balance in self.items() if balance}

    def save(self, path: str):
        pass


class Ledger(UserDict[str, TAccount]):
    def post(self, debit: str, credit: str, amount: Amount):
        return self.post_one(Entry(debit, credit, amount))


    def post_one(self, entry: Entry):
        self.data[entry.debit].debit(entry.amount)
        self.data[entry.credit].credit(entry.amount)
        return self 

    def post_many(self, entries: list[Entry]):
        for entry in entries:
            self.post_one(entry)
        return self    

    @property    
    def balances(self):
        return AccountBalances(
            {name: account.balance() for name, account in self.items()}
        )


def contra_pairs(chart: Chart, contra_t: Type[ContraAccount]):
    attr = {
        "ContraAsset": "assets",
        "ContraLiability": "liabilities",
        "ContraCapital": "capital",
        "ContraExpense": "expenses",
        "ContraIncome": "income",
    }[contra_t.__name__]
    return [
        (a.name, x)
        for a in map(Account.from_string, getattr(chart, attr))
        for x in a.contra_accounts
    ]


class Pipeline:
    """A pipeline to accumulate ledger transformations."""

    def __init__(self, chart: Chart, ledger: Ledger):
        self.chart = chart
        self.ledger = deepcopy(ledger)
        self.closing_entries: list[Entry] = []

    def append_and_post(self, entry: Entry):
        self.ledger.post_one(entry)
        self.closing_entries.append(entry)

    def close_contra(self, contra_t: Type[ContraAccount]):
        """Close contra accounts of type `contra_t`."""
        for from_, to_ in contra_pairs(self.chart, contra_t):
            account = self.ledger.data[from_]
            entry = account.transfer_balance(from_, to_)
            self.append_and_post(entry)
        return self

    def close_to_isa(self):
        """Close income or expense accounts to income summary account."""
        for name, account in self.ledger.data.items():
            if isinstance(account, Income) or isinstance(account, Expense):
                entry = account.transfer_balance(
                    name, self.chart.income_summary_account
                )
                self.append_and_post(entry)
        return self

    def close_isa_to_re(self):
        """Close income summary account to retained earnings account."""
        entry = Entry(
            debit=self.chart.income_summary_account,
            credit=self.chart.retained_earnings_account,
            amount=self.ledger.data[self.chart.income_summary_account].balance(),
        )
        self.append_and_post(entry)
        return self

    def close_first(self):
        """Close contra income and contra expense accounts."""
        self.close_contra(ContraIncome)
        self.close_contra(ContraExpense)
        return self

    def close_second(self):
        """Close income and expense accounts to income summary account,
        then close income summary account to retained earnings."""
        self.close_to_isa()
        self.close_isa_to_re()
        return self

    def close_last(self):
        """Close permanent contra accounts."""
        self.close_contra(ContraAsset)
        self.close_contra(ContraLiability)
        self.close_contra(ContraCapital)
        return self


chart = Chart(
    assets=["cash", "ar", "inventory"],
    capital=[Account("equity", contra_accounts=["ts"])],
    income=[Account("sales", contra_accounts=["refunds", "voids"])],
    liabilities=["ap", "dd"],
    expenses=["salaries"],
)

ledger = chart.ledger().post_many([
    Entry("cash", "equity", 120),
    Entry("ts", "cash", 20),
  #  Entry("cash", "sales", 130),
  #  Entry("refunds", "cash", 20),
  #  Entry("voids", "cash", 10),
  #  Entry("salaries", "cash", 50),
])

# initial ledger does not change after copy
le0 = Chart(assets=["cash"], capital=["equity"]).ledger().post("cash", "equity", 100)
assert le0.balances.nonzero() == {'cash': 100, 'equity': 100}
le1 = deepcopy(le0)
le1 = le1.post("cash", "equity", 200)
assert le0.balances.nonzero() == {'cash': 100, 'equity': 100}

# correct up to this point

book = Pipeline(chart, ledger).close_first().close_second().close_last().ledger
print(book.balances.nonzero())  
# Incorrect:
# {'cash': 150, 'ts': -100, 're': -50, 'refunds': -110, 'voids': 10}

# # Next: entry, post and report
