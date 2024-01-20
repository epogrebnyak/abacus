from abc import ABC, abstractmethod
from collections import UserDict, namedtuple
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
    def __setitem__(self, name: str, value: Regular | Contra):
        if isinstance(value, Contra) and value.links_to not in self.data.keys():
            raise KeyError(
                f"Account '{name}' is not in chart, "
                "cannot add a contrа account to it."
            )
        self.data[name] = value

    def add_regular(self, t: T, name: str):
        """Add regular account to chart."""
        self[name] = Regular(t)
        return self

    def add_offset(self, name: str, contra_name: str):
        """Offset an existing account in chart with a new contra account."""
        self[contra_name] = Contra(links_to=name)
        return self

    def contra_pairs(self, t: T) -> list[tuple[str, str]]:
        """List contra accounts, similar to `[('sales', 'refunds')]`."""
        return [
            (p.links_to, name)
            for name, p in self.items()
            if isinstance(p, Contra) and self[p.links_to] == Regular(t)
        ]

    def regular_names(self, ts: list[T]) -> list[str]:
        """List regular account names by type."""
        return [n for t in ts for n, p in self.items() if p == Regular(t)]


@dataclass
class Chart:
    retained_earnings_account: str = "retained_earnings"
    income_summary_account: str = "income_summary_account"
    dict: ChartDict = field(default_factory=ChartDict)

    def add_many(self, t, *names: str):
        for name in names:
            self.add(t, name)
        return self

    def add(self, t: T, name: str, contra_names: list[str] | None = None):
        self.dict.add_regular(t, name)
        if contra_names is None:
            return self
        for contra_name in contra_names:
            self.dict.add_offset(name, contra_name)
        return self

    def constructor(self, name):
        match self.dict[name]:
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
        self.dict[self.retained_earnings_account] = Regular(T.Capital)
        ledger = Ledger({k: self.constructor(k)() for k in self.dict.keys()})
        ledger[self.income_summary_account] = IncomeSummaryAccount()
        return ledger


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


def is_balanced(entry: Entry) -> bool:
    def sums(f):
        return sum([r.amount for r in entry if f(r)])

    return sums(f=is_debit) == sums(f=is_credit)


@dataclass
class TAccount(ABC):
    """T-account will hold amounts on debits and credit side."""

    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    def debit(self, amount: Amount) -> None:
        """Add debit amount to account."""
        self.debits.append(amount)

    def credit(self, amount: Amount) -> None:
        """Add credit amount to account."""
        self.credits.append(amount)

    @property
    @abstractmethod
    def side(self) -> Side:
        """Return side of account netting, either debit or credit."""

    # NOTE: may be cached and checked later
    def balance(self) -> Amount:
        """Return account balance."""
        return sum(self.balance_tuple_net())

    def balance_tuple(self) -> tuple[Amount, Amount]:
        """Return a tuple of debit and credit side balances."""
        return (sum(self.debits), sum(self.credits))

    def balance_tuple_net(self) -> tuple[Amount, Amount]:
        """Return a tuple of netted debit and credit side balances."""
        a, b = self.balance_tuple()
        match self.side:
            case Side.Debit:
                return (a - b, 0)
            case Side.Credit:
                return (0, b - a)

    def condense(self) -> "TAccount":
        """Create a new account of the same type with only one value as account balance."""
        return self.empty().topup(self.balance())

    def empty(self) -> "TAccount":
        """Create a new empty account of the same type."""
        return self.__class__()

    def topup(self, balance) -> "TAccount":
        """Add starting balance to the proper side of account."""
        match self.side:
            case Side.Debit:
                self.debit(balance)
                return self
            case Side.Credit:
                self.credit(balance)
                return self


class DebitAccount(TAccount):
    @property
    def side(self):
        return Side.Debit

    @staticmethod
    def reverse():
        return CreditAccount


class CreditAccount(TAccount):
    @property
    def side(self):
        return Side.Credit

    @staticmethod
    def reverse():
        return DebitAccount


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


class LedgerError(Exception):
    ...


class Ledger(UserDict[str, TAccount]):
    def post(self, entry: Entry):
        if not is_balanced(entry):
            raise LedgerError(entry)
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
    def balance_tuples(self):
        return {name: account.balance_tuple() for name, account in self.data.items()}

    @property
    def net_balance_tuples(self):
        return {
            name: account.balance_tuple_net() for name, account in self.data.items()
        }

    def subset(self, ta: Type[TAccount]):
        return self.__class__({k: v for k, v in self.items() if isinstance(v, ta)})


@dataclass
class Move:
    """Indicate where from and where to transfer the account balances.
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
        self.ledger = Ledger({n: a.condense() for n, a in self.ledger.items()})

    def move(self, frm: str, to: str):
        """Transfer balance of account `frm` to account `to`."""
        self.moves.append(move := Move(frm, to))
        entry = move.to_entry(self.ledger)
        self.closing_entries.append(entry)
        self.ledger.post(entry)
        return self

    def close_contra(self, ts: list[T]):
        """Close contra accounts that offset accounts of types `ts`."""
        for t in ts:
            for name, contra_name in self.chart.dict.contra_pairs(t):
                self.move(contra_name, name)
        return self

    def close_temporary(self):
        """Close temporary accounts (income, expenses) and transfer their balances
        to income summary account."""
        for name in chart.dict.regular_names([T.Income, T.Expense]):
            self.move(name, self.chart.income_summary_account)
        return self

    def close_isa(self):
        """Transfer balance from income summary account to retained earnings account."""
        isa = self.chart.income_summary_account
        re = self.chart.retained_earnings_account
        return self.move(isa, re)

    def close_first(self):
        """Close contra accounts to income and expenses.
        Makes ledger ready for income statement."""
        return self.close_contra([T.Income, T.Expense])

    def close_second(self):
        """Close income summary account and move balance to retained earnings.
        Should be used after .close_first() method."""
        return self.close_temporary().close_isa()

    def close_last(self):
        """Do netting (close contra accounts) for permanent accounts."""
        return self.close_contra([T.Asset, T.Capital, T.Liability])

    def flush(self):
        self.closing_entries = []
        self.moves = []
        return self


def close(chart, ledger):
    return Pipeline(chart, ledger).close_first().close_second().close_last().ledger


def statements(chart, ledger):
    a = Pipeline(chart, ledger).close_first()
    b = Pipeline(chart, ledger).close_first().close_second().close_last()
    return a.ledger, b.ledger


if __name__ == "__main__":
    chart = (
        Chart()
        .add_many(T.Asset, "cash", "ar")
        .add(T.Capital, "equity", contra_names=["buyback"])
        .add(T.Income, "sales", contra_names=["refunds", "voids"])
        .add(T.Liability, "vat")
        .add(T.Expense, "salary")
    )
    print(chart)
    ledger = chart.create_ledger()
    print(ledger)
    ledger.post_many(
        [
            double_entry("cash", "equity", 1200),
            double_entry("buyback", "cash", 200),
            [debit("ar", 70), credit("sales", 60), credit("vat", 10)],
            double_entry("cash", "ar", 30),
            [
                debit("voids", 20),
                debit("refunds", 10),
                debit("vat", 5),
                credit("ar", 35),
            ],
            [debit("salary", 18), credit("cash", 18)],
        ]
    )
    print(ledger.balances)
    assert ledger.balances == {
        "cash": 1012,
        "ar": 5,
        "equity": 1200,
        "buyback": 200,
        "sales": 60,
        "refunds": 10,
        "voids": 20,
        "vat": 5,
        "salary": 18,
        "retained_earnings": 0,
        "income_summary_account": 0,
    }
    print(ledger.balance_tuples)
    print(ledger.net_balance_tuples)
    print(Pipeline(chart, ledger).close_contra([T.Income]).moves)
    print(Pipeline(chart, ledger).close_contra([T.Capital]).moves)
    print(
        (
            p := Pipeline(chart, ledger)
            .close_contra([T.Income, T.Expense])
            .flush()
            .close_temporary()
        ).moves
    )
    print(a := p.flush().close_isa().closing_entries[0])
    print(
        b := double_entry(
            chart.income_summary_account,
            "retained_earnings",
            12,
        )
    )
    assert a[0] == b[0]
    assert a[1] == b[1]

    # ledger does not change
    assert ledger.balances["retained_earnings"] == 0
    assert close(chart, ledger).balances["retained_earnings"] == 12
    assert ledger.balance_tuples["retained_earnings"] == (0, 0)

    # netted buyback 1200-200=1000
    assert close(chart, ledger).balances["equity"] == 1000

    assert ledger.subset(Asset).balances == {"cash": 1012, "ar": 5}

    # - Entry may be a dataclass with records field, checked by is_balanced
    # - Statement and viewers classes next
    # - Company with chart and entries from experimental.py are next
