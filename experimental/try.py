from engine.accounts import ContraIncome

# split on caps - must return 'Сontra income' and 'Retained earnings'
def split_on_caps(cls):
    import re
    return " ".join(re.findall('[A-Z][^A-Z]*', cls.__name__))

assert split_on_caps(ContraIncome) == 'Contra Income'

