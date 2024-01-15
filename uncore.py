from abc import ABC, abstractmethod
from collections import UserDict
from copy import copy, deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


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


@dataclass
class Chart:
    income_summary_account: str
    retained_earnings_account: str
    accounts: dict[str, Regular | Contra] = field(default_factory=dict)

    def __post_init__(self):
        self.accounts[self.retained_earnings_account] = Regular(T.Capital)

    def names(self, t):
        return [k for k, v in self.accounts.items() if isinstance(v, t)]

    def update(self, t, name):
        self.accounts[name] = Regular(t)
        return self

    def offset(self, name, contra_name):
        if name in self.names(Regular):
            self.accounts[contra_name] = Contra(name)
        return self

    def verify(self, name, contra_names: list[str]):
        if name in self.names(Regular):
            raise ValueError(name)
        for contra_name in contra_names:
            if contra_name in self.names(Regular) + self.names(Contra):
                raise ValueError(contra_name)

    def add_many(self, t, *names: str, strict: bool = False):
        for name in names:
            self.add(t, name, strict=strict)
        return self

    def add(self, t, name, contra_names: list[str] | None = None, strict: bool = False):
        if contra_names is None:
            contra_names = []
        if strict:
            self.verify(name, contra_names)
        self.update(t, name)
        for contra_name in contra_names:
            self.offset(name, contra_name)
        return self

    def constructor(self, name):
        match self.accounts[name]:
            case Regular(T.Asset):
                return DebitAccount
            case Regular(T.Expense):
                return DebitAccount
            case Regular(T.Capital):
                return CreditAccount
            case Regular(T.Liability):
                return CreditAccount
            case Regular(T.Income):
                return CreditAccount
            case Contra(name):
                return self.constructor(name).reverse()
            case _:
                raise ValueError(name)

    def create_ledger(self):
        ledger = Ledger({k: self.constructor(k)() for k in self.accounts.keys()})
        ledger[self.income_summary_account] = IncomeSummaryAccount()
        return ledger


Amount = Decimal | int | float
Record = tuple[Side, str, Amount]
Entry = list[Record]


def debit(name, amount) -> Record:
    return (Side.Debit, name, amount)


def credit(name, amount) -> Record:
    return (Side.Credit, name, amount)


def double_entry(dr, cr, amount) -> Entry:
    return [debit(dr, amount), credit(cr, amount)]


def value(r: Record):
    return r[2]


def is_debit(r: Record):
    return r[0] == Side.Debit


def is_credit(r: Record):
    return r[0] == Side.Credit


def is_valid(rs: list[Record]) -> bool:
    def sumfun(rs, f):
        return sum([value(r) for r in rs if f(r)])

    return sumfun(rs, is_debit) == sumfun(rs, is_credit)


def name(r):
    return r[1]


def to_double_entry(rs) -> tuple[str, str, Amount]:
    a, b = rs[0], rs[1]
    if not (value(a) == value(b)):
        raise ValueError(rs)
    return (name(a), name(b), value(a))


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
    def tuple_balance(self) -> tuple[Amount, Amount]:
        """Return a tuple of debit and credit side balances."""

    def condense(self):
        """Create a new account of the same type with only one value as account balance."""
        return self.empty().topup(self.balance())

    def empty(self):
        """Create a new empty account of the same type."""
        return self.__class__()

    @abstractmethod
    def topup(self, balance):
        """Add starting balance to the proper side of account."""


class DebitAccount(TAccount):
    def topup(self, balance):
        self.debit(balance)

    @staticmethod
    def reverse():
        return CreditAccount

    def balance(self):
        return sum(self.debits) - sum(self.credits)

    def tuple_balance(self):
        return (self.balance(), 0)


class CreditAccount(TAccount):
    def topup(self, balance):
        self.credit(balance)

    @staticmethod
    def reverse():
        return DebitAccount

    def balance(self):
        return sum(self.credits) - sum(self.debits)

    def tuple_balance(self):
        return (0, self.balance())


@dataclass
class RetainedEarningsAccount(CreditAccount):
    ...


@dataclass
class IncomeSummaryAccount(CreditAccount):
    ...


class Ledger(UserDict[str, "TAccount"]):
    def post(self, entry: Entry):
        if not is_valid(entry):
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
    def tuple_balances(self):
        return {name: account.tuple_balance() for name, account in self.data.items()}

    def _find_one(self, account_type):
        names = [k for k, v in self.data.items() if isinstance(v, account_type)]
        if len(names) == 1:
            return names[0]
        else:
            raise ValueError(names)

    @property
    def _isa(self) -> str:
        return self.find_one(IncomeSummaryAccount)

    @property
    def _re(self) -> str:
        return self.find_one(RetainedEarningsAccount)


chart = (
    Chart("isa", "retained_earnings")
    .add_many(T.Asset, "cash", "ar")
    .add(T.Capital, "equity", contra_names=["provisions", "treasury_stock"])
    .add(T.Income, "sales", contra_names=["refunds", "voids"])
    .add(T.Liability, "vat")
    .add(T.Expense, "salary")
)
print(chart)


ledger = chart.create_ledger().post_many(
    [
        double_entry("cash", "equity", 1200),
        double_entry("treasury_stock", "cash", 200),
        [debit("ar", 70), credit("sales", 60), credit("vat", 10)],
        double_entry("cash", "ar", 30),
        [debit("voids", 20), debit("refunds", 10), debit("vat", 5), credit("ar", 35)],
        double_entry("provisions", "ar", 5),
        [debit("salary", 18), credit("cash", 18)],
    ]
)

print(ledger.tuple_balances)


def contra_pairs(chart: Chart, t: T):
    return [
        (p.links_to, name)
        for name, p in chart.accounts.items()
        if isinstance(p, Contra) and chart.accounts[p.links_to] == Regular(t)
    ]


assert contra_pairs(chart, T.Income) == [("sales", "refunds"), ("sales", "voids")]
assert contra_pairs(chart, T.Capital) == [
    ("equity", "provisions"),
    ("equity", "treasury_stock"),
]


@dataclass
class Move:
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


def transfer_balance_entry(account, from_, to_, balance=None):
    if balance is None:
        balance = account.balance()
    match account:
        case DebitAccount(_, _):
            return double_entry(to_, from_, balance)
        case CreditAccount(_, _):
            return double_entry(from_, to_, balance)


@dataclass
class Pipeline:
    chart: Chart
    ledger: Ledger
    moves: list[Move] = field(default_factory=list)
    closing_entries: list[Entry] = field(default_factory=list)

    def __post_init__(self):
        self.ledger = deepcopy(self.ledger)

    def move(self, from_, to_):
        self.moves.append(move:=Move(from_, to_))
        entry = move.to_entry(self.ledger)
        self.closing_entries.append(entry)
        self.ledger.post(entry)
        return self   

    def close_contra_accounts(self, t):
        for name, contra_name in contra_pairs(self.chart, t):
            self.move(contra_name, name)
        return self

    def close_contra_accounts_all(self):
        for t in T:
            self.close_contra_accounts(t)
        return self

    def close_isa(self):
        for name, p in chart.accounts.items():
            if p in [Regular(T.Income), Regular(T.Expense)]:
                self.move(name, self.chart.income_summary_account)
        return self

    def close_re(self):
        return self.move(self.chart.income_summary_account, self.chart.retained_earnings_account)


    def close(self):
        return self.close_contra_accounts_all().close_isa().close_re()

    def flush(self):
        self.closing_entries = []
        self.moves = []
        return self


print(Pipeline(chart, ledger).close_contra_accounts(T.Income).moves)
print(Pipeline(chart, ledger).close_contra_accounts(T.Capital).moves)
print(Pipeline(chart, ledger).close_contra_accounts_all().moves)
print(
    (
        p := Pipeline(chart, ledger)
        .close_contra_accounts(T.Income)
        .close_contra_accounts(T.Expense)
        .flush()
        .close_isa()
    ).moves
)
assert to_double_entry(p.flush().close_re().closing_entries[0]) == (
    "isa",
    "retained_earnings",
    12,
)


def close(chart, ledger):
    return Pipeline(chart, ledger).close().ledger


# does not change
assert ledger.balances["retained_earnings"] == 0
assert close(chart, ledger).balances["retained_earnings"] == 12
assert ledger.tuple_balances["retained_earnings"] == (0, 0)

# after provisions
assert close(chart, ledger).balances["equity"] == 995
