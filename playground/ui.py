from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, List

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

# type alias for user inputed number
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
        t = account_name, Amount(amount or self._amount)  # type: ignore
        self.debits.append(t)
        return self

    def credit(self, account_name: AccountName, amount: Numeric | None = None):
        """Add credit entry."""
        t = account_name, Amount(amount or self._amount)  # type: ignore
        self.credits.append(t)
        return self


class EntryList(BaseModel):
    saved: List[NamedEntry] = []
    _current: NamedEntry = NamedEntry()
    _current_id: int = 0  # for testing and future use

    def commit(self):
        self.saved.append(self._current)
        self._current = None
        return self

    def append(self, entry: NamedEntry):
        self.saved.append(entry)
        return self

    def extend(self, entries: List[NamedEntry]):
        self.saved.extend(entries)
        return self

    def increment(self):
        self._current_id += 1
        return self


# TODO: test EntryStore

from abc import ABC, abstractmethod


class LoadSaveMixin(BaseModel, ABC):
    _path: Path | None = None

    @property
    @abstractmethod
    def _default_path() -> Path:
        pass
    

    def load(cls, path: Path | None = None):
        _p = path or cls._default_path
        return cls.model_validate_json(_p.read_text())

    def save(self, path: Path | None = None):
        _path = path or self._path or self._default_path
        _path.write_text(self.model_dump_json(indent=2))

class EntryStore(EntryList, LoadSaveMixin):

    @property
    def _default_path(sef) -> Path:
        return Path("./entries.json")


@dataclass
class Book:
    company: str
    chart: FastChart = field(default_factory=FastChart.default)
    entries: EntryList = field(default_factory=EntryList)
    _ledger: Ledger | None = None
    _income_statement: IncomeStatement | None = None
    _chart_path: Path = Path("./chart.json")
    _entries_path: Path = Path("./entries.json")

    # FIXME: use ChartManager and EntriesManager to handle paths

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
        """Return trial balance."""
        return TrialBalance.new(self._ledger)

    @property
    def balance_sheet(self):
        """Return balance sheet."""
        return BalanceSheet.new(self._ledger, self.chart)

    def set_title(self, account_name: str, title: str):
        """Set descriptive title for account."""
        # not implemented yet
        return self

    def _add(
        self,
        t: T5,
        account_name: str,
        title: str | None,  # reserved
        offsets: list[str] | None,
    ):
        """Add new account to chart."""
        self.chart.add(t, account_name, offsets or [])
        if title:
            self.set_title(account_name, title)
        return self

    def add_asset(self, account, *, title=None, offsets=None):
        """Add asset account to chart."""
        return self._add(T5.Asset, account, title, offsets)

    def add_assets(self, *account_names):
        """Add several asset accounts to chart."""
        for name in account_names:
            self.add_asset(name)
        return self

    def add_liability(self, account, *, title=None, offsets=None):
        """Add liability account to chart."""
        return self._add(T5.Liability, account, title, offsets)

    def add_liabilities(self, *account_names):
        """Add several liability accounts to chart."""
        for name in account_names:
            self.add_liability(name)
        return self

    def add_capital(self, account, *, title=None, offsets=None):
        """Add capital account to chart."""
        return self._add(T5.Capital, account, title, offsets)

    def add_capitals(self, *account_names):
        """Add several capital accounts to chart."""
        for name in account_names:
            self.add_capital(name)
        return self

    def add_income(self, account, *, title=None, offsets=None):
        """Add income account to chart."""
        return self._add(T5.Income, account, title, offsets)

    def add_incomes(self, *account_names):
        """Add several income accounts to chart."""
        for name in account_names:
            self.add_income(name)
        return self

    def add_expense(self, account, *, title=None, offsets=None):
        """Add expense account to chart."""
        return self._add(T5.Expense, account, title, offsets)

    def add_expenses(self, *account_names):
        """Add several expense accounts to chart."""
        for name in account_names:
            self.add_expense(name)
        return self

    def set_income_summary_account(self, account_name: str):
        """Set name of income summary account."""
        self.chart.income_summary_account = account_name
        return self

    def set_retained_earnings(self, account_name: str):
        """Set name of retained earnings account."""
        self.chart.set_retained_earnings(account_name)
        return self

    def open(self):
        """Create new ledger."""
        self._ledger = Ledger.new(self.chart)
        return self

    def entry(self, title: str):
        """Start new entry."""
        self.entries._current = NamedEntry(title=title)
        return self

    def amount(self, amount: Amount | int | float):
        """Set amount for the current entry."""
        self.entries._current.amount(amount)
        return self

    def debit(self, account_name: str, amount: Amount | int | float | None = None):
        """Add debit part to current entry."""
        self.entries._current.debit(account_name, amount)
        return self

    def credit(self, account_name: str, amount: Amount | int | float | None = None):
        """Add credit part to current entry."""
        self.entries._current.credit(account_name, amount)
        return self

    def commit(self):
        """Post current entry to ledger and write it to entry store."""
        self.entries.increment()
        self.follow()
        return self

    def follow(self):
        """Commit current entry, reuse previous transaction id."""
        self._ledger.post(self.entries._current)
        self.entries.commit()
        return self

    def close(self):
        """Close ledger."""
        closingentries, self._ledger, self._income_statement = self._ledger.close(
            self.chart
        )
        self.entries.increment()
        for ce in closingentries:
            self.entries.append(ce.add_title("Closing entry"))
        return self

    def is_closed(self) -> bool:
        """Return True if ledger was closed."""
        return self._income_statement is not None

    @property
    def proxy_income_statement(self):
        """Income statement proxy (to use before ledger is closed)."""
        _, _, income_statement = self._ledger.copy().close(self.chart)
        return income_statement

    @property
    def proxy_net_earnings(self) -> Amount:
        """Net earnings proxy (to use before ledger is closed)."""
        return self.proxy_income_statement.net_earnings

    @property
    def income_statement(self):
        """Return income statement."""
        return self._income_statement or self.proxy_income_statement
