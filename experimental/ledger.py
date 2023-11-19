"""Ledger data structure, can be created from chart, used to post entries and produce reports."""
from collections import UserDict
from typing import Dict, Iterable, List, Tuple, Type

from abacus.engine.accounts import (
    CreditAccount,
    DebitAccount,
    TAccount,
    ContraIncome,
    ContraExpense,
    ContraAsset,
    ContraLiability,
    ContraCapital,
    Income,
    Expense,
)
from abacus.engine.base import AbacusError, AccountName, Amount, Entry, MultipleEntry
from composer import Chart, BaseChart
from dataclasses import dataclass


@dataclass
class Ledger:
    data: Dict[str, TAccount]
    base_chart: Chart

    def post(self, debit, credit, amount) -> None:
        return self.post_many([Entry(debit, credit, amount)])

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

    def apply(self, f):
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

    def close(self):
        return Closer(self.condense(), self.base_chart)


from dataclasses import dataclass


def close_first(chart, ledger):
    """Close contra income and contra expense accounts."""
    c1 = closing_contra_entries(chart, ledger, ContraIncome)
    c2 = closing_contra_entries(chart, ledger, ContraExpense)
    closing_entries = list(c1) + list(c2)
    return ledger.condense().post_many(closing_entries), closing_entries


def close_to_isa(chart, ledger, cls):
    for name, account in ledger.data.items():
        if isinstance(account, cls):
            yield account.transfer(name, chart.income_summary_account)


def close_second(chart, dummy_ledger):
    """Close income and expense to income summary account ("isa"),
    then close isa to retained earnings."""
    # Close income and expense to isa
    a = close_to_isa(chart, dummy_ledger, Income)
    b = close_to_isa(chart, dummy_ledger, Expense)
    closing_entries = list(a) + list(b)
    dummy_ledger.post_many(closing_entries)
    # Close to retained earnings
    isa, re = chart.income_summary_account, chart.retained_earnings_account
    transfer_entry = Entry(
        debit=isa, credit=re, amount=dummy_ledger.data[isa].balance()
    )
    closing_entries.append(transfer_entry)
    return dummy_ledger.post_many([transfer_entry]), closing_entries


def close_last(chart, ledger):
    """Close permanent contra accounts."""
    c3 = closing_contra_entries(chart, ledger, ContraAsset)
    c4 = closing_contra_entries(chart, ledger, ContraLiability)
    c5 = closing_contra_entries(chart, ledger, ContraCapital)
    closing_entries = list(c3) + list(c4) + list(c5)
    return ledger.post_many(closing_entries), closing_entries


def closing_contra_entries(chart, ledger, contra_cls):
    for name, contra_name in chart.contra_pairs(contra_cls):
        yield ledger.data[contra_name].transfer(contra_name, name)  # type: ignore


@dataclass
class Closer:
    ledger0: Ledger
    base_chart: BaseChart

    def closing_entries_for_income_statement(self) -> List[Entry]:
        dummy_ledger = self.ledger0.deep_copy()
        _, entries_1 = close_first(self.base_chart, dummy_ledger)
        return entries_1

    def closing_entries_for_end_balances(self) -> List[Entry]:
        dummy_ledger = self.ledger0.deep_copy()
        dummy_ledger, entries_1 = close_first(self.base_chart, dummy_ledger)
        _, entries_2 = close_second(self.base_chart, dummy_ledger)
        return entries_1 + entries_2

    def closing_entries_for_balance_sheet(self) -> List[Entry]:
        dummy_ledger = self.ledger0.deep_copy()
        dummy_ledger, entries_1 = close_first(self.base_chart, dummy_ledger)
        dummy_ledger, entries_2 = close_second(self.base_chart, dummy_ledger)
        _, entries_3 = close_last(self.base_chart, dummy_ledger)
        return entries_1 + entries_2 + entries_3


closer = (
    Chart()
    .add("asset:cash")
    .add("capital:equity")
    .offset("equity", "ts")
    .add("expense:cogs")
    .add("income:sales")
    .offset("sales", "refunds")
    .ledger()
    .post("cash", "equity", 1000)
    .post("ts", "cash", 200)
    .post("cash", "sales", 110)
    .post("refunds", "cash", 10)
    .post("cogs", "null", 60)
    .close()
)

assert closer.closing_entries_for_income_statement() == [
    Entry(debit="sales", credit="refunds", amount=10)
]

assert closer.closing_entries_for_end_balances() == [
    Entry(debit="sales", credit="refunds", amount=10),
    Entry(debit="sales", credit="current_profit", amount=100),
    Entry(debit="current_profit", credit="cogs", amount=60),
    Entry(debit="current_profit", credit="retained_earnings", amount=40),
]

assert closer.closing_entries_for_balance_sheet() == [
    Entry(debit="sales", credit="refunds", amount=10),
    Entry(debit="sales", credit="current_profit", amount=100),
    Entry(debit="current_profit", credit="cogs", amount=60),
    Entry(debit="current_profit", credit="retained_earnings", amount=40),
    Entry(debit="equity", credit="ts", amount=200),
]


if __name__ == "__main__":
    from composer import Chart

    chart0 = Chart().add("asset:cash").add("capital:equity").add("contra:equity:ts")
    assert chart0.ledger().post("cash", "equity", 1000).post(
        "ts", "cash", 200
    ).nonzero_balances() == {"cash": 800, "equity": 1000, "ts": 200}
    assert chart0.ledger().post_many(
        [Entry("cash", "equity", 1000), Entry("ts", "cash", 200)]
    ).nonzero_balances() == {"cash": 800, "equity": 1000, "ts": 200}

    chart2 = (
        Chart()
        .add("asset:cash")
        .add("asset:goods")
        .add("capital:equity")
        .add("contra:equity:ts")
        .add("income:sales")
        .add("expense:cogs")
        .offset("sales", "refunds")
    )
    ledger2 = (
        chart2.ledger()
        .post("cash", "equity", 1000)
        .post("goods", "cash", 300)
        .post("cash", "sales", 250)
        .post("refunds", "cash", 50)
        .post("cogs", "goods", 170)
        .post("ts", "cash", 500)
    )
    # assert ledger2.close_most(chart2).close_final(chart2).nonzero_balances() == {
    #     "cash": 400,
    #     "goods": 130,
    #     "equity": 500,
    #     "retained_earnings": 30,
    # }


# def to_multiple_entry(ledger: Ledger, starting_balances: dict) -> MultipleEntry:
#     debit_entries = []
#     credit_entries = []
#     for account_name in starting_balances.keys():
#         try:
#             ledger[account_name]
#         except KeyError:
#             raise AbacusError(f"Account {account_name} does not exist in ledger.")
#     for account_name, amount in starting_balances.items():
#         match ledger[account_name]:
#             case DebitAccount(_, _):
#                 debit_entries.append((account_name, amount))
#             case CreditAccount(_, _):
#                 credit_entries.append((account_name, amount))
#     return MultipleEntry(debit_entries, credit_entries).validate()
