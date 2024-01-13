"""Write and read accounting entries from a file."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from abacus.core import Chart, Entry

__all__ = ["LineJSON"]


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

    @classmethod
    def load(cls, path: Path | str | None = None):
        if path is None:
            path = Path("./entries.linejson")
        return cls(Path(path))

    @property
    def file(self) -> File:
        return File(Path(self.path))

    def append(self, entry: Entry) -> None:
        self.append_many([entry])

    def _open(self, mode: str):
        return open(self.path, mode, newline="\n", encoding="utf-8")

    def append_many(self, entries: list[Entry]) -> None:
        with self._open("a") as file:
            for entry in entries:
                file.write(entry.to_json() + "\n")

    def yield_entries(self) -> Iterable[Entry]:
        with self._open("r") as file:
            for line in file:
                yield Entry.from_string(line)

    def yield_entries_for_income_statement(self, chart: Chart) -> Iterable[Entry]:
        """Filter entries that will not close income accounts.
        Used to produce income statement."""
        from itertools import filterfalse

        isa = chart.income_summary_account

        def touches_isa(entry):
            """True if entry touches income summary account."""
            return (entry.debit == isa) or (entry.credit == isa)

        return filterfalse(touches_isa, self.yield_entries())
