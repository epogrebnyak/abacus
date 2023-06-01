"""
Usage:
jaba chart new --output chart.json  
jaba chart add --assets <names> --chart chart.json
jaba chart add --expenses <names> --chart chart.json   
jaba chart add --capital <names> --chart chart.json   
jaba chart add --liabilities <names> --chart chart.json   
jaba chart add --income <names> --chart chart.json   
jaba chart offset <name> --contra-accounts <names> --resulting-name <new_name> --chart chart.json   
jaba store new [--start-balances start_balances.json] --output entries.json
jaba entry new --dr dr_account --cr cr_account --amount amount [--chart chart.json]
jaba entry add --dr dr_account --cr cr_account --amount amount --store entries.json [--chart chart.json]
jaba store list ([--entry] [--rename] [--mark]) | [--all] --store entries.json
jaba report -t --chart chart.json --store entries.json > trial_balance.json
jaba close --contra-income --contra-expenses --chart chart.json --store entries.json 
jaba close --income --expenses --isa --chart chart.json --store entries.json 
jaba report -i --chart chart.json --store entries.json > income_statement.json 
jaba report -b --chart chart.json --store entries.json > balance_sheet.json 
jaba report -e --chart chart.json --store entries.json > end_balances.json
"""
