from typing import Tuple, List, Dict
from dataclasses import dataclass, field

Amount = int
Account = Tuple[List[Amount], List[Amount]]
AccountName = str
Legder = Dict[AccountName, Account]

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
            return sum(ds)-sum(cs)
        case CreditAccount(ds, cs):
            return sum(cs)-sum(ds)


@dataclass
class Chart:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    equity: List[str]
    liabilities: List[str]
    income: List[str]
    contraccounts: List[str]

    @property
    def debit_account_names(self) -> List[str]:
        return self.assets + self.expenses

    @property
    def credit_account_names(self) -> List[str]:
        return self.equity + self.liabilities + self.income + self.contraccounts



def account() -> Account:
    return ([], [])


def make_ledger(chart):
    accounts = {}
    for account_name in chart.debit_account_names:
        accounts[account_name] = DebitAccount()
    for account_name in chart.credit_account_names:
        accounts[account_name] = CreditAccount()
    return accounts

def process_entry(ledger, entry):
    ledger[entry.dr].debit(entry.amount)
    ledger[entry.cr].credit(entry.amount)
    return ledger

def process_entries(ledger, entries):
    for entry in entries:
        ledger = process_entry(ledger, entry)
    return ledger    


@dataclass
class Pair:
    dr: AccountName
    cr: AccountName

@dataclass
class EntryP:
    amount: Amount
    pair: Pair

@dataclass
class Entry:
    dr: AccountName
    cr: AccountName
    amount: Amount

def process_named_entries(ledger, named_entries_dict, named_entries_stream):
    for (operation, amount) in named_entries_stream:
        entry = Entry(*named_entries_dict[operation], amount)
        ledger=process_entry(ledger, entry)
    return ledger

def account_names(chart):
    return chart.debit_account_names + chart.credit_account_names

def balances(ledger):
    return {account_name:balance(account) for account_name, account in ledger.items()}

def sum_of_balances(ledger, account_names):
    return sum(balance(ledger[account_name]) for account_name in account_names)


def income(ledger, chart):
    return sum_of_balances(ledger, chart.income)


def expenses(ledger, chart):
    return sum_of_balances(ledger, chart.expenses)


def current_profit(ledger, chart):
    return income(ledger, chart) - expenses(ledger, chart)
