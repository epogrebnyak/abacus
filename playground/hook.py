from dataclasses import dataclass, field

def idle():
    raise NotImplementedError

@dataclass
class Item:
    name: str
    hook: callable = field(default=idle)

@dataclass
class Base:
    item: Item
    store: dict

    def __post_init__(self):
        self.item.hook = self.post

    def post(self, key, value):
        self.store[key] = value


b = Base(Item('abc'), {})
b.item.hook('1', 'occupied')
print(b.store)
