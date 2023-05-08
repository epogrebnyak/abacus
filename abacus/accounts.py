"""T-account classes:

1. "regular" accounts:
   - permanent accounts - `Asset`, `Capital`, and `Liability` 
   - temporary (closed at period end) - `Income` and `Expense`
2. contra accounts
3. income summary account (`IncomeSummaryAccount`)
"""
from dataclasses import dataclass, field
from typing import List, Optional

from abacus import Entry
from .accounting_types import AccountName, Amount


@dataclass
class Netting:
    contra_accounts: List[AccountName]
    target_name: AccountName

    def safe_copy(self):
        return self


@dataclass
class Account:
    debits: List[Amount] = field(default_factory=list)
    credits: List[Amount] = field(default_factory=list)

    def balance(self) -> Amount:
        raise NotImplementedError

    def transfer_balance_entry(
        self, this_account: AccountName, other_account: AccountName
    ) -> Entry:
        raise NotImplementedError

    def debit(self, amount: Amount):
        self.debits.append(amount)

    def credit(self, amount: Amount):
        self.credits.append(amount)

    def safe_copy(self):
        return self.__class__(self.debits.copy(), self.credits.copy())


@dataclass
class RegularAccount(Account):
    netting: Optional[Netting] = None

    def safe_copy(self):
        netting = self.netting.safe_copy() if self.netting else None
        return self.__class__(self.debits.copy(), self.credits.copy(), netting)


class DebitAccount(Account):
    def balance(self) -> Amount:
        return sum(self.debits) - sum(self.credits)

    def transfer_balance_entry(
        self, this_account: AccountName, other_account: AccountName
    ) -> Entry:
        return Entry(cr=this_account, dr=other_account, amount=self.balance())


class CreditAccount(Account):
    def balance(self) -> Amount:
        return sum(self.credits) - sum(self.debits)

    def transfer_balance_entry(
        self, this_account: AccountName, other_account: AccountName
    ) -> Entry:
        return Entry(dr=this_account, cr=other_account, amount=self.balance())


class Asset(DebitAccount, RegularAccount):
    pass


class Expense(DebitAccount, RegularAccount):
    pass


class Capital(CreditAccount, RegularAccount):
    pass


class Liability(CreditAccount, RegularAccount):
    pass


class Income(CreditAccount, RegularAccount):
    pass


class IncomeSummaryAccount(CreditAccount):
    pass


class ContraAccount:
    pass


class DebitContraAccount(DebitAccount, ContraAccount):
    pass


class CreditContraAccount(CreditAccount, ContraAccount):
    pass
