"""Ledger data structure, can be created from chart, used to post entries and produce reports."""

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List

from composer import BaseChart, Chart

from abacus.engine.accounts import (  # type: ignore
    ContraAsset,
    ContraCapital,
    ContraExpense,
    ContraIncome,
    ContraLiability,
    Expense,
    Income,
    TAccount,
)
from abacus.engine.base import AbacusError, Entry  # type: ignore


@dataclass
class Ledger:
    data: Dict[str, TAccount]
    chart: Chart

    def post(self, debit, credit, amount) -> None:
        return self.post_one(Entry(debit, credit, amount))

    def post_one(self, entry: Entry):
        return self.post_many([entry])

    def post_many(self, entries: Iterable[Entry]):
        failed = []
        for entry in entries:
            try:
                self.data[entry.debit].debit(entry.amount)
                self.data[entry.credit].credit(entry.amount)
            except KeyError:
                failed.append(entry)
        if failed:
            raise AbacusError(failed)
        return self

    def apply(self, f: Callable):
        self.data = {name: f(taccount) for name, taccount in self.data.items()}
        return self

    def deep_copy(self):
        return Ledger({k: v.deep_copy() for k, v in self.data.items()}, self.chart.base)

    def condense(self):
        return self.apply(lambda taccount: taccount.condense())

    def balances(self):
        return self.apply(lambda taccount: taccount.balance()).data

    def nonzero_balances(self):
        return {k: v for k, v in self.balances().items() if v != 0}

    def manage(self):
        return ClosingEntryManager(self.condense(), self.chart.base)

    def runner(self):
        return LedgerRunner(self.chart.base, self)

    def report(self):
        return Reporter(self, self.chart.titles)

    def replicate(self, dictionary):
        return Ledger(dictionary, self.chart)

    def subset(self, cls):
        """Filter ledger by account type."""
        return self.replicate(
            {
                account_name: t_account
                for account_name, t_account in self.data.items()
                if isinstance(t_account, cls)
            }
        )


def closing_contra_entries(chart, ledger, contra_cls):
    for name, contra_name in chart.contra_pairs(contra_cls):
        yield ledger.data[contra_name].transfer(contra_name, name)  # type: ignore


def close_to_isa(chart, ledger, cls):
    for name, account in ledger.data.items():
        if isinstance(account, cls):
            yield account.transfer(name, chart.income_summary_account)


def close_first(chart, ledger):
    """Close contra income and contra expense accounts."""
    c1 = closing_contra_entries(chart, ledger, ContraIncome)
    c2 = closing_contra_entries(chart, ledger, ContraExpense)
    closing_entries = list(c1) + list(c2)
    return ledger.condense().post_many(closing_entries), closing_entries


def close_second(chart, dummy_ledger):
    """Close income and expense accounts to income summary account ("ISA"),
    then close ISA to retained earnings."""
    # Close income and expense to isa
    a = close_to_isa(chart, dummy_ledger, Income)
    b = close_to_isa(chart, dummy_ledger, Expense)
    closing_entries = list(a) + list(b)
    dummy_ledger.post_many(closing_entries)
    # Close isa to retained earnings
    isa, re = chart.income_summary_account, chart.retained_earnings_account
    b = dummy_ledger.data[isa].balance()
    transfer_entry = Entry(debit=isa, credit=re, amount=b)
    closing_entries.append(transfer_entry)
    return dummy_ledger.post_many(closing_entries), closing_entries


def close_last(chart, ledger):
    """Close permanent contra accounts."""
    c3 = closing_contra_entries(chart, ledger, ContraAsset)
    c4 = closing_contra_entries(chart, ledger, ContraLiability)
    c5 = closing_contra_entries(chart, ledger, ContraCapital)
    closing_entries = list(c3) + list(c4) + list(c5)
    return ledger.post_many(closing_entries), closing_entries


class LedgerRunner:
    def __init__(self, base_chart, ledger):
        self.base_chart = base_chart
        self.current_ledger = ledger.condense().deep_copy()
        self.closing_entries = []

    def apply(self, f: Callable):
        self.current_ledger, closing_entries = f(self.base_chart, self.current_ledger)
        self.closing_entries.extend(closing_entries)
        return self

    def close_for_income_statement(self) -> List[Entry]:
        return self.apply(close_first)

    def close_for_end_balances(self) -> List[Entry]:
        return self.apply(close_first).apply(close_second)

    def close_for_balance_sheet(self) -> List[Entry]:
        return self.apply(close_first).apply(close_second).apply(close_last)


@dataclass
class ClosingEntryManager:
    ledger0: Ledger
    base_chart: BaseChart

    @property
    def runner(self):
        return LedgerRunner(self.base_chart, self.ledger0)

    def closing_entries_for_income_statement(self) -> List[Entry]:
        return self.runner.close_for_income_statement().closing_entries

    def closing_entries_for_end_balances(self) -> List[Entry]:
        return self.runner.close_for_end_balances().closing_entries

    def closing_entries_for_balance_sheet(self) -> List[Entry]:
        return self.runner.close_for_balance_sheet().closing_entries


@dataclass
class Reporter:
    ledger: Ledger
    titles: Dict[str, str]

    def _prepare_ledger(self, method_name: str):
        closing_entries = getattr(self.ledger.manage(), method_name)
        return self.ledger.condense().post_many(closing_entries)

    def income_statement(self, header="Income Statement"):
        from abacus.engine.report import IncomeStatement, IncomeStatementViewer

        statement = IncomeStatement.new(
            self.ledger.runner().close_for_income_statement().current_ledger
        )
        return IncomeStatementViewer(statement, self.titles, header)

    def balance_sheet(self, header="Balance Sheet"):
        from abacus.engine.report import BalanceSheet, BalanceSheetViewer

        statement = BalanceSheet.new(
            self.ledger.runner().close_for_balance_sheet().current_ledger
        )
        return BalanceSheetViewer(statement, self.titles, header)

    # def trial_balance(self, chart: Chart):
    #     from abacus.engine.report import view_trial_balance

    #     return view_trial_balance(chart, self)


#                Balance Sheet
#  Assets    5500  Capital                5500
#    Cash    5500    Equity               5000
#                    Retained earnings     500
#                  Liabilities               0
#  Total:    5500  Total:                 5500
#               Income Statement
#  Income                                 3500
#    Services                             3500
#  Expenses                               3000
#    Salaries                             2000
#    Marketing                            1000
#  Current profit                          500
