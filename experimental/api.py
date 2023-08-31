import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pytest
from engine.base import AbacusError, AccountName
from engine.chart import Chart
from engine.ledger import Ledger
from pydantic import BaseModel


def cwd() -> Path:
    return Path(os.getcwd())


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, content):
    return Path(path).write_text(
        json.dumps(content, ensure_ascii=True, indent=4), encoding="utf-8"
    )


class Config(BaseModel):
    chart: str = "chart.json"
    entries: str = "entries.csv"

    @classmethod
    def path(cls, directory: Path):
        return directory / "abacus.json"

    @classmethod
    def read(cls, directory: Path):
        return Config.parse_file(Config.path(directory))

    @classmethod
    def exists(cls, directory: Path):
        return cls.path(directory).exists()

    def save(self, directory: Path):
        write_json(self.path(directory), self.dict())

    def init(self, directory):
        if not self.exists(directory):
            Config().save(directory)
        else:
            sys.exit(
                f"Directory not empty, file already exists: {Config.path(self.directory)}"
            )


def parse_location(directory: Path) -> "FullPath":
    cfg = Config.read(directory)
    return FullPath(directory / cfg.chart, directory / cfg.entries)


@dataclass
class FullPath:
    chart: Path
    entries: Path

    def read_chart(self):
        return Chart.parse_file(self.chart)

    def write_chart(self, chart: Chart):
        write_json(self.chart, chart.dict())

    def read_entries(self):
        pass

    def append_entry(self):
        pass


@dataclass
class ChartCommand:
    chart: Chart

    def set_retained_earnings(self, account_name):
        """Set name of null account (override default name).

        Command:
        ```
        bx set --retained-earnings <account_name>
        ```
        """

    def set_null_account(self, account_name):
        """Set name of null account (override default name).

        Command:
        ```
        bx set --null-account <account_name>
        ```
        """

    def set_isa(self, account_name):
        """Set name of income summary account (override default name).

        Command:
        ```
        bx set --income-summary-account <account_name>
        ```
        """
        pass

    def _add(self, attribute: str, account_names: List[str]):
        cli_flags = ["assets", "capital", "liabilities", "income", "expenses"]
        attribute = "equity" if (attribute == "capital") else attribute
        try:
            account_names = getattr(self.chart, attribute) + account_names
            setattr(self.chart, attribute, account_names)
        except:
            raise AbacusError(f"Flag must be one of {cli_flags}, provided: {attribute}")

    def add_assets(self, account_names: List[str]):
        self._add("assets", account_names)
        return self

    def add_capital(self, account_names):
        # note: add_capital() will add account_names to 'equity' attribute
        self._add("equity", account_names)
        return self

    def add_liabilities(self, account_names):
        self._add("liabilities", account_names)
        return self

    def add_income(self, account_names):
        self._add("income", account_names)
        return self

    def add_expenses(self, account_names):
        self._add("expenses", account_names)
        return self

    def offset(self, account_name, contra_account_names):
        pass

    def name(self, account_name, title):
        pass

    def show(self, account: AccountName | None = None):
        pass

    def validate(self):
        pass


# TODO: create test_api.py and code with asserts to test_api.py as pytest unit tests
#      use nsames like test_add_tests(),
#      the following command should run as a test: poetry run pytest experimental
#      if you install just command runner `just go` should also pass
assert ChartCommand(Chart()).add_assets(["cash"]).chart.assets == ["cash"]
assert ChartCommand(Chart()).add_capital(["equity"]).chart.equity == ["equity"]
assert ChartCommand(Chart()).add_liabilities(["ap"]).chart.liabilities == ["ap"]
assert ChartCommand(Chart()).add_income(["sales"]).chart.income == ["sales"]
assert ChartCommand(Chart()).add_expenses(["cogs"]).chart.expenses == ["cogs"]

with pytest.raises(AbacusError):
    ChartCommand(Chart())._add("no such attribute", [])

# end of TODO here


class LedgerCommand:
    ledger: Ledger

    def start(self, filename: str | None = None):
        pass

    def post(self):
        pass

    def close(self):
        pass


class ReportCommand:
    def trial_balance(self):
        pass

    def balance_sheet(self, json: bool):
        pass

    def income_statement(self, json: bool):
        pass

    def end_balances(self, json: bool):
        pass
