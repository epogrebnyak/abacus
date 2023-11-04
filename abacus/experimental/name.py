from abacus import Chart

chart = Chart()
chart.assets += ["cash"]
print(chart)
print(chart.namer.qualified_name("cash"))
