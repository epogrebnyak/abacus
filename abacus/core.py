# pylint: disable=missing-docstring, pointless-string-statement

from collections import UserDict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Amount = int
AccountName = str


@dataclass
class Account:
    debits: List[Amount] = field(default_factory=list)
    credits: List[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        self.debits.append(amount)

    def credit(self, amount: Amount):
        self.credits.append(amount)


Legder = Dict[AccountName, Account]


class DebitAccount(Account):
    pass


class CreditAccount(Account):
    pass


"""General ledger that holds all accounts."""
Ledger = Dict[AccountName, Account]


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

    @property
    def debit_account_names(self) -> List[AccountName]:
        return self.assets + self.expenses

    @property
    def credit_account_names(self) -> List[AccountName]:
        return self.equity + self.liabilities + self.income + self.contraccounts


def make_ledger(chart: Chart) -> Ledger:
    accounts = {}
    for account_name in chart.debit_account_names:
        accounts[account_name] = DebitAccount()
    for account_name in chart.credit_account_names:
        accounts[account_name] = CreditAccount()
    return accounts


def account_names(chart: Chart) -> List[AccountName]:
    return chart.debit_account_names + chart.credit_account_names


class AccountBalanceDict(UserDict):
    def total(self):
        return sum(self.values())

    def subset(self, account_names: List[AccountName]):
        items = (
            (account_name, balance)
            for account_name, balance in self.items()
            if account_name in account_names
        )
        return AccountBalanceDict(items)


def balances(ledger: Ledger) -> AccountBalanceDict:
    items = (
        (account_name, balance(account)) for account_name, account in ledger.items()
    )
    return AccountBalanceDict(items)


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


def process_raw_entry(ledger: Ledger, entry: RawEntry):
    ledger[entry.dr].debit(entry.amount)
    ledger[entry.cr].credit(entry.amount)
    return ledger


def process_raw_entries(ledger, entries: List[RawEntry]):
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
