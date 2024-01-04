from typing import Dict, List, Tuple

from abacus import Amount, Chart, Entry, MultipleEntry
from abacus.cli.base import BaseCommand
from abacus.engine.entries import LineJSON


class LedgerCommand(BaseCommand):
    @property
    def store(self):
        return LineJSON(self.path)

    def init(self) -> "LedgerCommand":
        self.assert_does_not_exist()
        self.path.touch()
        self.log(f"Wrote ledger file {self.path}.")
        return self

    def show(self, sep=","):
        for entry in self.store.yield_entries():
            print(entry.debit, entry.credit, entry.amount, sep=sep)

    def post_compound(
        self,
        chart: Chart,
        debit_tuples: List[Tuple[str, int]],
        credit_tuples: List[Tuple[str, int]],
    ):
        me = MultipleEntry(debit_entries=debit_tuples, credit_entries=credit_tuples)
        entries = me.entries(chart.base_chart.null_account)
        return self.post_many(entries, "single")

    def post_starting_balances(self, chart: Chart, starting_balances_dict: Dict):
        # 1. check all accounts are present in chart
        _ = chart.ledger(starting_balances_dict)
        # 2. do actual job
        me = chart.ledger().make_multiple_entry(starting_balances_dict)
        entries = me.entries(chart.base_chart.null_account)
        return self.post_many(entries, "starting")

    def post_entry(self, debit: str, credit: str, amount: str):
        entry = Entry(debit=debit, credit=credit, amount=Amount(amount))
        return self.post_many([entry], "double")

    def post_many(self, entries: list[Entry], noun=""):
        self.store.append_many(entries)
        if noun:
            noun = noun + " "
        for entry in entries:
            self.log(f"Posted {noun}entry to ledger: {entry}")
        return self

    def post_operations(self, chart, operations):
        opnames = [opname for opname, _ in operations]
        amounts = [amount for _, amount in operations]
        entries = chart.make_entries_for_operations(opnames, amounts)
        return self.post_many(entries, "operation")

    def post_closing_entries(self, chart):
        closing_entries = (
            chart.ledger()
            .post_many(entries=self.store.yield_entries())
            .closing_entries(chart)
        )
        return self.post_many(closing_entries, "closing")
