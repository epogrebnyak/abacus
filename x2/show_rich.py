"""Rich formatting for income statement and balance sheet."""

from rich.console import Console
from rich.table import Table
from rich.text import Text
from show import (
    AccountLine,
    Amount,
    EmptyLine,
    HeaderLine,
    IncomeStatement,
    Line,
    income_statement_lines,
    left_and_right,
)

__all__ = ["rich_print"]


def rich_print(report, rename_dict=None, width=80):
    if rename_dict is None:
        rename_dict = {}
    match report.__class__.__name__:
        case "BalanceSheet":
            return rich_print_balance_sheet(report, rename_dict, width=width)
        case "IncomeStatement":
            return rich_print_income_statement(report, rename_dict, width=width)
        case _:
            raise TypeError(report)


def start_balance_sheet_table(title, width) -> Table:
    table = Table(title=title, box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    table.add_column("")
    table.add_column("", justify="right", style="green")
    return table


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


def rich_print_balance_sheet(
    statement, rename_dict: dict[str, str], title="Balance sheet", width: int = 80
) -> None:
    left, right = left_and_right(statement, rename_dict)
    table = start_balance_sheet_table(title, width)
    for line_1, line_2 in zip(left, right):
        a, b = unpack(line_1)
        c, d = unpack(line_2)
        table.add_row(a, b, c, d)
    Console().print(table)


def rich_print_income_statement(
    report: IncomeStatement,
    rename_dict: dict[str, str],
    title: str = "Income Statement",
    width: int = 80,
):
    left = income_statement_lines(report, rename_dict)
    table = Table(title=title, box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    for line in left:
        a, b = unpack(line)
        table.add_row(a, b)
    Console().print(table)
