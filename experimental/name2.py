import itertools
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Type

from pydantic import BaseModel

from abacus import AbacusError, Ledger  # type: ignore
from abacus.engine.accounts import (  # type: ignore
    Asset,
    Capital,
    ContraAccount,
    ContraAsset,
    ContraCapital,
    ContraExpense,
    ContraIncome,
    ContraLiability,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    NullAccount,
    RegularAccount,
    RetainedEarnings,
    TAccount,
)

from dataclasses import dataclass, field


@dataclass
class Name:
    account_name: str
    contra_accounts: None | List[str]

    def _accounts(self, cls, contra_cls):
        yield self.account_name, cls
        if self.contra_accounts:
            for contra_account in self.contra_accounts:
                yield contra_account, contra_cls


@dataclass
class AssetName(Name):
    def accounts(self):
        yield from self._accounts(Asset, ContraAsset)


class LiabilityName(Name):
    def accounts(self):
        yield from self._accounts(Liability, ContraLiability)


class CapitalName(Name):
    def accounts(self):
        yield from self._accounts(Capital, ContraCapital)


class IncomeName(Name):
    def accounts(self):
        yield from self._accounts(Income, ContraIncome)


class ExpenseName(Name):
    def accounts(self):
        yield from self._accounts(Expense, ContraExpense)


class RetainedEarningsName(Name):
    def accounts(self):
        yield self.account_name, RetainedEarnings


class IncomeSummaryName(Name):
    def accounts(self):
        yield self.account_name, IncomeSummaryAccount


class NullName(Name):
    def accounts(self):
        yield self.account_name, NullAccount


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

    def yield_names(self):
        attributes = ["assets", "expenses", "capital", "liabilities", "income"]
        name_classes = [AssetName, ExpenseName, CapitalName, LiabilityName, IncomeName]
        for attribute, name_class in zip(attributes, name_classes):
            for account_name in getattr(self, attribute):
                contra_accounts = self.contra_accounts.get(account_name, [])
                yield name_class(account_name, contra_accounts)
        yield RetainedEarningsName(self.retained_earnings_account, None)
        yield IncomeSummaryName(self.income_summary_account, None)
        yield NullName(self.null_account, None)

    def filter_accounts(self, account_classes: List[Type[TAccount]]):
        for account_name, account_cls in self.ledger_items():
            for account_class in account_classes:
                if account_cls == account_class:
                    yield account_name

    def ledger_items(self):
        for name in self.yield_names():
            for account_name, account_cls in name.accounts():
                yield account_name, account_cls

    def ledger(self):
        return Ledger(
            (account_name, account_cls())
            for account_name, account_cls in self.ledger_items()
        )


base = BaseChart(
    assets=["cash"], capital=["equity"], contra_accounts=dict(equity=["ts"])
)
assert list(base.yield_names()) == [
    AssetName(account_name="cash", contra_accounts=[]),
    CapitalName(account_name="equity", contra_accounts=["ts"]),
    RetainedEarningsName(account_name="re", contra_accounts=None),
    IncomeSummaryName(account_name="current_profit", contra_accounts=None),
    NullName(account_name="null", contra_accounts=None),
]

assert list(base.ledger_items()) == [
    ("cash", Asset),
    ("equity", Capital),
    ("ts", ContraCapital),
    ("re", RetainedEarnings),
    ("current_profit", IncomeSummaryAccount),
    ("null", NullAccount),
]


assert list(CapitalName("equity", ["ts"]).accounts()) == [
    ("equity", Capital),
    ("ts", ContraCapital),
]
assert list(base.filter_accounts([ContraCapital])) == ["ts"]

# def prefix(name: Name) -> str:
#     t = t_account_constructor(name)
#     return t.__name__.lower()


# assert create(ExpenseName("cogs")) == Expense(debits=[], credits=[])
# assert str(ExpenseName("cogs")) == "expense:cogs"


# def yield_regular_accounts(chart):
#     for constructor in mapper():
#         for account_name in getattr(chart, constructor.attribute):
#             yield account_name, constructor.t_account


# def yield_contra_accounts(chart):
#     for constructor in mapper():
#         for account_name in getattr(chart, constructor.attribute):
#             for contra_account in chart.contra_accounts.get(account_name, []):
#                 yield contra_account, constructor.t_account_contra
#     yield from []


# def yield_unique_accounts(chart):
#     yield chart.retained_earnings_account, RetainedEarnings
#     yield chart.income_summary_account, IncomeSummaryAccount
#     yield chart.null_account, NullAccount


# def yield_all_accounts(chart):
#     return itertools.chain(
#         yield_regular_accounts(chart),
#         yield_contra_accounts(chart),
#         yield_unique_accounts(chart),
#     )


# def detect(prefix: str, account_name) -> Name:
#     prefix = prefix.lower()
#     if prefix in ["asset", "assets"]:
#         return AssetName(account_name)
#     elif prefix in ["liability", "liabilities"]:
#         return LiabilityName(account_name)
#     elif prefix in ["capital", "equity"]:
#         return CapitalName(account_name)
#     elif prefix in ["expense", "expenses"]:
#         return ExpenseName(account_name)
#     elif prefix in ["income"]:
#         return IncomeName(account_name)
#     else:
#         raise AbacusError(f"Invalid account prefix: {prefix}")


def extract(label: str) -> Name:
    match label.split(":"):
        case (prefix, account_name):
            return prefix, account_name
        case "contra", account_name, contra_account_name:
            return account_name, contra_account_name
        case _:
            raise AbacusError(f"Invalid account label: {label}")


# def get_account_name(name: Name) -> str:
#     match name:
#         case Name(account_name):
#             return account_name
#         case ContraName(_, contra_account_name):
#             return contra_account_name


#     # def promote(self, name: Name | ContraName):
#     #     match name:
#     #         case AssetName(account_name):
#     #             self.add_regular("assets", account_name)
#     #         case CapitalName(account_name):
#     #             self.add_regular("capital", account_name)
#     #         case LiabilityName(account_name):
#     #             self.add_regular("liabilities", account_name)
#     #         case IncomeName(account_name):
#     #             self.add_regular("income", account_name)
#     #         case ExpenseName(account_name):
#     #             self.add_regular("expenses", account_name)
#     #         case ContraName(account_name, contra_account_name):
#     #             self.add_contra(account_name, contra_account_name)
#     #         case _:
#     #             raise AbacusError(f"Invalid name: {name}")
#     #     return self

#     # def promote_many(self, names: Iterable[Name]):
#     #     for name in names:
#     #         self.promote(name)
#     #     return self

#     # def add_regular(self, attribute: str, account_name: str):
#     #     self.check.does_not_exist_in_attribute(account_name, attribute)
#     #     self.check.does_not_exist(account_name)
#     #     account_names = getattr(self, attribute) + [account_name]
#     #     setattr(self, attribute, account_names)
#     #     return self

#     # def add_contra(self, account_name, contra_account_name):
#     #     self.check.does_not_exist(contra_account_name)
#     #     self.check.exists(account_name)
#     #     self.contra_accounts[account_name] = self.contra_accounts.get(
#     #         account_name, []
#     #     ) + [contra_account_name]
#     #     return self

#     # def account_names_as_strings(self) -> Iterable[str]:
#     #     return map(get_account_name, self.account_names_all())

#     # def account_names_all(self) -> Iterable[Name]:
#     #     for constructor in mapper():
#     #         for account_name in getattr(self, constructor.attribute):
#     #             yield constructor.name(account_name)
#     #     for account_name, values in self.contra_accounts.items():
#     #         for contra_account_name in values:
#     #             yield ContraName(account_name, contra_account_name)

#     # def filter_accounts(self, account_classes: List[Type[TAccount]]):
#     #     for account_name, cls in yield_all_accounts(self):
#     #         for account_class in account_classes:
#     #             if isinstance(cls(), account_class):
#     #                 yield account_name
#     #     yield from []

#     # @property
#     # def check(self):
#     #     return Check(self)

#     # def ledger(self):
#     #     from abacus import Ledger

#     #     return Ledger(
#     #         (account_name, cls()) for account_name, cls in yield_all_accounts(self)
#     #     )


@dataclass
class Check:
    chart: BaseChart

    def all_account_names(self):
        return [account_name for account_name, _ in self.chart.ledger_items()]

    def contains(self, account_name):
        return account_name in self.all_account_names()

    def exists(self, account_name):
        if not self.contains(account_name):
            raise AbacusError(
                f"Account name <{account_name}> must be specified in chart"
                " to enable this operation."
            )

    def does_not_exist(self, account_name):
        if self.contains(account_name):
            raise AbacusError(
                "Account name must be unique, "
                f"there is already <{account_name}> in chart."
            )
        return self

    def does_not_exist_in_attribute(self, account_name, attribute):
        if account_name in getattr(self.chart, attribute):
            raise AbacusError(
                f"Account name <{account_name}> already exists "
                f"within <{attribute}> chart attribute."
            )


# class BetterChart(BaseModel):
#     chart: BaseChart = BaseChart()
#     titles: Dict[str, str] = {}
#     operations: Dict[str, Dict[str, str]] = {}

#     def add(self, label, title=None):
#         name = extract(label)
#         self.chart.promote(name)
#         self.set_title(get_account_name(name), title)
#         return self

#     def name(self, account_name, title):
#         return self.set_title(account_name, title)

#     def set_title(self, account_name, title: str | None):
#         if title is not None:
#             self.titles[account_name] = title
#         return self

#     def get_title(self, account_name):
#         default_name = account_name.replace("_", " ").title()
#         return self.titles.get(account_name, default_name)

#     def get_label(self, account_name_) -> str | None:
#         for name in self.chart.account_names_all():
#             if get_account_name(name) == account_name_:
#                 return str(name)
#         return None


# if __name__ == "__main__":
#     a = (
#         BetterChart()
#         .add("asset:cash")
#         .name("cash", title="Cash and equivalents")
#         .add("capital:equity")
#         .add("contra:equity:ts", title="What is it?")
#         .name("ts", "Treasury shares")
#     )

#     assert a.get_label("cash") == "asset:cash"

#     b = BaseChart(
#         assets=["cash"],
#         capital=["equity"],
#         contra_accounts={"equity": ["ts"]},
#     )
#     assert a == BetterChart(
#         chart=b, titles={"cash": "Cash and equivalents", "ts": "Treasury shares"}
#     )

#     names = list(b.account_names_all())
#     assert names == [
#         AssetName("cash"),
#         CapitalName("equity"),
#         ContraName("equity", "ts"),
#     ]
#     assert BaseChart().promote_many(names) == b

#     assert list(yield_all_accounts(a.chart)) == [
#         ("cash", Asset),
#         ("equity", Capital),
#         ("ts", ContraCapital),
#         ("re", RetainedEarnings),
#         ("current_profit", IncomeSummaryAccount),
#         ("null", NullAccount),
#     ]

#     assert list(b.filter_accounts([ContraCapital])) == ["ts"]
#     assert list(b.filter_accounts([Asset, Capital])) == ["cash", "equity", "re"]

#     assert isinstance(a.chart.ledger(), Ledger)

# # chart0 = (
# #     BetterChart()
# #     .add("asset:cash")
# #     .add("capital:equity", title="Shareholder equity")
# #     .add("contra:equity:ts", title="Treasury shares")
# #     .alias("capitalize", debit="cash", credit="equity")
# #     .alias("buyback", debit="ts", credit="cash")
# #     .set_isa("net_income")
# #     .set_re("re")
# #     .set_null("null")
# #     .name("cash", "Cash and equivalents")
# # )

# # # cx add asset:cash
# # # cx add asset:cash capital:equity contra:equity:ts
# # # cx name ts --title "Treasury shares"
# # # cx add --asset cash --title "Cash and equivalents"
# # # cx add --asset cash goods ar
# # # cx name ar --title "Accounts receivable"
# # # cx offset equity ts --title "Treasury shares"
# # # cx add income:sales
# # # cx offset sales voids refunds cashback
# # # cx alias capitalize --debit cash --credit equity
# # # cx set --income-summary-account current_profit --retained-earings-account re --null-account null

# # # add(account_label, title)
# # # add_many(prefix, account_names)
# # # name()
# # # offset()
# # # offset_many()
# # # alias()
# # # promote(name: Name)
# # # promote_many(names: List[Name])
# # # set_isa()
# # # set_re()
# # # set_null()
# # chart = (
# #     BetterChart()
# #     .add("asset:cash")
# #     .add("capital:equity")
# #     .add("asset:ar", title="Accounts receivable")
# #     .add("asset:goods", title="Goods for resale")
# #     .add("expense:cogs", title="Cost of goods sold")
# #     .add("expense:sga", title="Selling, general and adm. expenses")
# #     .add("income:sales")
# #     .offset_many("sales", ["refunds", "voids"])
# #     .add("contra:equity:wd")  # fictional, may only be in partnerships
# #     .name("wd", title="Withdrawals")
# #     .offset("equity", "ts", title="Treasury shares")
# #     .add("liability:dd", title="Dividend due")
# #     .alias("invoice", debit="ar", credit="sales")
# #     .alias("cost", debit="goods", credit="cogs")
# #     .set_isa("current_profit")  # will be added by default
# #     .set_null("null")  # will be added by default
# #     .set_re("re")  # will be added by default
# # )

# # from abacus.engine.accounts import (
# #     AssetName,
# #     CapitalName,
# #     LiabilityName,
# #     IncomeName,
# #     ExpenseName,
# #     ContraName,
# # )

# # from dataclasses import dataclass


# # @dataclass
# # class NullName:
# #     account_name: str


# # @dataclass
# # class IncomeSummaryName:
# #     account_name: str


# # @dataclass
# # class RetainedEarningsName:
# #     account_name: str


# # assert chart.account_names() == [
# #     AssetName("cash"),
# #     AssetName("ar"),
# #     AssetName("goods"),
# #     CapitalName("equity"),
# #     RetainedEarningsName("re"),
# #     LiabilityName("dd"),
# #     IncomeName("sales"),
# #     ExpenseName("cogs"),
# #     ExpenseName("sga"),
# #     ContraName("wd", "equity"),
# #     ContraName("ts", "equity"),
# #     ContraName("refunds", "sales"),
# #     ContraName("voids", "sales"),
# #     NullName("null"),
# #     IncomeSummaryName("current_profit"),
# # ]

# # chart.promote(ExpenseName("cogs"))
# # chart.promote(RetainedEarningsName("net_income"))

# # # make definition circular
# # assert BetterChart().promote_many(chart.account_names()).base_chart == chart.base_chart


# # assert chart.regular_account_names(prefixes=[Prefix.INCOME, Prefix.EXPENSE])
# # assert chart.special_account_names() == [
# #     RetainedEarningsName("re"),
# #     IncomeSummaryName("current_profit"),
# #     NullName("null"),
# # ]

# # assert chart.contra_account_names(offsets=Prefix.INCOME) == [
# #     ContraName("refunds", "sales"),
# #     ContraName("voids", "sales"),
# # ]

# # assert chart.contra_account_names(offsets=Prefix.EQUITY) == [
# #     ContraName("wd", "equity"),
# #     ContraName("ts", "equity"),
# # ]


# # assert chart.get_name("dd") == LiabilityName("dd")
# # assert str(LiabilityName("dd")) == "liability:dd"
# # assert chart.get_name("dd") == "Dividend due"

# # ledger = chart.ledger()
# # # ledger.start() is ledger.post_compound()
# # # ledger.post(debit, credit, amount, title)
# # # ledger.post_compound(single_entries)
# # # ledger.post_alias(operations, title)
# # # ledger.close()
