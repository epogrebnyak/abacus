"""A minmal, yet valid double-entry accounting system.

To use the module:

- create a chart of accounts using `Chart` class,
- create ledger from Chart,
- post accoutning entries to ledger,
- use `Reporter` class to generate financial statements
- print to screen or save to file.

Cool things implemented in this library are:

1. proper closing of accounts at accounting period end,
2. contra accounts — there can be a "refunds" account that offsets "income:sales"
   and "depreciation" account that offsets "asset:ppe", 
3. multiple entries — debit and credit several accounts in one transaction.

Assumptions — things that were made intentionally simple:

1. there is the only level of account hierarchy and no sub-accounts  ,
2. account names must be unique, cannot use "asset:other" and "expense:other",
  these names must be "asset:other_assets" and "expense:other_expenses"),
3. no cashflow statement yet;
4. the entry does not store date or title, only amounts and account names;
5. one currency.

"""
from abc import ABC, abstractmethod
from collections import UserDict
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Type


class T(Enum):
    """Five types of accounts and standard prefixes for account names."""

    Asset = "asset"
    Liability = "liability"
    Capital = "capital"
    Income = "income"
    Expense = "expense"


class Holder(ABC):
    """The `Holder` class is a wrapper to hold an account type:

    - regular account via `Regular(Holder)` child class,
    - contra account via `Contra(Holder)` child class, or
    - temporary account like income summary and null account
      via `Temporary(Holder)`.

    This wrapping enables to pattern match on account type.
    """

    @abstractmethod
    def t_account(
        self,
    ) -> type["RegularAccount"] | type["ContraAccount"] | type["ExtraAccount"]:
        """Provide T-account constructor."""
        ...


@dataclass
class Regular(Holder):
    t: T

    @property
    def t_account(self) -> type["RegularAccount"]:
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
            case _:
                raise ValueError(f"Invalid type: {self}")


@dataclass
class Contra(Holder):
    t: T

    @property
    def t_account(self) -> Type["ContraAccount"]:
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
                raise ValueError(f"Invalid type: {self}")


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
    """T-account will hold amounts on debits and credit side."""

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
        """Create an entry that transfers account balance from this account
        to destination account.

        This account name is `my_name` and destination account name is `dest_name`.
        """
        ...


class DebitAccount(TAccount):
    def balance(self):
        return sum(self.debits) - sum(self.credits)

    def transfer_balance(self, my_name: str, dest_name: str) -> "Entry":
        return Entry(debit=dest_name, credit=my_name, amount=self.balance())


class CreditAccount(TAccount):
    def balance(self):
        return sum(self.credits) - sum(self.debits)

    def transfer_balance(self, my_name: str, dest_name: str) -> "Entry":
        return Entry(debit=my_name, credit=dest_name, amount=self.balance())


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


class ExtraAccount:
    ...


class ExtraCreditAccount(ExtraAccount, CreditAccount):
    ...


class TAccountRetainedEarnings(ExtraCreditAccount):
    ...


class TAccountNull(ExtraCreditAccount):
    ...


class ExtraDebitAccount(ExtraAccount, DebitAccount):
    ...


@dataclass
class Extra(Holder):
    """Holder for extra account that does not belong to any of 5 account types."""

    t: type[ExtraAccount]

    @property
    def t_account(self) -> type[ExtraAccount]:
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
        yield self.income_summary_account, Extra(TAccountRetainedEarnings)
        yield self.null_account, Extra(TAccountNull)

    def pure_accounts(self, xs: list[str | Account]) -> list[Account]:
        return [Account.from_string(x) for x in xs]

    def stream(self, items, t):
        for account in self.pure_accounts(items):
            yield account.name, Regular(t)
            for contra_name in account.contra_accounts:
                yield contra_name, Contra(t)

    def ledger(self):
        return Ledger({name: h.t_account() for name, h in self.dict_items()})


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
    """Return list of account and contra account name pairs for a given type of contra account."""
    attr = {
        "ContraAsset": "assets",
        "ContraLiability": "liabilities",
        "ContraCapital": "capital",
        "ContraExpense": "expenses",
        "ContraIncome": "income",
    }[contra_t.__name__]
    regular_accounts = chart.pure_accounts(getattr(chart, attr))
    return [
        (account.name, contra_name)
        for account in regular_accounts
        for contra_name in account.contra_accounts
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


class TrialBalance(UserDict[str, tuple[Amount, Amount]]):
    ...


class ChartDict(UserDict[str, Holder]):
    ...
