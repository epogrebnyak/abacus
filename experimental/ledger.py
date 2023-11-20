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
)  # type: ignore
from abacus.engine.base import AbacusError, Entry  # type: ignore


@dataclass
class Ledger:
    data: Dict[str, TAccount]
    base_chart: Chart

    def post(self, debit, credit, amount) -> None:
        return self.post_many([Entry(debit, credit, amount)])

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
        return Ledger({k: v.deep_copy() for k, v in self.data.items()}, self.base_chart)

    def condense(self):
        return self.apply(lambda taccount: taccount.condense())

    def balances(self):
        return self.apply(lambda taccount: taccount.balance()).data

    def nonzero_balances(self):
        return {k: v for k, v in self.balances().items() if v != 0}

    def manage(self):
        return ClosingEntryManager(self.condense(), self.base_chart)

    def report(self):
        return Reporter(self, self.base_chart)

    def subset(self, cls):
        """Filter ledger by account type."""
        return Ledger(
            data={
                account_name: t_account
                for account_name, t_account in self.data.items()
                if isinstance(t_account, cls)
            },
            base_chart=self.base_chart,
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


def jobs(chart: BaseChart, ledger: Ledger, fs: List[Callable]):
    dummy_ledger = ledger.condense().deep_copy()
    result = []
    for f in fs:
        dummy_ledger, closing_entries = f(chart, dummy_ledger)
        result.extend(closing_entries)
    return result


@dataclass
class ClosingEntryManager:
    ledger0: Ledger
    base_chart: BaseChart

    def do(self, *fs: List[Callable]):
        return jobs(self.base_chart, self.ledger0, fs)

    def closing_entries_for_income_statement(self) -> List[Entry]:
        return self.do(close_first)

    def closing_entries_for_end_balances(self) -> List[Entry]:
        return self.do(close_first, close_second)

    def closing_entries_for_balance_sheet(self) -> List[Entry]:
        return self.do(close_first, close_second, close_last)


# Next add reporter, will need subset() method for ledger
@dataclass
class Reporter:
    ledger: Ledger
    titles: Dict[str, str]

    def income_statement(self):
        from abacus.engine.report import IncomeStatement

        closing_entries = self.ledger.manage().closing_entries_for_income_statement()
        ledger = self.ledger.condense().post_many(closing_entries)
        return IncomeStatement.new(ledger)

    def balance_sheet(self):
        from abacus.engine.report import BalanceSheet

        closing_entries = self.ledger.manage().closing_entries_for_balance_sheet()
        ledger = self.ledger.condense().post_many(closing_entries)
        return BalanceSheet.new(ledger)

    # def trial_balance(self, chart: Chart):
    #     from abacus.engine.report import view_trial_balance

    #     return view_trial_balance(chart, self)


chart = (
    Chart()
    .asset("cash")
    .capital("equity")
    .liability("loan")
    .income("sales")
    .expense("sga")
)
ledger = (
    chart.ledger()
    .post("cash", "equity", 5000)
    .post("cash", "sales", 250)
    .post("sga", "cash", 100)
    .post("cash", "loan", 1000)
)
print(ledger.report().income_statement())
print(ledger.report().balance_sheet())
