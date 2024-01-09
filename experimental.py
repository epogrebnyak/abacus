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


class Author(Enum):
    User = "from_user"
    Machine = "generated"


class Transaction(BaseModel):
    title: str
    entries: list[Entry]
    author: Author
    # may include date and UUID


def prefix(p, strings):
    return [p + ":" + s for s in strings]


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
    starting_balances: dict[str, Amount] = field(default_factory=dict)

    @property
    def company(self):
        return self.chart.company_name

    @property
    def entries(self) -> list[Entry]:
        return [e for t in self.transactions for e in t.entries]

    @property
    def entries_not_touching_isa(self) -> list[Entry]:
        isa = self.chart.income_summary_account

        def not_isa(entry):
            return (entry.debit != isa) and (entry.credit != isa)

        return list(filter(not_isa, self.entries))

    def post(self, title, amount, debit, credit):
        entry = Entry(debit, credit, amount)
        self._transact_user(title, [entry])

    def post_compound(self, title, debits, credits):
        entry = CompoundEntry(debits, credits)
        self._transact_user(title, entry.to_entries(self.chart.null_account))

    # TODO: post to first transaction
    @property
    def _ledger0(self) -> Ledger:
        return self.chart.chart().ledger(self.starting_balances)

    @property
    def ledger(self):
        """Current state of the ledger unmodified."""
        return self._ledger0.post_many(self.entries)

    def pipeline(self, ledger):
        return Pipeline(self.chart.chart(), ledger)

    @property
    def _ledger_for_income_statement(self):
        ledger = self._ledger0.post_many(self.entries_not_touching_isa).condense()
        p = self.pipeline(ledger).close_first()
        return ledger.post_many(p.closing_entries)

    def close_period(self):
        """Add closing entries at the end of accounting period."""
        p = self.pipeline(self.ledger).close()
        self._transact_machine("Closing entries", p.closing_entries)

    def _transact_machine(self, title, entries):
        self._transact(title, entries, Author.Machine)

    def _transact_user(self, title, entries):
        self._transact(title, entries, Author.User)

    def _transact(self, title, entries, author):
        t = Transaction(title=title, entries=entries, author=author)
        self.transactions.append(t)

    def is_closed(self) -> bool:
        return "Closing entries" in [
            t.title for t in self.transactions if t.author == Author.Machine
        ]

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
# load balances.json
# user_chart as book.chart
# book.chart.set_assets(cash, ar, inv)
# load should load as first transaction
# company name in user_chart p
# question about post to ledger
# extract.py question about testing mkdocs scripts
