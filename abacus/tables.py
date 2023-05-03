from dataclasses import dataclass
from abacus.core import BalanceSheet, IncomeStatement, AccountBalancesDict
from typing import Dict, Optional
from rich.text import Text
from rich.console import Console
from rich.table import Table


def yield_lines(report, parts):
    for part in parts:
        items = getattr(report, part)
        yield Header(part, items.total())
        for name, value in items.items():
            yield Line(name, value)


def lines(report, parts):
    return list(yield_lines(report, parts))


@dataclass
class LineBase:
    text: str
    value: str


class Header(LineBase):
    pass


class Line(LineBase):
    pass


def unpack(line):
    match line:
        case Header(a, b):
            return bold(a), bold(red(b))
        case Line(a, b):
            return ("  " + a, red(b))


def red(b):
    if b and b < 0:
        return Text(str(b), style="red")
    else:
        return Text(str(b))


def bold(s):
    if isinstance(s, Text):
        s.stylize("bold")
        return s
    else:
        return Text(str(s), style="bold")


def rename_factory(rename_dict={}):
    def mut(s):
        return rename_dict.get(s, s).capitalize().replace("_", " ")

    def f(line):
        line.text = mut(line.text)
        return line

    return f


def unline(rename_dict, lines):
    lines = map(rename_factory(rename_dict), lines)
    return list(map(unpack, lines))


def balance_sheet_table(bs, rename_dict=dict(), width=None):
    left = lines(bs, ["assets"])
    right = lines(bs, ["capital", "liabilities"])
    n = max(len(left), len(right))
    left += [Line("", "")] * (n - len(left))
    right += [Line("", "")] * (n - len(right))
    left += [Header("Total", bs.assets.total())]
    right += [Header("Total", bs.capital.total() + bs.liabilities.total())]
    left = unline(rename_dict, left)
    right = unline(rename_dict, right)
    table = Table(title="Balance sheet", box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    table.add_column("")
    table.add_column("", justify="right", style="green")
    for (a, b), (c, d) in zip(left, right):
        table.add_row(a, b, c, d)
    return table


def income_statement_table(inc, rename_dict=dict(), width=None):
    inc_ = lines(inc, ["income", "expenses"]) + [Header("Profit", inc.current_profit())]
    inc_ = unline(rename_dict, inc_)
    table = Table(title="Income statement", box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    for a, b in inc_:
        table.add_row(a, b)
    return table


@dataclass
class ConsoleViewer:
    rename_dict: Dict
    width: Optional[int] = None

    def print(self, report):
        if isinstance(report, BalanceSheet):
            table = balance_sheet_table(report, self.rename_dict, self.width)
        elif isinstance(report, IncomeStatement):
            table = income_statement_table(report, self.rename_dict, self.width)
        console = Console()
        console.print(table)
