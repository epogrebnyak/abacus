from dataclasses import dataclass
from pathlib import Path

from abacus import AbacusError, Chart
from abacus.engine.accounts import RegularAccountEnum
from abacus.engine.base import AccountName
from abacus.experimental.base import Logger


def contra_phrase(account_name, contra_account_names):
    return account_name + " is offset by " + ", ".join(contra_account_names)


@dataclass
class ChartCommand:
    chart: Chart
    logger: Logger = Logger(messages=[])

    def echo(self):
        self.logger.echo()
        return self

    def log(self, message):
        self.logger.log(message)
        return self

    @classmethod
    def init(cls, path: Path) -> "ChartCommand":
        """Write empty chart to *path* if does not file exist."""
        if path.exists():
            raise AbacusError(f"{path} already exists.")
        return ChartCommand.new().write(path)

    @classmethod
    def new(cls) -> "ChartCommand":
        return ChartCommand(chart=Chart())

    @classmethod
    def read(cls, path: Path) -> "ChartCommand":
        return ChartCommand(chart=Chart.parse_file(path), logger=Logger(messages=[]))

    def write(self, path: Path) -> "ChartCommand":
        content = self.chart.json(indent=4, ensure_ascii=True)
        Path(path).write_text(content, encoding="utf-8")
        self.log(f"Wrote chart file {path}.")
        return self

    def set_retained_earnings(self, account_name) -> "ChartCommand":
        """Override default name of retained earnings account."""
        self.chart.retained_earnings_account = account_name
        return self

    def set_null_account(self, account_name) -> "ChartCommand":
        """Override default name of null account."""
        self.chart.null_account = account_name
        return self

    def set_isa(self, account_name) -> "ChartCommand":
        """Override default name of income summary account."""
        self.chart.income_summary_account = account_name
        return self

    def add_by_enum(
        self, account_type: RegularAccountEnum, account_name: str
    ) -> "ChartCommand":
        return self._add(account_type.chart_attribute(), account_name)

    def _add(self, attribute: str, account_name: str) -> "ChartCommand":
        """Generic method to add account of *attribute* type to chart.
        Attribute in any of ['assets', 'liabilities', 'equity', 'income', 'expenses'].
        """
        if attribute not in self.chart.five_types_of_accounts():
            raise AbacusError(f"Invalid attribute: {attribute}")
        account_names = getattr(self.chart, attribute)
        if self.chart.viewer.contains(account_name):
            if account_name in account_names:
                self.log(
                    f"Account name <{account_name}> already exists within <{attribute}>."
                )
                return self
            else:
                raise AbacusError(f"Account name <{account_name}> already taken.")
        setattr(self.chart, attribute, account_names + [account_name])
        # FIXME: may refine the message
        self.log(
            f"Added account to chart: <{account_name}>, account types is <{attribute}>."
        )
        return self

    def offset_many(self, account_name, contra_account_names) -> "ChartCommand":
        for contra_account_name in contra_account_names:
            self.chart.offset(account_name, contra_account_name)
            self.log(f"Added contra account <{contra_account_name}> to chart.")
        return self

    def offset(self, account_name, contra_account_name) -> "ChartCommand":
        return self.offset_many(account_name, [contra_account_name])

    # FIXME: operations not supported on cli level
    def add_operation(self, name: str, debit: AccountName, credit: AccountName):
        self.chart.add_operation(name, debit, credit)
        self.log(
            f"Added operation {name} where debit account is {debit}, credit account is {credit}."
        )
        return self

    def set_name(self, account_name, title) -> "ChartCommand":
        self.chart.set_name(account_name, title)
        self.log(f'Changed account <{account_name}> title to "{title}".')
        return self

    def promote(self, string: str) -> "ChartCommand":
        parts = string.split(":")
        match len(parts):
            case 1:
                self.chart.viewer.assert_contains(parts[0])
                self.log(f"Account <{parts[0]}> is already in chart.")
            case 2:
                self.add_by_enum(detect_prefix(parts[0]), parts[1])
            case 3:
                if parts[0] == "contra":
                    self.offset(account_name=parts[1], contra_account_name=parts[2])
                else:
                    raise AbacusError(f"Wrong format for contra account name: {string}")
            case _:
                raise AbacusError(f"Too many colons (:) in account name: {string}")
        return self

    def json(self):
        return self.chart.json(indent=4, ensure_ascii=True)

    def show(self):
        print(self.json())
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
