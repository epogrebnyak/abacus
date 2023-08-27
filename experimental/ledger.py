"""Ledger data structure, can be created from chart, used to post entries and produce reports."""
from collections import UserDict
from typing import Dict, List, Type

from engine import (
    AccountName,
    Amount,
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
    """General ledger that holds all accounts. Accounts are referenced by name.
    (No wonder - this is a dictionary.)"""

    @classmethod
    def new(cls, chart: Chart) -> "Ledger":
        """Create an empty ledger from chart."""
        return make_ledger(chart)

    def deep_copy(self) -> "Ledger":
        """Return a copy of the ledger, taking care of copying the debit and credit lists in accounts."""
        return Ledger(
            {
                account_name: taccount.deep_copy()
                for account_name, taccount in self.items()
            }
        )

    def condense(self) -> "Ledger":
        """Purge data from ledger leaving only account balances.
        Creates a copy of ledger."""
        return Ledger(
            {
                account_name: taccount.condense()
                for account_name, taccount in self.items()
            }
        )

    def balances(self) -> Dict[AccountName, Amount]:
        """Return account balances."""
        return {
            account_name: t_account.balance()
            for account_name, t_account in self.items()
        }

    def subset(self, classes: Type | List[Type]) -> "Ledger":
        """Filter ledger by account type."""
        if not isinstance(classes, list):
            classes = [classes]

        def belongs(t_account: TAccount):
            return any(isinstance(t_account, cls) for cls in classes)

        return Ledger(
            [
                (account_name, t_account)
                for account_name, t_account in self.items()
                if belongs(t_account)
            ]
        )

    def post(self, entries: Entry | List[Entry]) -> "Ledger":
        # Note that post() mutates the existing data structure
        if isinstance(entries, list):
            post_entries(self, entries)
        elif isinstance(entries, Entry):
            post_entry(self, entries)
        else:
            raise TypeError(entries)
        return self

    def close_some(self, chart: Chart) -> "Ledger":
        """Close contra accounts corresponding to income and expense.
        Returns a copy of a ledger."""
        from closing import close_contra_expense as ce
        from closing import close_contra_income as ci

        closing_entries = ci(chart, self) + ce(chart, self)
        return self.condense().post(closing_entries)

    def income_statement(self, chart: Chart, post_close_entries=None):
        from report import IncomeStatement

        if post_close_entries is None:
            post_close_entries = []
        ledger = self.close_some(chart).post(post_close_entries)
        return IncomeStatement.new(ledger)

    def close(self, chart: Chart) -> "Ledger":
        """Close all accounts related to retained earnings and to permanent accounts.
        Returns a copy of a ledger."""
        from closing import flush_permanent_accounts, make_closing_entries

        closing_entries = make_closing_entries(
            chart, self
        ).all() + flush_permanent_accounts(chart, self)
        return self.condense().post(closing_entries)

    def balance_sheet(self, chart: Chart, post_close_entries=None):
        from report import BalanceSheet

        if post_close_entries is None:
            post_close_entries = []
        ledger = self.close(chart).post(post_close_entries)
        return BalanceSheet.new(ledger)


def make_ledger(chart: Chart) -> Ledger:
    """Create empty ledger from chart."""
    ledger = Ledger()
    for attribute, (Class, ContraClass) in chart.mapping():
        for account_name in getattr(chart, attribute):
            # create regular accounts
            ledger[account_name] = Class()
            try:
                # create contra accounts if found
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


if __name__ == "__main__":
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
        .subset(
            [Asset, ContraIncome]
        )  # arbitrary subset of account types, no real usecase
        .deep_copy()
        .condense()
    )
    assert res.balances() == {"cash": 1000, "ar": 200, "refunds": 50}

    assert make_ledger(Chart(assets=["cash"], equity=["equity"])) == {
        "cash": Asset(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "re": RetainedEarnings(debits=[], credits=[]),
        "current_profit": IncomeSummaryAccount(debits=[], credits=[]),
    }

    ledger1 = make_ledger(Chart(assets=["cash"], equity=["equity"]))
    post_entry(ledger1, Entry(debit="cash", credit="equity", amount=799))
    post_entry(ledger1, Entry(debit="cash", credit="equity", amount=201))
    assert ledger1["cash"].debits == ledger1["equity"].credits == [799, 201]
    assert ledger1["cash"].balance() == ledger1["equity"].balance() == 1000

    # condense() also makes a copy, similar to deep_copy()
    ledger2 = ledger1.condense()
    post_entry(ledger2, Entry(debit="cash", credit="equity", amount=-1000))
    # ledger1 not affected
    assert ledger1["cash"].balance() == ledger1["equity"].balance() == 1000
    # ledger2 not changed
    assert ledger2["cash"].balance() == ledger2["equity"].balance() == 0

    ledger_ = Ledger.new(_chart).post(
        [
            Entry("cash", "equity", 1000),
            Entry("ar", "sales", 250),
            Entry("refunds", "ar", 50),
        ]
    )

    assert ledger_.balance_sheet(_chart).dict() == {
        "assets": {"cash": 1000, "ar": 200},
        "capital": {"equity": 1000, "re": 200},
        "liabilities": {},
    }
    assert ledger_.income_statement(_chart).dict() == {
        "income": {"sales": 200},
        "expenses": {},
    }
