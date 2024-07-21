"""Viewers for trial balance, income statement, balance sheet reports."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from rich.console import Console  # type: ignore
from rich.table import Table as RichTable  # type: ignore
from rich.text import Text  # type: ignore

from abacus.core import Amount, BalanceSheet, IncomeStatement


@dataclass
class TextColumn:
    """Column for creating tables.
    Methods to manipulate a column include align and concatenate."""

    strings: list[str]

    @property
    def width(self):
        return max(len(s) for s in self.strings)

    def align(self, method: str, fill_char: str):
        """Generic method to align all strings in the column."""
        width = self.width  # avoid calculating width too many times

        def f(s):
            return getattr(s, method)(width, fill_char)

        return self.__class__([f(s) for s in self.strings])

    def align_left(self, fill_char=" "):
        """Align all strings to the left."""
        return self.align("ljust", fill_char)

    def align_right(self, fill_char=" "):
        """Align all strings to the right."""
        return self.align("rjust", fill_char)

    def align_center(self):
        """Align all strings to center."""
        return self.align("center", " ")

    def empty(self, n: int = 1):
        """Create a new column filled with `n` spaces."""
        return self.refill(" " * n)

    def add_right(self, string: str):
        """Add `string` to the right of the column."""
        return self + self.refill(string)

    def add_space(self, n: int = 1):
        """Add `n` spaces to the right of the column."""
        return self + self.empty(n)

    def add_space_left(self, n: int = 1):
        """Add `n` spaces to the left of the column."""
        return self.empty(n) + self

    def refill(self, text):
        """Create a new column where all strings are replaced by `text`."""
        return self.__class__([text] * len(self.strings))

    def merge(self, column):
        """Merge two columns into one."""
        return self.__class__([a + b for a, b in zip(self.strings, column.strings)])  # type: ignore

    def __add__(self, column):
        return self.merge(column)

    def insert_top(self, text):
        """Insert text at the top of the column."""
        return self.__class__([text] + self.strings)

    def insert_bottom(self, text):
        """Insert text at the bottom of the column."""
        return self.__class__(self.strings + [text])

    def header(self, text):
        """Add a header line to the column."""
        return self.insert_top(text.center(self.width))

    def __str__(self):
        """Return a string representation of the column, ready to print ot screen."""
        return "\n".join(self.strings)


@dataclass
class String:
    s: str

    def __str__(self):
        return self.s

    def rich(self):
        return Text(self.s)


@dataclass
class Number:
    n: Amount

    def __str__(self):
        return str(self.n)

    def rich(self):
        return red(self.n)


@dataclass
class Format: ...


@dataclass
class BoldF(Format): ...


@dataclass
class OffsetF(Format): ...


BOLD = BoldF()
OFFSET = OffsetF()


@dataclass
class Cell:
    content: String | Number
    formats: list[Format] = field(default_factory=list)

    def rename(self, f: Callable):
        match self.content:
            case String(s):
                self.content.s = f(s)
            case _:
                pass
        return self

    def __str__(self):
        r = str(self.content)
        if OFFSET in self.formats:
            r = "  " + r
        if BOLD in self.formats:
            r = r.upper()
        return r

    def rich(self):
        r = self.content.rich()
        if OFFSET in self.formats:
            r = Text("  ") + r
        if BOLD in self.formats:
            r = bold(r)
        return r


EMPTY = Cell(String(""))


def maps(f, xs):
    return list(map(f, xs))


def red(t: Amount) -> Text:
    """Make digit red if negative."""
    if t < 0:
        return Text(str(t), style="red")
    else:
        return Text(str(t))


def bold(s: Text | str) -> Text:
    if isinstance(s, Text):
        s.stylize("bold")  # type: ignore
        return s
    else:
        return Text(str(s), style="bold")


@dataclass
class PairColumn:
    xs: list[Cell]
    ys: list[Cell]

    def __len__(self):
        return len(self.xs)

    @classmethod
    def from_dict(cls, d: dict):
        xs = []
        ys = []
        for k, vs in d.items():
            n = sum(vs.values())
            xs.append(Cell(String(k), [BOLD]))
            ys.append(Cell(Number(n), [BOLD]))
            for name, value in vs.items():
                xs.append(Cell(String(name), [OFFSET]))
                ys.append(Cell(Number(value)))
        return cls(xs, ys)

    def text_table(self):
        a = TextColumn(maps(str, self.xs)).align_left().add_space(2)
        b = TextColumn(maps(str, self.ys)).align_right()
        return a + b

    def append_empty(self, n):
        for _ in range(n):
            self.xs.append(EMPTY)
            self.ys.append(EMPTY)

    def add_footer(self, s: str, n: Amount):
        self.xs.append(Cell(String(s), [BOLD]))
        self.ys.append(Cell(Number(n), [BOLD]))

    def rename(self, rename_dict=None):
        rename_dict = rename_dict or {}

        def g(s):
            if s in rename_dict.keys():
                return rename_dict[s]
            return s.replace("_", " ").strip().capitalize()

        self.xs = [x.rename(g) for x in self.xs]


def equalize_length(p1: PairColumn, p2: PairColumn):
    n = max(len(p1), len(p2))
    p1.append_empty(n - len(p1))
    p2.append_empty(n - len(p2))


@dataclass
class Viewer(ABC):
    def use(self, rename_dict: dict[str, str]):
        self.rename_dict.update(rename_dict)  # type: ignore
        return self

    @abstractmethod
    def text_table(self): ...

    @abstractmethod
    def rich_table(self, width): ...

    def print(self, width: int | None = None):
        """Rich printing to console."""
        t = self.rich_table(width)
        Console().print(t)

    def __str__(self):
        prefix = ""
        if self.title:  # type: ignore
            prefix = self.title + "\n"  # type: ignore
        return prefix + str(self.text_table())

    @property
    def width(self):
        return max(map(len, str(self).split("\n")))


@dataclass
class IncomeStatementViewer(Viewer):
    statement: IncomeStatement
    title: str = "Income Statement"
    rename_dict: dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        return dict(income=self.statement.income, expenses=self.statement.expenses)

    @property
    def pair_column(self):
        pi = PairColumn.from_dict(self.to_dict())
        pi.add_footer("current profit", self.statement.current_profit())
        pi.rename(self.rename_dict)
        return pi

    def text_table(self):
        return self.pair_column.text_table()

    def rich_table(self, width):
        table = RichTable(title=self.title, box=None, width=width, show_header=False)
        table.add_column()
        table.add_column(justify="right", style="green")
        p = self.pair_column
        for a, b in zip(p.xs, p.ys):
            table.add_row(a.rich(), b.rich())
        return table


@dataclass
class BalanceSheetViewer(Viewer):
    statement: BalanceSheet
    title: str = "Balance sheet"
    rename_dict: dict[str, str] = field(default_factory=dict)

    def to_dicts(self):
        return [
            dict(assets=self.statement.assets),
            dict(
                capital=self.statement.capital, liabilities=self.statement.liabilities
            ),
        ]

    @property
    def pair_columns(self):
        d1, d2 = self.to_dicts()
        p1 = PairColumn.from_dict(d1)
        p2 = PairColumn.from_dict(d2)
        equalize_length(p1, p2)
        p1.add_footer("total", sum(self.statement.assets.values()))
        _s = self.statement
        p2.add_footer(
            "total",
            sum(_s.capital.values()) + sum(_s.liabilities.values()),
        )
        p1.rename(self.rename_dict)
        p2.rename(self.rename_dict)
        return p1, p2

    def text_table(self):
        p1, p2 = self.pair_columns
        return p1.text_table().add_space(2) + p2.text_table()

    def rich_table(self, width=None):
        table = RichTable(title=self.title, box=None, width=width, show_header=False)
        table.add_column()
        table.add_column(justify="right", style="green")
        table.add_column()
        table.add_column(justify="right", style="green")
        p1, p2 = self.pair_columns
        for a, b, c, d in zip(p1.xs, p1.ys, p2.xs, p2.ys):
            table.add_row(a.rich(), b.rich(), c.rich(), d.rich())
        return table


@dataclass
class TrialBalanceViewer(Viewer):
    statement: dict[str, tuple[Amount, Amount]]
    rename_dict: dict[str, str] = field(default_factory=dict)
    headers: tuple[str, str, str] = "Account", "Debit", "Credit"
    title: str = "Trial balance"

    @property
    def debits(self) -> list[str]:
        return [str(d) for (d, _) in self.statement.values()]

    @property
    def credits(self) -> list[str]:
        return [str(c) for (_, c) in self.statement.values()]

    @property
    def account_names(self):
        return list(self.statement.keys())

    def account_names_column(self, header: str):
        return (
            TextColumn(strings=self.account_names)
            .add_space(1)
            .align_left(".")
            .add_right("...")
            .header(header)
        )

    def numeric_column(self, values, header):
        return TextColumn(values).align_right().add_space_left(3).header(header)

    def text_table(self) -> TextColumn:
        return (
            self.account_names_column(self.headers[0])
            + self.numeric_column(self.debits, self.headers[1])
            + self.numeric_column(self.credits, self.headers[2])
        )

    def rich_table(self, width=None) -> RichTable:
        table = RichTable(title=self.title, box=None, width=width, show_header=True)
        table.add_column(header=self.headers[0])
        table.add_column(header=self.headers[1], justify="right", style="green")
        table.add_column(header=self.headers[2], justify="right", style="green")
        for a, b, c in zip(self.account_names, self.debits, self.credits):
            table.add_row(Text(a), red(Amount(b)), red(Amount(c)))
        return table


def print_viewers(
    rename_dict: dict[str, str],
    tv: TrialBalanceViewer,
    bv: BalanceSheetViewer,
    iv: IncomeStatementViewer,
):
    # +2 for padding and boundaries in RichTable
    width = 2 + max(bv.width, iv.width, tv.width)
    tv.print(width)
    bv.use(rename_dict).print(width)
    iv.use(rename_dict).print(width)
