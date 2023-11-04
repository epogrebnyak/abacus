from dataclasses import dataclass

from abacus import AbacusError, Chart
from abacus.cli.base import BaseCommand
from abacus.engine.accounts import RegularAccountEnum


def contra_phrase(account_name, contra_account_names):
    return account_name + " is offset by " + ", ".join(contra_account_names)


@dataclass
class ChartCommand(BaseCommand):
    chart: Chart = Chart()

    def json(self):
        return self.chart.json(indent=4, ensure_ascii=True)

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
        parts = string.split(":")
        match len(parts):
            case 1:
                self.chart.viewer.assert_contains(parts[0])
                self.log(f"Account <{parts[0]}> is already in chart.")
            case 2:
                chart_attribute = detect_prefix(parts[0]).chart_attribute()
                self.add_by_attribute(chart_attribute, parts[1])
            case 3:
                if parts[0] == "contra":
                    self.offset(account_name=parts[1], contra_account_name=parts[2])
                else:
                    raise AbacusError(f"Wrong format for contra account name: {string}")
            case _:
                raise AbacusError(f"Too many colons (:) in account name: {string}")
        return self

    def add_by_attribute(
        self, chart_attribute: str, account_name: str
    ) -> "ChartCommand":
        """Add account of *attribute* type to chart.
        Attribute in any of ['assets', 'liabilities', 'equity', 'income', 'expenses'].
        """
        try:
            account_names = getattr(self.chart, chart_attribute)
        except AttributeError:
            raise AbacusError(f"Invalid attribute: {chart_attribute}")
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
                    f"Account name <{account_name}> is already taken in this chart."
                )
        setattr(self.chart, chart_attribute, account_names + [account_name])
        self.log(
            f"Added account <{account_name}> to chart, "
            f"account type is <{chart_attribute}>."
        )
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
            f"Added operation <{name}> where debit account is <{debit}>, credit account is <{credit}>."
        )
        return self

    def set_name(self, account_name, title) -> "ChartCommand":
        self.chart.set_name(account_name, title)
        self.log(f'Changed account <{account_name}> title to "{title}".')
        return self

    def show(self):
        # FIXME: can print more verbose name
        print("This will print chart")
        return self


def detect_prefix(prefix: str) -> RegularAccountEnum:
    prefix = prefix.lower()
    if prefix in ["asset", "assets"]:
        return RegularAccountEnum.ASSET
    elif prefix in ["liability", "liabilities"]:
        return RegularAccountEnum.LIABILITY
    elif prefix in ["capital", "equity"]:
        return RegularAccountEnum.EQUITY
    elif prefix in ["expense", "expenses"]:
        return RegularAccountEnum.EXPENSE
    elif prefix in ["income"]:
        return RegularAccountEnum.INCOME
    else:
        raise AbacusError(f"Invalid account prefix: {prefix}")
