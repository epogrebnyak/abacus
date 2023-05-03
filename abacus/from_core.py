# pylint: disable=import-error, no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from .base import (
    Account,
    Amount,
    DebitAccount,
    CreditAccount,
    AccountName,
    Chart,
    Asset,
    Expense,
    Capital,
    Liability,
    Income,
    IncomeSummaryAccount,
    Ledger,
    AccountBalancesDict,
    Entry,
    BalanceSheet,
    IncomeStatement,
    ClosingEntry,
)
from typing import List, Tuple


def make_ledger(chart: Chart) -> Ledger:
    ledger = Ledger()
    attributes = [
        ("assets", Asset),
        ("expenses", Expense),
        ("equity", Capital),
        ("liabilities", Liability),
        ("income", Income),
    ]
    for attr, _cls in attributes:
        for account_name in getattr(chart, attr):
            ledger[account_name] = _cls()
    ledger[chart.income_summary_account] = IncomeSummaryAccount()
    return ledger


def subset_by_class(ledger, cls):
    return Ledger(
        (account_name, account)
        for account_name, account in ledger.items()
        if isinstance(account, cls)
    )


def income_summary_account_name(ledger: Ledger) -> AccountName:
    return list(subset_by_class(ledger, IncomeSummaryAccount).keys())[0]


def assets(ledger):
    return subset_by_class(ledger, Asset)


def expenses(ledger):
    return subset_by_class(ledger, Expense)


def capital(ledger):
    return subset_by_class(ledger, Capital)


def liabilities(ledger):
    return subset_by_class(ledger, Liability)


def income(ledger):
    return subset_by_class(ledger, Income)


def process_entries(ledger: Ledger, entries: List[Entry]) -> Ledger:
    ledger, _failed_entries = safe_process_entries(ledger, entries)
    if _failed_entries:
        raise KeyError(_failed_entries)
    return ledger


def safe_process_entries(
    ledger: Ledger, entries: List[Entry]
) -> Tuple[Ledger, List[Entry]]:
    _ledger = ledger.safe_copy()
    _failed = []
    for entry in entries:
        try:
            _ledger[entry.dr].debit(entry.amount)
            _ledger[entry.cr].credit(entry.amount)
        except KeyError:
            _failed.append(entry)
    return _ledger, _failed


def balance(account: Account) -> Amount:
    match account:
        case DebitAccount(ds, cs):
            return sum(ds) - sum(cs)
        case CreditAccount(ds, cs):
            return sum(cs) - sum(ds)


def balances(ledger: Ledger) -> AccountBalancesDict:
    return AccountBalancesDict(
        (account_name, balance(account)) for account_name, account in ledger.items()
    )


def closing_entries_for_income_accounts(ledger) -> List[ClosingEntry]:
    isa = income_summary_account_name(ledger)
    return [
        ClosingEntry(
            amount=amount,
            dr=account_name,
            cr=isa,
        )
        for account_name, amount in balances(income(ledger)).items()
    ]


def closing_entries_for_expense_accounts(ledger) -> List[ClosingEntry]:
    isa = income_summary_account_name(ledger)
    return [
        ClosingEntry(
            amount=amount,
            dr=isa,
            cr=account_name,
        )
        for account_name, amount in balances(expenses(ledger)).items()
    ]


def closing_entries(
    ledger: Ledger, retained_earnings_account_name: AccountName
) -> List[ClosingEntry]:
    isa = income_summary_account_name(ledger)
    # fmt: off
    entries = closing_entries_for_income_accounts(ledger) \
            + closing_entries_for_expense_accounts(ledger)
    # fmt: on

    # We actually process the closing to find out the profit.
    # Alternative is to use amount = current_profit(ledger).
    # process_entries() was altering ledger before proper
    # coping was introduced with .safe_copy() methods
    # in Legder and Account classes.
    _dummy_ledger = process_entries(ledger, entries)
    amount = balance(_dummy_ledger[isa])

    return entries + [
        ClosingEntry(
            amount=amount,
            cr=retained_earnings_account_name,
            dr=isa,
        )
    ]


def close(ledger: Ledger, retained_earnings_account_name: AccountName) -> Ledger:
    entries = closing_entries(ledger, retained_earnings_account_name)
    return process_entries(ledger, entries)


def balance_sheet(ledger: Ledger) -> BalanceSheet:
    return BalanceSheet(
        assets=balances(assets(ledger)),
        capital=balances(capital(ledger)),
        liabilities=balances(liabilities(ledger)),
    )


def income_statement(ledger: Ledger) -> IncomeStatement:
    return IncomeStatement(
        income=balances(income(ledger)),
        expenses=balances(expenses(ledger)),
    )


def current_profit(ledger: Ledger) -> Amount:
    return income_statement(ledger).current_profit()


chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
)

# pay capital
e1 = Entry(dr="cash", cr="equity", amount=1000)
# aquire goods
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250)
# sell goods
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200)
e4 = Entry(cr="sales", dr="cash", amount=400)
# selling expenses
e5 = Entry(cr="cash", dr="sga", amount=50)
entries = [e1, e2, e3, e4, e5]

ledger = make_ledger(chart)
ledger2 = process_entries(ledger, entries)
ledger3 = close(ledger2, retained_earnings_account_name="re")
assert balances(ledger3) == {
    "cash": 1100,
    "receivables": 0,
    "goods_for_sale": 50,
    "cogs": 0,
    "sga": 0,
    "equity": 1000,
    "re": 150,
    "divp": 0,
    "payables": 0,
    "sales": 0,
    "profit": 0,
}

# make this a test
print(balance_sheet(ledger3))
print(income_statement(ledger2))

# make trial balance

# Chart -> Ledger -> [Entry] -> Ledger -> [ClosingEntry] -> Ledger
# Ledger -> IncomeStatement
# Ledger -> BalanceSheet
# Ledger -> TrialBalance
# TrialBalance -> Ledger (for reset of balances)

# NamedEntries
# Depreciation/Amortisation and accumulation rules
# Print to screen
# Idea of app workflow
