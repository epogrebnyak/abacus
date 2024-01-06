from dataclasses import dataclass, field
from abacus.core import Amount, AccountBalances
from rich.table import Table as RichTable
from abacus.viewers import (
    Column as TextTable,
)  # this is correct: single column is table and may be expanded

# from abc import ABC, abstractmethod
# from abacus.core import BalanceSheet as BS, IncomeStatement as IS


@dataclass
class String:
    s: str


@dataclass
class Number:
    n: Amount


class Empty:
    ...


Content = String | Number | Empty


@dataclass
class Cell:
    content: Content
    level: int = 0
    is_bold: bool = False


Column = list[Cell]


@dataclass
class Table:
    """This is internal representation of a table."""

    headers: list[str]
    columns: list[Column]
    title: str | None = None

    def text_table(self) -> TextTable:
        ...

    def rich_table(self, width: int) -> RichTable:
        ...


class Viewer:
    column_content: dict[str, AccountBalances]
    title: str | None = None
    rename_dict: dict[str, str] = field(default_factory=dict)

    @property
    @abstractmethod
    def table(self) -> Table:
        ...

    @abstractmethod
    def print(self, width: int):
        """Rich printing to console."""
        return self.table.rich_table(width)

    def __str__(self):
        return str(self.table.text_table())
