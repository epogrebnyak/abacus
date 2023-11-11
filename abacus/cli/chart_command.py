from dataclasses import dataclass

from abacus import AbacusError, Chart
from abacus.cli.base import BaseCommand


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
        self.chart.set_re(account_name)
        self.log(f"Retained earnings account name was set to <{account_name}>.")
        return self

    def set_null_account(self, account_name) -> "ChartCommand":
        """Override default name of null account."""
        self.chart.set_null(account_name)
        self.log(f"Null account name was set to <{account_name}>.")
        return self

    def set_isa(self, account_name) -> "ChartCommand":
        """Override default name of income summary account."""
        self.chart.set_isa(account_name)
        self.log(f"Income summary account was set to <{account_name}>.")
        return self

    def promote(self, string: str) -> "ChartCommand":
        try:
            self.chart.add(string)
        except AbacusError as e:
            self.log(str(e))
        return self

    def offset_many(self, account_name, contra_account_names) -> "ChartCommand":
        for contra_account_name in contra_account_names:
            self.chart.offset(account_name, contra_account_name)
            self.log(f"Added contra account <{contra_account_name}> to chart.")
        return self

    def offset(self, account_name, contra_account_name) -> "ChartCommand":
        return self.offset_many(account_name, [contra_account_name])

    def add_operation(self, name: str, debit: str, credit: str):
        self.chart.alias(name, debit, credit)
        self.log(
            f"Added operation <{name}> where debit account is <{debit}>,"
            f" credit account is <{credit}>."
        )
        return self

    def set_name(self, account_name, title) -> "ChartCommand":
        self.chart.name(account_name, title)
        self.log(f'Changed account <{account_name}> title to "{title}".')
        return self

    def show(self):
        self.chart.print()
        return self
