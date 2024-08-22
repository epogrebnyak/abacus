"""Double-entry bookkeeping module.

Accounting workflow:

1. create chart of accounts and set retained earnings account
2. create ledger from chart
3. post entries to ledger
4. show proxy income statement 
5. close ledger at accounting period end and make income statement
6. make post-close entries and produce balance sheet
7. save permanent account balances for next period  
8. show trial balance at any time after step 3

Accounting conventions:

- regular accounts of five types (asset, liability, capital, income, expense)
- contra accounts to regular accounts are possible (eg depreciation, discounts, etc.)
- intermediate income summary account used for net income calculation

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
- net earnings are income less expenses, no gross profit or earnings before tax calculated    
- period end closing will transfer net earnings to retained earnings
- no cash flow statement
- no statement of changes in equity
- no date or transaction metadata recorded
"""

import decimal
from abc import ABC, abstractmethod
from collections import UserDict
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

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

    @abstractmethod
    def taccount(self) -> "DebitAccount | CreditAccount | DebitOrCreditAccount":
        """Create T-account for this account definition."""


def from_side(side: Side) -> "DebitAccount | CreditAccount":
    """Create debit or credit account based on the specified side."""
    return DebitAccount() if side.is_debit() else CreditAccount()


@dataclass
class Regular(AccountDefinition):
    """Regular account of any of five types of accounts."""

    t: T5

    def taccount(self):
        return from_side(self.t.side)


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
        return from_side(self.t.side.reverse())


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
    - Entry
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


class Entry(BaseModel):
    debits: list[tuple[AccountName, Amount]] = []
    credits: list[tuple[AccountName, Amount]] = []

    def __iter__(self):
        _drs = [DebitEntry(name, amount) for name, amount in self.debits]
        _crs = [CreditEntry(name, amount) for name, amount in self.credits]
        return iter(_drs + _crs)

    def dr(self, account_name, amount):
        self.debits += [(account_name, amount)]
        return self

    def cr(self, account_name, amount):
        self.credits += [(account_name, amount)]
        return self

    def validate_balance(self):
        if not self.is_balanced():
            self._raise_error()
        return self

    def is_balanced(self) -> bool:
        """Check if sum of debits and sum credits are equal."""

        def _sum(xs):
            return sum(a for _, a in xs)

        return _sum(self.debits) == _sum(self.credits)

    def _raise_error(self):
        raise AbacusError(["Sum of debits does not equal to sum of credits.", self])


def double_entry(debit: AccountName, credit: AccountName, amount: Amount) -> Entry:
    return Entry().dr(debit, amount).cr(credit, amount)


class FastChart(BaseModel):
    income_summary_account: str
    retained_earnings_account: str
    accounts: dict[str, tuple[T5, list[str]]] = {}

    def model_post_init(self, __context: Any) -> None:
        self.accounts[self.retained_earnings_account] = (T5.Capital, [])
        return self


    def set_retained_earnings(self, account_name: str):
        del self.accounts[self.retained_earnings_account]
        self.retained_earnings_account = account_name
        self.accounts[account_name] = (T5.Capital, [])
        return self

    def add(self, t: T5, account_name: str, offsets: list[str] | None = None):
        """Add account name, type and contra accounts to chart."""
        self.accounts[account_name] = (t, offsets or [])
        return self

    def items(self):
        """Assign account types to account names."""
        for account_name, (t, offsets) in self.accounts.items():
            yield account_name, Regular(t)
            for offset in offsets:
                yield offset, Contra(t)
        yield self.income_summary_account, Intermediate(Profit.IncomeStatementAccount)

    def __getitem__(self, t: T5):
        """Return account names and contra accounts for a given account type."""
        return [
            (name, contra_names)
            for name, (_t, contra_names) in self.accounts.items()
            if _t == t
        ]

    def add_asset(self, account: str, contra_accounts=None):
        return self.add(T5.Asset, account, contra_accounts)

    def add_liability(self, account: str, contra_accounts=None):
        return self.add(T5.Liability, account, contra_accounts)

    def add_capital(self, account: str, contra_accounts=None):
        return self.add(T5.Capital, account, contra_accounts)

    def add_expense(self, account: str, contra_accounts=None):
        return self.add(T5.Expense, account, contra_accounts)

    def add_income(self, account: str, contra_accounts=None):
        return self.add(T5.Income, account, contra_accounts)


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
    ) -> "Entry":
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

        def make_entry(dr, cr) -> Entry:
            return double_entry(dr, cr, self.balance)

        return (
            make_entry(dr=destination_name, cr=my_name)
            if self.side.is_debit()
            else make_entry(dr=my_name, cr=destination_name)
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
        return Side.Credit if self.right >= self.left else Side.Debit


class Ledger(UserDict[AccountName, TAccountBase]):
    @classmethod
    def new(cls, chart: FastChart):
        """Create new ledger from chart of accounts."""
        return cls({name: definition.taccount() for name, definition in chart.items()})

    def copy(self):
        return Ledger({name: deepcopy(account) for name, account in self.items()})

    def _post(self, single_entry: SingleEntry):
        """Post single entry to ledger. Will raise `KeyError` if account name is not found."""
        match single_entry:
            case DebitEntry(name, amount):
                self.data[name].debit(Amount(amount))
            case CreditEntry(name, amount):
                self.data[name].credit(Amount(amount))

    def post(self, entry: Entry):
        """Post a stream of single entries to ledger."""
        not_found = []
        cannot_post = []
        for single_entry in iter(entry):
            try:
                self._post(single_entry)
            except KeyError:
                not_found.append(entry)
            except AbacusError:
                cannot_post.append(entry)
        if not_found or cannot_post:
            raise AbacusError(
                {
                    "Could not post to ledger": cannot_post,
                    "Account does not exist": not_found,
                }
            )

    def post_many(self, entries: list[Entry]):
        """Post several streams of entries to ledger."""
        for entry in entries:
            self.post(entry)

    @property
    def trial_balance(self):
        """Create trial balance from ledger."""
        return TrialBalance.new(self)

    def balances(self) -> dict[str, Amount]:
        """Return account balances."""
        return {name: account.balance for name, account in self.items()}

    def close(self, chart: FastChart):
        """Close ledger at accounting period end."""
        return close(self, chart)


def close(
    ledger: Ledger, chart: FastChart
) -> tuple[list[Entry], Ledger, "IncomeStatement"]:
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
    for t in T5.Income, T5.Expense:
        for name, contra_names in chart[t]:
            for contra_name in contra_names:
                proceed(from_=contra_name, to_=name)

    # 2. Close income and expense accounts and create income statement.
    income_summary = IncomeStatement(income={}, expenses={})
    for name, _ in chart[T5.Income]:
        b = ledger[name].balance
        income_summary.income[name] = b
        proceed(name, chart.income_summary_account)
    for name, _ in chart[T5.Expense]:
        b = ledger[name].balance
        income_summary.expenses[name] = b
        proceed(name, chart.income_summary_account)

    # 3. Close income summary account to retained earnings account.
    proceed(chart.income_summary_account, chart.retained_earnings_account)

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


def net_balance(
    ledger: Ledger, name: AccountName, contra_names: list[AccountName]
) -> Amount:
    """Calculate net balance of an account by substracting the balances of its contra accounts."""
    b = ledger[name].balance
    for contra_name in contra_names:
        b -= ledger[contra_name].balance
    return b


class BalanceSheet(Report):
    assets: dict[AccountName, Amount]
    capital: dict[AccountName, Amount]
    liabilities: dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger: Ledger, chart: FastChart):
        """Create balance sheet from ledger and chart.

        Account will balances will be shown net of contra account balances."""

        def subset(t: T5) -> dict[str, Amount]:
            return {
                name: net_balance(ledger, name, contra_names)
                for (name, contra_names) in chart[t]
            }

        return cls(
            assets=subset(T5.Asset),
            capital=subset(T5.Capital),
            liabilities=subset(T5.Liability),
        )
