# I need to save debit(string), credit(string), amount(float) tuples to a CSV file
# The CSV file should be open for appending.

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List

from engine.base import Amount, Entry


@dataclass
class CsvFile:
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

    def touch(self):
        if not self.path.exists():
            self.path.touch()

    def erase(self):
        if self.path.exists():
            self.path.unlink()
