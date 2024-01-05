"""Viewers for trial balance, income statement, balance sheet reports."""

from dataclasses import dataclass, field
from typing import Callable

from abacus.core import AccountBalances, Amount, BalanceSheet, IncomeStatement

__all__ = ["echo", "show"]


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


def echo(statement, header):
    print(header, show(statement), sep="\n")


def show(report, rename_dict=None) -> str:
    if rename_dict is None:
        rename_dict = {}
    match report.__class__.__name__:
        case "BalanceSheet":
            return view_balance_sheet(report, rename_dict)
        case "IncomeStatement":
            return view_income_statement(report, rename_dict)
        case "TrialBalance":
            return str(TrialBalanceViewer(report, rename_dict))
        case _:
            raise TypeError(report)


def use_title(s: str, rename_dict: dict[str, str]) -> str:
    return rename_dict.get(s, s).replace("_", " ").strip().capitalize()


def total(balances) -> Amount:
    return sum(balances.values())


@dataclass
class Line:
    text: str
    value: str | Amount

    def __post_init__(self):
        self.value = str(self.value)

    def rename(self, rename_dict: dict[str, str]):
        self.text = use_title(self.text, rename_dict)
        return self


class HeaderLine(Line):
    ...


class AccountLine(Line):
    ...


class EmptyLine(Line):
    ...


def lines(base: dict[str, AccountBalances]):
    lines: list[Line] = []
    for header, balances in base.items():
        h = HeaderLine(header, total(balances))
        lines.append(h)
        for name, value in balances.items():
            a = AccountLine(name, value)
            lines.append(a)
    return lines


def empty_line() -> EmptyLine:
    return EmptyLine("", "")


def rename(lines, rename_dict):
    return [line.rename(rename_dict) for line in lines]


def left_and_right(
    report: BalanceSheet, rename_dict: dict[str, str]
) -> tuple[list[Line], list[Line]]:
    left = lines({"assets": report.assets})
    right = lines({"capital": report.capital, "liabilities": report.liabilities})
    # rename lines
    left = rename(left, rename_dict)
    right = rename(right, rename_dict)
    # make `left` and `right` same number of lines by adding empty lines
    n = max(len(left), len(right))
    left += [empty_line()] * (n - len(left))
    right += [empty_line()] * (n - len(right))
    # add end lines
    h1 = HeaderLine("Total:", total(report.assets))
    left.append(h1)
    t = total(report.capital) + total(report.liabilities)
    h2 = HeaderLine("Total:", t)
    right.append(h2)
    return left, right


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


def view_balance_sheet(report: BalanceSheet, rename_dict: dict[str, str]) -> str:
    left, right = left_and_right(report, rename_dict)
    a, b = to_columns(left)
    col1 = a.align_left(".").add_right("... ") + b.align_right()
    c, d = to_columns(right)
    col2 = c.align_left(".").add_right("... ") + d.align_right()
    return str(col1.add_space(2) + col2)


def income_statement_lines(report: IncomeStatement, rename_dict: dict[str, str]):
    left = lines({"income": report.income, "expenses:": report.expenses})
    left = [line.rename(rename_dict) for line in left]
    h1 = HeaderLine("Current profit", str(report.current_profit()))
    left.append(h1)
    return left


def view_income_statement(report: IncomeStatement, rename_dict: dict[str, str]) -> str:
    left = income_statement_lines(report, rename_dict)
    a, b = to_columns(left)
    col = a.align_left(fill_char=".").add_right("... ") + b.align_right(fill_char=" ")
    return str(col)


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
