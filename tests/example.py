from abacus.engine.better_chart import BaseChart

b = BaseChart(assets=["cash"], capital=["equity"], contra_accounts=dict(equity=["ts"]))

print(list(b.yield_names()))
