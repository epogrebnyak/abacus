from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Dict, List, Type, Iterable

from pydantic import BaseModel

from abacus import AbacusError
from abacus.engine.accounts import Asset, Capital, Expense, Income, Liability


@dataclass
class RegularName(ABC):
    account_name: str
    constructor: ClassVar[Type]

    def create(self):
        return self.constructor()


@dataclass
class AssetName(RegularName):
    constructor: Type = Asset


class LiabilityName(RegularName):
    constructor: Type = Liability


class CapitalName(RegularName):
    constructor: Type = Capital


class IncomeName(RegularName):
    constructor: Type = Income


class ExpenseName(RegularName):
    constructor: ClassVar[Type] = Expense


assert ExpenseName("cogs").create() == Expense(debits=[], credits=[])


@dataclass
class ContraName:
    account_name: str
    contra_account_name: str


class Prefix(Enum):
    """Prefixes for five types of regular accounts."""

    ASSET = "asset"
    CAPITAL = "capital"
    LIABILITY = "liability"
    INCOME = "income"
    EXPENSE = "expense"

    @staticmethod
    def all():
        return [p.value for p in Prefix]


def detect_prefix(prefix: str, account_name) -> RegularName:
    prefix = prefix.lower()
    if prefix in ["asset", "assets"]:
        return AssetName(account_name)
    elif prefix in ["liability", "liabilities"]:
        return LiabilityName(account_name)
    elif prefix in ["capital", "equity"]:
        return CapitalName(account_name)
    elif prefix in ["expense", "expenses"]:
        return ExpenseName(account_name)
    elif prefix in ["income"]:
        return IncomeName(account_name)
    else:
        raise AbacusError(f"Invalid account prefix: {prefix}")


def extract(label: str):
    match label.split(":"):
        case (prefix, account_name):
            return detect_prefix(prefix, account_name)
        case "contra", account_name, contra_account_name:
            return ContraName(account_name, contra_account_name)
        case _:
            raise AbacusError(f"Invalid account label: {label}")


def account_name(name):
    match name:
        case RegularName(account_name):
            return account_name
        case ContraName(_, contra_account_name):
            return contra_account_name


class BaseChart(BaseModel):
    """Chart of accounts."""

    assets: List[str] = []
    expenses: List[str] = []
    capital: List[str] = []
    liabilities: List[str] = []
    income: List[str] = []
    income_summary_account: str = "current_profit"
    retained_earnings_account: str = "re"
    null_account = "null"
    contra_accounts: Dict[str, List[str]] = {}

    def add(self, label):
        return self.promote(name=extract(label))

    def promote(self, name: RegularName | ContraName):
        match name:
            case AssetName(account_name):
                self.add_regular("assets", account_name)
            case CapitalName(account_name):
                self.add_regular("capital", account_name)
            case LiabilityName(account_name):
                self.add_regular("liabilities", account_name)
            case IncomeName(account_name):
                self.add_regular("income", account_name)
            case ExpenseName(account_name):
                self.add_regular("expenses", account_name)
            case ContraName(account_name, contra_account_name):
                self.add_contra(account_name, contra_account_name)
            case _:
                raise AbacusError(f"Invalid name: {name}")
        return self

    def promote_many(self, names: Iterable[RegularName | ContraName]):
        for name in names:
            self.promote(name)
        return self

    def assert_does_not_contain(self, account_name):
        if account_name in self.account_names_str():
            raise AbacusError(
                "Account name must be unique, "
                f"but <{account_name}> is already in chart."
            )
        return self

    def add_regular(self, attribute: str, account_name: str):
        if account_name in getattr(self, attribute):
            raise AbacusError(
                f"Account name <{account_name}> already exists "
                f"within <{attribute}> chart attribute."
            )
        self.assert_does_not_contain(account_name)
        account_names = getattr(self, attribute) + [account_name]
        setattr(self, attribute, account_names)
        return self

    def add_contra(self, account_name, contra_account_name):
        self.assert_does_not_contain(contra_account_name)
        if account_name not in self.account_names_str():
            raise AbacusError(
                f"Account name <{account_name}> must be in chart "
                f"before adding a contra account <{contra_account_name}>."
            )
        self.contra_accounts[account_name] = self.contra_accounts.get(
            account_name, []
        ) + [contra_account_name]
        return self

    def account_names_str(self) -> Iterable[str]:
        return map(account_name, self.account_names_all())

    def account_names_all(self) -> Iterable[RegularName | ContraName]:
        for cls, attribute in [
            (AssetName, "assets"),
            (CapitalName, "capital"),
            (LiabilityName, "liabilities"),
            (IncomeName, "income"),
            (ExpenseName, "expenses"),
        ]:
            for account_name in getattr(self, attribute):
                yield cls(account_name)
        for account_name, values in self.contra_accounts.items():
            for contra_account_name in values:
                yield ContraName(account_name, contra_account_name)


class BetterChart(BaseModel):
    chart: BaseChart = BaseChart()
    titles: Dict[str, str] = {}
    operations: Dict[str, Dict[str, str]] = {}

    def add(self, label, title=None):
        name = extract(label)
        self.chart.promote(name)
        self.set_title(account_name(name), title)
        return self

    def name(self, account_name, title):
        return self.set_title(account_name, title)

    def set_title(self, account_name, title: str | None):
        if title is not None:
            self.titles[account_name] = title
        return self

    def get_title(self, account_name):
        default_name = account_name.replace("_", " ").title()
        return self.titles.get(account_name, default_name)

    def ledger(self):
        pass


a = (
    BetterChart()
    .add("asset:cash")
    .name("cash", title="Cash and equivalents")
    .add("capital:equity")
    .add("contra:equity:ts", title="What is it?")
    .name("ts", "Treasury shares")
)

b = BaseChart(
    assets=["cash"],
    capital=["equity"],
    contra_accounts={"equity": ["ts"]},
)
assert a == BetterChart(
    chart=b, titles={"cash": "Cash and equivalents", "ts": "Treasury shares"}
)

names = list(b.account_names_all())
assert names == [
    AssetName("cash"),
    CapitalName("equity"),
    ContraName("equity", "ts"),
]
assert BaseChart().promote_many(names) == b


# chart0 = (
#     BetterChart()
#     .add("asset:cash")
#     .add("capital:equity", title="Shareholder equity")
#     .add("contra:equity:ts", title="Treasury shares")
#     .alias("capitalize", debit="cash", credit="equity")
#     .alias("buyback", debit="ts", credit="cash")
#     .set_isa("net_income")
#     .set_re("re")
#     .set_null("null")
#     .name("cash", "Cash and equivalents")
# )

# # cx add asset:cash
# # cx add asset:cash capital:equity contra:equity:ts
# # cx name ts --title "Treasury shares"
# # cx add --asset cash --title "Cash and equivalents"
# # cx add --asset cash goods ar
# # cx name ar --title "Accounts receivable"
# # cx offset equity ts --title "Treasury shares"
# # cx add income:sales
# # cx offset sales voids refunds cashback
# # cx alias capitalize --debit cash --credit equity
# # cx set --income-summary-account current_profit --retained-earings-account re --null-account null

# # add(account_label, title)
# # add_many(prefix, account_names)
# # name()
# # offset()
# # offset_many()
# # alias()
# # promote(name: Name)
# # promote_many(names: List[Name])
# # set_isa()
# # set_re()
# # set_null()
# chart = (
#     BetterChart()
#     .add("asset:cash")
#     .add("capital:equity")
#     .add("asset:ar", title="Accounts receivable")
#     .add("asset:goods", title="Goods for resale")
#     .add("expense:cogs", title="Cost of goods sold")
#     .add("expense:sga", title="Selling, general and adm. expenses")
#     .add("income:sales")
#     .offset_many("sales", ["refunds", "voids"])
#     .add("contra:equity:wd")  # fictional, may only be in partnerships
#     .name("wd", title="Withdrawals")
#     .offset("equity", "ts", title="Treasury shares")
#     .add("liability:dd", title="Dividend due")
#     .alias("invoice", debit="ar", credit="sales")
#     .alias("cost", debit="goods", credit="cogs")
#     .set_isa("current_profit")  # will be added by default
#     .set_null("null")  # will be added by default
#     .set_re("re")  # will be added by default
# )

# from abacus.engine.accounts import (
#     AssetName,
#     CapitalName,
#     LiabilityName,
#     IncomeName,
#     ExpenseName,
#     ContraName,
# )

# from dataclasses import dataclass


# @dataclass
# class NullName:
#     account_name: str


# @dataclass
# class IncomeSummaryName:
#     account_name: str


# @dataclass
# class RetainedEarningsName:
#     account_name: str


# assert chart.account_names() == [
#     AssetName("cash"),
#     AssetName("ar"),
#     AssetName("goods"),
#     CapitalName("equity"),
#     RetainedEarningsName("re"),
#     LiabilityName("dd"),
#     IncomeName("sales"),
#     ExpenseName("cogs"),
#     ExpenseName("sga"),
#     ContraName("wd", "equity"),
#     ContraName("ts", "equity"),
#     ContraName("refunds", "sales"),
#     ContraName("voids", "sales"),
#     NullName("null"),
#     IncomeSummaryName("current_profit"),
# ]

# chart.promote(ExpenseName("cogs"))
# chart.promote(RetainedEarningsName("net_income"))

# # make definition circular
# assert BetterChart().promote_many(chart.account_names()).base_chart == chart.base_chart


# assert chart.regular_account_names(prefixes=[Prefix.INCOME, Prefix.EXPENSE])
# assert chart.special_account_names() == [
#     RetainedEarningsName("re"),
#     IncomeSummaryName("current_profit"),
#     NullName("null"),
# ]

# assert chart.contra_account_names(offsets=Prefix.INCOME) == [
#     ContraName("refunds", "sales"),
#     ContraName("voids", "sales"),
# ]

# assert chart.contra_account_names(offsets=Prefix.EQUITY) == [
#     ContraName("wd", "equity"),
#     ContraName("ts", "equity"),
# ]


# assert chart.get_name("dd") == LiabilityName("dd")
# assert str(LiabilityName("dd")) == "liability:dd"
# assert chart.get_name("dd") == "Dividend due"

# ledger = chart.ledger()
# # ledger.start() is ledger.post_compound()
# # ledger.post(debit, credit, amount, title)
# # ledger.post_compound(single_entries)
# # ledger.post_alias(operations, title)
# # ledger.close()
