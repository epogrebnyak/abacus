from abc import ABC, abstractmethod
from typing import Type


class Parent:
    ...


class Son(Parent):
    ...


class Daughter(Parent):
    ...


class House(ABC):
    @abstractmethod
    def tenant(self) -> Type[Son] | Type[Daughter]:
        ...


class HouseA(House):
    def tenant(self) -> Type[Son]:
        return Son


class HouseB(House):
    def tenant(self) -> Type[Daughter]:
        return Daughter
