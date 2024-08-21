"""Save strings as LineJSON (currently not used)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

__all__ = ["LineJSON"]


@dataclass
class LineJSON:
    path: Path

    def _open(self, mode: str):
        return open(self.path, mode, newline="\n", encoding="utf-8")

    def append_many(self, strings: list[str]) -> None:
        with self._open("a") as file:
            file.write("\n".join(strings) + "\n")

    def append(self, string: str) -> None:
        self.append_many([string])
        return self

    def __iter__(self) -> Iterable[str]:
        with self._open("r") as file:
            for line in file:
                yield line.rstrip("\n")


path = Path("temp.linejson")
LineJSON(path).path.unlink(missing_ok=True)
xs = [a for a in LineJSON(path).append("abc").append("def")]
assert xs == ["abc", "def"]
LineJSON(path).path
