# read examples.as as YAML file
# prepend commands with bx
# run commands from console


import pathlib
from dataclasses import dataclass

doc = pathlib.Path("example.as").read_text()


@dataclass
class Key:
    term: str


@dataclass
class Command:
    term: str


def parse(doc):
    for line in doc.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith(" "):
            yield Command(line.strip())
        if line.endswith(":"):
            yield Key(line[:-1])


elements = list(parse(doc))

prefix = None
for element in elements:
    match element:
        case Key(term):
            prefix = "bx " + term
            continue
        case Command(term):
            command = term
            if prefix:
                print(prefix + " " + command)
