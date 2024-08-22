from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from core import (
    T5,
    AccountName,
    Amount,
    BalanceSheet,
    Entry,
    FastChart,
    IncomeStatement,
    Ledger,
    TrialBalance,
)

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


class EntryList(BaseModel):
    saved: List[NamedEntry] = []
    _current: NamedEntry = NamedEntry()
    _current_id: int = 0  # for testing and future use

    def append(self, entry: NamedEntry):
        self.saved.append(entry)
        self._current = NamedEntry()
        return self

    def increment(self):
        self._current_id += 1
        return self


def default_chart() -> FastChart:
    return FastChart(
        income_summary_account="__isa__", retained_earnings_account="retained_earnings"
    )


@dataclass
class Book:
    company: str
    chart: FastChart = field(default_factory=default_chart)
    entries: EntryList = field(default_factory=EntryList)
    _ledger: Ledger | None = None
    _income_statement: IncomeStatement | None = None
    _chart_path: Path = Path("./chart.json")
    _entries_path: Path = Path("./entries.json")

    @property
    def income_statement(self):
        return self._income_statement or self.proxy_income_statement

    def save_chart(self, path: Path | None = None):
        _path = path or self._chart_path
        _path.write_text(self.chart.model_dump_json(indent=2))

    def save_entries(self, path: Path | None = None):
        _path = path or self._entries_path
        _path.write_text(self.entries.model_dump_json(indent=2))

    def load_chart(self, path: Path | None = None):
        _path = path or self._chart_path
        self.chart = FastChart.model_validate_json(_path.read_text())

    def load_entries(self, path: Path | None = None):
        _path = path or self._entries_path
        self.entries = EntryList.model_validate_json(_path.read_text())

    @property
    def trial_balance(self):
        return TrialBalance.new(self.ledger, self.chart)

    @property
    def balance_sheet(self):
        return BalanceSheet.new(self.ledger, self.chart)

    def set_title(self, account_name: str, title: str):
        # not implemented yet
        return self

    def _add(
        self,
        t: T5,
        account_name: str,
        title: str | None,  # reserved
        offsets: list[str] | None,
    ):
        self.chart.add(t, account_name, offsets or [])
        self.set_title(account_name, title)
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
        self._ledger = Ledger.new(self.chart)
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
        self._ledger.post(self._current_entry)
        self.entries.append(self._current_entry)
        self.entries.increment()
        return self

    def close(self):
        """Close ledger."""
        closing_entries, self._ledger, self._income_statement = self._ledger.close(
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
