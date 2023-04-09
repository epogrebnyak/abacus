from dataclasses import dataclass, field
from typing import Dict, List, Tuple

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


def balance(account: Account) -> Amount:
    match account:
        case DebitAccount(ds, cs):
            return sum(ds) - sum(cs)
        case CreditAccount(ds, cs):
            return sum(cs) - sum(ds)


@dataclass
class Balances:
    assets: Dict[AccountName, Amount]
    expenses: Dict[AccountName, Amount]
    equity: Dict[AccountName, Amount]
    liabilities: Dict[AccountName, Amount]
    income: Dict[AccountName, Amount]


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


def process_raw_entry(ledger, entry):
    ledger[entry.dr].debit(entry.amount)
    ledger[entry.cr].credit(entry.amount)
    return ledger


@dataclass
class Pair:
    dr: AccountName
    cr: AccountName


@dataclass
class EntryP:
    amount: Amount
    pair: Pair


def account_names(chart):
    return chart.debit_account_names + chart.credit_account_names


def balances(ledger):
    return {account_name: balance(account) for account_name, account in ledger.items()}


@dataclass
class RawEntry:
    dr: AccountName
    cr: AccountName
    amount: Amount


@dataclass
class NamedEntry:
    name: str
    amount: Amount


@dataclass
class Book:
    chart: Chart
    shortcode_dict: Dict[str, Tuple[AccountName, AccountName]] = field(
        default_factory=dict
    )
    raw_entries: List[RawEntry] = field(default_factory=list)

    def validate_raw_entry(self, e: RawEntry):
        for name in (e.dr, e.cr):
            if name not in account_names(self.chart):
                raise ValueError(name + " is not a valid account name.")

    def append_raw_entry(self, e: RawEntry):
        self.validate_raw_entry(e)
        self.raw_entries.append(e)

    def to_raw_entry(self, named_entry: NamedEntry):
        dr, cr = self.shortcode_dict[named_entry.name]
        return RawEntry(dr, cr, named_entry.amount)

    def append_named_entry(self, named_entry: NamedEntry):
        e = self.to_raw_entry(named_entry)
        self.append_raw_entry(e)

    def append_named_entries(self, named_entries):
        for named_entry in named_entries:
            self.append_named_entry(named_entry)

    def get_ledger(self, ledger=None):
        if not ledger:
            ledger = make_ledger(self.chart)
        for e in self.raw_entries:
            ledger = process_raw_entry(ledger, e)
        return ledger


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


chart_1 = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "retained_earnings"],
    liabilities=["payables"],
    income=["sales"],
)

entry_shortcodes_1 = dict(
    pay_shareholder_capital=("cash", "equity"),
    buy_goods_for_cash=("goods_for_sale", "cash"),
    invoice_buyer=("receivables", "sales"),
    transfer_goods_sold=("cogs", "goods_for_sale"),
    accept_payment=("cash", "receivables"),
    accrue_salary=("sga", "payables"),
    pay_salary=("payables", "cash"),
)

named_entries_1 = [
    NamedEntry(name="pay_shareholder_capital", amount=501),
    NamedEntry(name="pay_shareholder_capital", amount=499),
    NamedEntry(name="buy_goods_for_cash", amount=820),
    NamedEntry(name="invoice_buyer", amount=600),
    NamedEntry(name="transfer_goods_sold", amount=360),
    NamedEntry(name="accept_payment", amount=549),
    NamedEntry(name="accrue_salary", amount=400),
    NamedEntry(name="pay_salary", amount=345),
    NamedEntry(name="invoice_buyer", amount=160),
    NamedEntry(name="transfer_goods_sold", amount=80),
    NamedEntry(name="accept_payment", amount=80),
]


book = Book(chart_1, entry_shortcodes_1)
book.append_named_entries(named_entries_1)
ledger = book.get_ledger()
balances_dict = balances(ledger)
print(named_entries_1)
print(ledger)
print(balances_dict)

assets_dict = assets(balances_dict, chart_1)
capital_dict = capital(balances_dict, chart_1)
liabilities_dict = liabilties(balances_dict, chart_1)
a = dict_sum(assets_dict)
cap = dict_sum(capital_dict)
liab = dict_sum(liabilities_dict)
print("     Assets:", a, assets_dict)
print("    Capital:", cap, capital_dict)
print("Liabilities:", liab, liabilities_dict)
assert a == cap + liab
