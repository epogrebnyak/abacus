from pathlib import Path
from abacus import Chart, AbacusError #, AccountName
from dataclasses import dataclass


def init_chart(path: Path):
    """Write empty chart to *path* if does not file exist."""
    if not path.exists():
        ChartCommand.new().write(path)
    else:
        raise AbacusError

def contra_phrase(account_name, contra_account_names):
    return account_name + " is offset by " + ", ".join(contra_account_names)

@dataclass
class Lоgger:
    message: str = ""

@dataclass
class ChartCommand:
    chart: Chart
    logger: Lоgger = Lоgger()

    @classmethod
    def new(cls) -> "ChartCommand":
        return ChartCommand(chart=Chart())

    @classmethod
    def read(cls, path: Path) -> "ChartCommand":
        return ChartCommand(chart=Chart.parse_file(path))

    def write(self, path: Path) -> None:
        content = self.chart.json(indent=4, ensure_ascii=True)
        Path(path).write_text(content, encoding="utf-8")

    def set_retained_earnings(self, account_name) -> "ChartCommand":
        """Оverride default name of retained earnings account."""
        self.chart.retained_earnings_account = account_name
        return self

    def set_null_account(self, account_name) -> "ChartCommand":
        """Оverride default name of null account."""
        self.chart.null_account = account_name
        return self

    def set_isa(self, account_name) -> "ChartCommand":
        """Оverride default name of income summary account."""
        self.chart.income_summary_account = account_name
        return self

    def _add(self, attribute: str, account_name: str) -> "ChartCommand":
        account_names = getattr(self.chart, attribute) + [account_name]
        setattr(self.chart, attribute, account_names)
        return self

    def add_asset(self, account_name: str):
        return self._add("assets", account_name)

    def add_capital(self, account_name: str):
        # will add account_name to 'equity' attribute
        return self._add("equity", account_name)

    def add_liability(self, account_name: str):
        return self._add("liabilities", account_name)

    def add_income(self, account_name: str):
        return self._add("income", account_name)

    def add_expense(self, account_name: str):
        return self._add("expenses", account_name)

    def offset(self, account_name, contra_account_names) ->     "ChartCommand":
        for contra_account_name in contra_account_names:
            self.chart.offset(account_name, contra_account_name)
        # logging
        text = "Added contra account:"
        if len(contra_account_names) > 1:
            text = "Added contra accounts:"
        self.logger.message = text + " " + contra_phrase(account_name, contra_account_names) + "."
        return self

    def alias(self, name: str, debit: AccountName, credit: AccountName):
        self.chart.add_operation(name, debit, credit)
        self.logger.message = f"Added operation: {name} (debit is {debit}, credit is {credit})."
        return self

    def set_name(self, account_name, title) -> str:
        self.chart.set_name(account_name, title)
        return "Added account title: " + self.chart.compose_name(account_name) + "."

    def set_code(self, account_name, code: str) -> str:
        self.chart.set_code(account_name, code)
        return f"Set code {code} for account {account_name}."
