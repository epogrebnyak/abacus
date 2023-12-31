"""Simple double-entry accounting system.


To use the library:

- create a chart of accounts using `Chart` class,
- create ledger from Chart,
- post accoutning entries to ledger,
- use `Reporter` class to generate financial statements
- print to screen or save to file.

Trivial example: the company has just cash and equity accounts 
and received $499 and $501 from two investors. What is the company 
balance sheet?

```python
chart = Chart(assets=["cash"], capital=["equity"])
ledger = chart.ledger()
ledger.post(debit="cash", credit="equity", amount=499)
ledger.post(debit="cash", credit="equity", amount=501)
reporter = Reporter(chart, ledger)
print(reporter.balance_sheet)
```

Chart and balances can be saved to file:

```python 
chart.save("chart.json")
ledger.balances.save("end_balances.json")
```

Cool things implemented:

- proper closing of accounts at accounting period end,
- contra accounts — there can be a "refunds" account that offsets "income:sales",
- multiple entries — debit and credit several accounts in one transaction.

Things that were made intentionally simple:

- no sub-accounts, the only level of account hierarchy;
- account names must be unique, cannot use "asset:other" and "expense:other";
- no cashflow statement yet;
- the entry does not store date or title, only amounts and account names;
- one currency.

"""
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


class Holder(ABC):
    
    @abstractmethod
    def t_account(self) -> Type["TAccount"]:
        ... 

@dataclass
class Regular(Holder):
    t: T

    @property
    def t_account(self) -> Type["TAccount"]:
        match self:
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


@dataclass
class Contra(Holder):
    t: T

    @property
    def t_account(self) -> Type["TAccount"]:
        match self:
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
                raise ValueError(f"Invalid type: {self.t}")


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
class Temporary(Holder):
    t: Type[TAccount]

    @property
    def t_account(self):
        return self.t


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
        return Ledger({name: t.t_account() for name, t in self.dict_items()})


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

    def subset(self, cls: Type[TAccount]):
        """Filter ledger by account type."""
        return self.__class__(
            {
                account_name: t_account
                for account_name, t_account in self.data.items()
                if isinstance(t_account, cls)
            }
        )


def contra_pairs(chart: Chart, contra_t: Type[ContraAccount]) -> list[tuple[str, str]]:
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

    def close_contra(self, t: Type[ContraAccount]):
        """Close contra accounts of type `t`."""
        for account, contra_account in contra_pairs(self.chart, t):
            entry = self.ledger.data[contra_account].transfer_balance(
                contra_account, account
            )
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


@dataclass
class Reporter:
    chart: Chart
    ledger: Ledger

    @property
    def pipeline(self):
        return Pipeline(self.chart, self.ledger)

    @property
    def balance_sheet(self):
        p = self.pipeline.close_first().close_second().close_last()
        return BalanceSheet.new(p.ledger)

    @property
    def income_statement(self):
        p = self.pipeline.close_first()
        return IncomeStatement.new(p.ledger)


class Statement:
    ...


@dataclass
class BalanceSheet(Statement):
    assets: AccountBalances
    capital: AccountBalances
    liabilities: AccountBalances

    @classmethod
    def new(cls, ledger: Ledger):
        return cls(
            assets=ledger.subset(Asset).balances,
            capital=ledger.subset(Capital).balances,
            liabilities=ledger.subset(Liability).balances,
        )


@dataclass
class IncomeStatement(Statement):
    income: AccountBalances
    expenses: AccountBalances

    @classmethod
    def new(cls, ledger: Ledger):
        return cls(
            income=ledger.subset(Income).balances,
            expenses=ledger.subset(Expense).balances,
        )

    def current_account(self):
        return sum(self.income.values()) - sum(self.expenses.values())
