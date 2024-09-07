from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, ClassVar, List

from pydantic import BaseModel, PrivateAttr

from core import (
    T5,
    AbacusError,
    AccountName,
    Amount,
    BalanceSheet,
    Entry,
    FastChart,
    IncomeStatement,
    Ledger,
)

# type alias for user inputed number
Numeric = Amount | int | float


class Chart(FastChart):
    names: dict[str, str] = {}

    def set_title(self, account_name: str, title: str | None):
        if title:
            self.names[account_name] = title
        return self

    def offset(
        self,
        account_name: str,
        contra_account_name: str,
        contra_account_title: str | None = None,
    ) -> "Chart":
        """Add contra account to chart."""
        self.add_contra_account(account_name, contra_account_name)
        self.set_title(contra_account_name, contra_account_title)
        return self

    def add(
        self,
        t: T5,
        account_name: str,
        title: str | None,
        offsets: List[str] | None = None,
    ):
        """Add new account to chart."""
        self.set_account(t, account_name)
        if offsets:
            for offset in offsets:
                self.add_contra_account(account_name, offset)
        self.set_title(account_name, title)
        return self

    def add_asset(self, account, *, title=None, offsets=None):
        """Add asset account to chart."""
        return self.add(T5.Asset, account, title, offsets)

    def add_assets(self, *account_names):
        """Add several asset accounts to chart."""
        for name in account_names:
            self.add_asset(name)
        return self

    def add_liability(self, account, *, title=None, offsets=None):
        """Add liability account to chart."""
        return self.add(T5.Liability, account, title, offsets)

    def add_liabilities(self, *account_names):
        """Add several liability accounts to chart."""
        for name in account_names:
            self.add_liability(name)
        return self

    def add_capital(self, account, *, title=None, offsets=None):
        """Add capital account to chart."""
        return self.add(T5.Capital, account, title, offsets)

    def add_capitals(self, *account_names):
        """Add several capital accounts to chart."""
        for name in account_names:
            self.add_capital(name)
        return self

    def add_income(self, account, *, title=None, offsets=None):
        """Add income account to chart."""
        return self.add(T5.Income, account, title, offsets)

    def add_incomes(self, *account_names):
        """Add several income accounts to chart."""
        for name in account_names:
            self.add_income(name)
        return self

    def add_expense(self, account, *, title=None, offsets=None):
        """Add expense account to chart."""
        return self.add(T5.Expense, account, title, offsets)

    def add_expenses(self, *account_names):
        """Add several expense accounts to chart."""
        for name in account_names:
            self.add_expense(name)
        return self


class NamedEntry(Entry):
    """Create entry with title and use .debit() and .credit() methods.
    Use .amount() method to set default amount for the entry.

    The syntax is similar to 'medici' package <https://github.com/flash-oss/medici>.
    """

    title: str | None = None
    _amount: Amount | None = None

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


def idle(named_entry: NamedEntry) -> None:
    """Do nothing."""
    pass


class UserEntry(NamedEntry):
    _post: Callable[[NamedEntry], None] = idle
    _append: Callable[[NamedEntry], None] = idle

    def commit(self):
        """Add current entry to list of saved entries and post to ledger."""
        named_entry = NamedEntry(
            title=self.title,
            debits=self.debits,
            credits=self.credits,
        )
        named_entry.validate_balance()
        self._post(named_entry)
        self._append(named_entry)
        return self


class EntryList(BaseModel):
    entries_before_close: List[NamedEntry] = []
    closing_entries: List[NamedEntry] = []
    entries_after_close: List[NamedEntry] = []

    def __iter__(self):
        return iter(self.entries_before_close + self.closing_entries + self.entries)

    def __len__(self):
        return (
            len(self.entries_before_close)
            + len(self.closing_entries)
            + len(self.entries_after_close)
        )

    def is_closed(self) -> bool:
        """Return True if ledger was closed."""
        return len(self.closing_entries) > 0

    def append(self, entry: NamedEntry):
        """Append entry to the list."""
        if self.is_closed():
            self.entries_after_close.append(entry)
        else:
            self.entries_before_close.append(entry)
        return self

    def append_closing(self, entry: NamedEntry):
        """Append closing entry to the list."""
        self.closing_entries.append(entry)
        return self


class LoadSaveMixin(BaseModel):
    default_directory: ClassVar[Path] = Path(".")
    default_filename: ClassVar[str] = "data.json"
    directory: Path | None = None
    filename: str | None = None

    def __init__(self, **data) -> None:
        super().__init__(**data)
        if self.directory is None:
            self.directory = self.default_directory
        if self.filename is None:
            self.filename = self.default_filename

    @property
    def path(self) -> Path:
        if isinstance(self.directory, Path) and self.filename is not None:
            return self.directory / self.filename
        raise AbacusError("Directory and filename were not set.")

    @classmethod
    def from_file(
        cls, directory: Path | str | None = None, filename: str | Path | None = None
    ):
        _path = Path(directory or cls.default_directory) / (
            filename or cls.default_filename
        )
        return cls.model_validate_json(_path.read_text())

    def to_file(
        self, directory: Path | str | None = None, filename: str | Path | None = None
    ):
        _path = Path(directory or self.directory) / (filename or self.filename)  # type: ignore
        _path.write_text(self.model_dump_json(indent=2))
        return _path


class EntryStore(EntryList, LoadSaveMixin):
    default_filename: ClassVar[str] = "entries.json"


class ChartStore(Chart, LoadSaveMixin):
    default_filename: ClassVar[str] = "chart.json"


class AccountBalancesDict(BaseModel):
    data: dict[str, Amount]


class AccountBalancesStore(AccountBalancesDict, LoadSaveMixin):
    default_filename: ClassVar[str] = "balances.json"


@dataclass
class Book:
    company: str
    chart: ChartStore = field(default_factory=ChartStore.default)
    entries: EntryStore = field(default_factory=EntryStore)  # type: ignore
    ledger: Ledger = PrivateAttr(default_factory=Ledger)
    _income_statement: IncomeStatement | None = None

    def entry(self, title: str) -> UserEntry:
        """Create new entry with callbacks to ledger and entry store."""
        _current_entry = UserEntry(title=title)
        _current_entry._post = self.ledger.post
        _current_entry._append = self.entries.append
        return _current_entry

    def double_entry(self, title, dr_account, cr_account, amount) -> UserEntry:
        """Create double entry."""
        return self.entry(title).amount(amount).debit(dr_account).credit(cr_account)

    def save(self, directory: Path = Path(".")):
        self.chart.to_file(directory=directory)
        self.entries.to_file(directory=directory)
        self.account_balances.to_file(directory=directory)
        return self

    @property
    def account_balances(self) -> AccountBalancesStore:
        return AccountBalancesStore(data=self.ledger.balances())  # type: ignore

    @classmethod
    def load(cls, company: str, directory: Path = Path(".")) -> "Book":
        book = cls(company)
        book.chart = ChartStore.from_file(directory=directory)
        book.entries = EntryStore.from_file(directory=directory)
        book.open()
        book.ledger.post_many(book.entries.entries_before_close)
        if book.entries.closing_entries:
            book._replicate_closing_entries(book.entries)
        return book

    def _replicate_closing_entries(self, entries):
        self._income_statement = IncomeStatement.new(self.ledger, self.chart)
        self.ledger.post_many(entries.closing_entries)
        for name in self.chart.temporary_accounts:
            del self.ledger[name]
        self.ledger.post_many(entries.entries_after_close)

    @property
    def trial_balance(self):
        """Return trial balance."""
        return self.ledger.trial_balance

    @property
    def balance_sheet(self):
        """Return balance sheet."""
        return BalanceSheet.new(self.ledger, self.chart)

    def open(self, opening_balances: dict[str, Amount] | None = None):
        """Create new ledger."""
        self.ledger = Ledger.new(self.chart)
        if opening_balances:
            self._commit_opening_entry(opening_balances)
        return self

    def _commit_opening_entry(self, opening_balances, title="Opening balances"):
        """Create and commit opening balances entry."""
        entry = self.entry(title)
        for account_name, amount in opening_balances.items():
            if self.ledger[account_name].side.is_debit():
                entry.debit(account_name, amount)
            else:
                entry.credit(account_name, amount)
        entry.commit()

    def close(self, title="Closing entry"):
        """Close ledger."""
        self._income_statement = IncomeStatement.new(self.ledger, self.chart)
        for closing_entry in self.ledger.close(self.chart):
            named_entry = closing_entry.add_title(title)
            self.entries.append_closing(named_entry)
        return self

    @property
    def income_statement(self):
        """Return income statement."""
        if self.entries.is_closed():
            return self._income_statement
        else:
            return IncomeStatement.new(self.ledger.copy(), self.chart)
