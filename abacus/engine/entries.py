"""Write and read accounting entries from a file."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from abacus.engine.base import Entry
from abacus.engine.better_chart import Chart

__all__ = ["LineJSON"]


def touches_isa(chart: Chart, entry: Entry) -> bool:
    """True if entry touches income summary account."""
    isa = chart.base_chart.income_summary_account
    return (entry.debit == isa) or (entry.credit == isa)


def income_statement_stream(entries, chart):
    for entry in entries:
        if not touches_isa(chart, entry):
            yield entry


@dataclass
class File:
    """Create and erase file."""

    path: Path

    def touch(self):
        if not self.path.exists():
            self.path.touch()
        return self

    def erase(self):
        if self.path.exists():
            self.path.unlink()
        return self


@dataclass
class LineJSON:
    path: Path

    @property
    def file(self) -> File:
        return File(Path(self.path))

    def append(self, entry: Entry) -> None:
        self.append_many([entry])

    def _open(self, mode: str):
        return open(self.path, mode, newline="\n", encoding="utf-8")

    def append_many(self, entries: List[Entry]) -> None:
        with self._open("a") as file:
            for entry in entries:
                file.write(entry.to_json() + "\n")

    def yield_entries(self) -> Iterable[Entry]:
        with self._open("r") as file:
            for line in file:
                yield Entry(**json.loads(line.strip()))

    def yield_entries_for_income_statement(self, chart: Chart) -> Iterable[Entry]:
        """Filter entries that will not close income accounts.
        Used to produce income statement."""
        return income_statement_stream(self.yield_entries(), chart)
