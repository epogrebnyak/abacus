from dataclasses import dataclass, field
from typing import Callable, List

from pydantic import BaseModel

from core import AccountName, Amount, BalanceSheet, Entry, IncomeStatement, Ledger


class UserChart(BaseModel):
    """UserChart is serialisable chart of accounts that a user can modify."""

    assets: list[str] = []
    capital: list[str] = []
    liabilities: list[str] = []
    income: list[str] = []
    expenses: list[str] = []
    retained_earnings: str = "retained_earnings"
    income_summary: str = "_isa"
    contra_accounts: dict[str, list[str]] = {}
    names: dict[str, str] = {}

    @property
    def chart_dict(self):
        from core import T5, ChartDict

        cd = ChartDict()
        for attrib, t in [
            ("assets", T5.Asset),
            ("capital", T5.Capital),
            ("liabilities", T5.Liability),
            ("income", T5.Income),
            ("expenses", T5.Expense),
        ]:
            for name in getattr(self, attrib):
                cd.set(t, name)
        for name, contra_accounts in self.contra_accounts.items():
            for contra_name in contra_accounts:
                cd.offset(name, contra_name)
        return cd

    @property
    def strict(self) -> "Chart":
        from core import Chart

        return Chart(
            income_summary_account=self.income_summary,
            retained_earnings_account=self.retained_earnings,
            accounts=self.chart_dict,
        )

    def add(self, attrib: str, name: str, title: str, contra_accounts: list[str]):
        getattr(self, attrib).append(name)
        self.set_title(name, title)
        for contra_name in contra_accounts:
            self.offset(name, contra_name)

    def add_asset(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("assets", name, title, contra_accounts or [])

    def add_capital(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("capital", name, title, contra_accounts or [])

    def add_liability(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("liabilities", name, title, contra_accounts or [])

    def add_income(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("income", name, title, contra_accounts or [])

    def add_expense(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("expenses", name, title, contra_accounts or [])

    def offset(self, name: str, contra_name: str, title: str = ""):
        if name not in self.contra_accounts:
            self.contra_accounts[name] = []
        self.contra_accounts[name].append(contra_name)
        self.set_title(contra_name, title)

    def set_title(self, name: str, title: str):
        if title:
            self.names[name] = title

    def set_retained_earnings_account(self, name: str):
        self.retained_earnings = name

    def set_income_summary_account(self, name: str):
        self.income_summary = name


# type alias for user inputed number
Numeric = Amount | int | float


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

    @classmethod
    def from_entry(cls, entry: Entry, title: str) -> "NamedEntry":
        """Create named entry with title."""

        return cls(title=title, debits=entry.debits, credits=entry.credits)

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


def idle(_: NamedEntry):
    pass


class UserEntry(NamedEntry):
    post_hook: Callable[[NamedEntry], None]
    append_hook: Callable[[NamedEntry], None]

    def commit(self):
        """Add current entry to list of saved entries and post to ledger."""
        named_entry = NamedEntry(
            title=self.title,
            debits=self.debits,
            credits=self.credits,
        )
        named_entry.validate_balance()
        self.post_hook(named_entry)
        self.append_hook(named_entry)
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


@dataclass
class Book:
    chart: UserChart = field(default_factory=UserChart)
    entries: EntryList = field(default_factory=EntryList)
    ledger: Ledger = field(default_factory=Ledger)
    _finalised_income_statement: IncomeStatement | None = None

    def open(self, opening_balances: dict[str, Amount] | None = None):
        """Create new ledger."""
        self.ledger = Ledger.new(self.chart.strict)
        if opening_balances:
            entry = self.entry(title="Opening balances")
            for account_name, amount in opening_balances.items():
                if self.ledger[account_name].side.is_debit():
                    entry.debit(account_name, amount)
                else:
                    entry.credit(account_name, amount)
            entry.commit()
        return self

    def entry(self, title: str) -> UserEntry:
        """Create new entry with callbacks to ledger and entry store."""
        return UserEntry(
            title=title, post_hook=self.ledger.post, append_hook=self.entries.append
        )

    def close(self):
        """Close ledger."""
        self._finalised_income_statement = IncomeStatement.new(
            self.ledger, self.chart.strict
        )
        for closing_entry in self.ledger.close(self.chart.strict):
            named_entry = closing_entry.add_title(title="Closing entry")
            self.entries.append_closing(named_entry)
        return self

    @property
    def income_statement(self):
        """Return income statement."""
        if self.entries.is_closed():
            return self._finalised_income_statement
        else:
            return IncomeStatement.new(self.ledger.copy(), self.chart.strict)

    @property
    def trial_balance(self):
        """Return trial balance."""
        return self.ledger.trial_balance

    @property
    def balance_sheet(self):
        """Return balance sheet."""
        return BalanceSheet.new(self.ledger, self.chart.strict)


book = Book()
book.chart.add_asset("cash")
book.chart.add_asset("ar", title="Accounts receivable")
book.chart.add_asset("inventory")
book.chart.set_title("ar", "Accounts receivable")
book.chart.add_capital("equity")
book.chart.offset("equity", "ts", title="Treasury shares")
book.chart.add_income("sales", contra_accounts=["refunds", "cashback"])
book.chart.add_expense("cogs", title="Cost of goods sold")
book.chart.add_expense("salaries")
book.chart.add_expense("cit", title="Income tax")
book.chart.add_liability("vat", title="VAT payable")
book.chart.add_liability("dividend")
book.chart.add_liability("cit_due", title="Income tax payable")
book.chart.set_retained_earnings_account("re")
book.chart.set_income_summary_account("_isa")
# fmt: off
book.open(opening_balances={"cash": 1500, "equity": 1500})
book.entry("Bought inventory (no VAT)").amount(1000).debit("inventory").credit("cash").commit()
book.entry("Invoice with 20% VAT").debit("ar", 1200).credit("sales", 1000).credit("vat", 200).commit()
book.entry("Registered costs").amount(600).debit("cogs").credit("inventory").commit()
book.entry("Accepted payment").amount(900).credit("ar").debit("cash").commit()
book.entry("Made refund").amount(50).debit("refunds").credit("ar").commit()
book.entry("Provided  cashback").amount(50).debit("cashback").credit("cash").commit()
book.entry("Paid salaries").amount(150).credit("cash").debit("salaries").commit()
assert book.income_statement.net_earnings == 150
book.entry("Accrue corporate income tax 20%").amount(30).credit("cit_due").debit("cit").commit()
book.close()
book.entry("Bought back shares").amount(30).debit("ts").credit("cash").commit()
book.entry("Announced dividend").amount(60).debit("re").credit("dividend").commit()
book.entry("Paid corporate income tax").amount(30).debit("cit_due").credit("cash").commit()
# fmt: on
assert book.income_statement.dict() == {
    "income": {"sales": 900},
    "expenses": {"cogs": 600, "salaries": 150, "cit": 30},
}

assert book.balance_sheet.dict() == {
    "assets": {"cash": 1140, "ar": 250, "inventory": 400},
    "capital": {"equity": 1470, "re": 60},
    "liabilities": {"vat": 200, "dividend": 60, "cit_due": 0},
}
