from dataclasses import dataclass, field
from pathlib import Path
from pydantic import BaseModel

from core import (
    T5,
    AccountName,
    Amount,
    BalanceSheet,
    Chart,
    IncomeStatement,
    Ledger,
    MultipleEntry,
    TrialBalance,
)


# may substitute MultipleEntry with Entry
class Entry(BaseModel):
    debits: list[tuple[AccountName, Amount]] = []
    credits: list[tuple[AccountName, Amount]] = []


# type alias for int | float | Decimal
Numeric = Amount | int | float


class NamedEntry(Entry):
    """Create entry with title and use .debit() and .credit() methods.
    Use .amount() method to set default amount for the entry.

    The syntax is similar to 'medici' package <https://github.com/flash-oss/medici>.
    """

    title: str | None = None
    _amount: Amount | None = None

    # added to prevent tests from failing
    def __eq__(self, other):
        return (
            self.title == other.title
            and self.debits == other.debits
            and self.credits == other.credits
        )

    def amount(self, amount: Numeric):
        """Set default amount for this entry."""
        self._amount = Amount(amount)
        return self

    def debit(self, account_name: AccountName, amount: Numeric | None = None):
        """Add debit entry."""
        t = account_name, Amount(amount or self._amount)
        self.debits.append(t)
        return self

    def credit(self, account_name: AccountName, amount: Numeric | None = None):
        """Add credit entry."""
        t = account_name, Amount(amount or self._amount)
        self.credits.append(t)
        return self

    @property
    def _multiple_entry(self):
        return MultipleEntry(self.debits, self.credits)

    def __iter__(self):
        return iter(self._multiple_entry)


@dataclass
class Book:
    company: str
    chart: Chart = Chart()
    ledger: Ledger | None = None
    entries: list[NamedEntry] = field(default_factory=list)
    _current_entry: NamedEntry = field(default_factory=NamedEntry)
    _current_id: int = 0
    income_statement: IncomeStatement = IncomeStatement(income={}, expenses={})

    def save_chart(self, path=Path("./chart.json")):
        path.write_text(self.chart.json())

    def save_ledger(self, path=Path("./ledger.json")):
        path.write_text(self.ledger.json())

    @property
    def trial_balance(self):
        return TrialBalance.new(self.ledger, self.chart)

    @property
    def balance_sheet(self):
        return BalanceSheet.new(self.ledger, self.chart)

    def set_title(self, account_name: str, title: str):
        pass  # not implemented yet
        return self

    def _add(
        self,
        t: T5,
        account_name: str,
        title: str | None,
        offsets: list[str] | None,
    ):
        self.chart.accounts.put(t, account_name, offsets or [])
        return self

    def add_asset(self, account, *, title=None, offsets=None):
        return self._add(T5.Asset, account, title, offsets)

    def add_assets(self, *account_names):
        for name in account_names:
            self.add_asset(name)
        return self

    def add_liability(self, account, *, title=None, offsets=None):
        return self._add(T5.Liability, account, title, offsets)

    def add_liabilities(self, *account_names):
        for name in account_names:
            self.add_liability(name)
        return self

    def add_capital(self, account, *, title=None, offsets=None):
        return self._add(T5.Capital, account, title, offsets)

    def add_capitals(self, *account_names):
        for name in account_names:
            self.add_capital(name)
        return self

    def add_income(self, account, *, title=None, offsets=None):
        return self._add(T5.Income, account, title, offsets)

    def add_incomes(self, *account_names):
        for name in account_names:
            self.add_income(name)
        return self

    def add_expense(self, account, *, title=None, offsets=None):
        return self._add(T5.Expense, account, title, offsets)

    def add_expenses(self, *account_names):
        for name in account_names:
            self.add_expense(name)
        return self

    def set_income_summary_account(self, account_name: str):
        self.chart.income_summary_account = account_name
        return self

    def set_retained_earnings(self, account_name: str):
        self.chart.set_retained_earnings(account_name)
        return self

    def open(self):
        """Create new ledger."""
        self.ledger = Ledger.new(self.chart)
        return self

    def entry(self, title: str):
        """Start new entry."""
        self._current_entry = NamedEntry(title=title)
        return self

    def amount(self, amount: Amount | int | float):
        """Set amount for the current entry."""
        self._current_entry._amount = Amount(amount)
        return self

    def debit(self, account_name: str, amount: Amount | int | float | None = None):
        """Add debit part to current entry."""
        self._current_entry.debit(account_name, amount)
        return self

    def credit(self, account_name: str, amount: Amount | int | float | None = None):
        """Add credit part to current entry."""
        self._current_entry.credit(account_name, amount)
        return self

    def commit(self):
        """Post current entry to ledger and write it to entry store."""
        self.ledger.post(self._current_entry)
        self.entries.append(self._current_entry)
        self._current_entry = NamedEntry()
        self._current_id += 1
        return self

    def close(self):
        """Close ledger."""
        closing_entries, self.ledger, self.income_statement = self.ledger.close(
            self.chart
        )
        for ce in closing_entries:
            ne = NamedEntry(title="Closing entry", debits=ce.debits, credits=ce.credits)
            self.entries.append(ne)
        return self

    @property
    def proxy_income_statement(self):
        _, _, income_statement = self.ledger.copy().close(self.chart)
        return income_statement

    @property
    def proxy_net_earnings(self) -> Amount:
        return self.proxy_income_statement.net_earnings
