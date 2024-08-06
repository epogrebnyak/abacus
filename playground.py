"""Accounting module for double-entry bookkeeping.

add assumptions from issue 80 
and:
- account is always defined as either debit side or credit side
- no journals, entries get posted to ledger directly
- how closing is made
- net earnings made of income and expenses, no gross profit or profit before tax calculated    
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
    """Indicate debit or credit side of the account."""

    Debit = "debit"
    Credit = "credit"

    def reverse(self) -> "Side":
        """Change side from debit to credit or vice versa."""
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

    @property
    def side(self) -> Side:
        """Indicate side of account (debit or credit)."""
        if self in [T5.Asset, T5.Expense]:
            return Side.Debit
        return Side.Credit


class Holder(ABC):
    """Abstract base class for regular, contra or intermediate account definitation.

    Parent class for Regular, Contra and Intermediate classes.

    Usage examples:
        Regular(T5.Asset)
        Contra(T5.Income)
        Intermediate(Profit.IncomeSummaryAccount)

    Regular and Contra constructors define any of five account types
    and their contra accounts. Intermediate constructor used for
    profit accounts, that live for a short while when closing the ledger.
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
    """Regular account of any of five types."""

    t: T5

    @property
    def side(self) -> Side:
        return self.t.side


@dataclass
class Contra(Holder):
    """A contra account to any of five types of accounts.

    Examples of contra accounts (generated text below):
        - contra property, plant, equipment: accumulated depreciation
        - contra liability: discount on bonds payable
        - contra capital: treasury stock
        - contra income: refunds
        - contra expense: purchase discounts
    """

    t: T5

    @property
    def side(self) -> Side:
        return self.t.side.reverse()


class Profit(Enum):
    IncomeSummaryAccount = "isa"
    OtherComprehensiveIncome = "oci"  # not implemented yet


@dataclass
class Intermediate(Holder):
    """Intermediate account, used for profit accounts only."""

    t: Profit

    @property
    def side(self) -> Side:
        if isinstance(self.t, Profit):
            return Side.Credit
        raise AbacusError("Unknown intermediate account: " + str(self.t))


@dataclass
class SingleEntry(ABC):
    """Single entry changes either a debit or a credit side of an account."""

    name: AccountName
    amount: Amount


class DebitEntry(SingleEntry):
    """An entry that increases the debit side of an account."""


class CreditEntry(SingleEntry):
    """An entry that increases the credit side of an account."""


class MultipleEntry(UserList[SingleEntry]):
    """Multiple entry is a list of single entries."""

    @classmethod
    def new(cls, *entries) -> "MultipleEntry":
        """Shorthand method for creating a multiple entry with commas."""
        return MultipleEntry(entries)  # type: ignore

    def _sum(self, type: type[DebitEntry | CreditEntry]):
        """Sum of entries of either of debit or of credit type."""
        return sum(x.amount for x in self.data if isinstance(x, type))

    def validate(self):
        """Check if sum of debits and sum credits are equal."""
        a = self._sum(DebitEntry)
        b = self._sum(CreditEntry)
        if a == b:
            return self
        raise AbacusError(f"Sum of debits {a} is not equal to sum of credits {b}.")


class EntryBase(Iterable):
    """Base class to derive DoubleEntry and NamedEntry."""

    @property
    @abstractmethod
    def multiple_entry(self) -> MultipleEntry:
        """Return multiple entry."""
        pass

    def __iter__(self):
        """Make class iterable, similar to list[SingleEntry].
        Will validate entry before iterating.
        """
        return self.multiple_entry.validate().__iter__()


@dataclass
class DoubleEntry(EntryBase):
    """Create entry from debit account name, credit account name and entry amount."""

    debit: AccountName
    credit: AccountName
    amount: Amount

    @property
    def multiple_entry(self) -> MultipleEntry:
        return MultipleEntry.new(
            DebitEntry(self.debit, self.amount),
            CreditEntry(self.credit, self.amount),
        )


@dataclass
class NamedEntry(EntryBase):
    """Create entry using .debit() and .credit() methods.

    The syntax is similar to 'medici' package (<https://github.com/flash-oss/medici>).
    """

    title: str
    _amount: Amount | int | float | None = None
    _multiple_entry: MultipleEntry = field(default_factory=MultipleEntry)

    def amount(self, amount: Amount | int | float):
        """Set default amount for this entry."""
        self._amount = amount
        return self

    def _append(self, cls, name, amount):
        a = Amount(amount or self._amount)
        if not a:
            raise AbacusError("Amount is not defined.")
        entry = cls(name, a)
        self._multiple_entry.data.append(entry)
        return self

    def debit(self, name: AccountName, amount: Amount | int | float | None = None):
        """Add debit entry or debit account name."""
        return self._append(DebitEntry, name, amount)

    def credit(self, name: AccountName, amount: Amount | int | float | None = None):
        """Add credit entry or credit account name."""
        return self._append(CreditEntry, name, amount)

    @property
    def multiple_entry(self) -> MultipleEntry:
        return self._multiple_entry


@dataclass
class Account:
    """Account definition with account name and names of associated contra accounts."""

    name: AccountName
    contra_accounts: list[AccountName] = field(default_factory=list)

    def stream(self, account_type: T5):
        """Yield account definitions for original account and associated contra accounts."""
        yield self.name, Regular(account_type)
        for contra_name in self.contra_accounts:
            yield contra_name, Contra(account_type)


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

    def dict(self) -> dict[AccountName, Holder]:
        """Return chart as a dictionary with unique account names"""
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
        """Yield account definitions for a list of accounts."""
        for account in accounts:
            yield from account.stream(account_type)

    def __post_init__(self):
        xs = list(self.dict().keys())
        ys = [x[0] for x in self.items()]
        if len(xs) != len(ys):
            raise AbacusError(
                [
                    "Chart should not contain duplicate account names.",
                    len(xs) - len(ys),
                    set(ys) - set(xs),
                ]
            )


@dataclass
class TAccount:
    """T-account holds amounts on debit and credit side."""

    side: Side
    debits: list[Amount] = field(default_factory=list)
    credits: list[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        """Add amount to debit side of T-account."""
        self.debits.append(amount)

    def credit(self, amount: Amount):
        """Add amount to credit side of T-account."""
        self.credits.append(amount)

    def _is_debit_account(self) -> bool:
        """Return True if this account is a debit-side account."""
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

    def _post(self, entry: SingleEntry):
        """Post single entry to ledger. Will raise `KeyError` if account name is not found."""
        match entry:
            case DebitEntry(name, amount):
                self.data[name].debit(Amount(amount))
            case CreditEntry(name, amount):
                self.data[name].credit(Amount(amount))

    def post(self, entries: Iterable[SingleEntry]):
        """Post a stream of single entries to ledger."""
        failed = []
        for entry in entries:
            try:
                self._post(entry)
            except KeyError:
                failed.append(entry)
        if failed:
            raise AbacusError(["Could not post to ledger:", failed])

    def post_many(self, entries: list[MultipleEntry]):
        """Post several multiple entries to ledger."""
        for entry in entries:
            self.post(entry)

    @property
    def trial_balance(self):
        """Create trial balance from ledger."""
        return TrialBalance.new(self)

    def balances(self) -> dict[str, Amount]:
        """Return account balances."""
        return {name: account.balance() for name, account in self.items()}

    def close(self, chart):
        """Close ledger at accounting period end."""
        return close(self, chart)


class Report(ABC):
    """Base class for financial reports."""

    def dict(self):
        """Allow serialisation."""
        return self.__dict__


class TrialBalance(UserDict[str, tuple[Side, Amount]], Report):
    """Trial balance contains account names, account sides and balances."""

    @classmethod
    def new(cls, ledger: Ledger):
        return cls(
            {
                account_name: (t_account.side, t_account.balance())
                for account_name, t_account in ledger.items()
            }
        )

    def tuples(self) -> dict[str, tuple[Amount, Amount]]:
        """Return account names and a tuples like (0, balances) or (balance, 0)."""

        def to_tuples(side: Side, balance: Amount):
            match side:
                case Side.Debit:
                    return balance, 0
                case Side.Credit:
                    return 0, balance

        return {
            name: to_tuples(side, balance) for name, (side, balance) in self.items()
        }

    def amounts(self) -> dict[str, Amount]:
        """Return account names and amount balances."""
        return {name: balance for name, (_, balance) in self.items()}

    def entries(self) -> list[SingleEntry]:
        """Return trial balance as a list of single entries."""
        return [
            (
                DebitEntry(name, balance)
                if side == Side.Debit
                else CreditEntry(name, balance)
            )
            for name, (side, balance) in self.items()
        ]


@dataclass
class IncomeSummary(Report):
    income: dict[AccountName, Amount] = field(default_factory=dict)
    expenses: dict[AccountName, Amount] = field(default_factory=dict)

    @property
    def net_earnings(self):
        """Calculate net earnings as income less expenses."""
        return sum(self.income.values()) - sum(self.expenses.values())

    # NOTE: will need add income tax posting and more post close accounts.


@dataclass
class BalanceSheet(Report):
    assets: dict[AccountName, Amount]
    capital: dict[AccountName, Amount]
    liabilities: dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger: Ledger, chart: Chart):
        return ledger.trial_balance.amounts()


def close(ledger: Ledger, chart: Chart):
    """Close ledger at accounting period end in the following order.

       1. Close income and expense contra accounts.
       2. Close income and expense accounts to income summary account.
       3. Close income summary account to retained earnings.

    Returns:
        closing_entries: list of closing entries,
        ledger: ledger after account closing (without temporary and intermediate accounts),
        income_summary: income statement data.
    """
    isa = chart.income_summary_account
    re = chart.retained_earnings_account
    closing_entries = []

    def proceed(a, e):
        closing_entries.append(e)
        ledger.post(e)
        del ledger[a]

    # 1. Close contra income and contra expense accounts
    for account in chart.income:
        for a in account.contra_accounts:
            e = DoubleEntry(debit=account.name, credit=a, amount=ledger[a].balance())
            proceed(a, e)
    for account in chart.expenses:
        for a in account.contra_accounts:
            e = DoubleEntry(debit=a, credit=account.name, amount=ledger[a].balance())
            proceed(a, e)

    # 2. Close income and expense accounts
    income_summary = IncomeSummary()
    for account in chart.income:
        a = account.name
        b = ledger[a].balance()
        income_summary.income[a] = b
        e = DoubleEntry(debit=a, credit=isa, amount=b)
        proceed(a, e)
    for account in chart.expenses:
        a = account.name
        b = ledger[a].balance()
        income_summary.expenses[a] = b
        e = DoubleEntry(debit=isa, credit=a, amount=b)
        proceed(a, e)

    # 3. Close to retained earnings
    e = DoubleEntry(debit=isa, credit=re, amount=ledger[isa].balance())
    proceed(isa, e)
    # NOTE: we actually did mutate the incoming ledger, may want to create a copy instead
    return closing_entries, ledger, income_summary


# End-to-end example

# Create chart of accounts
chart = Chart(
    assets=[Account("cash"), Account("ar")],
    capital=[Account("equity")],
    liabilities=[Account("ap")],
    income=[Account("sales", contra_accounts=["refunds"])],
    expenses=[Account("salaries")],
)

# Create ledger from chart
ledger = Ledger.new(chart)

# Define double or multiple entries and post them to ledger
entries = [
    DoubleEntry("cash", "equity", Amount(100)),
    NamedEntry("Sold $200 worth of goods with 10% refund and 50% prepayment")
    .debit("cash", 90)
    .debit("ar", 90)
    .debit("refunds", 20)
    .credit("sales", 200),
    MultipleEntry.new(
        DebitEntry("salaries", Amount(250)), CreditEntry("ap", Amount(250))
    ),
    NamedEntry("Received $10 payment for goods sold")
    .amount(10)
    .debit("cash")
    .credit("ar"),
]
ledger.post_many(entries)

# Close ledger at accounting period end
closing_entries, ledger, income_summary = ledger.close(chart)

# Show income statement data
assert income_summary.dict() == {
    "income": {"sales": 180},
    "expenses": {"salaries": 250},
}

# Show balance sheet data
# TODO: show balance sheet data with contra accounts
balance_sheet = BalanceSheet.new(ledger, chart)
print(balance_sheet)
# - get trail balance
# - create proxy balance
# - close contra accounts
# - create BalanceSheet
# - use depreciation as example
# - maybe need name after contra accounts 

# Show account balances
assert ledger.trial_balance.amounts() == {
    "cash": 200,
    "equity": 100,
    "retained_earnings": -70,
    "ap": 250,
    "ar": 80,
}
