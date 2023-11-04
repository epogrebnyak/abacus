from abacus import Chart

chart = Chart()
chart.assets += ["cash"]
chart.expenses += ["cogs"]
print(chart)
print(chart.namer.get_name("cogs").qualified())
