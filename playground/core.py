"""Accounting module for double-entry bookkeeping.

Accounting workflow used:
1. create chart of accounts
2. create ledger from chart
3. post entries to ledger
4. show trial balance at any time
5. close ledger at accounting period end and produce income statement
6. make post-close entries and produce balance sheet
7. save permanent account balances for next period  

Accounting conventions used:
- regular accounts of 5 types (asset, liability, capital, income, expense)
- contra accounts to regular accounts are possibe (eg depreciation, discounts, etc.)
- the only intermediate account is income summary account used for profit calculation
- accounts holds amounts on debit and credit side ("T-account")
- the balancing side of the account can be fixed (eg asset is always debit side)
  or can be determined by the balance (eg income summary account is credit side 
  if balance is positive)
- accounts balances cannot go negative

Assumptions and simplifications (some may be relaxed in future versions): 
- one level of accounts, no subaccounts
- account names must be globally unique
- chart always has "retained earnigns account"
- chart always has "income summary account" 
- there are no journals, entries are posted to ledger directly
- an entry can touch any accounts
- entry amount can be positive or negative 
- one currency
- net earnings are income less expenses, no gross profit or profit before tax calculated    
- period end closing tranfsers net earnings to retained earnings
- no cash flow statement
- no statement of changes in equity
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

    def is_debit(self) -> bool:
        """Return True if this is a debit side."""
        return self == Side.Debit

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


class AccountDefinition(ABC):
    """Abstract base class for regular, contra or intermediate account definitions.

    Parent class for Regular, Contra and Intermediate classes.

    Usage examples of child classes:
        Regular(T5.Asset)
        Contra(T5.Income)
        Intermediate(Profit.IncomeSummaryAccount)

    Regular and Contra classes define any of five account types
    and their contra accounts. Intermediate class used for profit accounts
    that live for a short while when closing the ledger.
    """

    @property
    @abstractmethod
    def side(self) -> Side:
        """Indicate balancing side of account (debit or credit)."""
        pass

    def taccount(self):
        """Create T-account for this account definition."""
        match self.side:
            case Side.Debit:
                return DebitAccount()
            case Side.Credit:
                return CreditAccount()


@dataclass
class Regular(AccountDefinition):
    """Regular account of any of five types of accounts."""

    t: T5

    @property
    def side(self) -> Side:
        return self.t.side


@dataclass
class Contra(AccountDefinition):
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
class Intermediate(AccountDefinition):
    """Intermediate account, used for profit accounts only."""

    t: Profit

    @property
    def side(self) -> Side:
        if isinstance(self.t, Profit):
            return Side.Credit
        raise AbacusError("Unknown intermediate account: " + str(self.t))

    def taccount(self):
        if isinstance(self.t, Profit):
            return DebitOrCreditAccount()
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
        """Shorthand method for creating a multiple entry with commas:

        Example:
            MultipleEntry.new(DebitEntry("cash", 100), CreditEntry("equity", 100))

        """
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
    """Base class for streams of entries."""

    @property
    @abstractmethod
    def multiple_entry(self) -> MultipleEntry:
        """Return multiple entry."""
        pass

    def __iter__(self):
        """Make class iterable, similar to list[SingleEntry].
        Will validate entry before iterating (but this is not very clean)
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
class Account:
    """Account definition with account name and names of associated contra accounts."""

    name: AccountName
    contra_accounts: list[AccountName] = field(default_factory=list)

    def stream(self, account_type: T5):
        """Yield account definitions for the regular account
        and associated contra accounts (if any).
        """
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

    def dict(self) -> dict[AccountName, AccountDefinition]:
        """Return chart as a dictionary with unique account names"""
        return dict(self.items())

    def items(self) -> Iterable[tuple[AccountName, Regular | Contra | Intermediate]]:
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
        self.assert_unique_names()

    def assert_unique_names(self) -> None:
        """Ensure all account names in chart are unique."""
        unique_names = list(self.dict().keys())
        all_names = [x[0] for x in self.items()]
        if len(unique_names) != len(all_names):
            n = len(all_names) - len(unique_names)
            raise AbacusError(
                [
                    f"Chart contains {n} duplicate account names",
                    set(all_names) - set(unique_names),
                    sorted(unique_names),
                    sorted(all_names),
                ]
            )


@dataclass
class TAccountBase(ABC):
    """Base class for T-account that holds amounts on the left and right sides."""

    left: Amount = Amount(0)
    right: Amount = Amount(0)

    def debit(self, amount: Amount):
        """Add amount to debit side of T-account."""
        self.left += amount

    def credit(self, amount: Amount):
        """Add amount to credit side of T-account."""
        self.right += amount

    @property
    @abstractmethod
    def balance(self) -> Amount:
        pass

    @property
    @abstractmethod
    def side(self) -> Side:
        pass

    def make_closing_entry(
        self, my_name: AccountName, destination_name: AccountName
    ) -> "DoubleEntry":
        """
        Make closing entry to transfer balance from *my_name* account
        to *destination_name* account.

        When closing debit account, the closing entry will be:
           - Cr my_name
           - Dr destination_name

        When closing credit account, the closing entry will be:
            - Dr my_name
            - Cr destination_name
        """
        match self.side:
            case Side.Debit:
                return DoubleEntry(
                    debit=destination_name, credit=my_name, amount=self.balance
                )
            case Side.Credit:
                return DoubleEntry(
                    debit=my_name, credit=destination_name, amount=self.balance
                )


class UnrestrictedDebitAccount(TAccountBase):

    @property
    def balance(self) -> Amount:
        return self.left - self.right

    @property
    def side(self):
        return Side.Debit


class UnrestrictedCreditAccount(TAccountBase):

    @property
    def balance(self) -> Amount:
        return self.right - self.left

    @property
    def side(self):
        return Side.Credit


class DebitAccount(UnrestrictedDebitAccount):

    def credit(self, amount: Amount):
        if amount > self.balance:
            raise AbacusError(
                f"Account balance is {self.balance}, cannot credit {amount}."
            )
        self.right += amount


class CreditAccount(UnrestrictedCreditAccount):

    def debit(self, amount: Amount):
        if amount > self.balance:
            raise AbacusError(
                f"Account balance is {self.balance}, cannot debit {amount}."
            )
        self.left += amount


class DebitOrCreditAccount(TAccountBase):
    """Account that can be either debit or credit depending on the balance."""

    @property
    def balance(self) -> Amount:
        return abs(self.left - self.right)

    @property
    def side(self) -> Side:
        if self.right >= self.left:
            return Side.Credit
        return Side.Debit


class Ledger(UserDict[AccountName, TAccountBase]):
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
        return {name: account.balance for name, account in self.items()}

    def close(self, chart):
        """Close ledger at accounting period end."""
        return close(self, chart)


def net_balance(ledger: Ledger, account: Account):
    b = ledger[account.name].balance
    for name in account.contra_accounts:
        b -= ledger[name].balance
    return b


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
                account_name: (t_account.side, t_account.balance)
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
        """Return account names and balances."""
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


@dataclass
class BalanceSheet(Report):
    assets: dict[AccountName, Amount]
    capital: dict[AccountName, Amount]
    liabilities: dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger: Ledger, chart: Chart):
        def subset(accounts: list[Account]):
            return {account.name: net_balance(ledger, account) for account in accounts}

        return cls(
            assets=subset(chart.assets),
            capital=subset(chart.capital),
            liabilities=subset(chart.liabilities),
        )


def close(ledger: Ledger, chart: Chart):
    """Close ledger at accounting period end in the following order.

       1. Close income and expense contra accounts.
       2. Close income and expense accounts to income summary account.
       3. Close income summary account to retained earnings.

    Returns:
        closing_entries: list of closing entries,
        ledger: ledger after account closing (only permanent accounts,
                temporary and intermediate accounts will have zero balance
                and will be removed),
        income_summary: income statement data.
    """
    isa = chart.income_summary_account
    re = chart.retained_earnings_account
    closing_entries = []

    def proceed(from_, to_):
        entry = ledger[from_].make_closing_entry(from_, to_)
        closing_entries.append(entry)
        ledger.post(entry)
        del ledger[from_]

    # 1. Close contra income and contra expense accounts
    for account in chart.income + chart.expenses:
        for contra_account_name in account.contra_accounts:
            proceed(from_=contra_account_name, to_=account.name)

    # 2. Close income and expense accounts
    income_summary = IncomeSummary()
    for account in chart.income:
        b = ledger[account.name].balance
        income_summary.income[account.name] = b
        proceed(from_=account.name, to_=isa)
    for account in chart.expenses:
        b = ledger[account.name].balance
        income_summary.expenses[account.name] = b
        proceed(account.name, isa)

    # 3. Close income summary account to retained earnings account
    proceed(isa, re)

    # NOTE: we actually did mutate the incoming ledger, may want to create a copy instead
    return closing_entries, ledger, income_summary
