from abacus import Chart
from abacus.engine.accounts import RegularAccountEnum, from_flag

print(from_flag("--asset"))

print(from_flag("equity").value)

print(RegularAccountEnum.all())

print(Chart().viewer.get_account_names(RegularAccountEnum.ASSET))
