from collections import UserDict
from typing import Dict, List, Type

from engine import (
    AccountName,
    Asset,
    Capital,
    Chart,
    ContraIncome,
    Entry,
    IncomeSummaryAccount,
    RetainedEarnings,
    TAccount,
)


class Ledger(UserDict[AccountName, TAccount]):
    """General ledger that holds all accounts where accounts can be referenced by name."""

    @classmethod
    def new(cls, chart: Chart) -> "Ledger":
        return make_ledger(chart)

    def deep_copy(self) -> "Ledger":
        return Ledger(
            {
                account_name: taccount.deep_copy()
                for account_name, taccount in self.items()
            }
        )

    def condense(self) -> "Ledger":
        return Ledger(
            {
                account_name: taccount.condense()
                for account_name, taccount in self.items()
            }
        )

    def balances(self) -> Dict:
        return balances(self)

    def subset(self, classes) -> "Ledger":
        return subset(self, classes)

    def post(self, entries: Entry | List[Entry]) -> "Ledger":
        if isinstance(entries, list):
            post_entries(self, entries)
        elif isinstance(entries, Entry):
            post_entry(self, entries)
        else:
            raise TypeError(entries)
        return self


def balances(ledger: Ledger):
    return {
        account_name: t_account.balance() for account_name, t_account in ledger.items()
    }


def subset(ledger: Ledger, classes: Type | List[Type]) -> Ledger:
    if not isinstance(classes, list):
        classes = [classes]

    def isin(t_account: TAccount, classes: List[Type]):
        return any(isinstance(t_account, cls) for cls in classes)

    return Ledger(
        [
            (account_name, t_account)
            for account_name, t_account in ledger.items()
            if isin(t_account, classes)
        ]
    )


def make_ledger(chart: Chart) -> Ledger:
    ledger = Ledger()
    for attribute, (Class, ContraClass) in chart.mapping():
        for account_name in getattr(chart, attribute):
            # create regular accounts
            ledger[account_name] = Class()
            try:
                # create contra accounts (if found)
                for contra_account_name in chart.contra_accounts[account_name]:
                    ledger[contra_account_name] = ContraClass()
            except KeyError:
                pass
    ledger[chart.retained_earnings_account] = RetainedEarnings()
    ledger[chart.income_summary_account] = IncomeSummaryAccount()
    return ledger


def post_entry(ledger: Ledger, entry: Entry) -> None:
    ledger[entry.debit].debit(entry.amount)
    ledger[entry.credit].credit(entry.amount)


def post_entries(ledger: Ledger, entries: List[Entry]):
    for entry in entries:
        post_entry(ledger, entry)


_chart = Chart(
    assets=["cash", "ar"],
    equity=["equity"],
    income=["sales"],
    expenses=[],
    contra_accounts={"sales": ["refunds"]},
)

res = (
    Ledger.new(_chart)
    .post(
        [
            Entry("cash", "equity", 1000),
            Entry("ar", "sales", 250),
            Entry("refunds", "ar", 50),
        ]
    )
    .subset([Asset, ContraIncome])
    .deep_copy()
    .condense()
    .balances()
)
assert res == {'cash': 1000, 'ar': 200, 'refunds': 50}

assert make_ledger(Chart(assets=["cash"], equity=["equity"])) == {
    "cash": Asset(debits=[], credits=[]),
    "equity": Capital(debits=[], credits=[]),
    "re": RetainedEarnings(debits=[], credits=[]),
    "current_profit": IncomeSummaryAccount(debits=[], credits=[]),
}
