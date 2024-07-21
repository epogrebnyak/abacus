# Assumptions
# - one currency
import decimal
from abc import ABC, abstractmethod
from collections import UserDict, namedtuple
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Type


class AbacusError(Exception):
    """Custom error for this project."""


Amount = decimal.Decimal
AccountName = str


class T(Enum):
    """Five types of accounts."""

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


class Profit(Enum):
    IncomeSummaryAccount = "isa"
    OtherComprehensiveIncome = "oci"


@dataclass
class Intermediate:
    t: Profit


Enter = namedtuple("Enter", "account_name amount")


@dataclass
class MultipleEntry:
    debit: list[Enter]
    credit: list[Enter]

    def __post_init__(self):
        self.verify()

    def verify(self):
        if not sum(d.amount for d in self.debit) == sum(c.amount for c in self.credit):
            raise AbacusError(
                "Debits and credits not equal in this entry: " + str(self)
            )


@dataclass
class DoubleEntry:
    debit: AccountName
    credit: AccountName
    amount: Amount

    def to_multiple_entry(self) -> MultipleEntry:
        return MultipleEntry(
            debit=[Enter(self.debit, self.amount)],
            credit=[Enter(self.credit, self.amount)],
        )


@dataclass
class Account:
    name: AccountName
    contra_accounts: list[AccountName] = field(default_factory=list)


@dataclass
class Chart:
    """Chart of accounts.

    Example:

    ```python
    chart = Chart(assets=[Account("cash")], capital=[Account("equity")])
    ```
    """

    income_summary_account: str = "isa"
    retained_earnings_account: str = "retained_earnings"
    assets: list[Account] = field(default_factory=list)
    capital: list[Account] = field(default_factory=list)
    liabilities: list[Account] = field(default_factory=list)
    income: list[Account] = field(default_factory=list)
    expenses: list[Account] = field(default_factory=list)

    def dict(self):
        return dict(self.items())

    def items(self):
        """Assign account types to account names."""
        yield from self.stream(self.assets, T.Asset)
        yield from self.stream(self.capital, T.Capital)
        yield self.retained_earnings_account, Regular(T.Capital)
        yield from self.stream(self.liabilities, T.Liability)
        yield from self.stream(self.income, T.Income)
        yield from self.stream(self.expenses, T.Expense)
        yield self.income_summary_account, Intermediate(Profit.IncomeSummaryAccount)

    @staticmethod
    def stream(accounts: list[Account], account_type: T):
        for account in accounts:
            yield account.name, Regular(account_type)
            for contra_name in account.contra_accounts:
                yield contra_name, Contra(account_type)

    def __post_init__(self):
        self.validate()

    def validate(self):
        a = list(self.dict().keys())
        b = [x[0] for x in self.items()]
        if len(a) != len(b):
            raise AbacusError(
                [
                    "Chart should not contain duplicate account names.",
                    len(b) - len(a),
                    set(b) - set(a),
                ]
            )


@dataclass
class TAccount(ABC):
    """T-account will hold amounts on debits and credit side."""

    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        """Add debit amount to account."""
        self.debits.append(amount)

    def credit(self, amount: Amount):
        """Add credit amount to account."""
        self.credits.append(amount)

    @abstractmethod
    def balance(self) -> Amount:
        """Return account balance."""

    @staticmethod
    def reverse(t_account: Type["TAccount"]) -> Type["TAccount"]:
        if isinstance(t_account(), DebitAccount):
            return CreditAccount
        else:
            return DebitAccount

    @classmethod
    def new(cls, slug: Regular | Contra | Intermediate) -> Type["TAccount"]:
        match slug:
            case Regular(t):
                if t in [T.Asset, T.Expense]:
                    return DebitAccount
                return CreditAccount
            case Contra(t):
                return cls.reverse(cls.new(Regular(t)))
            case Intermediate(t):
                if t == Profit.IncomeSummaryAccount:
                    return CreditAccount
                else:
                    # Other comprehensive income not implemented yet.
                    raise AbacusError("Invalid account type: " + str(t))


class DebitAccount(TAccount):
    def balance(self):
        return sum(self.debits) - sum(self.credits)


class CreditAccount(TAccount):
    def balance(self):
        return sum(self.credits) - sum(self.debits)


class Ledger(UserDict[AccountName, TAccount]):

    @classmethod
    def new(cls, chart: Chart):
        return cls({name: TAccount.new(slug)() for name, slug in chart.items()})

    def post_double_entry(self, entry: DoubleEntry):
        """Post one double entry to ledger."""
        return self.post_one(entry.to_multiple_entry())

    def post_double_entries(self, double_entries: Iterable[DoubleEntry]):
        """Post several double entries to ledger."""
        return self.post_many([entry.to_multiple_entry() for entry in double_entries])

    def post_one(self, entry: MultipleEntry):
        """Post one multiple entry to ledger."""
        return self.post_many([entry])

    def post_many(self, entries: Iterable[MultipleEntry]):
        """Post several multiple  entries to ledger."""
        failed = []
        for entry in entries:
            try:
                for debit in entry.debit:
                    self.data[debit.account_name].debit(amount=debit.amount)
                for credit in entry.credit:
                    self.data[credit.account_name].credit(amount=credit.amount)
            except KeyError:
                failed.append(entry)
        if failed:
            raise AbacusError(failed)
        return self


entries = [
    DoubleEntry("cash", "equity", 100),
    DoubleEntry("inventory", "cash", 90),
    DoubleEntry("expense", "inventory", 60),
    DoubleEntry("cash", "sales", 75),
]

chart = Chart(
    income_summary_account="isa",
    retained_earnings_account="retained_earnings",
    assets=[Account("cash"), Account("inventory")],
    capital=[Account("equity")],
    expenses=[Account("expense")],
    income=[Account("sales")],
)


def trial_balance(ledger: Ledger):
    result = {}
    for account_name, t_account in ledger.items():
        b = t_account.balance()
        if isinstance(t_account, DebitAccount):
            result[account_name] = b, 0
        else:
            result[account_name] = 0, b
    return result


def close(ledger: Ledger, chart: Chart):
    isa = chart.income_summary_account
    re = chart.retained_earnings_account
    closing_entries = []
    for account in chart.income:
        a = account.name
        # must add closing of contra accounts
        e = DoubleEntry(debit=a, credit=isa, amount=ledger[a].balance())
        closing_entries.append(e)
        ledger.post_double_entry(e)
        del ledger[a]
    for account in chart.expenses:
        a = account.name
        # must add closing of contra accounts
        e = DoubleEntry(debit=isa, credit=a, amount=ledger[a].balance())
        closing_entries.append(e)
        ledger.post_double_entry(e)
        del ledger[a]
    e = DoubleEntry(debit=isa, credit=re, amount=ledger[isa].balance())
    closing_entries.append(e)
    ledger.post_double_entry(e)
    del ledger[isa]
    return closing_entries, ledger


def to_balances(pair):
    match pair:
        case (x, 0):
            return x
        case (0, x):
            return x
        case _:
            raise AbacusError("Invalid pair: " + str(pair))


ledger = Ledger.new(chart)
ledger.post_double_entries(entries)
print(ledger)
tb1 = trial_balance(ledger)
print(tb1)
assert tb1 == {
    "cash": (85, 0),
    "inventory": (30, 0),
    "equity": (0, 100),
    "retained_earnings": (0, 0),
    "sales": (0, 75),
    "expense": (60, 0),
    "isa": (0, 0),
}
_, ledger = close(ledger, chart)
tb2 = trial_balance(ledger)
print(tb2)
balances = {k: to_balances(v) for k, v in tb2.items()}
print(balances)
assert balances == {"cash": 85, "inventory": 30, "equity": 100, "retained_earnings": 15}

# TODO: add closing of contra account "rebates"
