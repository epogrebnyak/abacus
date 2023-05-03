# pylint: disable=import-error, no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name


# Chart -> Ledger -> [Entry] -> Ledger -> [ClosingEntry] -> Ledger
# Ledger -> IncomeStatement
# Ledger -> BalanceSheet
# Ledger -> TrialBalance
# TrialBalance -> Ledger (for reset of balances)

# NamedEntries
# Depreciation/Amortisation and accumulation rules
# Print to screen
# Idea of app workflow


from typing import List, Tuple
from abacus.accounting_types import (
    Amount,
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


def income_summary_account_name(ledger: Ledger) -> AccountName:
    return list(subset_by_class(ledger, IncomeSummaryAccount).keys())[0]


def subset_by_class(ledger, cls):
    return Ledger(
        (account_name, account)
        for account_name, account in ledger.items()
        if isinstance(account, cls)
    )


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


def balances(ledger: Ledger) -> AccountBalancesDict:
    return AccountBalancesDict(
        {account_name: account.balance() for account_name, account in ledger.items()}
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
    isa = income_summary_account_name(_dummy_ledger)
    amount = _dummy_ledger[isa].balance()

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
