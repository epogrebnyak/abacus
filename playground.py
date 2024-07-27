"""Accounting module for double-entry bookkeeping.

add assumptions from issue 80 
and:
- account is always either debit side or credit side
- no journals, entries get poted to ledger directly
- how closing is made
- net earnings made of income and expenses, no gross profit or profit before tax   
"""

import decimal
from abc import ABC, abstractmethod
from collections import UserDict, UserList
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class AbacusError(Exception):
    """Custom error for the abacus project."""


AccountName = str
Amount = decimal.Decimal



class Side(Enum):
    """Indicate debit (right) or credit (left) side of the account."""

    Debit = "debit"
    Credit = "credit"

    def reverse(self) -> "Side":
        """Change side from debit to credit and vice versa."""
        if self == Side.Debit:
            return Side.Credit
        return Side.Debit

    def __repr__(self):
        """Make this enum look better in messages."""
        return str(self)


class T5(Enum):
    """Five types of accounts."""

    Asset = "asset"
    Liability = "liability"
    Capital = "capital"
    Income = "income"
    Expense = "expense"

    @staticmethod
    def which(t: "T5") -> Side:
        """Associate each type of account with debit or credit side."""
        if t in [T5.Asset, T5.Expense]:
            return Side.Debit
        return Side.Credit


class Holder(ABC):
    """Abstract class for construction regular, contra or intermediate accounts.

    Examples:
        Regular(T5.Asset)
        Contra(T5.Income)
        Intermediate(Profit.IncomeSummaryAccount)

    Regular and Contra constructors help to define each of five account types
    and their contra accounts. Intermediate constructor used for profit accounts,
    that live a short while after closing entries.
    """

    @property
    @abstractmethod
    def side(self) -> Side:
        """Indicate side of account (debit or credit)."""
        pass

    def taccount(self):
        """Create T-account for this account definition."""
        return TAccount(self.side)


@dataclass
class Regular(Holder):
    """Regular accounts of five types."""

    t: T5

    @property
    def side(self) -> Side:
        return T5.which(self.t)


@dataclass
class Contra(Holder):
    """A contra account to any of five types of account.

    Examples of contra accounts (generated text below):
        - contra property, plant, equipment account: accumulated depreciation
        - contra liability account: discount on bonds payable (?)
        - contra capital account: treasury stock
        - contra income account: refunds
        - contra expense account: purchase discounts
    """

    t: T5

    @property
    def side(self) -> Side:
        return T5.which(self.t).reverse()


class Profit(Enum):
    IncomeSummaryAccount = "isa"
    OtherComprehensiveIncome = "oci"  # not implemented yet


@dataclass
class Intermediate(Holder):
    """Intermediate account used for profit accounts only."""

    t: Profit

    @property
    def side(self) -> Side:
        if isinstance(self.t, Profit):
            return Side.Credit
        raise AbacusError("Unknown intermediate account: " + str(self.t))

@dataclass
class SingleEntry(ABC):
    """Single entry that changes either a debit or a credit side of an account."""
    name: AccountName
    amount: Amount

    def __post_init__(self):
        self.amount = Amount(self.amount)
        
class Debit(SingleEntry):...
class Credit(SingleEntry):...


@dataclass
class MultipleEntry:
    data: list[SingleEntry]

    def sum(self, type):
        return sum(x.amount for x in self.data if isinstance(x, type))

    def __post_init__(self):
        if self.sum(Debit) != self.sum(Credit):
            raise AbacusError(
                "Sum of debits and sum of credits should be equal: " + str(self)
            )
        
    def __iter__(self):
        return iter(self.data)   

import pytest
with pytest.raises(AbacusError):
   MultipleEntry(data=[Debit("a", 100), Credit("b", 99)])

def double_entry(debit, credit, amount) -> MultipleEntry:
    """Create entry from debit account name, credit account name and entry amount."""
    return multiple_entry(Debit(debit, amount), Credit(credit, amount))


def multiple_entry(*entries) -> MultipleEntry:
    return MultipleEntry(entries)


@dataclass
class Account:
    """Account definition with contra accounts."""

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
        yield from self.stream(self.assets, T5.Asset)
        yield from self.stream(self.capital, T5.Capital)
        yield self.retained_earnings_account, Regular(T5.Capital)
        yield from self.stream(self.liabilities, T5.Liability)
        yield from self.stream(self.income, T5.Income)
        yield from self.stream(self.expenses, T5.Expense)
        yield self.income_summary_account, Intermediate(Profit.IncomeSummaryAccount)

    @staticmethod
    def stream(accounts: list[Account], account_type: T5):
        for account in accounts:
            yield account.name, Regular(account_type)
            for contra_name in account.contra_accounts:
                yield contra_name, Contra(account_type)

    def __post_init__(self):
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
class TAccount:
    """T-account holds amounts on debit and credit side."""

    side: Side
    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        """Add debit amount to account."""
        self.debits.append(amount)

    def credit(self, amount: Amount):
        """Add credit amount to account."""
        self.credits.append(amount)

    def _is_debit_account(self) -> bool:
        """Return True if this account is debit account."""
        return self.side == Side.Debit

    def balance(self) -> Amount:
        """Return account balance."""
        b = Amount(sum(self.debits) - sum(self.credits))
        return b if self._is_debit_account() else -b


class Ledger(UserDict[AccountName, TAccount]):
    @classmethod
    def new(cls, chart: Chart):
        """Create new ledger from chart of accounts."""
        return cls({name: definition.taccount() for name, definition in chart.items()})

    def posts(self, entry: SingleEntry):
        """Post single entry to ledger."""
        match entry:
            case Debit(name, amount):
                self.data[name].debit(amount)
            case Credit(name, amount):
                self.data[name].credit(amount)

    def post(self, entries: Iterable[SingleEntry]):
        """Post a stream of single entries to ledger."""
        failed = []
        for entry in entries:
            try:
                self.posts(entry)
            except KeyError:
                failed.append(entry)
        if failed:
            raise AbacusError(["Could not post to ledger:", failed])

    def post_many(self, entries: list[MultipleEntry]):
        for entry in entries:
            self.post(entry)

    def trial_balance(self):
        return TrialBalance.new(self)


book = Ledger({"a": TAccount(Side.Debit), "b": TAccount(Side.Credit)})
assert book.post(double_entry("a", "b", 100)) == {
    "a": TAccount(side=Side.Debit, debits=[Amount(100)], credits=[]),
    "b": TAccount(side=Side.Credit, debits=[], credits=[Amount(100)]),
}


class TrialBalance(UserDict[str, tuple[Side, Amount]]):

    @classmethod
    def new(cls, ledger: Ledger):
        return cls(
            {
                account_name: (t_account.side, t_account.balance())
                for account_name, t_account in ledger.items()
            }
        )

    def tuples(self):
        def to_tuples(side, balance):
            match side:
                case Side.Debit:
                    return balance, 0
                case Side.Credit:
                    return 0, balance

        return {
            name: to_tuples(side, balance) for name, (side, balance) in self.items()
        }

    def balances(self):
        return {name: balance for name, (_, balance) in self.items()}


@dataclass
class IncomeSummary:
    income: dict[AccountName, Amount] = field(default_factory=dict)
    expenses: dict[AccountName, Amount] = field(default_factory=dict)

    @property
    def net_earnings(self):
        return sum(self.income.values()) - sum(self.expenses.values())


def close(ledger: Ledger, chart: Chart):
    """Close ledger at accounting period end following these steps:
    - close income and expense contra accounts,
    - close income and expense accounts to income summary account,
    - close income summary account to retained earnings.
    """
    isa = chart.income_summary_account
    re = chart.retained_earnings_account
    closing_entries = []

    def proceed(a, e):
        closing_entries.append(e)
        ledger.post(e)
        del ledger[a]

    # Close contra_accounts
    for account in chart.income:
        for a in account.contra_accounts:
            e = double_entry(debit=account.name, credit=a, amount=ledger[a].balance())
            proceed(a, e)
    for account in chart.expenses:
        for a in account.contra_accounts:
            e = double_entry(debit=a, credit=account.name, amount=ledger[a].balance())
            proceed(a, e)
    income_summary = IncomeSummary()
    # Close income and expense accounts
    for account in chart.income:
        a = account.name
        b = ledger[a].balance()
        income_summary.income[a] = b
        e = double_entry(debit=a, credit=isa, amount=b)
        proceed(a, e)
    for account in chart.expenses:
        a = account.name
        b = ledger[a].balance()
        income_summary.expenses[a] = b
        e = double_entry(debit=isa, credit=a, amount=b)
        proceed(a, e)
    # Close to retained earnings
    e = double_entry(debit=isa, credit=re, amount=ledger[isa].balance())
    proceed(isa, e)
    # note we actually mutate the ledger
    return closing_entries, ledger, income_summary


entries = [
    double_entry("cash", "equity", 100),
    double_entry("inventory", "cash", 90),
    double_entry("cogs", "inventory", 60),
    multiple_entry(Debit("cash", 75), Debit("refunds", 2), Credit("sales", 77)),
]

chart = Chart(
    income_summary_account="isa",
    retained_earnings_account="retained_earnings",
    assets=[Account("cash"), Account("inventory")],
    capital=[Account("equity")],
    expenses=[Account("cogs")],
    income=[Account("sales", contra_accounts=["refunds"])],
)

print(chart)
ledger = Ledger.new(chart)
ledger.post_many(entries)
print(ledger)
tb1 = ledger.trial_balance()
print(tb1)
assert tb1.tuples() == {
    "cash": (85, 0),
    "inventory": (30, 0),
    "equity": (0, 100),
    "retained_earnings": (0, 0),
    "sales": (0, 77),
    "refunds": (2, 0),
    "cogs": (60, 0),
    "isa": (0, 0),
}
_, ledger, income_summary = close(ledger, chart)
tb2 = ledger.trial_balance()
print("\n", tb2)
balances = tb2.balances()
print("\n", balances)
assert balances == {
    "cash": 85,
    "inventory": 30,
    "equity": 100,
    "retained_earnings": 15,
}
print(income_summary)

assert income_summary.net_earnings == 15

# NOTE: may need add more post close accounts (e.g. income tax posting)
