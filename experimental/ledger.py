"""Ledger data structure, can be created from chart, used to post entries and produce reports."""
from collections import UserDict
from typing import Dict, Iterable, List, Tuple, Type

from abacus.engine.accounts import (
    CreditAccount,
    DebitAccount,
    TAccount,
    ContraIncome,
    ContraExpense,
    ContraAsset,
    ContraLiability,
    ContraCapital,
    Income,
    Expense
)
from abacus.engine.base import AbacusError, AccountName, Amount, Entry, MultipleEntry
from abacus.engine.better_chart import Chart


def apply_to_keys(ledger, f):
    return LedgerBase({name: f(taccount) for name, taccount in ledger.items()})


class LedgerBase(UserDict[AccountName, TAccount]):
    pass

    def post(self, debit, credit, amount) -> None:
        return self.post_many([Entry(debit, credit, amount)])

    def post_many(self, entries: Iterable[Entry]):
        failed = []
        for entry in entries:
            try:
                self[entry.debit].debit(entry.amount)
                self[entry.credit].credit(entry.amount)
            except KeyError:
                failed.append(entry)
        if failed:
            raise AbacusError(failed)
        return self

    def condense(self):
        return apply_to_keys(self, lambda taccount: taccount.condense())

    def balances(self):
        return apply_to_keys(self, lambda taccount: taccount.balance())

    def nonzero_balances(self):
        return {k: v for k, v in self.balances().items() if v != 0}

    def close_some(self, chart):
        c1 = closing_contra_entries(chart, self, ContraIncome)
        c2 = closing_contra_entries(chart, self, ContraExpense)
        return self.condense().post_many(c1).post_many(c2)

    def close_most(self, chart):
        dummy_ledger = self.close_some(chart)
        # close income and expense to isa
        a = closing_entries(chart, dummy_ledger, Income)
        b = closing_entries(chart, dummy_ledger, Expense)
        dummy_ledger.post_many(a).post_many(b)
        # close to retained earnings
        return dummy_ledger.post(debit=chart.base.income_summary_account, credit=chart.base.retained_earnings_account, amount=dummy_ledger[chart.base.income_summary_account].balance())

    def close_final(self, chart):   
        c3 = closing_contra_entries(chart, self, ContraAsset)
        c4 = closing_contra_entries(chart, self, ContraLiability)
        c5 = closing_contra_entries(chart, self, ContraCapital)
        return self.post_many(c3).post_many(c4).post_many(c5)

def closing_entries(chart, ledger, cls):
    for name, account in ledger.items():
        if isinstance(account, cls):
            yield account.transfer(name, chart.base.income_summary_account)


def closing_contra_entries(chart, ledger, contra_cls):
    for name, contra_name in chart.base.contra_pairs(contra_cls):
        yield ledger[contra_name].transfer(contra_name, name)  # type: ignore


from composer import Chart

chart0 = Chart().add("asset:cash").add("capital:equity").add("contra:equity:ts")
assert chart0.base.ledger(LedgerBase).post("cash", "equity", 1000).post(
    "ts", "cash", 200
).nonzero_balances() == {"cash": 800, "equity": 1000, "ts": 200}
assert chart0.base.ledger(LedgerBase).post_many(
    [Entry("cash", "equity", 1000), Entry("ts", "cash", 200)]
).nonzero_balances() == {"cash": 800, "equity": 1000, "ts": 200}


chart2 = (
    Chart()
    .add("asset:cash")
    .add("asset:goods")
    .add("capital:equity")
    .add("contra:equity:ts")
    .add("income:sales")
    .add("expense:cogs")
    .offset("sales", "refunds")
)
ledger2 = (
    chart2.base.ledger(LedgerBase)
    .post("cash", "equity", 1000)
    .post("goods", "cash", 300)
    .post("cash", "sales", 250)
    .post("refunds", "cash", 50)
    .post("cogs", "goods", 170)
    .post("ts", "cash", 500)
)
assert ledger2.close_most(chart2).close_final(chart2).nonzero_balances() == {'cash': 400, 'goods': 130, 'equity': 500, 'retained_earnings': 30}


class Ledger(UserDict[AccountName, TAccount]):
    """General ledger that holds all accounts. Accounts are referenced by name."""

    def apply(self, attribute: str):
        """Apply an *attribute* to all accounts in ledger and return a new ledger."""
        return Ledger(
            {
                account_name: getattr(taccount, attribute)()
                for account_name, taccount in self.items()
            }
        )

    def deep_copy(self) -> "Ledger":
        """Return a copy of the ledger, taking care of copying
        debit and credit lists in accounts."""
        return self.apply("deep_copy")

    def condense(self) -> "Ledger":
        """Purge data from ledger leaving only account balances.
        Creates a copy of ledger."""
        return self.apply("condense")

    def empty(self) -> "Ledger":
        """Purge data from ledger. Creates a copy of ledger."""
        return self.apply("empty")

    def make_multiple_entry(self, starting_balances: dict) -> MultipleEntry:
        """Make a multiple entry from starting balances."""
        return to_multiple_entry(self, starting_balances)

    def balances(self) -> Dict[AccountName, Amount]:
        """Return account balances."""
        return dict(self.apply("balance").data)

    def nonzero_balances(self) -> Dict[AccountName, Amount]:
        """Return nonzero account balances."""
        return {k: v for k, v in self.balances().items() if v != 0}

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

    def post(self, entry: Entry) -> "Ledger":
        # Note that post() mutates the existing data structure
        post_entry(self, entry)
        return self

    def post_many(self, entries: Iterable[Entry]) -> "Ledger":
        post_entries(self, entries)
        return self

    def closing_entries_for_income_statement(self, chart: Chart):
        from abacus.engine.closing import close_contra_expense as ce
        from abacus.engine.closing import close_contra_income as ci

        return ci(chart, self) + ce(chart, self)

    def close_some(self, chart: Chart) -> "Ledger":
        """Close contra accounts corresponding to income and expense.
        Returns a copy of a ledger.
        """
        closing_entries = self.closing_entries_for_income_statement(chart)
        return self.condense().post_many(closing_entries)

    def income_statement(self, chart: Chart, post_close_entries=None):
        from abacus.engine.report import IncomeStatement

        if post_close_entries is None:
            post_close_entries = []
        ledger = self.condense().close_some(chart).post_many(post_close_entries)
        return IncomeStatement.new(ledger)

    def closing_entries_for_balance_sheet(self, chart: Chart):
        from abacus.engine.closing import flush_permanent_accounts, make_closing_entries

        closing_entries_struct = make_closing_entries(chart, self)
        return closing_entries_struct.all() + flush_permanent_accounts(chart, self)

    def closing_entries(self, chart):
        return self.closing_entries_for_balance_sheet(chart)

    def close(self, chart: Chart) -> "Ledger":
        """Close all accounts related to retained earnings and to permanent accounts.
        Returns a copy of a ledger.
        """
        closing_entries = self.closing_entries_for_balance_sheet(chart)
        return self.condense().post_many(closing_entries)

    def balance_sheet(self, chart: Chart, post_close_entries=None):
        from abacus.engine.report import BalanceSheet

        if post_close_entries is None:
            post_close_entries = []
        ledger = self.close(chart).post_many(post_close_entries)
        return BalanceSheet.new(ledger)

    def trial_balance(self, chart: Chart):
        from abacus.engine.report import view_trial_balance

        return view_trial_balance(chart, self)


def post_entry(ledger: Ledger, entry: Entry) -> None:
    ledger[entry.debit].debit(entry.amount)
    ledger[entry.credit].credit(entry.amount)


def post_entries(ledger: Ledger, entries: Iterable[Entry]):
    ledger, failed_entries = unsafe_post_entries(ledger, entries)
    if failed_entries:
        raise AbacusError(failed_entries)


def unsafe_post_entries(
    ledger: Ledger, entries: Iterable[Entry]
) -> Tuple[Ledger, Iterable[Entry]]:
    failed = []
    for entry in entries:
        try:
            post_entry(ledger, entry)
        except KeyError:
            failed.append(entry)
    return ledger, failed


def to_multiple_entry(ledger: Ledger, starting_balances: dict) -> MultipleEntry:
    debit_entries = []
    credit_entries = []
    for account_name in starting_balances.keys():
        try:
            ledger[account_name]
        except KeyError:
            raise AbacusError(f"Account {account_name} does not exist in ledger.")
    for account_name, amount in starting_balances.items():
        match ledger[account_name]:
            case DebitAccount(_, _):
                debit_entries.append((account_name, amount))
            case CreditAccount(_, _):
                credit_entries.append((account_name, amount))
    return MultipleEntry(debit_entries, credit_entries).validate()
