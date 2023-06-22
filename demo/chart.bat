bx init --force
bx init 
bx chart set --assets cash ar goods 
bx chart set --capital equity
bx chart set --income sales
bx chart set --expenses cogs sga
bx chart set --liabilities ap
bx chart set --retained-earnings re
bx chart offset sales --contra-accounts discounts refunds
bx chart offset equity --contra-accounts treasury_stock
bx chart show 
bx chart show --json

