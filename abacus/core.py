# %%
"""
Chart -> Ledger -> [RawEntry] -> Ledger, [RawEntry] -> [RawEntry] -> (BalanceSheet, IncomeStatement)  
"""

# pylint: disable=no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from collections import UserDict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Bool

Amount = int
AccountName = str


@dataclass
class RawEntry:
    dr: AccountName
    cr: AccountName
    amount: Amount


class AccountBalanceDict(UserDict[AccountName, Amount]):
    """Dictionary with account names and balances like {'cash': 100}."""

    def total(self) -> Amount:
        return sum(self.values())

    def subset(self, account_names: List[AccountName]):  # -> AccountBalanceDict
        return AccountBalanceDict(
            (account_name, balance)
            for account_name, balance in self.items()
            if account_name in account_names
        )


TrialBalance = AccountBalanceDict


@dataclass
class Account:
    debits: List[Amount] = field(default_factory=list)
    credits: List[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        self.debits.append(amount)

    def credit(self, amount: Amount):
        self.credits.append(amount)

    def copy(self):
        return self.__class__(self.debits.copy(), self.credits.copy())


class DebitAccount(Account):
    pass


class Asset(DebitAccount):
    pass


class Expense(DebitAccount):
    pass


class CreditAccount(Account):
    pass


class Capital(CreditAccount):
    pass


class Liability(CreditAccount):
    pass


class Income(CreditAccount):
    pass


class IncomeSummaryAccount(CreditAccount):
    pass


def balance(account: Account) -> Amount:
    match account:
        case DebitAccount(ds, cs):
            return sum(ds) - sum(cs)
        case CreditAccount(ds, cs):
            return sum(cs) - sum(ds)


@dataclass
class Chart:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    equity: List[str]
    liabilities: List[str]
    income: List[str]
    contraccounts: List[str] = field(default_factory=list)
    income_summary_account: str = "profit"

    @property
    def debit_account_names(self) -> List[AccountName]:
        return self.assets + self.expenses

    @property
    def credit_account_names(self) -> List[AccountName]:
        return (
            self.equity
            + self.liabilities
            + self.income
            + self.contraccounts
            + [self.income_summary_account]
        )


def account_names(chart: Chart) -> List[AccountName]:
    return chart.debit_account_names + chart.credit_account_names


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts."""

    def trial_balance(self):
        return TrialBalance(
            (account_name, balance(account)) for account_name, account in self.items()
        )

    def income_statement(self, chart):
        tb = self.trial_balance()
        return IncomeStatement(
            income=tb.subset(chart.income),
            expenses=tb.subset(chart.expenses),
        )

    def balance_sheet(self, chart):
        tb = self.trial_balance()
        return BalanceSheet(
            assets=tb.subset(chart.assets),
            capital=tb.subset(chart.equity),
            liabilities=tb.subset(chart.liabilities),
        )

    def close_entries(self, chart: Chart, retained_earnings_account_name: str):
        return close_entries(self, chart, retained_earnings_account_name)

    def copy(self):
        return Ledger((k, v.copy()) for k, v in self.items())

    def process(self, raw_entries: List[RawEntry]):
        return process_raw_entries(self, raw_entries)

    # TODO: move to Book class
    def accrue_dividend(
        self, amount, retained_earnings_account_name, dividend_payable_account_name
    ):
        entry = RawEntry(
            amount=amount,
            dr=retained_earnings_account_name,
            cr=dividend_payable_account_name,
        )
        return process_raw_entry(self, entry)

    # TODO: move to Book class
    def disburse_dividend(self, dividend_payable_account_name, cash_account_name):
        amount = balance(self[dividend_payable_account_name])
        entry = RawEntry(
            amount=amount, dr=dividend_payable_account_name, cr=cash_account_name
        )
        return process_raw_entry(self, entry)


def make_ledger(chart: Chart) -> Ledger:
    accounts = {}
    for account_name in chart.debit_account_names:
        accounts[account_name] = DebitAccount()
    for account_name in chart.credit_account_names:
        accounts[account_name] = CreditAccount()
    return Ledger(accounts)


def closing_entries_income_accounts(ledger, chart) -> List[RawEntry]:
    return [
        RawEntry(
            amount=balance(ledger[account_name]),
            dr=account_name,
            cr=chart.income_summary_account,
        )
        for account_name in chart.income
    ]


def closing_entries_expense_accounts(ledger, chart) -> List[RawEntry]:
    return [
        RawEntry(
            amount=balance(ledger[account_name]),
            cr=account_name,
            dr=chart.income_summary_account,
        )
        for account_name in chart.expenses
    ]


def closing_entries_to_retained_earnings(
    ledger, chart, retained_earnings_account_name
) -> List[RawEntry]:
    entries = closing_entries_income_accounts(
        ledger, chart
    ) + closing_entries_expense_accounts(ledger, chart)
    dummy_ledger = process_raw_entries(ledger, entries)
    amount = balance(dummy_ledger[chart.income_summary_account])
    return [
        RawEntry(
            amount=amount,
            cr=retained_earnings_account_name,
            dr=chart.income_summary_account,
        )
    ]


def closing_entries(ledger, chart, retained_earnings_account_name):
    return (
        closing_entries_income_accounts(ledger, chart)
        + closing_entries_expense_accounts(ledger, chart)
        + closing_entries_to_retained_earnings(
            ledger, chart, retained_earnings_account_name
        )
    )


def close_entries(ledger, chart, retained_earnings_account_name):
    entries = closing_entries(ledger, chart, retained_earnings_account_name)
    return process_raw_entries(ledger, entries)


def process_raw_entry(ledger: Ledger, entry: RawEntry) -> Ledger:
    _ledger = ledger.copy()
    _ledger[entry.dr].debit(entry.amount)
    _ledger[entry.cr].credit(entry.amount)
    return _ledger


def process_raw_entries(ledger, entries: List[RawEntry]) -> Ledger:
    _ledger = ledger.copy()
    failed = []
    for entry in entries:
        try:
            _ledger[entry.dr].debit(entry.amount)
            _ledger[entry.cr].credit(entry.amount)
        except KeyError:
            failed.append(entry)
    if failed:
        raise KeyError("Following entries could not be processed:" + str(failed))
    return _ledger


@dataclass
class BalanceSheet:
    assets: AccountBalanceDict
    capital: AccountBalanceDict
    liabilities: AccountBalanceDict

    def is_valid(self):
        return self.assets.total() == self.capital.total() + self.liabilities.total()


@dataclass
class IncomeStatement:
    income: AccountBalanceDict
    expenses: AccountBalanceDict

    def current_profit(self):
        return self.income.total() - self.expenses.total()


Pair = Tuple[AccountName, AccountName]
EntryShortcodeDict = Dict[str, Pair]
NamedEntry = Tuple[str, Amount]


class EntryShortcodes(UserDict[str, Tuple[AccountName, AccountName]]):
    def to_raw_entry(self, named_entry: NamedEntry) -> RawEntry:
        dr, cr = self[named_entry[0]]
        return RawEntry(dr, cr, named_entry[1])


@dataclass
class EntryFactory:
    retained_earnings: str = "re"
    dividend_payable: str = "divp"
    cash: str = "cash"

    def is_compatible(self, chart: Chart) -> Bool:
        return False

    def accrue_dividend(self, amount):
        return RawEntry(self.retained_earnings, self.dividend_payable, amount)

    def disburse_dividend(self, amount):
        return RawEntry(self.dividend_payable, self.cash, amount)


# TODO: split to naming part and data part
# book.is_compatible(ledger)


@dataclass
class Accountant:
    chart: Chart
    namer: EntryFactory
    shortcodes: EntryShortcodes = field(default_factory=EntryShortcodes)


@dataclass
class Book:
    chart: Chart
    entry_shortcodes: EntryShortcodes = field(default_factory=EntryShortcodes)
    raw_entries: List[RawEntry] = field(default_factory=list)

    def validate_raw_entry(self, entry: RawEntry):
        for name in (entry.dr, entry.cr):
            if name not in account_names(self.chart):
                raise ValueError(name + " is not a valid account name.")

    def append_raw_entry(self, entry: RawEntry):
        self.validate_raw_entry(entry)
        self.raw_entries.append(entry)
        return self

    def append_raw_entries(self, entries: List[RawEntry]):
        for entry in entries:
            self.append_raw_entry(entry)
        return self

    def append_named_entry(self, named_entry: NamedEntry):
        entry = self.entry_shortcodes.to_raw_entry(named_entry)
        self.append_raw_entry(entry)
        return self

    def append_named_entries(self, named_entries):
        for named_entry in named_entries:
            self.append_named_entry(named_entry)
        return self

    def get_ledger(self) -> Ledger:
        return make_ledger(self.chart).process(self.raw_entries)

    def get_trial_balance(self) -> TrialBalance:
        return self.get_ledger().trial_balance()

    def get_balance_sheet(self) -> BalanceSheet:
        return self.get_ledger().balance_sheet(self.chart)


def make_balance_sheet(ledger, chart):
    tb = ledger.trial_balance()
    return BalanceSheet(
        assets=tb.subset(chart.assets),
        capital=tb.subset(chart.equity),
        liabilities=tb.subset(chart.liabilities),
    )


def current_profit(ledger, chart):
    return make_income_statement(ledger, chart).current_profit()


def _make_interim_balance_sheet(ledger, chart):
    tb = ledger.trial_balance()
    cap = tb.subset(chart.equity)
    cap["current_profit"] = current_profit(ledger, chart)
    return BalanceSheet(
        assets=tb.subset(chart.assets),
        capital=cap,
        liabilities=tb.subset(chart.liabilities),
    )


def make_income_statement(balances_dict, chart):
    return IncomeStatement(
        income=balances_dict.subset(chart.income),
        expenses=balances_dict.subset(chart.expenses),
    )
