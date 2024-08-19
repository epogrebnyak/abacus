"""Double-entry bookkeeping module.

Accounting workflow used:

1. create chart of accounts
2. set retained earnings account
3. create ledger from chart
4. post entries to ledger
5. show proxy income statement 
6. close ledger at accounting period end and produce income statement
7. make post-close entries and produce balance sheet
8. save permanent account balances for next period  
9. show trial balance at any time after step 3

Accounting conventions used:

- regular accounts of five types (asset, liability, capital, income, expense)
- contra accounts to regular accounts are possible (eg depreciation, discounts, etc.)
- intermediate income summary account used for net income calculation
- T-account holds amounts on debit and credit side
- the balancing side income summary account is determined by the account balance,

Assumptions and simplifications (some may be relaxed in future versions): 

- one currency
- one level of accounts, no subaccounts
- account names must be globally unique
- chart always has "retained earnigns account"
- chart always has "income summary account" 
- no journals, entries are posted to ledger directly
- an entry can touch any accounts
- entry amount can be positive or negative
- account balances cannot go negative
- net earnings are income less expenses, no gross profit or profit before tax calculated    
- period end closing will transfers net earnings to retained earnings
- no cash flow statement
- no statement of changes in equity
- no date or transaction metadata recorded
"""

import decimal
from abc import ABC, abstractmethod
from collections import UserDict
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from pydantic import BaseModel


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
        Intermediate(Profit.IncomeStatementAccount)

    Regular and Contra classes define any of five account types and their contra accounts.
    Intermediate class used for profit accounts that live for a short while when closing the ledger.
    """

    @staticmethod
    def from_side(side: Side) -> "DebitAccount | CreditAccount":
        """Create debit or credit account based on the specified side."""
        match side:
            case Side.Debit:
                return DebitAccount()
            case Side.Credit:
                return CreditAccount()

    @abstractmethod
    def taccount(self) -> "DebitAccount | CreditAccount | DebitOrCreditAccount":
        """Create T-account for this account definition."""


@dataclass
class Regular(AccountDefinition):
    """Regular account of any of five types of accounts."""

    t: T5

    def taccount(self):
        return self.from_side(self.t.side)


@dataclass
class Contra(AccountDefinition):
    """A contra account to any of five types of accounts.

    Examples of contra accounts:
      - contra property, plant, equipment - accumulated depreciation,
      - contra liability - discount on bonds payable,
      - contra capital - treasury stock,
      - contra income - refunds,
      - contra expense - purchase discounts.
    """

    t: T5

    def taccount(self):
        return self.from_side(self.t.side.reverse())


class Profit(Enum):
    IncomeStatementAccount = "isa"
    OtherComprehensiveIncome = "oci"  # not implemented yet


@dataclass
class Intermediate(AccountDefinition):
    """Intermediate account, used for profit accounts only."""

    t: Profit

    def taccount(self):
        return DebitOrCreditAccount()


@dataclass
class SingleEntry(ABC):
    """Base class for a single entry changes either a debit or a credit side of an account."""

    name: AccountName
    amount: Amount


class DebitEntry(SingleEntry):
    """An entry that increases the debit side of an account."""


class CreditEntry(SingleEntry):
    """An entry that increases the credit side of an account."""


class IterableEntry(Iterable[SingleEntry], ABC):
    """Base class for classes that can stream single entries when posting to ledger.

    Child classes:
    - MultipleEntry
    - DoubleEntry
    - ui.NamedEntry
    """

    @abstractmethod
    def __iter__(self):
        """Make class iterable, similar to list[SingleEntry]."""
        pass

    def is_balanced(self) -> bool:
        """Check if sum of debits and sum credits are equal."""

        def _sum(cls):
            return sum(e.amount for e in iter(self) if isinstance(e, cls))

        return _sum(DebitEntry) == _sum(CreditEntry)

    def validate(self):
        """Check if sum of debits and sum credits are equal."""
        if not self.is_balanced():
            self._raise_error()
        return self

    def _raise_error(self):
        raise AbacusError(["Sum of debits does not equal to sum of credits.", self])


@dataclass
class MultipleEntry(IterableEntry):

    debits: list[DebitEntry] = field(default_factory=list)
    credits: list[CreditEntry] = field(default_factory=list)

    def __iter__(self):
        return iter(self.debits + self.credits)

    @classmethod
    def from_list(cls, entries: list[SingleEntry]):
        debits = [x for x in entries if isinstance(x, DebitEntry)]
        credits = [x for x in entries if isinstance(x, CreditEntry)]
        return cls(debits, credits)

    def debit(self, account_name, amount):
        self.debits.append(DebitEntry(account_name, amount))
        return self

    def credit(self, account_name, amount):
        self.credits.append(CreditEntry(account_name, amount))
        return self


@dataclass
class DoubleEntry(IterableEntry):
    """Create entry from debit account name, credit account name and entry amount."""

    debit: AccountName
    credit: AccountName
    amount: Amount

    @property
    def multiple_entry(self) -> MultipleEntry:
        a = self.amount
        return MultipleEntry().debit(self.debit, a).credit(self.credit, a)

    def __iter__(self):
        return iter(self.multiple_entry)


@dataclass
class Account:
    """Account definition with account name and names of associated contra accounts."""

    name: AccountName
    contra_accounts: list[AccountName] = field(default_factory=list)

    def offset(self, *contra_account_names):
        """Add contra account to the list of contra accounts."""
        self.contra_accounts.extend(contra_account_names)
        return self

    def stream(self, account_type: T5):
        """Yield account definitions for the regular account and associated contra accounts."""
        yield self.name, Regular(account_type)
        for contra_name in self.contra_accounts:
            yield contra_name, Contra(account_type)


@dataclass
class Chart:
    income_summary_account: str = "_isa"
    assets: list[Account] = field(default_factory=list)
    capital: list[Account] = field(default_factory=list)
    liabilities: list[Account] = field(default_factory=list)
    income: list[Account] = field(default_factory=list)
    expenses: list[Account] = field(default_factory=list)

    def items(self) -> Iterable[tuple[AccountName, Regular | Contra | Intermediate]]:
        """Assign account types to account names."""
        yield from self.stream(self.assets, T5.Asset)
        yield from self.stream(self.capital, T5.Capital)
        yield from self.stream(self.liabilities, T5.Liability)
        yield from self.stream(self.income, T5.Income)
        yield from self.stream(self.expenses, T5.Expense)
        yield self.income_summary_account, Intermediate(Profit.IncomeStatementAccount)

    @staticmethod
    def stream(accounts: list[Account], account_type: T5):
        """Yield account definitions for a list of accounts."""
        for account in accounts:
            yield from account.stream(account_type)

    def __post_init__(self):
        self.validate()

    @property
    def account_names(self) -> list[AccountName]:
        return [name for name, _ in self.items()]

    @property
    def account_names_unique(self) -> list[AccountName]:
        return list(set(self.account_names))

    def validate(self) -> None:
        """Ensure all account names in chart are unique."""
        if len(self.account_names) != len(self.account_names_unique):
            self._raise_error(self.account_names, self.account_names_unique)

    @staticmethod
    def _raise_error(all_names, unique_names):
        n = len(all_names) - len(unique_names)
        raise AbacusError(
            [
                f"Chart contains {n} duplicate account names",
                set(all_names) - set(unique_names),
                sorted(unique_names),
                sorted(all_names),
            ]
        )

    def set_retained_earnings(self, account_name: AccountName):
        """Set retained earnings account name.

        Adds new account to capital accounts if *account_name* not found in chart.
        """
        _capital_account_names = self.capital
        if account_name not in self.account_names:
            _capital_account_names.append(Account(account_name))
        return ClosableChart(
            income_summary_account=self.income_summary_account,
            assets=self.assets,
            capital=_capital_account_names,
            liabilities=self.liabilities,
            income=self.income,
            expenses=self.expenses,
            retained_earnings_account=account_name,
        )


@dataclass
class ClosableChart(Chart):
    """Chart of accounts that can be closed at accounting period end.

    Suggested values for *retained_earnings_account* parameter are:

        - "retained_earnings" for corporation,
        - "owner_capital_account" for sole proprietorship.

    See: https://www.accountingcoach.com/blog/what-is-the-income-summary-account
    """

    # Added None as default to allow inhertance from Chart.
    retained_earnings_account: AccountName | None = None

    def assert_re_was_set(self):
        if not self.retained_earnings_account:
            raise AbacusError(f"Account {self.retained_earnings_account} was not set.")

    def assert_re_in_chart(self):
        re = self.retained_earnings_account
        if re not in [account.name for account in self.capital]:
            raise AbacusError(f"Account {re} was not set as capital account.")

    def __post_init__(self):
        self.assert_re_was_set()
        self.assert_re_in_chart()


@dataclass
class TAccountBase(ABC):
    """Base class for T-account that holds amounts on the left and right sides.

    Parent class for:

      - UnrestrictedDebitAccount
      - UnrestrictedCreditAccount
      - DebitAccount
      - CreditAccount
      - DebitOrCreditAccount
    """

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
        Make closing entry to transfer account balance
        from *my_name* account to *destination_name* account.

        When closing a debit account, the closing entry will be:
           - Cr my_name
           - Dr destination_name

        When closing a credit account, the closing entry will be:
            - Dr my_name
            - Cr destination_name
        """

        def make_entry(dr, cr):
            return DoubleEntry(dr, cr, self.balance)

        match self.side:
            case Side.Debit:
                return make_entry(dr=destination_name, cr=my_name)
            case Side.Credit:
                return make_entry(dr=my_name, cr=destination_name)


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

    def copy(self):
        return Ledger({name: deepcopy(account) for name, account in self.items()})

    def _post(self, entry: SingleEntry):
        """Post single entry to ledger. Will raise `KeyError` if account name is not found."""
        match entry:
            case DebitEntry(name, amount):
                self.data[name].debit(Amount(amount))
            case CreditEntry(name, amount):
                self.data[name].credit(Amount(amount))

    def post(self, entries: IterableEntry):
        """Post a stream of single entries to ledger."""
        failed = []
        try:
            entries.validate()
        except AbacusError:
            failed.append(entries)
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

    def close(self, chart: ClosableChart):
        """Close ledger at accounting period end."""
        # This is a dulpicate check, made to make mypy happy at return statement.
        if not chart.retained_earnings_account:
            raise AbacusError("Retained earnings account was not set.")
        return close(self, chart, chart.retained_earnings_account)


def close(
    ledger: Ledger, chart: Chart, retained_earnings_account: AccountName
) -> tuple[list[DoubleEntry], Ledger, "IncomeStatement"]:
    """Close ledger at accounting period end in the following order.

       1. Close income and expense contra accounts.
       2. Close income and expense accounts to income summary account.
       3. Close income summary account to retained earnings.

    Returns:
        closing_entries: list of closing entries,
        ledger: ledger after account closing with permanent accounts only --
                temporary and intermediate accounts will be removed,
        income_summary: income statement data.
    """
    closing_entries = []

    def proceed(from_, to_):
        entry = ledger[from_].make_closing_entry(from_, to_)
        closing_entries.append(entry)
        ledger.post(entry)
        del ledger[from_]

    # 1. Close contra income and contra expense accounts.
    for account in chart.income + chart.expenses:
        for contra_account_name in account.contra_accounts:
            proceed(from_=contra_account_name, to_=account.name)

    # 2. Close income and expense accounts and create income statement.
    income_summary = IncomeStatement(income={}, expenses={})
    for account in chart.income:
        b = ledger[account.name].balance
        income_summary.income[account.name] = b
        proceed(from_=account.name, to_=chart.income_summary_account)
    for account in chart.expenses:
        b = ledger[account.name].balance
        income_summary.expenses[account.name] = b
        proceed(account.name, chart.income_summary_account)

    # 3. Close income summary account to retained earnings account.
    proceed(chart.income_summary_account, retained_earnings_account)

    return closing_entries, ledger, income_summary


class TrialBalance(UserDict[str, tuple[Side, Amount]]):
    """Trial balance contains account names, account sides and balances."""

    @classmethod
    def new(cls, ledger: Ledger):
        """Create trial balance from ledger."""
        return cls(
            {
                account_name: (t_account.side, t_account.balance)
                for account_name, t_account in ledger.items()
            }
        )

    def tuples(self) -> dict[str, tuple[Amount, Amount]]:
        """Return account names and tuples like (0, balances) or (balance, 0)."""

        def to_tuples(side: Side, balance: Amount):
            return (balance, 0) if side.is_debit() else (0, balance)

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
                if side.is_debit()
                else CreditEntry(name, balance)
            )
            for name, (side, balance) in self.items()
        ]


class Report(BaseModel):
    """Base class for financial reports."""


class IncomeStatement(Report):
    income: dict[AccountName, Amount]
    expenses: dict[AccountName, Amount]

    @property
    def net_earnings(self):
        """Calculate net earnings as income less expenses."""
        return sum(self.income.values()) - sum(self.expenses.values())


def net_balance(ledger: Ledger, account: Account) -> Amount:
    """Calculate net balance of an account by substracting the balances of its contra accounts."""
    b = ledger[account.name].balance
    for contra_name in account.contra_accounts:
        b -= ledger[contra_name].balance
    return b


class BalanceSheet(Report):
    assets: dict[AccountName, Amount]
    capital: dict[AccountName, Amount]
    liabilities: dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger: Ledger, chart: Chart):
        """Create balance sheet from ledger and chart.

        Account will balances will be shown net of contra account balances."""

        def subset(accounts: list[Account]) -> dict[str, Amount]:
            return {account.name: net_balance(ledger, account) for account in accounts}

        return cls(
            assets=subset(chart.assets),
            capital=subset(chart.capital),
            liabilities=subset(chart.liabilities),
        )
