from dataclasses import dataclass
from typing import List, Type

from engine import (
    AccountName,
    Amount,
    Asset,
    Capital,
    Chart,
    Entry,
    Expense,
    Income,
    Liability,
    RegularAccount,
)
from ledger import Ledger

__all__ = [
    "close_contra_income",
    "close_contra_expense",
    "make_closing_entries",
    "flush_permanent_accounts",
]


def flush_permanent_accounts(chart: Chart, ledger: Ledger) -> List[Entry]:
    def f(cls):
        return _flush(chart, ledger, cls)

    return f(Asset) + f(Capital) + f(Liability)


@dataclass
class ClosingEntries:
    """Closing entries for accounts related to income and expenses."""

    closing_contra_income: List[Entry]
    closing_contra_expense: List[Entry]
    closing_income: List[Entry]
    closing_expense: List[Entry]
    closing_isa: Entry

    @property
    def closing_contra_accounts(self) -> List[Entry]:
        return self.closing_contra_income + self.closing_contra_expense

    @property
    def closing_income_expense_isa(self) -> List[Entry]:
        return self.closing_income + self.closing_expense + [self.closing_isa]

    def all(self):
        return self.closing_contra_accounts + self.closing_income_expense_isa


def make_closing_entries(chart: Chart, ledger: Ledger) -> ClosingEntries:
    """Create a data structure holding closing entries related to income and expense accounts.
    Steps taken are the following:
    - close contra accounts to income and expense accounts
    - close income and expense accounts
    - close iscome summary account to retained earnings.
    Must post entries to ledger copy between these steps to obtain proper account balances.
    """
    dummy_ledger = ledger.condense()
    a = close_contra_income(chart, dummy_ledger)
    b = close_contra_expense(chart, dummy_ledger)
    dummy_ledger.post(a + b)
    c = close_income_to_isa(chart.income_summary_account, dummy_ledger)
    d = close_expenses_to_isa(chart.income_summary_account, dummy_ledger)
    dummy_ledger.post(c + d)
    e = close_isa(
        isa=chart.income_summary_account,
        re=chart.retained_earnings_account,
        ledger=dummy_ledger,
    )
    return ClosingEntries(
        closing_contra_income=a,
        closing_contra_expense=b,
        closing_income=c,
        closing_expense=d,
        closing_isa=e,
    )


def _flush(chart: Chart, ledger: Ledger, cls: Type[RegularAccount]) -> List[Entry]:
    """Make a list of entries for transferring balances for accounts of a certain type.
    The type of accounts is contra accounts for *cls*, e.g. when provided Income,
    the entries will transfer balances from ContraIncome accounts to Income accounts.
    These entries are used to close contra accounts."""
    return [
        ledger[contra_account_name].transfer(contra_account_name, regular_account_name)  # type: ignore
        for regular_account_name, contra_account_name in chart.contra_account_pairs(cls)
    ]


def close_contra_income(chart: Chart, ledger: Ledger) -> List[Entry]:
    """Make entries for closing contra income accounts (eg discounts, refunds made to clients).
    Balance transfered from contra account to corresponding income account.
    The income accounts will hold net value after these entries are posted.
    """
    return _flush(chart, ledger, Income)


def close_contra_expense(chart: Chart, ledger: Ledger) -> List[Entry]:
    """Make entries for closing contra expense accounts (eg discounts received).
    Balance transfered from contra account to corresponding expense account.
    The expense account will hold net value after these entries are posted.
    """
    return _flush(chart, ledger, Expense)


def close_income_to_isa(isa: AccountName, ledger: Ledger) -> List[Entry]:
    return [
        Entry(account_name, isa, t_account.balance())
        for account_name, t_account in ledger.subset(Income).items()
    ]


def close_expenses_to_isa(isa: AccountName, ledger: Ledger) -> List[Entry]:
    return [
        Entry(isa, account_name, t_account.balance())
        for account_name, t_account in ledger.subset(Expense).items()
    ]


def close_isa(isa: AccountName, re: AccountName, ledger: Ledger) -> Entry:
    """Make entry to close income summary account ("isa") and move its balance to retained earnings."""
    amount = ledger[isa].balance()
    return Entry(isa, re, amount)


if __name__ == "__main__":
    doc_ = """
    cash,equity,1000
    goods,cash,800
    cogs,goods,700
    ar,sales,899
    refunds,ar,89
    cashback,ar,10
    cash,ar,400
    sga,cash,50
    """

    def to_entries(doc: str):
        def make(line):
            a, b, c = line.split(",")
            return Entry(a.strip(), b.strip(), Amount(c))

        return [make(line) for line in doc.strip().split("\n")]

    chart_ = Chart(
        assets=["cash", "goods", "ar"],
        equity=["equity"],
        income=["sales"],
        expenses=["cogs", "sga"],
        contra_accounts={"sales": ["refunds", "cashback"]},
    )
    ledger_ = Ledger.new(chart_).post(to_entries(doc_))
    assert len(make_closing_entries(chart_, ledger_).all()) == 6
    assert ledger_.close(chart_).balances()["re"] == 50
    assert ledger_.close_some(chart_).subset([Income, Expense]).balances() == {
        "cogs": 700,
        "sga": 50,
        "sales": 800,
    }
