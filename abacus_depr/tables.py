"""Display financial reports as tables (rich.text.Table) on console."""

# mypy: ignore-errors
# pyright: ignore

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.table import Table
from rich.text import Text

from abacus_depr.accounting_types import Amount, total
from abacus_depr.reports import BalanceSheet, IncomeStatement, Report

__all__ = ["PlainTextViewer", "RichViewer"]


@dataclass
class Line:
    text: str
    value: str


class HeaderLine(Line):
    pass


class AccountLine(Line):
    pass


def yield_lines(report: Report, parts: List[str]):
    for part in parts:
        items = getattr(report, part)
        # The header line shows sum of the items
        yield HeaderLine(part, total(items))
        for name, value in items.items():
            yield AccountLine(name, value)


def get_lines(report: Report, parts: List[str]) -> List[Line]:
    return list(yield_lines(report, parts))


def unpack(line: Line) -> Tuple[Text, Text]:
    """Convert Line to rich.Text tuple"""
    match line:
        case HeaderLine(a, b):
            return bold(a), bold(red(b))
        case AccountLine(a, b):
            return ("  " + a, red(b))
        case _:
            raise ValueError(line)


def unpack_many(lines: List[Line]) -> List[Tuple[Text, Text]]:
    return [unpack(line) for line in lines]


def red(b: Amount) -> Text:
    """Make digit red if negative."""
    if b and b < 0:
        return Text(str(b), style="red")
    else:
        return Text(str(b))


def bold(s) -> Text:
    if isinstance(s, Text):
        s.stylize("bold")
        return s
    else:
        return Text(str(s), style="bold")


def rename_factory(rename_dict={}):
    def mut(s):
        return rename_dict.get(s, s).capitalize().replace("_", " ")

    def f(line):
        return line.__class__(mut(line.text), line.value)

    return f


def rename_lines(rename_dict: Dict[str, str], lines: List[Line]):
    f = rename_factory(rename_dict)
    return [f(line) for line in lines]


def empty_line() -> AccountLine:
    return AccountLine("", "")


def balance_sheet_lines(
    bs: BalanceSheet,
    rename_dict: Dict[str, str] = dict(),
    end_line: str = "Total",
) -> Tuple[List[Line], List[Line]]:
    left = get_lines(bs, ["assets"])
    right = get_lines(bs, ["capital", "liabilities"])
    # make left and right same number of lines
    n = max(len(left), len(right))
    left += [AccountLine("", "")] * (n - len(left))
    right += [AccountLine("", "")] * (n - len(right))
    # Add end line
    left.append(HeaderLine(end_line, total(bs.assets)))
    right.append(HeaderLine(end_line, total(bs.capital) + total(bs.liabilities)))
    # Rename using rename_dict
    return rename_lines(rename_dict, left), rename_lines(rename_dict, right)


def balance_sheet_table(
    bs: BalanceSheet,
    rename_dict: Dict[str, str] = dict(),
    width: Optional[int] = None,
    table_header: str = "Balance sheet",
    end_line: str = "Total",
) -> Table:
    left, right = balance_sheet_lines(bs, rename_dict, end_line)
    # convert to rich.Text
    left = unpack_many(left)
    right = unpack_many(right)
    # make table
    table = Table(title=table_header, box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    table.add_column("")
    table.add_column("", justify="right", style="green")
    for (a, b), (c, d) in zip(left, right):
        table.add_row(a, b, c, d)
    return table


def income_statement_lines(
    inc: IncomeStatement,
    rename_dict: Dict[str, str] = dict(),
    end_line: str = "Profit",
) -> List[Line]:
    lines = get_lines(inc, ["income", "expenses"])
    lines.append(HeaderLine(end_line, inc.current_profit()))
    return rename_lines(rename_dict, lines)


def income_statement_table(
    inc: IncomeStatement,
    rename_dict: Dict[str, str] = dict(),
    width: Optional[int] = None,
    table_header: str = "Income statement",
    end_line: str = "Profit",
) -> Table:
    lines = unpack_many(income_statement_lines(inc, rename_dict, end_line))
    table = Table(title=table_header, box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    for a, b in lines:
        table.add_row(a, b)
    return table


@dataclass
class RichViewer:
    rename_dict: Dict
    width: Optional[int] = None

    def print(self, report):
        if isinstance(report, BalanceSheet):
            table = balance_sheet_table(report, self.rename_dict, self.width)
        elif isinstance(report, IncomeStatement):
            table = income_statement_table(report, self.rename_dict, self.width)
        console = Console()
        console.print(table)


def offset(line: Line) -> Tuple[str, str]:
    match line:
        case HeaderLine(a, b):
            return (a, str(b))
        case AccountLine(a, b):
            if a:
                return ("- " + a, str(b))
            else:
                return ("", "")
        case _:
            raise ValueError


def plain(lines: List[Line]) -> List[str]:
    from tabulate import tabulate

    xs = map(offset, lines)
    return tabulate(xs, tablefmt="plain").split("\n")


def concat(left, right):
    return "\n".join(side_by_side(plain(left), plain(right)))


def side_by_side(left, right, space="  "):
    from itertools import zip_longest

    def longest(xs):
        return max(len(x) for x in xs)

    width = longest(left)
    gen = zip_longest(left, right, fillvalue="")
    gen = [(x.ljust(width, " "), y) for x, y in gen]
    return [f"{x}{space}{y}" for x, y in gen]


def balance_sheet_table_plain(bs, rename_dict):
    left, right = balance_sheet_lines(bs, rename_dict)
    return concat(left, right)


def income_statement_table_plain(inc, rename_dict):
    left = income_statement_lines(inc, rename_dict)
    return "\n".join(plain(left))


@dataclass
class PlainTextViewer:
    rename_dict: Dict

    def show(self, report):
        if isinstance(report, BalanceSheet):
            return balance_sheet_table_plain(report, self.rename_dict)
        elif isinstance(report, IncomeStatement):
            return income_statement_table_plain(report, self.rename_dict)

    def print(self, report):
        return print(self.show(report))
