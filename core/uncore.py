from abc import ABC, abstractmethod
from collections import UserDict, namedtuple
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class Side(Enum):
    Debit = "debit"
    Credit = "credit"


class T(Enum):
    """Five types of accounts and standard prefixes for account names."""

    Asset = "asset"
    Liability = "liability"
    Capital = "capital"
    Income = "income"
    Expense = "expense"


class AccountType:
    ...


@dataclass
class Regular(AccountType):
    t: T

    @property
    def side(self):
        return which(self.t)


@dataclass
class Contra(AccountType):
    t: T

    @property
    def side(self):
        return reverse(which(self.t))


@dataclass
class Intermediate(AccountType):
    side: Side


def which(t: T) -> Side:
    if t in [T.Asset, T.Expense]:
        return Side.Debit
    return Side.Credit


def reverse(side: Side):
    if side == Side.Debit:
        return Side.Credit
    elif side == Side.Credit:
        return Side.Debit


@dataclass
class Reference:
    """Reference class is used for contra account definition.
    `points_to` refers to 'parent' account name."""

    points_to: str


def assert_reference_exists(key, keys):
    if key not in keys:
        raise KeyError(
            f"Account '{key}' not in chart, cannot add a contrа account to it."
        )


@dataclass
class Label:
    prefix: str
    name: str


@dataclass
class Offset:
    points_to: str
    name: str


class ChartDict(UserDict[str, T | Reference]):
    def add(self, t: T, name: str):
        """Add regular account to chart."""
        self[name] = t
        return self

    def offset(self, name: str, contra_name: str):
        """Offset an existing account `name` in chart with a new `contra_name`."""
        assert_reference_exists(name, self.keys())
        self[contra_name] = Reference(name)
        return self

    def contra_pairs(self, t: T) -> list[tuple[str, str]]:
        """List contra accounts, result should similar to
        `[('sales', 'refunds'), ('sales', 'voids')]`."""
        return [
            (value.points_to, name)
            for name, value in self.items()
            if isinstance(value, Reference) and self[value.points_to] == t
        ]

    def regular_names(self, *ts: T) -> list[str]:
        """List regular account names by type."""
        return [name for name, value in self.items() if value in ts]

    def account_type(self, name) -> Contra | Regular:
        """Return regular or contra account type based on `name`."""
        what = self[name]
        if isinstance(what, Reference):
            t: T = self[what.points_to]  # type: ignore
            return Contra(t)
        elif isinstance(what, T):
            return Regular(what)


@dataclass
class Chart:
    income_summary_account: str
    retained_earnings_account: str
    dict: ChartDict = field(default_factory=ChartDict)

    def add_many(self, t, *names: str):
        for name in names:
            self.add(t, name)
        return self

    def add(self, t: T, name: str, contra_names: list[str] | None = None):
        self.dict.add(t, name)
        if contra_names is None:
            return self
        for contra_name in contra_names:
            self.dict.offset(name, contra_name)
        return self


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
class Account:
    account_type: AccountType
    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    def debit(self, amount: Amount) -> None:
        """Add debit amount to account."""
        self.debits.append(amount)

    def credit(self, amount: Amount) -> None:
        """Add credit amount to account."""
        self.credits.append(amount)

    def tuple(self):
        """Return account debits and credit side balance."""
        return sum(self.debits), sum(self.credits)

    def condense(self):
        """Return new account of same type with account balance
        on proper side debit or credit side."""
        match self.account_type.side:
            case Side.Debit:
                a, b = [self.balance()], []
            case Side.Credit:
                a, b = [], [self.balance()]
        return self.__class__(self.account_type, a, b)

    def balance(self):
        """Return account balance."""
        a, b = self.tuple()
        match self.account_type.side:
            case Side.Debit:
                return a - b
            case Side.Credit:
                return b - a


class Journal(UserDict[str, Account]):
    """Ledger that holds T-accounts. Each T-account is referenced by unique name."""

    @classmethod
    def new(
        cls,
        chart_dict: ChartDict,
    ):
        journal = cls()
        for key in chart_dict.keys():
            journal[key] = Account(chart_dict.account_type(key))
        return journal

    @classmethod
    def from_chart(
        cls,
        chart: Chart,
    ):
        return (
            cls.new(chart.dict)
            .set_isa(chart.income_summary_account)
            .set_re(chart.retained_earnings_account)
        )

    def set_isa(self, name):
        self[name] = Account(Intermediate(Side.Credit))
        return self

    def set_re(self, name):
        self[name] = Account(Regular(T.Capital))
        return self

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
    def tuples(self):
        return {name: account.tuple() for name, account in self.data.items()}

    def subset(self, t: T):
        cls = self.__class__
        return cls({k: a for k, a in self.items() if a.account_type == Regular(t)})


@dataclass
class Move:
    """Indicate how to transfer the account balances.
    Helps to trace closing entries."""

    frm: str
    to: str

    def to_entry(self, journal):
        account = journal[self.frm]
        b = account.balance()
        match account.account_type.side:
            case Side.Debit:
                return double_entry(self.to, self.frm, b)
            case Side.Credit:
                return double_entry(self.frm, self.to, b)


@dataclass
class Pipeline:
    chart: Chart
    journal: Journal
    moves: list[Move] = field(default_factory=list)
    closing_entries: list[Entry] = field(default_factory=list)

    def __post_init__(self):
        import copy

        self.journal = copy.deepcopy(self.journal)

    def move(self, frm: str, to: str):
        """Transfer balance of account `frm` to account `to`."""
        self.moves.append(move := Move(frm, to))
        entry = move.to_entry(self.journal)
        self.closing_entries.append(entry)
        self.journal.post(entry)
        return self

    def close_contra(self, *ts: T):
        """Close contra accounts that offset accounts of types `ts`."""
        for t in ts:
            for name, contra_name in self.chart.dict.contra_pairs(t):
                self.move(contra_name, name)
        return self

    def close_temporary(self):
        """Close temporary accounts (income, expenses) and transfer their balances
        to income summary account."""
        for name in self.chart.dict.regular_names(T.Income, T.Expense):
            self.move(name, self.chart.income_summary_account)
        return self

    def close_isa(self):
        """Transfer balance from income summary account to retained earnings account."""
        isa = self.chart.income_summary_account
        re = self.chart.retained_earnings_account
        return self.move(isa, re)

    def close_first(self):
        """Close contra accounts to income and expenses.
        Makes journal ready for income statement."""
        return self.close_contra(T.Income, T.Expense)

    def close_second(self):
        """Close income summary account and move balance to retained earnings.
        Should be used after .close_first() method."""
        return self.close_temporary().close_isa()

    def close_last(self):
        """Do netting (close contra accounts) for permanent accounts."""
        return self.close_contra(T.Asset, T.Capital, T.Liability)

    def flush(self):
        self.closing_entries = []
        self.moves = []
        return self


def close(chart, journal):
    return Pipeline(chart, journal).close_first().close_second().close_last().journal


def statements(chart, journal):
    a = Pipeline(chart, journal).close_first()
    b = Pipeline(chart, journal).close_first().close_second().close_last()
    return a.journal, b.journal


if __name__ == "__main__":
    chart = (
        Chart("isa", "re")
        .add_many(T.Asset, "cash", "ar")
        .add(T.Capital, "equity", contra_names=["buyback"])
        .add(T.Income, "sales", contra_names=["refunds", "voids"])
        .add(T.Liability, "vat")
        .add(T.Expense, "salary")
    )
    journal = Journal.from_chart(chart)
    journal.post_many(
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

    # - Statement and viewers classes next
    # - Company with chart and entries from experimental.py are next
