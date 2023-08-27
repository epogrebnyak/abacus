from dataclasses import dataclass
from typing import List, Type

# UserEntries -> ClosingEntries
from engine import (
    AccountName,
    Chart,
    ContraExpense,
    ContraIncome,
    Entry,
    Expense,
    Income,
    IncomeSummaryAccount,
    Ledger,
    RegularAccount,
    RetainedEarnings,
    UserEntries,
)


@dataclass
class ClosingEntries:
    closing_contra_income: List[Entry]
    closing_contra_expense: List[Entry]
    closing_income: List[Entry]
    closing_expense: List[Entry]
    closing_isa: List[Entry]


def make_closing_entries(chart: Chart, user_entries: UserEntries) -> ClosingEntries:
    dummy_ledger = user_entries.before_closing(chart).condense()
    a = close_contra_income(chart, dummy_ledger)
    b = close_contra_expense(chart, dummy_ledger)
    dummy_ledger.post(list(a + b))
    c = close_income_to_isa(chart.income_summary_account, dummy_ledger)
    d = close_expenses_to_isa(chart.income_summary_account, dummy_ledger)
    dummy_ledger.post(list(c + d))
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




def flush_contra_accounts(
    chart: Chart, ledger: Ledger, cls: Type[RegularAccount]
) -> List[Entry]:
    return [
        ledger[contra_account_name].transfer(contra_account_name, regular_account_name)
        for regular_account_name, contra_account_name in chart.contra_account_pairs(cls)
    ]

def close_contra_income(chart: Chart, ledger: Ledger) -> List[Entry]:
    """Make entries for closing contra income accounts (eg discounts, refunds made to clients).
    Balance transfered from contra account to corresponding income account.
    The income accounts will hold net value after these entries are posted.
    """
    return flush_contra_accounts(chart, ledger, Income)


def close_contra_expense(chart: Chart, ledger: Ledger) -> List[Entry]:
    """Make entries for closing contra expense accounts (eg discounts received).
    Balance transfered from contra account to corresponding expense account.
    The expense account will hold net value after these entries are posted.
    """
    return flush_contra_accounts(chart, ledger, Expense)


def close_income_to_isa(isa: AccountName, ledger: Ledger) -> List[Entry]:
    return [
        Entry(account_name, isa, t_account.balance())
        for account_name, t_account in subset(ledger, [Income]).items()
    ]


def close_expenses_to_isa(isa: AccountName, ledger: Ledger) -> List[Entry]:
    return [
        Entry(isa, account_name, t_account.balance())
        for account_name, t_account in subset(ledger, [Expense]).items()
    ]


def close_isa(isa: AccountName, re: AccountName, ledger: Ledger) -> Entry:
    """Make entry to close income summary account ("isa") and move its balance to retained earnings."""
    amount = ledger[isa].balance()
    return Entry(isa, re, amount)


def closing_entries(chart: Chart, ledger: Ledger) -> List[Entry]:
    x = closing_entries_temp(chart, ledger)
    y = closing_entries_rest(chart, ledger)
    return list(x + y)


def closing_entries_temp(chart: Chart, ledger: Ledger) -> List[Entry]:
    a = close_contra_income(chart, ledger)
    b = close_contra_expense(chart, ledger)
    return list(a + b)


def closing_entries_rest(chart: Chart, ledger: Ledger) -> List[Entry]:
    classes = [
        Income,
        Expense,
        ContraIncome,
        ContraExpense,
        RetainedEarnings,
        IncomeSummaryAccount,
    ]
    dummy_legder = subset(ledger, classes).condense()
    a = close_contra_income(chart, dummy_legder)
    b = close_contra_expense(chart, dummy_legder)
    dummy_legder.post(list(a + b))
    c = close_income_to_isa(chart.income_summary_account, dummy_legder)
    d = close_expenses_to_isa(chart.income_summary_account, dummy_legder)
    dummy_legder.post(list(c + d))
    e = close_isa(
        isa=chart.income_summary_account,
        re=chart.retained_earnings_account,
        ledger=dummy_legder,
    )
    return list(c + d + [e])
