from dataclasses import dataclass

from abacus import AbacusError, Chart
from abacus.cli.base import BaseCommand
from abacus.engine.accounts import (
    AssetName,
    CapitalName,
    ContraName,
    ExpenseName,
    IncomeName,
    LiabilityName,
    extract,
)


def contra_phrase(account_name, contra_account_names):
    return account_name + " is offset by " + ", ".join(contra_account_names)


@dataclass
class ChartCommand(BaseCommand):
    chart: Chart = Chart()

    def json(self):
        return self.chart.json(indent=4, ensure_ascii=True)

    @staticmethod
    def read(path):
        return ChartCommand(chart=Chart.parse_file(path), path=path)

    def write(self):
        self.path.write_text(self.json(), encoding="utf-8")
        self.log(f"Wrote chart file {self.path}.")
        return self

    def set_retained_earnings(self, account_name) -> "ChartCommand":
        """Override default name of retained earnings account."""
        self.chart.retained_earnings_account = account_name
        self.log(f"Retained earnings account name was set to <{account_name}>.")
        return self

    def set_null_account(self, account_name) -> "ChartCommand":
        """Override default name of null account."""
        self.chart.null_account = account_name
        self.log(f"Null account name was set to <{account_name}>.")
        return self

    def set_isa(self, account_name) -> "ChartCommand":
        """Override default name of income summary account."""
        self.chart.income_summary_account = account_name
        self.log(f"Income summary account was set to <{account_name}>.")
        return self

    def promote(self, string: str) -> "ChartCommand":
        """Add account to chart using notation like `asset:cash` or `contra:sales:voids`."""
        if ":" not in string:
            self.chart.viewer.assert_contains(string)
            self.log(f"Account <{string}> is already in chart.")
            return self
        match extract(string):
            case AssetName(account_name):
                self.add_by_attribute("assets", account_name)
            case LiabilityName(account_name):
                self.add_by_attribute("liabilities", account_name)
            case CapitalName(account_name):
                self.add_by_attribute("equity", account_name)
            case IncomeName(account_name):
                self.add_by_attribute("income", account_name)
            case ExpenseName(account_name):
                self.add_by_attribute("expenses", account_name)
            case ContraName(account_name, contra_account_name):
                self.offset(account_name, contra_account_name)
            case _:
                raise AbacusError(f"No action for {string}.")
        return self

    def add_by_attribute(self, chart_attribute, account_name):
        """Perform checks and add account to chart."""
        account_names = getattr(self.chart, chart_attribute)
        if self.chart.viewer.contains(account_name):
            if account_name in account_names:
                self.log(
                    f"Account name <{account_name}> already exists "
                    f"within <{chart_attribute}>."
                )
                return self
            else:
                raise AbacusError(
                    "Account names must be unique. "
                    f"Account name <{account_name}> is already taken."
                )
        setattr(self.chart, chart_attribute, account_names + [account_name])
        # FIXME: Account name format not unique
        self.log(f"Added account <{chart_attribute}:{account_name}>.")
        return self

    def offset_many(self, account_name, contra_account_names) -> "ChartCommand":
        for contra_account_name in contra_account_names:
            self.chart.offset(account_name, contra_account_name)
            self.log(f"Added contra account <{contra_account_name}> to chart.")
        return self

    def offset(self, account_name, contra_account_name) -> "ChartCommand":
        return self.offset_many(account_name, [contra_account_name])

    def add_operation(self, name: str, debit: str, credit: str):
        self.chart.add_operation(name, debit, credit)
        self.log(
            f"Added operation <{name}> where debit account is <{debit}>,"
            f" credit account is <{credit}>."
        )
        return self

    def set_name(self, account_name, title) -> "ChartCommand":
        self.chart.set_name(account_name, title)
        self.log(f'Changed account <{account_name}> title to "{title}".')
        return self

    def show(self):
        print_chart(self.chart)
        return self


def print_re(chart):
    print(
        "Retained earnings account:",
        chart.namer.compose_name(chart.retained_earnings_account) + ".",
    )


def print_chart(chart: Chart):
    def name(account_name):
        return chart.namer.compose_name(account_name)

    print("Accounts")
    for attribute in ("assets", "equity", "liabilities", "income", "expenses"):
        account_names = getattr(chart, attribute)
        if account_names:
            print(attribute.capitalize() + ":", ", ".join(map(name, account_names)))
    if chart.contra_accounts:
        print("Contra accounts:")
        for key, names in chart.contra_accounts.items():
            print("  -", contra_phrase(name(key), map(name, names)))
    print_re(chart)
    if chart.operations:
        print("Operation aliases:")
        for key, (debit, credit) in chart.operations.items():
            print("  -", key, f"(debit is {debit}, credit is {credit})")
