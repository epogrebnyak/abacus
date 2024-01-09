from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel

from abacus.base import Amount
from abacus.core import (
    BalanceSheet,
    CompoundEntry,
    Entry,
    IncomeStatement,
    Ledger,
    Pipeline,
    TrialBalance,
)
from abacus.user_chart import UserChart, make_user_chart
from abacus.viewers import BalanceSheetViewer, IncomeStatementViewer, TrialBalanceViewer


class EntryType(Enum):
    Starting = "starting"
    Business = "business"
    Adjustment = "adjustment"
    Closing = "closing"


class Transaction(BaseModel):
    title: str
    entries: list[Entry]
    type: EntryType
    # may include date and UUID


def create_book(company_name: str):
    user_chart = UserChart(
        income_summary_account="_isa",
        retained_earnings_account="retained_earnings",
        null_account="_null",
        company_name=company_name,
    )
    return Book(chart=user_chart)


@dataclass
class Book:
    chart: UserChart = field(default_factory=make_user_chart)
    transactions: list[Transaction] = field(default_factory=list)

    @property
    def company(self):
        return self.chart.company_name

    @property
    def entries(self) -> list[Entry]:
        return [e for t in self.transactions for e in t.entries]

    @property
    def entries_without_closing(self) -> list[Entry]:
        return [
            e
            for t in self.transactions
            if t.type != EntryType.Closing
            for e in t.entries
        ]

    def post(self, title, amount, debit, credit):
        entry = Entry(debit, credit, amount)
        self._transact(title, [entry], EntryType.Business)

    def post_compound(self, title, debits, credits):
        entries = CompoundEntry(debits, credits).to_entries(self.chart.null_account)
        self._transact(title, entries, EntryType.Business)

    def load(self, starting_balances):
        from abacus.core import starting_entries as f

        entries = f(self.chart.chart(), starting_balances)
        self._transact(self, "Starting balances", entries, EntryType.Starting)

    @property
    def _ledger0(self) -> Ledger:
        return self.chart.chart().ledger()

    @property
    def ledger(self):
        """Current state of the ledger."""
        return self._ledger0.post_many(self.entries)

    def _pipeline(self, ledger):
        return Pipeline(self.chart.chart(), ledger)

    @property
    def _ledger_for_income_statement(self):
        proxy_ledger = self._ledger0.post_many(self.entries_without_closing).condense()
        p = self._pipeline(proxy_ledger).close_first()
        return proxy_ledger.post_many(p.closing_entries)

    def close_period(self):
        """Add closing entries at the end of accounting period."""
        p = self._pipeline(self.ledger).close()
        self._transact("Closing entries", p.closing_entries, EntryType.Closing)

    def _transact(self, title, entries, type_):
        t = Transaction(title=title, entries=entries, type=type_)
        self.transactions.append(t)

    def is_closed(self) -> bool:
        return len([t for t in self.transactions if t.type == EntryType.Closing]) > 0

    @property
    def balance_sheet(self) -> BalanceSheetViewer:
        return BalanceSheetViewer(
            statement=BalanceSheet.new(self.ledger),
            title="Balance sheet: " + self.company,
            rename_dict=self.chart.rename_dict,
        )

    @property
    def income_statement(self) -> IncomeStatementViewer:
        return IncomeStatementViewer(
            statement=IncomeStatement.new(self._ledger_for_income_statement),
            title="Income statement: " + self.company,
            rename_dict=self.chart.rename_dict,
        )

    @property
    def trial_balance(self) -> TrialBalanceViewer:
        return TrialBalanceViewer(
            TrialBalance.new(self.ledger),
            title="Trial balance: " + self.company,
            rename_dict=self.chart.rename_dict,
        )

    @property
    def account_balances(self):
        return self.ledger.balances

    def print_all(self):
        t = self.trial_balance
        b = self.balance_sheet
        i = self.income_statement
        width = 2 + max(t.width, b.width, i.width)
        t.print(width)
        b.print(width)
        i.print(width)

    def save(self, chart_path, entries_path):
        ...


book = create_book("Dragon Trading Company")

# Register account names
book.chart.add_assets("cash", "ar", "inventory", "prepaid_insurance")
book.chart.add_capital("equity", retained_earnings_account="retained_earnings")
book.chart.add_liabilities("vat", "ap")
book.chart.add_income("sales")
book.chart.add_expenses("salaries", "rent", "insurance")
book.chart.offset("sales", "refunds")
book.chart.name("vat", "VAT payable")
book.chart.name("ap", "Other accounts payable")
book.chart.name("ar", "Accounts receivable")

# Post double entry
book.post("Shareholder investment", amount=1500, debit="cash", credit="equity")
# Post compound entry
book.post_compound(
    "Invoice with VAT", debits=[("ar", 120)], credits=[("sales", 100), ("vat", 20)]
)

# Close, print to screen and save
book.close_period()
print(book.entries)
print(book.transactions)
print(book.chart)
print(book.trial_balance)
print(book.balance_sheet)
print(book.income_statement)
print(book.account_balances)
book.print_all()
book.save(chart_path="./chart.json", entries_path="./entries.linejson")

# IDEAS: interchangeable list(in-memory) vs LineJSON
# .new(), .append(), .iter(), save()

# MORE IDEAS:
# set --assets cash ar inv prepaid_insurance
# set --liabilities ap
# set --capital equity
# set --income sales
# set --expenses cogs sga
# set --re retained_earnings
# offset
# name
# add contra:sales:refunds
# init "Dunder Mufflin"

