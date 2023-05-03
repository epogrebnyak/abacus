from abacus.core import BalanceSheet, IncomeStatement, AccountBalancesDict
from dataclasses import dataclass


@dataclass
class LineBase:
    text: str
    value: str


class Header(LineBase):
    pass


class Line(LineBase):
    pass


def longest(xs):
    return max(len(x) for x in xs)


def side_by_side(left, right, space="  "):
    from itertools import zip_longest

    width = longest(left)
    gen = zip_longest(left, right, fillvalue="")
    gen = [(x.ljust(width, " "), y) for x, y in gen]
    return [f"{x}{space}{y}" for x, y in gen]


def lineset0(xs, parts):
    def tot(items):
        return AccountBalancesDict(items).total()

    for part in parts:
        items = getattr(xs, part)
        yield Header(part, tot(items))
        for name, value in items.items():
            yield Line(name, value)


def rename_with(alt_dict={}):
    def mut(s):
        return alt_dict.get(s, s).capitalize().replace("_", " ")

    def f(line):
        line.text = mut(line.text)
        return line

    return f


def offset(line):
    match line:
        case Header(a, b):
            return (a, b)
        case Line(a, b):
            return ("- " + a, b)


def lineset(report, parts, alt_dict={}):
    abc = lineset0(report, parts)
    abc = map(rename_with(alt_dict), abc)
    abc = map(offset, abc)
    return list(abc)


def plain(xs):
    from tabulate import tabulate

    return tabulate(xs, tablefmt="plain").split("\n")


def balance_sheet_as_string(bs, alt_diсt={}):
    right = lineset(bs, ["capital", "liabilities"], alt_diсt)
    left = lineset(bs, ["assets"], alt_diсt)
    return "\n".join(side_by_side(plain(left), plain(right)))


def income_statement_as_string(inc, alt_diсt={}):
    right = lineset(inc, ["income", "expenses"], alt_diсt)
    left = []
    return "\n".join(side_by_side(plain(left), plain(right)))


bs = BalanceSheet(
    assets={"cash": 1130, "receivables": 25, "goods_for_sale": 45},
    capital={"equity": 1000, "re": 75},
    liabilities={"payables": 50, "divp": 75},
)
alt_dict = dict(
    re="retained earnings",
    divp="Dividend due",
    cogs="Cost of goods sold",
    sga="Selling, general and adm. expenses",
)
bp = balance_sheet_as_string(bs, alt_dict)
print(bp)

inc = IncomeStatement(income={"sales": 760}, expenses={"cogs": 440, "sga": 400})


def income_statement_as_string(inc, alt_diсt={}):
    left = lineset(inc, ["income", "expenses"], alt_diсt)
    right = []
    return "\n".join(side_by_side(plain(left), plain(right)))


ip = income_statement_as_string(inc, alt_dict)
print(ip)
