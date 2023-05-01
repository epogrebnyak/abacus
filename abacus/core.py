"""
Chart -> Ledger -> [RawEntry] -> Ledger -> Amount -> Ledger -> (BalanceSheet, IncomeStatement)  
"""

# pylint: disable=missing-docstring, pointless-string-statement

from collections import UserDict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

Amount = int
AccountName = str


class AccountBalanceDict(UserDict[AccountName, Amount]):
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


class DebitAccount(Account):
    pass


class CreditAccount(Account):
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
        return AccountBalanceDict(
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
        inc_st = self.income_statement(chart)
        ledger = close_entries(self, chart, retained_earnings_account_name)
        return (inc_st, ledger)
    
    def accrue_dividend(self, amount, retained_earnings_account_name, dividend_payable_account_name):
        entry = RawEntry(amount=amount, dr=retained_earnings_account_name, cr=dividend_payable_account_name)
        return process_raw_entry(self, entry)

    def disburse_dividend(self, dividend_payable_account_name, cash_account_name):
        amount = balance(self[dividend_payable_account_name])
        entry = RawEntry(amount=amount, dr=dividend_payable_account_name, cr=cash_account_name)
        return process_raw_entry(self, entry)



def make_ledger(chart: Chart) -> Ledger:
    accounts = {}
    for account_name in chart.debit_account_names:
        accounts[account_name] = DebitAccount()
    for account_name in chart.credit_account_names:
        accounts[account_name] = CreditAccount()
    return Ledger(accounts)


def closing_entries_income_accounts(ledger, chart):
    return [
        RawEntry(
            amount=balance(ledger[account_name]),
            dr=account_name,
            cr=chart.income_summary_account,
        )
        for account_name in chart.income
    ]


def closing_entries_expense_accounts(ledger, chart):
    return [
        RawEntry(
            amount=balance(ledger[account_name]),
            cr=account_name,
            dr=chart.income_summary_account,
        )
        for account_name in chart.expenses
    ]


def close_entries(ledger, chart, retained_earnings_account_name):
    entries = closing_entries_income_accounts(ledger, chart)
    ledger = process_raw_entries(ledger, entries)
    entries = closing_entries_expense_accounts(ledger, chart)
    ledger = process_raw_entries(ledger, entries)
    entry = RawEntry(
        amount=balance(ledger[chart.income_summary_account]),
        cr=retained_earnings_account_name,
        dr=chart.income_summary_account,
    )
    return process_raw_entry(ledger, entry)


def balances(ledger: Ledger) -> AccountBalanceDict:
    return AccountBalanceDict(
        (account_name, balance(account)) for account_name, account in ledger.items()
    )


@dataclass
class Balances:
    assets: AccountBalanceDict
    expenses: AccountBalanceDict
    equity: AccountBalanceDict
    liabilities: AccountBalanceDict
    income: AccountBalanceDict


@dataclass
class RawEntry:
    dr: AccountName
    cr: AccountName
    amount: Amount


def process_raw_entry(ledger: Ledger, entry: RawEntry) -> Ledger:
    ledger[entry.dr].debit(entry.amount)
    ledger[entry.cr].credit(entry.amount)
    return ledger


def process_raw_entries(ledger, entries: List[RawEntry]) -> Ledger:
    for entry in entries:
        ledger = process_raw_entry(ledger, entry)
    return ledger


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


class EntryShortcodes(UserDict):
    def to_raw_entry(self, named_entry: NamedEntry) -> RawEntry:
        dr, cr = self[named_entry[0]]
        return RawEntry(dr, cr, named_entry[1])


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
        ledger = make_ledger(self.chart)
        return process_raw_entries(ledger, self.raw_entries)

    def get_balances(self):
        return balances(self.get_ledger())

    def get_balance_sheet(self) -> BalanceSheet:
        return make_balance_sheet(self.get_balances(), self.chart)


def capital(balances_dict, chart):
    res = balances_dict.subset(chart.equity)
    res["current_profit"] = make_income_statement(balances_dict, chart).current_profit()
    return res


def make_balance_sheet(balances_dict, chart):
    return BalanceSheet(
        assets=balances_dict.subset(chart.assets),
        capital=capital(balances_dict, chart),
        liabilities=balances_dict.subset(chart.liabilities),
    )


def make_income_statement(balances_dict, chart):
    return IncomeStatement(
        income=balances_dict.subset(chart.income),
        expenses=balances_dict.subset(chart.expenses),
    )
