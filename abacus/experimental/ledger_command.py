from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from abacus import AbacusError, Amount, Entry, Ledger
from abacus.engine.entries import LineJSON
from abacus.experimental.base import Logger


@dataclass
class LedgerCommand:
    store: LineJSON
    logger: Logger = Logger([])

    def echo(self):
        print(self.logger.message)
        return self

    def log(self, message):
        self.logger.log(message)
        return self

    @classmethod
    def init(cls, path) -> "LedgerCommand":
        store = LineJSON(path).file.touch()
        return LedgerCommand(store).log(f"Created ledger file: {path}")

    # @classmethod
    # def start_ledger(cls, path) -> "LedgerCommand":
    #     store = LineJSON(path).file.touch()
    #     return LedgerCommand(store).log(f"Created ledger file: {path}")

    @classmethod
    def read(cls, path: Path) -> "LedgerCommand":
        return LedgerCommand(store=LineJSON(path))

    def erase(self) -> None:
        self.store.file.erase()

    def show(self, sep=","):
        for entry in self.store.yield_entries():
            print(entry.debit, entry.credit, entry.amount, sep=sep)

    def post_starting_balances(self, starting_balances_dict: Dict):
        _ = self.chart.ledger(starting_balances_dict)  # check all accounts are present in chart
        me = self.chart.ledger().make_multiple_entry(starting_balances_dict)
        entries = me.entries(self.chart.null_account)
        self.store.append_many(entries)
        for entry in entries:
            print("Posted starting entry:", entry)

    def post_entry(self, debit: str, credit: str, amount: str):
        try:
            entry = Entry(debit=debit, credit=credit, amount=Amount(amount))
        except TypeError:
            raise AbacusError(f"Invalid entry: {debit}, {credit}, {amount}.")
        self.store.append(entry)
        print("Posted entry to ledger:", entry)


    def post_closing_entries(self, chart):
        closing_entries = (
            Ledger.new(chart)
            .post_many(entries=self.store.yield_entries())
            .closing_entries(chart)
        )
        self.store.append_many(closing_entries)
        print("Posted closing entries to ledger:")
        for entry in closing_entries:
            print(" ", entry)

    # excludes post operation