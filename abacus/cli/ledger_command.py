from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from abacus import Amount, Chart, Entry, Ledger
from abacus.cli.logger import Logger
from abacus.engine.entries import LineJSON


@dataclass
class LedgerCommand:
    store: LineJSON
    logger: Logger = Logger()

    def echo(self):
        self.logger.echo()
        return self

    def log(self, message):
        self.logger.log(message)
        return self

    @classmethod
    def init(cls, path) -> "LedgerCommand":
        store = LineJSON(path)
        store.file.touch()
        return LedgerCommand(store).log(f"Created ledger file {path}.")

    @classmethod
    def read(cls, path: Path) -> "LedgerCommand":
        return LedgerCommand(store=LineJSON(path))

    def show(self, sep=","):
        for entry in self.store.yield_entries():
            print(entry.debit, entry.credit, entry.amount, sep=sep)

    def post_starting_balances(self, chart: Chart, starting_balances_dict: Dict):
        _ = chart.ledger(
            starting_balances_dict
        )  # check all accounts are present in chart
        me = chart.ledger().make_multiple_entry(starting_balances_dict)
        entries = me.entries(chart.null_account)
        return self.post_many(entries)

    def post_entry(self, debit: str, credit: str, amount: str):
        entry = Entry(debit=debit, credit=credit, amount=Amount(amount))
        return self.post_many([entry])

    def post_many(self, entries: list[Entry]):
        self.store.append_many(entries)
        for entry in entries:
            self.log(f"Posted entry to ledger: {entry}")
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
