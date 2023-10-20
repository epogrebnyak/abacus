from dataclasses import dataclass
from typing import List

@dataclass
class Logger:
    """Logger will hold string message about actions taken."""

    messages: List[str]

    def log(self, string: str):
        self.messages.append(string)

    def echo(self):
        for string in self.messages:
            print(string)    


# @dataclass
# class Command(ABC):
#     store: LineJSON
#     logger: Logger = Logger()

#     @
#     def file()

#     def echo(self):
#         print(self.logger.message)
#         return self

#     def log(self, message):
#         self.logger.log(message)
#         return self

#     @abstractmethod
#     def init(cls, path):
#         store = LineJSON(path).file.touch()
#         return LedgerCommand(store).log(f"Wrote ledger file: {path}")

#     def erase(self) -> None:
#         self.store.file.erase()


#     @classmethod
#     def read(cls, path: Path) -> "LedgerCommand":
#         return LedgerCommand(store=LineJSON(path))


#     def show(self, sep=","):
#         for entry in self.store.yield_entries():
#             print(entry.debit, entry.credit, entry.amount, sep=sep)
