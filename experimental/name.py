from abacus import Chart

chart = Chart()
chart.assets += ["cash"]
chart.expenses += ["cogs"]
print(chart)
print(chart.namer.get_name("cogs").qualified())


class BetterChart:
    pass


chart0 = (
    BetterChart()
    .add("asset:cash")
    .add("capital:equity", title="Shareholder equity")
    .add("contra:equity:ts", title="Treasury shares")
    .alias("capitalize", debit="cash", credit="equity")
    .alias("buyback", debit="ts", credit="cash")
    .set_isa("net_income")
    .set_re("re")
    .set_null("null")
    .name("cash", "Cash and equivalents")
)

# cx add asset:cash
# cx add asset:cash capital:equity contra:equity:ts
# cx name ts --title "Treasury shares"
# cx add --asset cash --title "Cash and equivalents"
# cx add --asset cash goods ar
# cx name ar --title "Accounts receivable"
# cx offset equity ts --title "Treasury shares"
# cx add income:sales
# cx offset sales voids refunds cashback
# cx alias capitalize --debit cash --credit equity
# cx set --income-summary-account current_profit --retained-earings-account re --null-account null

# add(account_label, title)
# add_many(prefix, account_names)
# name()
# offset()
# offset_many()
# alias()
# promote(name: Name)
# promote_many(names: List[Name])
# set_isa()
# set_re()
# set_null()
chart = (
    BetterChart()
    .add("asset:cash")
    .add("capital:equity")
    .add("asset:ar", title="Accounts receivable")
    .add("asset:goods", title="Goods for resale")
    .add("expense:cogs", title="Cost of goods sold")
    .add("expense:sga", title="Selling, general and adm. expenses")
    .add("income:sales")
    .offset_many("sales", ["refunds", "voids"])
    .add("contra:equity:wd")  # fictional, may only be in partnerships
    .name("wd", title="Withdrawals")
    .offset("equity", "ts", title="Treasury shares")
    .add("liability:dd", title="Dividend due")
    .alias("invoice", debit="ar", credit="sales")
    .alias("cost", debit="goods", credit="cogs")
    .set_isa("current_profit")  # will be added by default
    .set_null("null")  # will be added by default
    .set_re("re")  # will be added by default
)

from abacus.engine.accounts import (
    AssetName,
    CapitalName,
    LiabilityName,
    IncomeName,
    ExpenseName,
    ContraName,
)

from dataclasses import dataclass


@dataclass
class NullName:
    account_name: str


@dataclass
class IncomeSummaryName:
    account_name: str


@dataclass
class RetainedEarningsName:
    account_name: str


assert chart.account_names() == [
    AssetName("cash"),
    AssetName("ar"),
    AssetName("goods"),
    CapitalName("equity"),
    RetainedEarningsName("re"),
    LiabilityName("dd"),
    IncomeName("sales"),
    ExpenseName("cogs"),
    ExpenseName("sga"),
    ContraName("wd", "equity"),
    ContraName("ts", "equity"),
    ContraName("refunds", "sales"),
    ContraName("voids", "sales"),
    NullName("null"),
    IncomeSummaryName("current_profit"),
]

chart.promote(ExpenseName("cogs"))
chart.promote(RetainedEarningsName("net_income"))

# make definition circular
assert BetterChart().promote_many(chart.account_names()).base_chart == chart.base_chart

from enum import Enum


class Prefix(Enum):
    """Prefixes for five types of regular accounts."""

    ASSET = "asset"
    CAPITAL = "capital"
    LIABILITY = "liability"
    INCOME = "income"
    EXPENSE = "expense"


assert chart.regular_account_names(prefixes=[Prefix.INCOME, Prefix.EXPENSE])
assert chart.special_account_names() == [
    RetainedEarningsName("re"),
    IncomeSummaryName("current_profit"),
    NullName("null"),
]

assert chart.contra_account_names(offsets=Prefix.INCOME) == [
    ContraName("refunds", "sales"),
    ContraName("voids", "sales"),
]

assert chart.contra_account_names(offsets=Prefix.EQUITY) == [
    ContraName("wd", "equity"),
    ContraName("ts", "equity"),
]


assert chart.get_name("dd") == LiabilityName("dd")
assert str(LiabilityName("dd")) == "liability:dd"
assert chart.get_name("dd") == "Dividend due"

ledger = chart.ledger()
# ledger.start() is ledger.post_compound()
# ledger.post(debit, credit, amount, title)
# ledger.post_compound(single_entries)
# ledger.post_alias(operations, title)
# ledger.close()
