from itertools import chain
from typing import Dict, List

from pydantic import BaseModel

from abacus.accounting_types import AbacusError
from abacus.accounts import Account as TAccount
from abacus.accounts import (
    Asset,
    Capital,
    ContraAsset,
    ContraIncome,
    Expense,
    Income,
    IncomeSummaryAccount,
    RetainedEarnings,
    allocation,
)


class Account(BaseModel):
    name: str
    cls: TAccount | None = None


def is_unique(xs):
    return len(set(xs)) == len(xs)


def assert_unique(xs):
    if not is_unique(xs):
        raise AbacusError("Account names must be unique")


class BaseChart(BaseModel):
    assets: List[str] = []
    expenses: List[str] = []
    equity: List[str] = []
    liabilities: List[str] = []
    income: List[str] = []

    @property
    def attributes(self):
        return list(allocation.keys())

    def account_names(self):
        return [
            account_name
            for attr in self.attributes
            for account_name in getattr(self, attr)
        ]

    def yield_accounts(self):
        for attr, classes in allocation.items():
            for account in getattr(self, attr):
                yield account, classes[0]

    def set_retained_earnings(self, account_name):
        if account_name in self.equity:
            self.equity.remove(account_name)
        assert_unique(self.account_names() + [account_name])
        return Chart(base=self, retained_earnings_account=account_name)


class Chart(BaseModel):
    base: BaseChart
    retained_earnings_account: str
    income_summary_account: str = "_profit"
    contra_accounts: Dict[str, List[str]] = {}

    @classmethod
    def empty(self):
        return Chart(BaseChart(), "")

    def account_names(self):
        return (
            self.base.account_names()
            + [n for n, _ in self.yield_contra_accounts()]
            + [self.retained_earnings_account, self.income_summary_account]
        )

    def set_retained_earnings(self, account_name):
        self.base = self.base.set_retained_earnings(account_name).base
        self.retained_earnings_account = account_name

    def set_isa(self, account_name):
        self.income_summary_account = account_name
        assert_unique(self.account_names())
        return self

    def offset(self, account_name: str, contra_account_names: List[str]):
        self.contra_accounts[account_name] = contra_account_names
        assert_unique(self.account_names())
        return self

    def yield_contra_accounts(self):
        for attr, classes in allocation.items():
            account_names = getattr(self.base, attr)
            for nets_with, contra_account_names in self.contra_accounts.items():
                if nets_with in account_names:
                    for contra_account_name in contra_account_names:
                        yield contra_account_name, classes[1]

    def yield_accounts(self):
        more = iter(
            [
                (self.retained_earnings_account, RetainedEarnings),
                (self.income_summary_account, IncomeSummaryAccount),
            ]
        )
        return chain(self.base.yield_accounts(), more, self.yield_contra_accounts())

    def qualify(self) -> "Chart":
        return self.normalise()

    def book(self, starting_balances: dict | None = None):
        from abacus.book import Book

        if starting_balances is None:
            starting_balances = {}
        return Book(chart=self.qualify(), starting_balances=starting_balances)

    def ledger(self):
        """Create empty ledger based on this chart."""
        from abacus.ledger import Ledger

        return Ledger(
            (account_name, cls()) for account_name, cls in self.yield_accounts()
        )


print(
    BaseChart(
        assets=["cash", "goods", "ppe"],
        equity=["equity", "re"],
        income=["sales"],
        expenses=["cogs", "sga"],
    )
    .set_retained_earnings("re")
    .offset("ppe", ["depreciation"])
    # https://stripe.com/docs/revenue-recognition/methodology
    .offset("sales", ["refunds", "voids"]).ledger()
    == {
        "cash": Asset(debits=[], credits=[]),
        "goods": Asset(debits=[], credits=[]),
        "ppe": Asset(debits=[], credits=[]),
        "cogs": Expense(debits=[], credits=[]),
        "sga": Expense(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "sales": Income(debits=[], credits=[]),
        "re": RetainedEarnings(debits=[], credits=[]),
        "_profit": IncomeSummaryAccount(debits=[], credits=[]),
        "depreciation": ContraAsset(debits=[], credits=[]),
        "refunds": ContraIncome(debits=[], credits=[]),
        "voids": ContraIncome(debits=[], credits=[]),
    }
)
