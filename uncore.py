from abc import ABC, abstractmethod
from collections import UserDict, namedtuple
from copy import copy, deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Type


class Side(Enum):
    Debit = "debit"
    Credit = "credit"

    def __repr__(self):
        return f"'{self.value}'"


class T(Enum):
    """Five types of accounts and standard prefixes for account names."""

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
    links_to: str


class ChartDict(UserDict[str, Regular | Contra]):
    def __set_item__(self, name: str, value: Regular | Contra):
        match value:
            case Regular(_):
                self.data[name] = value
            case Contra(name):
                if name in self.data.keys():
                    self.data[name] = value
                else:
                    raise KeyError(
                        f"Account {name} not in chart, "
                        "cannot add a contrа account to it."
                    )
            case _:
                raise TypeError(value)

    def add_regular(self, t: T, name: str):
        self[name] = Regular(t)
        return self

    def add_offset(self, name: str, contra_name: str):
        self[contra_name] = Contra(name)
        return self


# test case: add R, add C, fail on adding C, and integer


@dataclass
class Chart:
    retained_earnings_account: str
    accounts: ChartDict = field(default_factory=ChartDict)
    income_summary_account: str = "_isa"

    def regular_names(self, t: T) -> list[str]:
        """List regular account names by type."""
        return [n for n, p in self.accounts.items() if p == Regular(t)]

    def names(self, cls: Type[Regular] | Type[Contra]) -> list[str]:
        """List all regular or all contra account names."""
        return [k for k, v in self.accounts.items() if isinstance(v, cls)]

    def add_many(self, t, *names: str):
        for name in names:
            self.add(t, name)
        return self

    def add(self, t: T, name: str, contra_names: list[str] | None = None):
        self.accounts.add_regular(t, name)
        if contra_names is None:
            contra_names = []
        for contra_name in contra_names:
            self.accounts.add_offset(name, contra_name)
        return self

    def constructor(self, name):
        match self.accounts[name]:
            case Regular(T.Asset):
                return Asset
            case Regular(T.Expense):
                return Expense
            case Regular(T.Capital):
                return Capital
            case Regular(T.Liability):
                return Liability
            case Regular(T.Income):
                return Income
            case Contra(name):
                return self.constructor(name).reverse()
            case _:
                raise ValueError(name)

    def create_ledger(self):
        self.accounts[self.retained_earnings_account] = Regular(T.Capital)
        ledger = Ledger({k: self.constructor(k)() for k in self.accounts})
        ledger[self.income_summary_account] = IncomeSummaryAccount()
        return ledger


# test case: overwrite any reserved name

Amount = Decimal | int | float
Record = namedtuple("Record", ["side", "name", "amount"])
Entry = list[Record]


def debit(name: str, amount: Amount) -> Record:
    return Record(Side.Debit, name, amount)


def credit(name: str, amount: Amount) -> Record:
    return Record(Side.Credit, name, amount)


def double_entry(dr: str, cr: str, amount: Amount) -> Entry:
    return [debit(dr, amount), credit(cr, amount)]


def is_debit(r: Record) -> bool:
    return r.side == Side.Debit


def is_credit(r: Record) -> bool:
    return r.side == Side.Credit


def is_balanced(rs: list[Record]) -> bool:
    def sums(f):
        return sum([r.amount for r in rs if f(r)])

    return sums(f=is_debit) == sums(f=is_credit)


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

    @abstractmethod
    def net_tuple_balance(self) -> tuple[Amount, Amount]:
        """Return a tuple of debit and credit side balances."""

    def condense(self):
        """Create a new account of the same type with only one value as account balance."""
        return self.empty().top_up(self.balance())

    def empty(self):
        """Create a new empty account of the same type."""
        return self.__class__()

    @abstractmethod
    def top_up(self, balance):
        """Add starting balance to the proper side of account."""


class DebitAccount(TAccount):
    def top_up(self, balance):
        self.debit(balance)

    @staticmethod
    def reverse():
        return CreditAccount

    def balance(self):
        return sum(self.debits) - sum(self.credits)

    def net_tuple_balance(self):
        return (self.balance(), 0)


class CreditAccount(TAccount):
    def top_up(self, balance):
        self.credit(balance)

    @staticmethod
    def reverse():
        return DebitAccount

    def balance(self):
        return sum(self.credits) - sum(self.debits)

    def net_tuple_balance(self):
        return (0, self.balance())


class Asset(DebitAccount):
    ...


class Expense(DebitAccount):
    ...


class Capital(CreditAccount):
    ...


class Liability(CreditAccount):
    ...


class Income(CreditAccount):
    ...


@dataclass
class RetainedEarningsAccount(CreditAccount):
    ...


@dataclass
class IncomeSummaryAccount(CreditAccount):
    ...


class Ledger(UserDict[str, "TAccount"]):
    def post(self, entry: Entry):
        if not is_balanced(entry):
            raise ValueError(entry)
        for record in entry:
            match record:
                case (Side.Debit, name, amount):
                    self.data[name].debit(amount)
                case (Side.Credit, name, amount):
                    self.data[name].credit(amount)
                case _:
                    raise TypeError(record)
        return self

    def post_many(self, entries: list[Entry]):
        for entry in entries:
            self.post(entry)
        return self

    @property
    def balances(self):
        return {name: account.balance() for name, account in self.data.items()}

    @property
    def net_tuple_balances(self):
        return {
            name: account.net_tuple_balance() for name, account in self.data.items()
        }

    def subset(self, ta):
        return self.__class__({k: v for k, v in self.items() if isinstance(v, ta)})


chart = (
    Chart(retained_earnings_account="retained_earnings")
    .add_many(T.Asset, "cash", "ar")
    .add(T.Capital, "equity", contra_names=["buyback"])
    .add(T.Income, "sales", contra_names=["refunds", "voids"])
    .add(T.Liability, "vat")
    .add(T.Expense, "salary")
)
print(chart)


ledger = chart.create_ledger().post_many(
    [
        double_entry("cash", "equity", 1200),
        double_entry("buyback", "cash", 200),
        [debit("ar", 70), credit("sales", 60), credit("vat", 10)],
        double_entry("cash", "ar", 30),
        [debit("voids", 20), debit("refunds", 10), debit("vat", 5), credit("ar", 35)],
        [debit("salary", 18), credit("cash", 18)],
    ]
)

print(ledger.net_tuple_balances)


def contra_pairs(chart: Chart, t: T):
    return [
        (p.links_to, name)
        for name, p in chart.accounts.items()
        if isinstance(p, Contra) and chart.accounts[p.links_to] == Regular(t)
    ]


assert contra_pairs(chart, T.Income) == [("sales", "refunds"), ("sales", "voids")]
assert contra_pairs(chart, T.Capital) == [("equity", "buyback")]


@dataclass
class Move:
    """Indicate where to transfer account balance.
    Helps to trace closing entries."""

    frm: str
    to: str

    def to_entry(self, ledger):
        account = ledger[self.frm]
        b = account.balance()
        match account:
            case DebitAccount(_, _):
                return double_entry(self.to, self.frm, b)
            case CreditAccount(_, _):
                return double_entry(self.frm, self.to, b)


@dataclass
class Pipeline:
    chart: Chart
    ledger: Ledger
    moves: list[Move] = field(default_factory=list)
    closing_entries: list[Entry] = field(default_factory=list)

    def __post_init__(self):
        self.ledger = deepcopy(self.ledger)

    def move(self, from_: str, to_: str):
        self.moves.append(move := Move(from_, to_))
        entry = move.to_entry(self.ledger)
        self.closing_entries.append(entry)
        self.ledger.post(entry)
        return self

    def close_contra(self, t):
        for name, contra_name in contra_pairs(self.chart, t):
            self.move(contra_name, name)
        return self

    def close_contra_all(self):
        for t in T:
            self.close_contra_accounts(t)
        return self

    def close_isa(self):
        for name in chart.regular_names(T.Income) + chart.regular_names(T.Expense):
            self.move(name, self.chart.income_summary_account)
        return self

    def close_re(self):
        return self.move(
            self.chart.income_summary_account, self.chart.retained_earnings_account
        )

    def close_first(self):
        return self.close_contra(T.Income).close_contra(T.Expense)

    def close_second(self):
        return self.close_isa().close_re()

    def close_last(self):
        return (
            self.close_contra(T.Asset).close_contra(T.Capital).close_contra(T.Liability)
        )

    def flush(self):
        self.closing_entries = []
        self.moves = []
        return self


print(Pipeline(chart, ledger).close_contra(T.Income).moves)
print(Pipeline(chart, ledger).close_contra(T.Capital).moves)
print(
    (
        p := Pipeline(chart, ledger)
        .close_contra(T.Income)
        .close_contra(T.Expense)
        .flush()
        .close_isa()
    ).moves
)
print(a := p.flush().close_re().closing_entries[0])
print(
    b := double_entry(
        "_isa",
        "retained_earnings",
        12,
    )
)
assert a == b


def close(chart, ledger):
    return Pipeline(chart, ledger).close_first().close_second().close_last().ledger


# ledger does not change
assert ledger.balances["retained_earnings"] == 0
assert close(chart, ledger).balances["retained_earnings"] == 12
assert ledger.net_tuple_balances["retained_earnings"] == (0, 0)

# netted buyback 1200-200=1000
assert close(chart, ledger).balances["equity"] == 1000


assert ledger.subset(Asset).balances == {"cash": 1012, "ar": 5}

# - Entry may be a dataclass with records field, checked by is_balanced
# - Statement and viewers classes next
# - Company with chart and entries from experimental.py are next
