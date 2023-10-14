# I need to save debit(string), credit(string), amount(float) tuples to a CSV file
# The CSV file should be open for appending.

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List

from abacus.engine.base import Amount, Entry
from abacus.engine.chart import Chart


@dataclass
class CsvFile:
    """File that stores accounting entries in CSV format."""

    path: Path

    def append(self, entry: Entry) -> None:
        with open(self.path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([entry.debit, entry.credit, entry.amount])

    def append_many(self, entries: List[Entry]) -> None:
        with open(self.path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            for entry in entries:
                writer.writerow([entry.debit, entry.credit, entry.amount])

    def yield_entries(self):
        with open(self.path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                yield Entry(row[0], row[1], Amount(row[2]))

    def yield_entries_for_income_statement(self, chart: Chart):
        """Filter entries that do not close income accounts."""

        def not_touches_isa(entry):
            return not touches_isa(chart, entry)

        return filter(not_touches_isa, self.yield_entries())

    def touch(self):
        if not self.path.exists():
            self.path.touch()
        return self

    def erase(self):
        if self.path.exists():
            self.path.unlink()
        return self


def touches_isa(chart: Chart, entry: Entry) -> bool:
    """True if entry touches income summary account."""
    isa = chart.income_summary_account
    return (entry.debit == isa) or (entry.credit == isa)
