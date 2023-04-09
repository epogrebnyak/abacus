Balances = Dict[AccountName, Amount]
Accumulation = Dict[AccountName, (List[Amount], List[Amount])]

@dataclass
class Accum:
    add: List[AccountName]
    substract: List[AccountName] = field(default_factory=list)

def subset(d, keys):
    return {k: v for k, v in d.items() if k in keys}

def accum(totals: Balances, accum: Accum, account_name: AccountName):
    a = sum(totals[name] for name in accum.add)
    b = sum(totals[name] for name in accum.substract)
    res = {k: v for k, v in totals.items() if not k in accum.add + accum.substract}
    res[account_name] = a - b
    return res

accumulation = dict(
    inventory = Accum(["raw", "wip", "finished_goods"]),
    ppe_net = Accum(["fixed_assets"], ["depreciation"]),
)

xs = balances(ledger)
for account_name, accum_item in accumulation.items():
   xs = accum(xs, accum_item, account_name)
print(xs)

# TODO: Accum should result in next chart
#Chart -> Accumulation -> Chart
#Balances -> Accumulation -> Balances

# subset(xs, "cash receivables inventory equity retained_earnings debt payables ppe_net".split())
