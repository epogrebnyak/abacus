from dataclasses import dataclass, field
from itertools import chain, groupby
from typing import Iterable, Type

from pydantic import BaseModel

import abacus.engine.accounts as accounts
from abacus.engine.accounts import TAccount, RegularAccount, ContraAccount


@dataclass
class Offset:
    name: str
    contra: str


@dataclass
class Label:
    name: str


class AssetLabel(Label):
    pass


class LiabilityLabel(Label):
    pass


class ExpenseLabel(Label):
    pass


class IncomeLabel(Label):
    pass


class CapitalLabel(Label):
    pass


class RetainedEarningsLabel(Label):
    pass


class IncomeSummaryLabel(Label):
    pass


class NullLabel(Label):
    pass


class Composer(BaseModel):
    """Extract and compose labels using prefixes, example is asset:cash."""

    asset: str = "asset"
    capital: str = "capital"
    liability: str = "liability"
    income: str = "income"
    expense: str = "expense"
    contra: str = "contra"
    income_summary: str = "isa"
    retained_earnings: str = "re"
    null: str = "null"

    def as_string(self, label: Label | Offset) -> str:
        def and_name(prefix: str) -> str:
            return prefix + ":" + label.name

        match label:
            case AssetLabel(name):
                return and_name(self.asset)
            case LiabilityLabel(name):
                return and_name(self.liability)
            case CapitalLabel(name):
                return and_name(self.capital)
            case IncomeLabel(name):
                return and_name(self.income)
            case ExpenseLabel(name):
                return and_name(self.expense)
            case IncomeSummaryLabel(name):
                return and_name(self.income_summary)
            case RetainedEarningsLabel(name):
                return and_name(self.retained_earnings)
            case NullLabel(name):
                return and_name(self.null)
            case Offset(name, contra):
                return f"{self.contra}:{name}:{contra}"
            case _:
                raise ValueError(f"Invalid label: {label}.")

    def extract(self, label_str: str) -> Label | Offset:
        match label_str.strip().lower().split(":"):
            case [self.asset, name]:
                return AssetLabel(name)
            case [self.liability, name]:
                return LiabilityLabel(name)
            case [self.capital, name]:
                return CapitalLabel(name)
            case [self.income, name]:
                return IncomeLabel(name)
            case [self.expense, name]:
                return ExpenseLabel(name)
            case [self.income_summary, name]:
                return IncomeSummaryLabel(name)
            case [self.retained_earnings, name]:
                return RetainedEarningsLabel(name)
            case [self.null, name]:
                return NullLabel(name)
            case [self.contra, name, contra_name]:
                return Offset(name, contra_name)
            case _:
                raise ValueError(f"Invalid label: {label_str}.")


class BaseChart(BaseModel):
    income_summary_account: str
    retained_earnings_account: str
    null_account: str
    assets: list[str] = []
    expenses: list[str] = []
    capital: list[str] = []
    liabilities: list[str] = []
    income: list[str] = []
    contra_accounts: dict[str, list[str]] = {}

    def safe_append(self, attribute, value):
        if value in self.account_names():
            raise ValueError(f"Duplicate account name: {value}.")
        getattr(self, attribute).append(value)

    def add(self, label_str: str, composer=Composer()):
        return self.promote(composer.extract(label_str))

    def promote(self, label: Label | Offset):
        match label:
            case AssetLabel(name):
                self.safe_append("assets", name)
            case LiabilityLabel(name):
                self.safe_append("liabilities", name)
            case CapitalLabel(name):
                self.safe_append("capital", name)
            case IncomeLabel(name):
                self.safe_append("income", name)
            case ExpenseLabel(name):
                self.safe_append("expenses", name)
            case IncomeSummaryLabel(name):
                self.income_summary_account = name
            case RetainedEarningsLabel(name):
                self.retained_earnings_account = name
            case NullLabel(name):
                self.null_account = name
            case Offset(name, contra):
                self.contra_accounts.setdefault(name, []).append(contra)
        return self

    def t_accounts(self):
        mapper = [
            ("assets", accounts.Asset, accounts.ContraAsset),
            ("capital", accounts.Capital, accounts.ContraCapital),
            ("liabilities", accounts.Liability, accounts.ContraLiability),
            ("income", accounts.Income, accounts.ContraIncome),
            ("expenses", accounts.Expense, accounts.ContraExpense),
        ]
        for attribute, cls, contra_cls in mapper:
            for name in getattr(self, attribute):
                yield name, cls
                for contra_name in self.contra_accounts.get(name, []):
                    yield contra_name, contra_cls
        yield self.income_summary_account, accounts.IncomeSummaryAccount
        yield self.retained_earnings_account, accounts.RetainedEarnings
        yield self.null_account, accounts.NullAccount

    def account_names(self):
        return [name for name, _ in self.t_accounts()]

    def contra_pairs(self, cls: Type[ContraAccount]):
        mapper = {
            "ContraAsset": "assets",
            "ContraLiability": "liabilities",
            "ContraCapital": "capital",
            "ContraExpense": "expenses",
            "ContraIncome": "income",
        }
        names = getattr(self, mapper[cls.__name__])
        return [
            (name, contra_name)
            for name in names
            for contra_name in self.contra_accounts.get(name, [])
        ]

    def label(self, account_name) -> Label | Offset:
        if account_name in self.assets:
            return AssetLabel(account_name)
        elif account_name in self.liabilities:
            return LiabilityLabel(account_name)
        elif account_name in self.capital:
            return CapitalLabel(account_name)
        elif account_name in self.income:
            return IncomeLabel(account_name)
        elif account_name in self.expenses:
            return ExpenseLabel(account_name)
        elif account_name == self.income_summary_account:
            return IncomeSummaryLabel(account_name)
        elif account_name == self.retained_earnings_account:
            return RetainedEarningsLabel(account_name)
        elif account_name == self.null_account:
            return NullLabel(account_name)
        for name, contra_names in self.contra_accounts.items():
            if account_name in contra_names:
                return Offset(name, account_name)
        raise ValueError(f"Invalid account name: {account_name}.")


def base():
    return BaseChart(
        income_summary_account="current_profit",
        retained_earnings_account="retained_earnings",
        null_account="null",
    )


class Chart(BaseModel):
    base: BaseChart = base()
    titles: dict[str, str] = {}
    operations: dict[str, tuple[str, str]] = {}
    composer: composer = Composer()

    def add(self, label_str: str):
        self.base.add(label_str, self.composer)
        return self

    def add_many(self, labels: list[str], prefix: str = ""):
        if prefix and not prefix.endswith(":"):
            prefix = prefix.strip() + ":"
        for label in labels:
            self.add(prefix + label)
        return self

    def offset(self, name: str, contra: str):
        self.base.promote(Offset(name, contra))
        return self

    def offset_many(self, name: str, contra_names: str):
        for contra in contra_names:
            self.offset(name, contra)
        return self

    def name(self, name: str, title: str):
        self.titles[name] = title
        return self

    def alias(self, operation: str, debit: str, credit: str):
        self.operations[operation] = (debit, credit)
        return self

    def label(self, account_name) -> str:
        return self.composer.as_string(self.base.label(account_name))

    def ledger(self):
        from ledger import Ledger

        return Ledger(
            data={name: t_account() for name, t_account in self.base.t_accounts()},
            base_chart=self.base,
        )


# TODO: move below to tests
if __name__ == "__main__":
    g = Composer()
    for string in ("expense:cogs", "contra:sales:refunds", "liability:loan"):
        assert g.as_string(g.extract(string)) == string

    b = (
        base()
        .add("income:sales")
        .add("contra:sales:refunds")
        .promote(Offset("sales", "voids"))
    )
    assert b.contra_accounts == {"sales": ["refunds", "voids"]}

    chart0 = (
        Chart()
        .add("asset:cash")
        .add("capital:equity")
        .add_many(["cogs", "sga"], prefix="expense")
        .name("cogs", "Cost of goods sold")
        .name("sga", "Selling, general, and adm. expenses")
        .add("contra:equity:ts")
        .name("ts", "Treasury share")
        .add("income:sales")
        .add_many(["refunds", "voids"], prefix="contra:sales")
        .add("asset:ar")
        .alias("invoice", "ar", "sales")
        .alias("accept", "cash", "ar")
        .add("asset:inventory")
        .alias("cost", "cogs", "inventory")
        .alias("purchase", "inventory", "cash")
        .alias("refund", "refunds", "cash")
        .add_many(["dd", "ap"], prefix="liability")
    )

    assert chart0.operations == {
        "invoice": ("ar", "sales"),
        "accept": ("cash", "ar"),
        "cost": ("cogs", "inventory"),
        "purchase": ("inventory", "cash"),
        "refund": ("refunds", "cash"),
    }
    assert chart0.composer.as_string(AssetLabel("cash")) == "asset:cash"
    assert chart0.dict() == {
        "base": {
            "income_summary_account": "current_profit",
            "retained_earnings_account": "retained_earnings",
            "null_account": "null",
            "assets": ["cash", "ar", "inventory"],
            "expenses": ["cogs", "sga"],
            "capital": ["equity"],
            "liabilities": ["dd", "ap"],
            "income": ["sales"],
            "contra_accounts": {"equity": ["ts"], "sales": ["refunds", "voids"]},
        },
        "titles": {
            "cogs": "Cost of goods sold",
            "sga": "Selling, general, and adm. expenses",
            "ts": "Treasury share",
        },
        "operations": {
            "invoice": ("ar", "sales"),
            "accept": ("cash", "ar"),
            "cost": ("cogs", "inventory"),
            "purchase": ("inventory", "cash"),
            "refund": ("refunds", "cash"),
        },
        "composer": {
            "asset": "asset",
            "capital": "capital",
            "liability": "liability",
            "income": "income",
            "expense": "expense",
            "contra": "contra",
            "income_summary": "isa",
            "retained_earnings": "re",
            "null": "null",
        },
    }
    assert list(chart0.ledger().data.keys()) == [
        "cash",
        "ar",
        "inventory",
        "equity",
        "ts",
        "dd",
        "ap",
        "sales",
        "refunds",
        "voids",
        "cogs",
        "sga",
        "current_profit",
        "retained_earnings",
        "null",
    ]

    from ledger import Ledger

    assert isinstance(chart0.ledger(), Ledger)
    assert chart0.ledger().data["cash"] == accounts.Asset(debits=[], credits=[])
    assert chart0.base.contra_pairs(accounts.ContraIncome) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]
    assert str(chart0.label("sales")) == "income:sales"
    assert str(chart0.label("refunds")) == "contra:sales:refunds"
