from pydantic import BaseModel, parse_obj_as
from pathlib import Path


class Entry(BaseModel):
    dr: str
    cr: str
    amount: int


class BusinessEntry(Entry):
    action: str = "post"


class AdjustmentEntry(Entry):
    action: str = "adjust"


class ClosingEntry(Entry):
    action: str = "close"


class PostEntry(Entry):
    action: str = "postclose"


class Rename(BaseModel):
    take: str
    make: str
    action: str = "rename"


ps = [
    BusinessEntry(dr="cash", cr="eq", amount=500),
    AdjustmentEntry(dr="cash", cr="eq", amount=100),
    Rename(take="eq", make="cap"),
]

import json


def readline(line):
    d = json.loads(line)
    mapper = {
        "post": BusinessEntry,
        "adjust": AdjustmentEntry,
        "close": ClosingEntry,
        "postclose": PostEntry,
        "rename": Rename,
    }
    return parse_obj_as(mapper[d["action"]], d)


for p in ps:
    s = p.json()
    x = readline(s)
    print(x, type(x))


def touch(path):
    pass


def append(path, posting):
    pass


def yield_postings(path):
    pass
