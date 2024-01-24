"""Accounting chart, journal and reports."""

from abc import ABC
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


class AccountType(ABC):
    @property
    def side(self) -> Side:
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
    _side: Side

    # workaround for mypy
    @property
    def side(self):
        return self._side


def which(t: T) -> Side:
    if t in [T.Asset, T.Expense]:
        return Side.Debit
    return Side.Credit


def reverse(side: Side):
    if side == Side.Debit:
        return Side.Credit
    elif side == Side.Credit:
        return Side.Debit


# not used
@dataclass
class Label:
    prefix: str
    name: str


# not used
@dataclass
class Offset:
    points_to: str
    name: str


def assert_reference_exists(key, keys):
    if key not in keys:
        raise KeyError(
            f"Account '{key}' not in chart, cannot add a contrа account to it."
        )


@dataclass
class ChartDict:
    regular_accounts: dict[str, T] = field(default_factory=dict)
    contra_accounts: dict[str, str] = field(default_factory=dict)

    def add(self, t: T, name: str):
        """Add regular account to chart."""
        self.regular_accounts[name] = t
        return self

    def offset(self, name: str, contra_name: str):
        """Offset an existing account `name` in chart with a new `contra_name`."""
        assert_reference_exists(name, self.regular_accounts.keys())
        self.contra_accounts[contra_name] = name
        return self

    def contra_pairs(self, t: T) -> list[tuple[str, str]]:
        """List contra accounts, result should similar to
        `[('sales', 'refunds'), ('sales', 'voids')]`."""
        return [
            (name, contra_name)
            for contra_name, name in self.contra_accounts.items()
            if self.regular_accounts[name] == t
        ]

    def regular_names(self, *ts: T) -> list[str]:
        """List regular account names by type."""
        return [name for name, t in self.regular_accounts.items() if t in ts]

    def __getitem__(self, name: str) -> Contra | Regular:
        """Return regular or contra account for `name`."""
        if name in self.regular_accounts:
            return Regular(self.regular_accounts[name])
        if name in self.contra_accounts:
            return Contra(self.regular_accounts[self.contra_accounts[name]])
        raise KeyError(name)

    def items(self):
        for k in list(self.regular_accounts.keys()) + list(self.contra_accounts.keys()):
            yield k, self[k]


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
    flavor: AccountType
    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    @property
    def side(self) -> Side:
        return self.flavor.side

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
        match self.side:
            case Side.Debit:
                a, b = [self.balance()], []
            case Side.Credit:
                a, b = [], [self.balance()]
            case _:
                raise ValueError(self)
        return self.__class__(self.flavor, a, b)

    def balance(self):
        """Return account balance."""
        a, b = self.tuple()
        match self.side:
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
        for key, account_type in chart_dict.items():
            journal[key] = Account(account_type)
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

    def condense(self):
        cls = self.__class__
        return cls({n: a.condense() for n, a in self.items()})

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
        return cls({k: a for k, a in self.items() if a.flavor == Regular(t)})


@dataclass
class Move:
    """Indicate how to transfer the account balances.
    Helps to trace closing entries."""

    frm: str
    to: str

    def to_entry(self, journal):
        account = journal[self.frm]
        b = account.balance()
        match account.side:
            case Side.Debit:
                return double_entry(self.to, self.frm, b)
            case Side.Credit:
                return double_entry(self.frm, self.to, b)


@dataclass
class Pipeline:
    """A pipeline to accumulate ledger transformations."""

    chart: Chart
    journal: Journal
    moves: list[Move] = field(default_factory=list)
    closing_entries: list[Entry] = field(default_factory=list)

    def __post_init__(self):
        self.journal = self.journal.condense()

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
        """Close contra accounts for permanent accounts (for assets, capital and liabilities)."""
        return self.close_contra(T.Asset, T.Capital, T.Liability)

    def flush(self):
        self.closing_entries = []
        self.moves = []
        return self


def close(chart, journal):
    return Pipeline(chart, journal).close_first().close_second().close_last().journal


def statements(chart, journal):
    t1 = trial_balance(journal)
    a = Pipeline(chart, journal).close_first().journal.condense()
    b = Pipeline(chart, a).close_second().close_last().journal.condense()
    t2 = trial_balance(b)
    return t1, IncomeStatement.new(a), BalanceSheet.new(b), t2


def income_statement(chart, journal):
    return IncomeStatement.new(Pipeline(chart, journal).close_first().journal)


def balance_sheet(chart, journal):
    return BalanceSheet.new(close(chart, journal))


class Statement:
    ...


AccountBalances = dict[str, Amount]


@dataclass
class BalanceSheet(Statement):
    assets: AccountBalances
    capital: AccountBalances
    liabilities: AccountBalances

    @classmethod
    def new(cls, journal: Journal):
        return cls(
            assets=journal.subset(T.Asset).balances,
            capital=journal.subset(T.Capital).balances,
            liabilities=journal.subset(T.Liability).balances,
        )


@dataclass
class IncomeStatement(Statement):
    income: AccountBalances
    expenses: AccountBalances

    @classmethod
    def new(cls, journal: Journal):
        return cls(
            income=journal.subset(T.Income).balances,
            expenses=journal.subset(T.Expense).balances,
        )

    @property
    def current_profit(self):
        return sum(self.income.values()) - sum(self.expenses.values())


class TrialBalance(UserDict[str, tuple[Amount, Amount, Side]], Statement):
    """Trial balance is a dictionary of account names and
    their debit side and credit side balances."""

    @classmethod
    def new(cls, journal: Journal):
        tb = cls()
        for side in [Side.Debit, Side.Credit]:
            for name, account in journal.items():
                if account.side == side:
                    x, y = account.tuple()
                    tb[name] = x, y, side
        return tb

    def net(self):
        """Show net balance on proper side of account."""
        tb = self.__class__()
        for n, (a, b, s) in self.items():
            if s == Side.Debit:
                tb[n] = a - b, 0, s
            else:
                tb[n] = 0, b - a, s
        return tb

    def drop_null(self):
        """Drop accounts where balance is null."""
        # These are usually temporary and intermediate accounts after closing.
        tb = self.__class__()
        for n, (a, b, s) in self.items():
            if (a + b) == 0:
                continue
            tb[n] = (a, b, s)
        return tb

    def brief(self) -> dict[str, tuple[Amount, Amount]]:
        """Hide information about debit or credit side of accounts."""
        return {n: (a, b) for n, (a, b, _) in self.items()}

    def balances(self) -> dict[str, Amount]:
        """Return dictionary with account balances."""
        return {n: a + b for n, (a, b, _) in self.net().items()}


def trial_balance(journal) -> TrialBalance:
    return TrialBalance.new(journal)


if __name__ == "__main__":
    chart = (
        Chart(income_summary_account="isa", retained_earnings_account="re")
        .add_many(T.Asset, "cash", "ar")
        .add(T.Capital, "equity", contra_names=["buyback"])
        .add(T.Income, "sales", contra_names=["refunds", "voids"])
        .add(T.Liability, "vat")
        .add(T.Expense, "salary")
    )
    journal = Journal.from_chart(chart)
    journal.post_many(
        [
            double_entry("cash", "equity", 1200.5),
            double_entry("buyback", "cash", 200.5),
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
    t, i, b, final_t = statements(chart, journal)
    print(t.brief())
    print(b)
    print(i)
    print(i.current_profit)
    print(final_t.drop_null().brief())

    # Next:
    # - test TrialBalance
    # - viewers (separate file)
    # - company with chart and transactions from experimental.py
