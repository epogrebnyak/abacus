from abacus import Chart
from abacus.core import Amount, AccountName
from abacus.accounting_types import Account, AccountBalancesDict
from dataclasses import dataclass
from typing import Optional, Dict, List


# It should be an error if both account and contraccount are on debit or credit-side.
# It should be an error if nets_with not found in Chart

chart = Chart(
    assets=["ppe"],
    expenses=[],
    equity=[],
    liabilities=[],
    income=["sales"],
    debit_contra_accounts=[("discounts", "sales")],
    credit_contra_accounts=[("depr", "ppe")],
)


def test_invalid_account():
    import pytest

    with pytest.raises(ValueError):
        Chart(
            assets=["ppe"],
            expenses=[],
            equity=[],
            liabilities=[],
            income=["sales"],
            debit_contra_accounts=[],
            credit_contra_accounts=[("abc", "zzz")],
        )


@dataclass
class Saldo:
    """Account balance (in Italian and some other languages)."""

    amount: Amount
    nets_with: Optional[AccountName] = None

    def __sub__(self, amount: Amount):
        return self.__class__(self.amount - amount)


class DebitSaldo(Saldo):
    pass


class CreditSaldo(Saldo):
    pass


TrialBalance = Dict[AccountName, Saldo]

TAccount = Account


@dataclass
class Nettable:
    account: TAccount
    nets_with: Optional[AccountName] = None


Ledger = Dict[AccountName, TAccount]


# Chart -> Dict[str, TAccount] -> Dict[str, Balance]

tb = dict(
    ppe=DebitSaldo(1000),
    sales=CreditSaldo(300),
    discounts=DebitSaldo(25, "sales"),
    depr=CreditSaldo(600, "ppe"),
)


def netting(tb: TrialBalance) -> TrialBalance:
    res = {}
    # create keys without nets_with - target accounts (like 'ppe')
    for account_name, saldo in tb.items():
        if not saldo.nets_with:
            res[account_name] = saldo
    # work with keys with nets_with - accounts netted to zero  (like 'depr')
    # we do not include zero accounts in netting() output
    for account_name, saldo in tb.items():
        if saldo.nets_with:
            match saldo, res[saldo.nets_with]:
                case DebitSaldo(amount, nets_with), CreditSaldo(_, _):
                    res[nets_with] -= amount
                case CreditSaldo(amount, nets_with), DebitSaldo(_, _):
                    res[nets_with] -= amount
                case (_, _):
                    raise ValueError([saldo, res[saldo.nets_with]])
    return res


def flush(tb: TrialBalance) -> AccountBalancesDict:
    """Discard  credit or debit side inofrmation."""
    return AccountBalancesDict((name, saldo.amount) for name, saldo in tb.items())


print(flush(netting(tb)))


def test_tb_twice():
    # must test twice - dictionaries may fail
    assert flush(netting(tb)) == AccountBalancesDict({"ppe": 400, "sales": 275})
    assert flush(netting(tb)) == AccountBalancesDict({"ppe": 400, "sales": 275})
