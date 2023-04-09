# pylint: disable=missing-docstring

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

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


def make_ledger(chart):
    accounts = {}
    for account_name in chart.debit_account_names:
        accounts[account_name] = DebitAccount()
    for account_name in chart.credit_account_names:
        accounts[account_name] = CreditAccount()
    return accounts


def account_names(chart):
    return chart.debit_account_names + chart.credit_account_names


def balances(ledger):
    return {account_name: balance(account) for account_name, account in ledger.items()}


@dataclass
class Balances:
    assets: Dict[AccountName, Amount]
    expenses: Dict[AccountName, Amount]
    equity: Dict[AccountName, Amount]
    liabilities: Dict[AccountName, Amount]
    income: Dict[AccountName, Amount]


@dataclass
class RawEntry:
    dr: AccountName
    cr: AccountName
    amount: Amount


def process_raw_entry(ledger: Ledger, entry: RawEntry):
    ledger[entry.dr].debit(entry.amount)
    ledger[entry.cr].credit(entry.amount)
    return ledger


NamedEntry = Tuple[str, Amount]


@dataclass
class BalanceSheet:
    assets: Dict[AccountName, Amount]
    capital: Dict[AccountName, Amount]
    liabilities: Dict[AccountName, Amount]

    @property
    def total_assets(self):
        return dict_sum(self.assets)

    @property
    def total_capital(self):
        return dict_sum(self.capital)

    @property
    def total_liabilities(self):
        return dict_sum(self.liabilities)

    def is_valid(self):
        return self.total_assets == self.total_capital + self.total_liabilities


@dataclass
class Book:
    chart: Chart
    shortcode_dict: Dict[str, Tuple[AccountName, AccountName]] = field(
        default_factory=dict
    )
    raw_entries: List[RawEntry] = field(default_factory=list)
    start_ledger: Optional[Ledger] = None

    def validate_raw_entry(self, entry: RawEntry):
        for name in (entry.dr, entry.cr):
            if name not in account_names(self.chart):
                raise ValueError(name + " is not a valid account name.")

    def append_raw_entry(self, e: RawEntry):
        self.validate_raw_entry(e)
        self.raw_entries.append(e)
        return self

    def to_raw_entry(self, named_entry: NamedEntry):
        dr, cr = self.shortcode_dict[named_entry[0]]
        return RawEntry(dr, cr, named_entry[1])

    def append_named_entry(self, named_entry: NamedEntry):
        entry = self.to_raw_entry(named_entry)
        self.append_raw_entry(entry)
        return self

    def append_named_entries(self, named_entries):
        for named_entry in named_entries:
            self.append_named_entry(named_entry)
        return self

    def get_ledger(self) -> Ledger:
        ledger = self.start_ledger if self.start_ledger else make_ledger(self.chart)
        for entry in self.raw_entries:
            ledger = process_raw_entry(ledger, entry)
        return ledger

    def get_balance_sheet(self) -> BalanceSheet:
        balances_dict = balances(self.get_ledger())
        return to_balance_sheet(balances_dict, self.chart)


def subset(balances_, keys):
    return {k: v for k, v in balances_.items() if k in keys}


def assets(balances_, chart):
    return subset(balances_, chart.assets)


def capital(balances_dict, chart):
    res = subset(balances_dict, chart.equity)
    res["current_profit"] = current_profit(balances_dict, chart)
    return res


def liabilties(balances_dict, chart):
    return subset(balances_dict, chart.liabilities)


def income(balances_dict, chart):
    return subset(balances_dict, chart.income)


def expenses(balances_dict, chart):
    return subset(balances_dict, chart.expenses)


def current_profit(balances_dict, chart):
    return dict_sum(income(balances_dict, chart)) - dict_sum(
        expenses(balances_dict, chart)
    )


def dict_sum(dict_):
    return sum(dict_.values())


def to_balance_sheet(balances_dict, chart):
    return BalanceSheet(
        assets=assets(balances_dict, chart),
        capital=capital(balances_dict, chart),
        liabilities=liabilties(balances_dict, chart),
    )
