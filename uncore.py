from dataclasses import dataclass, field
from collections import UserDict
from enum import Enum
from decimal import Decimal


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
    offsets: str


class ChartDict(UserDict[str, T | str]):
    @property
    def regular_names(self):
        return self.data.keys()

    @property
    def contra_names(self):
        return [v.offsets for v in self.data.values() if isinstance(v, Contra)]

    def update(self, t, name):
        self.data[name] = Regular(t)

    def offset(self, name, contra_name):
        if name in self.regular_names:
            self.data[contra_name] = Contra(name)

    def verify(self, name, contra_names: list[str]):
        if name in self.regular_names:
            raise ValueError(name)
        for contra_name in contra_names:
            if (contra_name in self.regular_names) or (
                contra_name in self.contra_names
            ):
                raise ValueError(contra_name)

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
        match self.data[name]:
            case Regular(T.Asset):
                return DebitAccount
            case Regular(T.Expense):
                return DebitAccount
            case Regular(T.Capital):
                return CrediteditAccount
            case Regular(T.Liability):
                return CrediteditAccount
            case Regular(T.Income):
                return CrediteditAccount
            case Contra(name):
                return reverse(self.constructor(name))

    @property
    def ledger(self):
        return Ledger({k: self.constructor(k)() for k in self.data.keys()})


Amount = Decimal


@dataclass
class Debit:
    debit: str
    amount: Amount


@dataclass
class Credit:
    credit: str
    amount: Amount


Entry = list[Debit | Credit]


def double_entry(debit, credit, amount) -> Entry:
    return [Debit(debit, amount), Credit(credit, amount)]


from abc import ABC, abstractmethod


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

    @abstractmethod
    def transfer_balance(self, my_name: str, dest_name: str) -> "Entry":
        """Crediteate an entry that transfers account balance from this account
        to destination account.

        This account name is `my_name` and destination account name is `dest_name`.
        """

    def condense(self):
        """Crediteate a new account of the same type with only one value as account balance."""
        return self.empty().topup(self.balance())

    def empty(self):
        """Crediteate a new empty account of the same type."""
        return self.__class__()

    def topup(self, balance):
        """Add starting balance to a proper side of account."""
        match self:
            case DebitAccount(_, _):
                self.debit(balance)
            case CrediteditAccount(_, _):
                self.credit(balance)
        return self


class DebitAccount(TAccount):
    def balance(self):
        return sum(self.debits) - sum(self.credits)

    def tuple_balance(self):
        return (self.balance(), 0)

    def transfer_balance(self, my_name: str, dest_name: str) -> Entry:
        return double_entry(debit=dest_name, credit=my_name, amount=self.balance())


class CrediteditAccount(TAccount):
    def balance(self):
        return sum(self.credits) - sum(self.debits)

    def tuple_balance(self):
        return (0, self.balance())

    def transfer_balance(self, my_name: str, dest_name: str) -> Entry:
        return double_entry(debit=my_name, credit=dest_name, amount=self.balance())


def reverse(a: DebitAccount | CrediteditAccount):
    match a.__name__:
        case "DebitAccount":
            return CrediteditAccount
        case "CrediteditAccount":
            return DebitAccount


class Ledger(UserDict[str, "TAccount"]):
    def post(self, entry: Entry):
        for record in entry:
            match record:
                case Debit(name, amount):
                    self.data[name].debit(amount)
                case Credit(name, amount):
                    self.data[name].credit(amount)
        return self

    def post_many(self, entries: list[Entry]):
        for entry in entries:
            self.post(entry)
        return self

    def balances(self):
        return {name: account.balance() for name, account in self.data.items()}

    def tuple_balances(self):
        return {name: account.tuple_balance() for name, account in self.data.items()}


def offset(name, contra_name):
    return name, [contra_name]


chart_dict = (
    ChartDict()
    .add(T.Asset, "cash")
    .add(T.Capital, "equity", contra_names=["treasury_stock"])
    .add(T.Income, "sales", contra_names=["refunds", "voids"])
    .add(T.Liability, "vat")
)


ledger = chart_dict.ledger.post_many(
    [
        double_entry("cash", "equity", 1200),
        double_entry("treasury_stock", "cash", 200),
        [Debit("cash", 70), Credit("sales", 60), Credit("vat", 10)],
        [Debit("voids", 15), Debit("refunds", 15), Debit("vat", 5), Credit("cash", 35)],
    ]
)
print(ledger.tuple_balances())

from copy import copy


@dataclass
class Chart:
    retained_earnings_account: str
    income_summary_account: str
    chart_dict: ChartDict

    def __post_init__(self):
        self.chart_dict.update(T.Capital, self.retained_earnings_account)

    def ledger0(self):  # no starting balances
        ledger = self.chart_dict.ledger
        ledger[self.income_summary_account] = CrediteditAccount()
        return ledger


@dataclass
class Company:
    chart: ChartDict
    entries: list[Entry]

    # may cache
    def ledger(self):  # no starting balances
        return self.chart.ledger0().post_many(self.entries)

    def close(self):
        """Post closing entries."""

    def _income_statement_balances(self):
        # disregard entries that affect income summary account + close income and expense accounts
        ...


def contra_pairs(chart_dict, t):
    return [
        (p.offsets, name)
        for name, p in chart_dict.items()
        if isinstance(p, Contra) and chart_dict[p.offsets] == Regular(t)
    ]


assert contra_pairs(chart_dict, T.Income) == [("sales", "refunds"), ("sales", "voids")]
assert contra_pairs(chart_dict, T.Capital) == [("equity", "treasury_stock")]


@dataclass
class Closer:
    chart_dict: ChartDict
    ledger: Ledger
    closing_entries: list[Entry] = field(default_factory=list)

    def close(self, t):
        for name, contra_name in contra_pairs(chart_dict, t):
            e = self.ledger[contra_name].transfer_balance(contra_name, name)
            self.closing_entries.append(e)
        return self

    def close_all(self):
        for t in T:
            self.close(t)
        return self

    def close_re(self, isa: str, re: str):
        for name, p in chart_dict.items():
            if p in [Regular(T.Income), Regular(T.Expense)]:
                e = self.ledger[name].transfer_balance(name, isa)
                self.closing_entries.append(e)
                self.ledger.post(e)
        e0 = self.ledger[isa].transfer_balance(isa, re)
        self.closing_entries.append(e0)
        return self

    def close(self, isa, re):
        return self.close_all().close_re(isa, re)


print(Closer(chart_dict, ledger).close(T.Income).closing_entries)
print(Closer(chart_dict, ledger).close_all().closing_entries)
