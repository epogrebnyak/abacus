"""Core double-entry accounting objects.

This module contains classes:

  - chart of accounts (Chart)
  - general ledger (Ledger)
  - multiple entry (Entry), and
  - reports (TrialBalance, IncomeStatement, BalanceSheet)

Accounting workflow:

1. create chart of accounts and set retained earnings account
2. create ledger from chart with opening balances
3. post entries to ledger
4. show trial balance at any time
5. show proxy income statement if necessary 
6. close ledger at accounting period end and make income statement
7. make post-close entries and make balance sheet
8. save permanent account balances for next period  

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
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterator, Sequence, Type

from pydantic import BaseModel


class AbacusError(Exception):
    """Custom error for the abacus project."""


def error(message: str, data):
    return AbacusError([message, data])


AccountName = str
Amount = decimal.Decimal
Pair = tuple[AccountName, AccountName]


class Side(Enum):
    """Indicate debit or credit side of the account."""

    Debit = "debit"
    Credit = "credit"

    def reverse(self) -> "Side":
        """Change side from debit to credit or vice versa."""
        return Side.Credit if self == Side.Debit else Side.Debit

    def is_debit(self) -> bool:
        """Return True if this is a debit side."""
        return self == Side.Debit

    @property
    def taccount(self) -> type["DebitAccount"] | type["CreditAccount"]:
        """Create debit or credit account based on the specified side."""
        return DebitAccount if self.is_debit() else CreditAccount

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


class Definition:
    """Base class for Regular, Contra and Just classes:

    Regular(T5.Asset)
    Contra("equity")
    Just(DebitorCreditAccount)
    """


@dataclass
class Regular(Definition):
    """Regular account of any of five types of accounts."""

    t: T5


@dataclass
class Contra(Definition):
    """A contra account to an existing account."""

    linked_to: AccountName


@dataclass
class Just(Definition):
    taccount_class: Type["TAccount"]


class ChartDict(UserDict[str, Definition]):

    def set(self, t: T5, name: str):
        """Add regular account to chart."""
        self.data[name] = Regular(t)
        return self

    def offset(self, existing_name: str, contra_name: str):
        """Add contra account to chart."""
        if existing_name not in self.data.keys():
            raise AbacusError(f"Account name {existing_name} not found in chart.")
        self.data[contra_name] = Contra(existing_name)
        return self

    def just(self, taccount_class: Type["TAccount"], name: str):
        """Add any account type to chart."""
        self.data[name] = Just(taccount_class)
        return self

    def taccount(self, definition) -> "TAccount":
        """Decide what kind of T-account to create for the definition."""
        match definition:
            case Regular(t):
                return t.side.taccount()
            case Contra(linked_to):
                return self[linked_to].t.side.reverse().taccount()  # type: ignore
            case Just(taccount_class):
                return taccount_class()
            case _:
                raise AbacusError(f"Unknown account definition: {definition}")

    def ledger(self) -> "Ledger":
        return Ledger(
            {name: self.taccount(definition) for name, definition in self.items()}
        )

    def closing_pairs(
        self,
        income_summary_account: AccountName,
        retained_earnings_account: AccountName,
    ) -> Iterator["Pair"]:
        """Return closing pairs for accounting period end."""
        for t in T5.Income, T5.Expense:
            # 1. Close contra income and contra expense accounts.
            for name in self.by_type(t):
                for contra_name in self.find_contra_accounts(name):
                    yield contra_name, name

            # 2. Close income and expense accounts to income summary account.
            for name in self.by_type(t):
                yield name, income_summary_account

        # 3. Close income summary account to retained earnings account.
        yield income_summary_account, retained_earnings_account

    def set_re(self, name: str):
        """Set retained earnings account in chart."""
        # Retained earnings account is already in chart, do nothing
        if self.get(name) == Regular(T5.Capital):
            return self
        # Retained earnings account is in chart but not a capital account, raise error
        elif name in self.keys():
            raise AbacusError(f"{name} already in chart and not a capital account.")
        # Retained earnings account not in chart, set it to capital account
        else:
            self.set(T5.Capital, name)
        return self

    def set_isa(self, name: str):
        """Set income summary account in chart."""
        self.just(DebitOrCreditAccount, name)
        return self

    def by_type(self, t: T5) -> list[AccountName]:
        """Return account names for a given account type."""
        return [
            name
            for name, definition in self.items()
            if isinstance(definition, Regular) and definition.t == t
        ]

    def find_contra_accounts(self, name: AccountName) -> list[AccountName]:
        """Find contra accounts for a given account name."""
        return [
            _name
            for _name, definition in self.items()
            if isinstance(definition, Contra) and definition.linked_to == name
        ]

    def qualify(self, income_summary_account, retained_earnings_account) -> "Chart":
        """Create chart with closing pairs."""
        self.set_isa(isa := income_summary_account)
        self.set_re(re := retained_earnings_account)
        pairs = list(self.closing_pairs(isa, re))
        return Chart(self, pairs)


@dataclass
class Chart:
    """Chart of accounts with closing pairs of accounts for the accounting period end."""

    accounts: ChartDict
    closing_pairs: list[Pair]

    @property
    def temporary_accounts(self) -> set[AccountName]:
        """Return temporary account names."""
        return set(name for name, _ in self.closing_pairs)

    def net_balances_factory(self, ledger) -> Callable[[T5], dict[AccountName, Amount]]:
        """Return a function that calculates net balances for a given account type."""

        return lambda t: {
            name: ledger.net_balance(name, self.accounts.find_contra_accounts(name))
            for name in self.accounts.by_type(t)
        }

    def validate(self):
        """Raise error if closing pairs are not valid."""
        try:
            self.accounts.ledger().close_by_pairs(self.closing_pairs)
        except KeyError as e:
            s = str(e).replace("'", "")
            raise AbacusError(s)


@dataclass
class SingleEntry(ABC):
    """Base class for a single entry changes either a debit or a credit side of an account."""

    name: AccountName
    amount: Amount


class DebitEntry(SingleEntry):
    """An entry that increases the debit side of an account."""


class CreditEntry(SingleEntry):
    """An entry that increases the credit side of an account."""


@dataclass
class Entry:
    debits: list[tuple[AccountName, Amount]] = field(default_factory=list)
    credits: list[tuple[AccountName, Amount]] = field(default_factory=list)

    def __iter__(self) -> Iterator[SingleEntry]:
        for name, amount in self.debits:
            yield DebitEntry(name, amount)
        for name, amount in self.credits:
            yield CreditEntry(name, amount)

    def dr(self, account_name, amount):
        """Add debit part to entry."""
        self.debits.append((account_name, amount))
        return self

    def cr(self, account_name, amount):
        """Add credit part to entry."""
        self.credits.append((account_name, amount))
        return self

    def validate_balance(self):
        """Raise error if sum of debits and sum credits are not equal."""
        if not self.is_balanced():
            raise error("Sum of debits does not equal to sum of credits", self)
        return self

    def is_balanced(self) -> bool:
        """Return True if sum of debits equals to sum credits."""

        def sums(xs):
            return sum(amount for _, amount in xs)

        return sums(self.debits) == sums(self.credits)


def double_entry(debit: AccountName, credit: AccountName, amount: Amount) -> Entry:
    """Create double entry with one debit and one credit part."""
    return Entry(debits=[(debit, amount)], credits=[(credit, amount)])


@dataclass
class TAccount(ABC):
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

    def copy(self):
        return self.__class__(
            left=self.left, right=self.right
        )  # hope it is pass by value

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

        When closing a debit account the closing entry is:
           - Dr destination_name
           - Cr my_name

        When closing a credit account the closing entry is:
            - Dr my_name
            - Cr destination_name
        """
        b = self.balance
        if self.side.is_debit():
            return double_entry(debit=destination_name, credit=my_name, amount=b)
        return double_entry(debit=my_name, credit=destination_name, amount=b)


class UnrestrictedDebitAccount(TAccount):

    @property
    def balance(self) -> Amount:
        return self.left - self.right

    @property
    def side(self):
        return Side.Debit


class UnrestrictedCreditAccount(TAccount):

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


class DebitOrCreditAccount(TAccount):
    """Account that can be either debit or credit depending on the balance."""

    @property
    def balance(self) -> Amount:
        return abs(self.left - self.right)

    @property
    def side(self) -> Side:
        return Side.Credit if self.right >= self.left else Side.Debit


class Ledger(UserDict[AccountName, TAccount]):

    @classmethod
    def new(_, chart: Chart) -> "Ledger":
        """Create ledger from chart."""
        return chart.accounts.ledger()

    def copy(self):
        return Ledger({name: account.copy() for name, account in self.items()})

    def post_single(self, single_entry: SingleEntry):
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
                self.post_single(single_entry)
            except KeyError as e:
                not_found.append((e, single_entry))
            except AbacusError as e:
                cannot_post.append((e, single_entry))
        if not_found:
            raise error("Accounts do not exist", not_found)
        if cannot_post:
            raise error("Could not post to ledger", cannot_post)

    def post_many(self, entries: Sequence[Entry]):
        """Post several streams of entries to ledger."""
        for entry in entries:
            self.post(entry)

    @property
    def trial_balance(self):
        """Create trial balance from ledger."""
        return TrialBalance.new(self)

    def balances(self) -> dict[AccountName, Amount]:
        """Return account balances."""
        return {name: account.balance for name, account in self.items()}

    def net_balance(self, name: AccountName, contra_names: list[AccountName]) -> Amount:
        """Calculate net balance of an account by substracting the balances of its contra accounts."""
        return self[name].balance - sum(
            self[contra_name].balance for contra_name in contra_names
        )

    def close_by_pairs(self, pairs: Sequence[Pair]):
        """Close ledger by using closing pairs of accounts."""
        closing_entries = []
        for from_, to_ in pairs:
            entry = self.data[from_].make_closing_entry(from_, to_)
            closing_entries.append(entry)
            self.post(entry)
            del self.data[from_]
        return closing_entries

    def close(self, chart: Chart) -> list[Entry]:
        """Close ledger at accounting period end."""
        return self.close_by_pairs(chart.closing_pairs)


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

        return {
            name: ((balance, Amount(0)) if side.is_debit() else (Amount(0), balance))
            for name, (side, balance) in self.items()
        }


class Report(BaseModel):
    """Base class for financial reports."""


class IncomeStatement(Report):
    income: dict[AccountName, Amount]
    expenses: dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger: Ledger, chart: Chart):
        """Create income statement from ledger and chart."""
        fill = chart.net_balances_factory(ledger)
        return cls(income=fill(T5.Income), expenses=fill(T5.Expense))

    @property
    def net_earnings(self):
        """Calculate net earnings as income less expenses."""
        return sum(self.income.values()) - sum(self.expenses.values())


class BalanceSheet(Report):
    assets: dict[AccountName, Amount]
    capital: dict[AccountName, Amount]
    liabilities: dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger: Ledger, chart: Chart):
        """Create balance sheet from ledger and chart.
        Account will balances will be shown net of contra account balances."""
        fill = chart.net_balances_factory(ledger)
        return cls(
            assets=fill(T5.Asset),
            capital=fill(T5.Capital),
            liabilities=fill(T5.Liability),
        )
