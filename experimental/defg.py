from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Account(ABC):
    x: int
    y: int

    @abstractmethod
    def balance(self):
        pass


class Concrete(Account):
    def balance(self):
        pass


c = Concrete(1, 2)
print(c)
print(isinstance(c, Account))
