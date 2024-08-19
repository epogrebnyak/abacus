from dataclasses import dataclass, field

from pydantic import BaseModel

from core import (
    T5,
    AbacusError,
    Account,
    AccountName,
    Amount,
    BalanceSheet,
    Chart,
    ClosableChart,
    IncomeStatement,
    IterableEntry,
    Ledger,
    MultipleEntry,
    TrialBalance,
)


class StoredEntry(BaseModel):
    title: str
    debits: list[tuple[AccountName, Amount]]
    credits: list[tuple[AccountName, Amount]]


@dataclass
class NamedEntry(IterableEntry):
    """Create entry using .debit() and .credit() methods.

    The syntax is similar to 'medici' package (<https://github.com/flash-oss/medici>),
    also added .amount() method to set default amount for the entry.
    """

    title: str | None = None
    _amount: Amount | int | float | None = None
    _entry: MultipleEntry = field(default_factory=MultipleEntry)

    def amount(self, amount: Amount | int | float):
        """Set default amount for this entry."""
        self._amount = Amount(amount)
        return self

    def debit(
        self, account_name: AccountName, amount: Amount | int | float | None = None
    ):
        """Add debit entry or debit account name."""
        amount = Amount(amount or self._amount)
        self._entry.debit(account_name, amount)
        return self

    def credit(
        self, account_name: AccountName, amount: Amount | int | float | None = None
    ):
        """Add credit entry or credit account name."""
        amount = Amount(amount or self._amount)
        self._entry.credit(account_name, amount)
        return self

    def __iter__(self):
        return iter(self._entry)

    @property
    def stored(self):
        return StoredEntry(
            title=self.title,
            debits=[(d.name, d.amount) for d in self._entry.debits],
            credits=[(c.name, c.amount) for c in self._entry.credits],
        )


MAPPER = dict(
    asset="assets",
    capital="capital",
    liability="liabilities",
    income="income",
    expense="expenses",
)


def t5_to_attr(t5: T5) -> str:
    return MAPPER[t5.value]


@dataclass
class Book:
    company_name: str
    chart_path: str = "./chart.json"
    entries_path: str = "./entries.linejson"
    chart: Chart | ClosableChart = Chart()
    ledger: Ledger | None = None
    entries: list[StoredEntry] = field(default_factory=list)
    _current_entry: NamedEntry = NamedEntry()
    _current_id: int = 0  # reserved
    income_statement: IncomeStatement = IncomeStatement(income={}, expenses={})

    @property
    def trial_balance(self):
        return TrialBalance.new(self.ledger, self.chart)

    @property
    def balance_sheet(self):
        return BalanceSheet.new(self.ledger, self.chart)

    def _add(self, t5: str, account_name: str | list[str], offsets: list[str] | None):
        if isinstance(account_name, list) and offsets:
            raise AbacusError("Cannot offset many accounts.")
        if isinstance(account_name, list):
            for name in account_name:
                self._add(t5, name, offsets)
            return self
        offsets = offsets or []
        account = Account(account_name, offsets)
        attr = t5_to_attr(t5)
        getattr(self.chart, attr).append(account)
        return self

    def add_asset(self, account, *, offsets=None):
        return self._add(T5.Asset, account, offsets)

    def add_liability(self, account, *, offsets=None):
        return self._add(T5.Liability, account, offsets)

    def add_capital(self, account, *, offsets=None):
        return self._add(T5.Capital, account, offsets)

    def add_income(self, account, *, offsets=None):
        return self._add(T5.Income, account, offsets)

    def add_expense(self, account, *, offsets=None):
        return self._add(T5.Expense, account, offsets)

    def set_income_summary_account(self, account_name: str):
        self.chart.income_summary_account = account_name
        return self

    def set_retained_earnings(self, account_name: str):
        self.chart = self.chart.set_retained_earnings(account_name)
        return self

    def open(self):
        """Create new ledger."""
        try:
            self.chart.retained_earnings_account
        except AttributeError:
            self.set_retained_earnings("retained_earnings")
        self.ledger = Ledger.new(self.chart)
        return self

    def entry(self, title: str):
        """Start new entry."""
        self._current_entry = NamedEntry(title)
        return self

    def amount(self, amount: Amount | int | float):
        """Set amount for the current entry."""
        self._current_entry.amount(amount)
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
        self.entries.append(self._current_entry.stored)
        self._current_entry = NamedEntry()
        self._current_id += 1
        return self

    def close(self):
        """Close ledger."""
        closing_entries, self.ledger, self.income_statement = self.ledger.close(
            self.chart
        )
        for ce in closing_entries:
            ne = NamedEntry("Closing entry", _entry=ce.multiple_entry)
            self.entries.append(ne.stored)
        return self

    @property
    def proxy_income_statement(self):
        _, _, income_statement = self.ledger.copy().close(self.chart)
        return income_statement

    @property
    def proxy_net_earnings(self) -> Amount:
        return self.proxy_income_statement.net_earnings

    def save_chart(self):
        pass

    def load_chart(self):
        pass

    def overwrite_entries(self):
        pass

    def append_entries(self):
        pass

    def load_entries(self):
        pass
