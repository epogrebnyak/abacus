from typing import Dict

from abacus import AbacusError, Amount, Chart, Entry, Ledger, MultipleEntry
from abacus.cli.base import BaseCommand
from abacus.engine.entries import LineJSON


class LedgerCommand(BaseCommand):
    @property
    def store(self):
        return LineJSON(self.path)

    def init(self) -> "LedgerCommand":
        if self.path.exists():
            raise AbacusError(f"{self.path} already exists.")
        else:
            self.path.touch()
            self.log(f"Created ledger file {self.path}.")
        return self

    def show(self, sep=","):
        for entry in self.store.yield_entries():
            print(entry.debit, entry.credit, entry.amount, sep=sep)

    def post_compound(self, chart: Chart, debit_tuples, credit_tuples):
        me = MultipleEntry(debit_entries=debit_tuples, credit_entries=credit_tuples)
        entries = me.entries(chart.null_account)
        return self.post_many(entries, "single")

    def post_starting_balances(self, chart: Chart, starting_balances_dict: Dict):
        # check all accounts are present in chart
        _ = chart.ledger(starting_balances_dict)
        me = chart.ledger().make_multiple_entry(starting_balances_dict)
        entries = me.entries(chart.null_account)
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

    def post_operations(self, chart, operations: list[str], amounts: list[str]):
        entries = chart.make_entries_for_operations(operations, amounts)
        return self.post_many(entries)

    def post_closing_entries(self, chart):
        closing_entries = (
            Ledger.new(chart)
            .post_many(entries=self.store.yield_entries())
            .closing_entries(chart)
        )
        return self.post_many(closing_entries)
