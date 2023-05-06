from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.table import Table
from rich.text import Text

from abacus.accounting_types import (Amount, BalanceSheet, IncomeStatement,
                                     Report)


def yield_lines(report: Report, parts: List[str]):
    for part in parts:
        items = getattr(report, part)
        # The header line shows sum of the items
        yield HeaderLine(part, items.total())
        for name, value in items.items():
            yield AccountLine(name, value)


def lines(report, parts):
    return list(yield_lines(report, parts))


@dataclass
class Line:
    text: str
    value: str


class HeaderLine(Line):
    pass


class AccountLine(Line):
    pass


def unpack(line: Line) -> Tuple[Text, Text]:
    """Convert Line to rich.Text tuple"""
    match line:
        case HeaderLine(a, b):
            return bold(a), bold(red(b))
        case AccountLine(a, b):
            return ("  " + a, red(b))
        case _:
            raise ValueError(line)


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


def unline(rename_dict, lines: List[Line]) -> List[Tuple[Text, Text]]:
    lines = map(rename_factory(rename_dict), lines)
    return list(map(unpack, lines))

def empty_line() -> AccountLine:
    return AccountLine("", "")
    
def balance_sheet_table(
    bs: BalanceSheet, rename_dict: Dict[str,str]=dict(), width: Optional[int] =None,
    table_header: str="Balance sheet", end_line: str = "Total"
) -> Table:
    left = lines(bs, ["assets"])
    right = lines(bs, ["capital", "liabilities"])
    # make left and right same number of lines
    n = max(len(left), len(right))
    left += [empty_line()] * (n - len(left))
    right += [empty_line()] * (n - len(right))
    # Add total
    left.append(HeaderLine(end_line, bs.assets.total()))
    right.append(HeaderLine(end_line, bs.capital.total() + bs.liabilities.total()))
    # convert to rich.Text
    left = unline(rename_dict, left)
    right = unline(rename_dict, right)
    # make table
    table = Table(title=table_header, box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    table.add_column("")
    table.add_column("", justify="right", style="green")
    for (a, b), (c, d) in zip(left, right):
        table.add_row(a, b, c, d)
    return table


def income_statement_table(
    inc: IncomeStatement,
    rename_dict: Dict[str,str] = dict(),
    width: Optional[int] =None,
    table_header: str ="Income statement",
    end_line: str ="Profit",
) -> Table:
    inc_lines = lines(inc, ["income", "expenses"]) + [
        HeaderLine(end_line, inc.current_profit())
    ]
    inc_lines = unline(rename_dict, inc_lines)
    table = Table(title=table_header, box=None, width=width, show_header=False)
    table.add_column("")
    table.add_column("", justify="right", style="green")
    for a, b in inc_lines:
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
