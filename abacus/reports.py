# pylint: disable=import-error, no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from dataclasses import dataclass

from abacus.accounting_types import AccountBalancesDict, Amount, Netting
from abacus.accounts import Asset, Capital, Expense, Income, Liability
from abacus.closing import make_closing_entries_for_permanent_contra_accounts
from abacus.ledger import Ledger

__all__ = ["BalanceSheet", "IncomeStatement"]


class Report:
    pass


@dataclass
class BalanceSheet(Report):
    assets: AccountBalancesDict
    capital: AccountBalancesDict
    liabilities: AccountBalancesDict


@dataclass
class IncomeStatement(Report):
    income: AccountBalancesDict
    expenses: AccountBalancesDict

    def current_profit(self):
        return self.income.total() - self.expenses.total()


def balance_sheet(ledger: Ledger, netting: Netting) -> BalanceSheet:
    # Ledger will have permanent contra accounts which we did not net
    # because we pass them to next period (eg accumulated depreciation
    # does not go away).
    # We close this ledger internally and will provide netted permanent
    # accounts in the balance sheet report.
    # This may change if we have a more complicated balance sheet report
    # with net.. = gross... - less...
    entries = make_closing_entries_for_permanent_contra_accounts(ledger, netting)
    _ledger = ledger.process_postings(list(entries))
    return BalanceSheet(
        assets=_ledger.subset(Asset).balances(),
        capital=_ledger.subset(Capital).balances(),
        liabilities=_ledger.subset(Liability).balances(),
    )


def income_statement(ledger: Ledger) -> IncomeStatement:
    return IncomeStatement(
        income=ledger.subset(Income).balances(),
        expenses=ledger.subset(Expense).balances(),
    )


def current_profit(ledger: Ledger) -> Amount:
    return income_statement(ledger).current_profit()
