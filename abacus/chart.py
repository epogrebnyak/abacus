"""Chart of accounts."""

from typing import Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, root_validator  # type: ignore

from .accounting_types import AbacusError, AccountName
from .accounts import (
    Account,
    Asset,
    Capital,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    Netting,
    RegularAccount,
    RetainedEarnings,
    get_contra_account_type,
)
from .ledger import Ledger

__all__ = ["Chart"]


def all_args(values):
    _isa = values["income_summary_account"]
    return (
        ([_isa] if _isa else [])
        + values["assets"]
        + values["expenses"]
        + values["equity"]
        + values.get("liabilities", [])
        + values["income"]
    )


class Chart(BaseModel):
    """Chart of accounts.

    May include contra accounts.
    Must set *retained_earnings_account* to be able to use Ledger.close()."""

    assets: list[str]
    expenses: list[str]
    equity: list[str]
    liabilities: list[str] = []
    income: list[str]
    contra_accounts: Dict[str, Tuple[List[str], str]] = {}
    income_summary_account: str = "_profit"
    retained_earnings_account: Optional[str] = None

    @root_validator
    def account_names_should_be_unique(cls, values):
        if not is_unique(all_args(values)):
            raise AbacusError("Account names must be unique")
        return values

    @root_validator
    def contra_accounts_should_match_chart_of_accounts(cls, values):
        if values.get("contra_accounts"):
            account_names = all_args(values)
            for account_name in values["contra_accounts"].keys():
                if account_name not in account_names:
                    raise AbacusError(
                        [
                            account_names,
                            f"{account_name} must be specified in chart before using as contra account name",
                        ]
                    )
        return values

    @root_validator
    def account_names_should_be_unique_after_contra_account_netting(cls, values):
        if values.get("contra_accounts"):
            resulting_accounts = [rn for (_, rn) in values["contra_accounts"].values()]
            if not is_unique(all_args(values) + resulting_accounts):
                raise AbacusError(
                    "Account names must be unique after contra account netting"
                )
        return values

    # def __post_init__(self):
    #     if (
    #         self.retained_earnings_account
    #         and self.retained_earnings_account not in self.equity
    #     ):
    #         raise AbacusError(
    #             f"{self.retained_earnings_account} must be in {self.equity}"
    #         )
    #     if not is_unique(self.account_names):
    #         raise AbacusError("Account names may not contain duplicates.")
    #     for account_name in self.contra_accounts.keys():
    #         if account_name not in self.account_names:
    #             raise AbacusError(
    #                 f"{account_name} must be specified in chart before using in contra accounts"
    #             )

    def set_retained_earnings_account(self, account_name: str):
        """Set which account from equity is retained earnings account."""
        if account_name in self.equity:
            self.retained_earnings_account = account_name
            return self
        else:
            raise AbacusError(f"{account_name} must be in {self.equity}")

    # FIXME: no good signature
    # -> List[Union[Tuple[Type[RetainedEarnings], List[str]], Tuple[ABCMeta, List[str]]]]
    def _flat(self):
        """Return regular account names by grouped by account class (without contra accounts)."""
        equity_account_names = self.equity.copy()
        if self.retained_earnings_account:
            addon = [(RetainedEarnings, [self.retained_earnings_account])]
            equity_account_names.remove(self.retained_earnings_account)
        else:
            addon = []
        return [
            (Asset, self.assets),
            (Expense, self.expenses),
            (Capital, equity_account_names),
            (Liability, self.liabilities),
            (Income, self.income),
            (IncomeSummaryAccount, [self.income_summary_account]),
        ] + addon

    def get_type(self, account_name: AccountName) -> Type[RegularAccount]:
        """Return account class by *account_name*."""
        return [
            Class
            for Class, account_names in self._flat()
            if account_name in account_names
        ][0]

    @property
    def account_names(self) -> List[AccountName]:
        """List all account names in chart."""
        return [
            account_name
            for _, account_names in self._flat()
            for account_name in account_names
        ]

    def make_ledger(self) -> Ledger:
        """Create empty ledger based on this chart."""
        ledger = make_regular_accounts(self)
        return add_contra_accounts(self, ledger)


def is_unique(xs):
    return len(set(xs)) == len(xs)


def make_regular_accounts(chart: Chart):
    return Ledger(
        (account_name, cls())
        for cls, account_names in chart._flat()
        for account_name in account_names
    )


def add_contra_accounts(chart: Chart, ledger: Ledger) -> Ledger:
    for refers_to, (
        contra_account_names,
        target_account,
    ) in chart.contra_accounts.items():
        ledger[refers_to].netting = Netting(contra_account_names, target_account)  # type: ignore
        cls = get_contra_account_type(chart.get_type(refers_to))
        for contra_account_name in contra_account_names:
            account: Account = cls()
            ledger[contra_account_name] = account
    return ledger
