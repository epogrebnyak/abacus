from dataclasses import dataclass, field

from pydantic import BaseModel

from core import (
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

    title: str
    _amount: Amount | int | float | None = None
    _entry: MultipleEntry = field(default_factory=MultipleEntry)

    @classmethod
    def empty(cls):
        return cls("Entry title was not set.")

    def amount(self, amount: Amount | int | float):
        """Set default amount for this entry."""
        self._amount = Amount(amount)
        return self

    def _get(self, amount: Amount | int | float | None = None) -> Amount:
        try:
            return Amount(amount or self._amount)
        except TypeError:
            raise AbacusError(f"Amount must be provided, got {amount}.")

    def debit(
        self, account_name: AccountName, amount: Amount | int | float | None = None
    ):
        """Add debit entry or debit account name."""
        amount = self._get(amount)
        self._entry.debit(account_name, amount)
        return self

    def credit(
        self, account_name: AccountName, amount: Amount | int | float | None = None
    ):
        """Add credit entry or credit account name."""
        amount = self._get(amount)
        self._entry.credit(account_name, amount)
        return self

    def __iter__(self):
        return iter(self._entry)

    @property
    def stored_entry(self) -> StoredEntry:
        return StoredEntry(
            title=self.title,
            debits=[(e.name, e.amount) for e in self._entry.debits],
            credits=[(e.name, e.amount) for e in self._entry.credits],
        )


@dataclass
class Book:
    company_name: str
    chart: Chart | ClosableChart = Chart()
    ledger: Ledger = Ledger({})
    entries: list[StoredEntry] = field(default_factory=list)
    _current_entry: NamedEntry = NamedEntry.empty()
    _current_id: int = 0  # reserved
    _last_added: str | None = None
    income_statement: IncomeStatement = IncomeStatement(income={}, expenses={})

    @property
    def trial_balance(self):
        return TrialBalance.new(self.ledger, self.chart)

    @property
    def balance_sheet(self):
        return BalanceSheet.new(self.ledger, self.chart)

    def _add(self, key, accounts):
        if isinstance(accounts, tuple):
            for a in accounts:
                self._add(key, a)
        if isinstance(accounts, str):
            accounts = Account(accounts)
        if isinstance(accounts, Account):
            getattr(self.chart, key).append(accounts)
            self._last_added = accounts.name
        return self

    def add_assets(self, *accounts):
        return self._add("assets", accounts)

    def add_liabilities(self, *accounts):
        return self._add("liabilities", accounts)

    def add_capital(self, *accounts):
        return self._add("capital", accounts)

    def add_income(self, *accounts):
        return self._add("income", accounts)

    def add_expenses(self, *accounts):
        return self._add("expenses", accounts)

    def offset(self, *contra_account_names):
        for attr in ["assets", "capital", "liabilities", "income", "expenses"]:
            for account in getattr(self.chart, attr):
                if account.name == self._last_added:
                    account.offset(*contra_account_names)
        return self

    def set_income_summary_account(self, account_name: str):
        self.chart.income_summary_account = account_name
        return self

    def set_retained_earnings_account(self, account_name: str):
        self.chart = self.chart.set_retained_earnings(account_name)
        return self

    def open(self):
        try:
            self.chart.retained_earnings_account
        except AttributeError:
            self.set_retained_earnings_account("retained_earnings")
        self.ledger = Ledger.new(self.chart)
        return self

    def entry(self, title: str):
        self._current_entry = NamedEntry(title)
        return self

    def amount(self, amount: Amount | int | float):
        self._current_entry.amount(amount)
        return self

    def debit(self, account_name: str, amount: Amount | int | float | None = None):
        self._current_entry.debit(account_name, amount)
        return self

    def credit(self, account_name: str, amount: Amount | int | float | None = None):
        self._current_entry.credit(account_name, amount)
        return self

    def commit(self):
        self.ledger.post(self._current_entry)
        self.entries.append(self._current_entry.stored_entry)
        self._current_entry = NamedEntry.empty()
        self._current_id += 1
        return self

    def close(self):
        closing_entries, self.ledger, self.income_statement = self.ledger.close(
            self.chart
        )
        self.entries.extend(closing_entries)
        return self

    @property
    def proxy_income_statement(self):
        _, _, income_statement = self.ledger.copy().close(self.chart)
        return income_statement

    @property
    def proxy_net_earnings(self) -> Amount:
        return self.proxy_income_statement.net_earnings
