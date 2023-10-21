from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from abacus import Amount, Chart, Entry, Ledger
from abacus.engine.entries import LineJSON
from abacus.cli.logger import Logger


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
        store = LineJSON(path).file.touch()
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
        self.store.append_many(entries)
        return self

    def post_entry(self, debit: str, credit: str, amount: str):
        entry = Entry(debit=debit, credit=credit, amount=Amount(amount))
        self.store.append(entry)
        self.log(f"Posted entry to ledger: {entry}")
        return self

    def post_closing_entries(self, chart):
        closing_entries = (
            Ledger.new(chart)
            .post_many(entries=self.store.yield_entries())
            .closing_entries(chart)
        )
        self.store.append_many(closing_entries)
        for entry in closing_entries:
            self.log(f"Posted entry to ledger: {entry}")
        return self   