import decimal
from abc import ABC, abstractmethod
from collections import UserDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class AbacusError(Exception):
    """Custom error for this project."""


Amount = decimal.Decimal
AccountName = str


class Side(Enum):
    Debit = "debit"
    Credit = "credit"

    def reverse(self) -> "Side":
        if self == Side.Debit:
            return Side.Credit
        return Side.Debit

    def __repr__(self):
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
        if t in [T5.Asset, T5.Expense]:
            return Side.Debit
        return Side.Credit


class Slug(ABC):
    @property
    @abstractmethod
    def side(self):
        pass

    def taccount(self):
        return TAccount(self.side)

@dataclass
class Regular(Slug):
    t: T5

    @property
    def side(self) -> Side:
        return T5.which(self.t)
    

@dataclass
class Contra(Slug):
    t: T5

    @property
    def side(self) -> Side:
        return T5.which(self.t).reverse()


class Profit(Enum):
    IncomeSummaryAccount = "isa"
    OtherComprehensiveIncome = "oci"


@dataclass
class Intermediate(Slug):
    t: Profit

    @property
    def side(self) -> Side:
        return Side.Credit

@dataclass
class Enter:
    account_name: AccountName
    amount: Amount


@dataclass
class MultipleEntry:
    debit: list[Enter]
    credit: list[Enter]

    def __post_init__(self):
        if not sum(d.amount for d in self.debit) == sum(c.amount for c in self.credit):
            raise AbacusError(
                "Debits and credits not equal in this entry: " + str(self)
            )


def entry(debit, credit, amount) -> MultipleEntry:
    "Create entry from debit account name, credit account name and entry amount."
    return MultipleEntry(
        debit=[Enter(debit, amount)],
        credit=[Enter(credit, amount)],
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
    """T-account will hold amounts on debits and credit side."""
    side: Side
    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        """Add debit amount to account."""
        self.debits.append(amount)

    def credit(self, amount: Amount):
        """Add credit amount to account."""
        self.credits.append(amount)

    def balance(self) -> Amount:
        """Return account balance."""
        b = Amount(sum(self.debits) - sum(self.credits))
        if self.side == Side.Debit:
            return b
        return -b


class Ledger(UserDict[AccountName, TAccount]):
    @classmethod
    def new(cls, chart: Chart):
        return cls({name: slug.taccount() for name, slug in chart.items()})

    def post_one(self, entry: MultipleEntry):
        """Post one multiple entry to ledger."""
        return self.post_many([entry])

    def post_many(self, entries: Iterable[MultipleEntry]):
        """Post several multiple entries to ledger."""
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
            raise AbacusError(["Could not post to ledger:", failed])
        return self


def flat(ledger: Ledger):
    return [
        (t_account.side, account_name, t_account.balance())
        for account_name, t_account in ledger.items()
    ]


def to_tuples(side, balance):
    if side == Side.Debit:
        return balance, 0
    else:
        return 0, balance


def trial_balance(ledger: Ledger):
    return {name: to_tuples(side, balance) for side, name, balance in flat(ledger)}


class TrialBalance(UserDict[str, tuple[Side, Amount]]):
    ...            


@dataclass
class IncomeSummary:
    income: dict[AccountName, Amount] = field(default_factory=dict)
    expenses: dict[AccountName, Amount] = field(default_factory=dict)


def close(ledger: Ledger, chart: Chart):
    """Closing order:
       - close income and expense contra accounts,
       - close income and expense accounts to income summary account,
       - close income summary account to retained earnings.
    """
    isa = chart.income_summary_account
    re = chart.retained_earnings_account
    closing_entries = []
    # Close contra_accounts
    for account in chart.income:
        for a in account.contra_accounts:
            e = entry(debit=account.name, credit=a, amount=ledger[a].balance())
            closing_entries.append(e)
            ledger.post_one(e)
            del ledger[a]
    for account in chart.expenses:
        for a in account.contra_accounts:
            e = entry(debit=a, credit=account.name, amount=ledger[a].balance())
            closing_entries.append(e)
            ledger.post_one(e)
            del ledger[a]
    income_summary = IncomeSummary()
    # Close income and expense accounts
    for account in chart.income:
        a = account.name
        b = ledger[a].balance()
        income_summary.income[a] = b
        e = entry(debit=a, credit=isa, amount=b)
        closing_entries.append(e)
        ledger.post_one(e)
        del ledger[a]
    for account in chart.expenses:
        a = account.name
        b = ledger[a].balance()
        income_summary.expenses[a] = b
        e = entry(debit=isa, credit=a, amount=b)
        closing_entries.append(e)
        ledger.post_one(e)
        del ledger[a]
    # Close to retained earnings
    e = entry(debit=isa, credit=re, amount=ledger[isa].balance())
    closing_entries.append(e)
    ledger.post_one(e)
    del ledger[isa]
    return closing_entries, ledger, income_summary

def to_balances(tb):
    return {k: from_pair(v) for k, v in tb.items()}


def from_pair(pair: tuple[Amount, Amount]) -> Amount:
    if pair[0] == 0:
        return pair[1]
    elif pair[1] == 0:
        return pair[0]
    else:
        raise AbacusError("Invalid pair: " + str(pair))


assert from_pair((decimal.Decimal("0"), decimal.Decimal("100"))) == 100

entries = [
    entry("cash", "equity", 100),
    entry("inventory", "cash", 90),
    entry("cogs", "inventory", 60),
    MultipleEntry(
        debit=[Enter("cash", 75), Enter("refunds", 2)], credit=[Enter("sales", 77)]
    ),
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
tb1 = trial_balance(ledger)
print(tb1)
assert tb1 == {
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
tb2 = trial_balance(ledger)
print("\n", tb2)
balances = to_balances(tb2)
print("\n", balances)
assert balances == {
    "cash": 85,
    "inventory": 30,
    "equity": 100,
    "retained_earnings": 15,
}
print(income_summary)

# NOTE: may need add more post close accounts (e.g. income tax posting)
