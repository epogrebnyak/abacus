"""Viewers for trial balance, income statement, balance sheet reports."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from rich.console import Console
from rich.table import Table
from rich.text import Text

from abacus.core import AccountBalances, Amount, BalanceSheet, IncomeStatement


@dataclass
class Column:
    """Column for creating tables.
    Methods to manipulate a column include align and concatenate."""

    strings: list[str]

    @property
    def width(self):
        return max(len(s) for s in self.strings)

    def apply(self, f: Callable):
        """Apply function `f` to each string in the column."""
        return Column([f(s) for s in self.strings])

    def align(self, method: str, fill_char: str):
        """Generic method to align all strings in the column."""
        width = self.width  # avoid calculating width too many times

        def f(s):
            return getattr(s, method)(width, fill_char)

        return Column([f(s) for s in self.strings])

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
        return Column([text] * len(self.strings))

    def merge(self, column):
        """Merge two columns into one."""
        return Column([a + b for a, b in zip(self.strings, column.strings)])

    def __add__(self, column: "Column"):
        return self.merge(column)

    def insert_top(self, text):
        """Insert text at the top of the column."""
        return Column([text] + self.strings)

    def insert_bottom(self, text):
        """Insert text at the bottom of the column."""
        return Column(self.strings + [text])

    def header(self, text):
        """Add a header line to the column."""
        return self.insert_top(text.center(self.width))

    def __str__(self):
        """Return a string representation of the column, ready to print ot screen."""
        return "\n".join(self.strings)


@dataclass
class BaseViewer:
    statement: BalanceSheet | IncomeStatement
    header: str | None = None
    rename_dict: dict[str, str] = field(default_factory=dict)

    def rename_factory(self):
        def rename_with(line):
            s = self.rename_dict.get(line.text, line.text)
            text = s.replace("_", " ").strip().capitalize()
            cls = line.__class__
            return cls(text, line.value)

        return rename_with


class Viewer(ABC):
    @abstractmethod
    def as_column(self) -> Column | str: ...

    def print(self):
        if self.header:
            print(self.header)
        print(self.as_column())


class RichViewer(ABC):
    @abstractmethod
    def as_table(self, width: int) -> Table: ...

    def print(self, width: int = 80):
        Console().print(self.as_table(width))


@dataclass
class BalanceSheetViewerBase(BaseViewer):
    def __post_init__(self):
        self.left, self.right = left_and_right(self.statement, self.rename_factory())


def it(x):
    return x


def lines(base: dict[str, AccountBalances]) -> list["Line"]:
    lines: list["Line"] = []
    for header, balances in base.items():
        h = HeaderLine(header, total(balances))
        lines.append(h)
        for name, value in balances.items():
            a = AccountLine(name, value)
            lines.append(a)
    return lines


def left_and_right(
    report: BalanceSheet, rename_with: Callable = it
) -> tuple[list["Line"], list["Line"]]:
    left = lines({"assets": report.assets})
    right = lines({"capital": report.capital, "liabilities": report.liabilities})
    # rename
    left = [rename_with(item) for item in left]
    right = [rename_with(item) for item in right]
    # make `left` and `right` same number of lines by adding empty lines
    n = max(len(left), len(right))
    left += [empty_line()] * (n - len(left))
    right += [empty_line()] * (n - len(right))
    # add end lines
    t = rename_with(Line("total", 0)).text.capitalize() + ":"
    h1 = HeaderLine(t, total(report.assets))
    left.append(h1)
    h2 = HeaderLine(t, total(report.capital) + total(report.liabilities))
    right.append(h2)
    return left, right


class BalanceSheetViewer(Viewer, BalanceSheetViewerBase):
    def as_column(self) -> Column:
        a, b = to_columns(self.left)
        col1 = a.align_left(".").add_right("... ") + b.align_right()
        c, d = to_columns(self.right)
        col2 = c.align_left(".").add_right("... ") + d.align_right()
        return col1.add_space(2).merge(col2)


class RichBalanceSheetViewer(RichViewer, BalanceSheetViewerBase):
    def as_table(self, width) -> Table:
        table = Table(title=self.header, box=None, width=width, show_header=False)
        table.add_column("")
        table.add_column("", justify="right", style="green")
        table.add_column("")
        table.add_column("", justify="right", style="green")
        for line_1, line_2 in zip(self.left, self.right):
            a, b = unpack(line_1)
            c, d = unpack(line_2)
            table.add_row(a, b, c, d)
        return table


@dataclass
class IncomeStatementViewerBase(BaseViewer):
    def __post_init__(self):
        self.lines = lines(
            {"income": self.statement.income, "expenses": self.statement.expenses}
        )
        h1 = HeaderLine("current profit", str(self.statement.current_profit()))
        self.lines.append(h1)
        f = self.rename_factory()
        self.lines = [f(item) for item in self.lines]


class IncomeStatementViewer(IncomeStatementViewerBase, Viewer):
    def as_column(self):
        a, b = to_columns(self.lines)
        return a.align_left(fill_char=".").add_right("... ") + b.align_right(
            fill_char=" "
        )


class RichIncomeStatementViewer(IncomeStatementViewerBase, RichViewer):
    def as_table(self, width):
        table = Table(title=self.header, box=None, width=width, show_header=False)
        table.add_column("")
        table.add_column("", justify="right", style="green")
        for line in self.lines:
            a, b = unpack(line)
            table.add_row(a, b)
        return table


def total(balances) -> Amount:
    return sum(balances.values())


@dataclass
class Line:
    text: str
    value: str | Amount

    def __post_init__(self):
        self.value = str(self.value)


class HeaderLine(Line): ...


class AccountLine(Line): ...


class EmptyLine(Line): ...


def empty_line() -> EmptyLine:
    return EmptyLine("", "")


def offset(line: Line) -> str:
    match line:
        case HeaderLine(s, _):
            return s.upper()
        case AccountLine(a, _):
            return "  " + a
        case EmptyLine(_, _):
            return ""
    raise TypeError  # mypy wanted it here


def to_columns(lines: list[Line]) -> tuple[Column, Column]:
    col1 = Column(strings=[offset(line) for line in lines])
    col2 = Column(strings=[str(line.value) for line in lines])
    return col1, col2


def string_from_columns(left, right) -> str:
    a, b = to_columns(left)
    col1 = a.align_left(".").add_right("... ") + b.align_right()
    c, d = to_columns(right)
    col2 = c.align_left(".").add_right("... ") + d.align_right()
    return str(col1.add_space(2).merge(col2))


def red(b) -> Text:
    """Make digit red if negative."""
    v = Amount(b)
    if v and v < 0:
        return Text(b, style="red")
    else:
        return Text(b)


def bold(s: Text | str) -> Text:
    if isinstance(s, Text):
        s.stylize("bold")
        return s
    else:
        return Text(str(s), style="bold")


def unpack(line: Line) -> tuple[Text, Text]:
    """Convert Line to tuple of two rich.Text instances."""
    match line:
        case HeaderLine(a, b):
            return bold(a), bold(red(b))
        case AccountLine(a, b):
            return (Text("  " + a), red(b))
        case EmptyLine(a, b):
            return Text(""), Text("")
        case _:
            raise ValueError(line)


@dataclass
class TrialBalanceViewer:
    trial_balance: dict[str, tuple[Amount, Amount]]
    titles: dict[str, str] = field(default_factory=dict)
    headers: tuple[str, str, str] = "Account", "Debit", "Credit"

    def account_names(self):
        return self.trial_balance.keys()

    def account_names_column(self, header):
        return (
            Column(self.account_names())
            .add_space(1)
            .align_left(".")
            .add_right("...")
            .header(header)
        )

    @property
    def debits(self) -> list[str]:
        return [str(d) for (d, _) in self.trial_balance.values()]

    @property
    def credits(self) -> list[str]:
        return [str(c) for (_, c) in self.trial_balance.values()]

    def numeric_column(self, values, header):
        return Column(values).align_right().add_space_left(3).header(header)

    def table(self):
        return (
            self.account_names_column(self.headers[0])
            + self.numeric_column(self.debits, self.headers[1])
            + self.numeric_column(self.credits, self.headers[2])
        )

    def __str__(self) -> str:
        return str(self.table())
