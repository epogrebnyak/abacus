# TODO: add more codes from https://www.audit-it.ru/plan_schetov/
bx chart erase --force
bx chart init
bx chart add --asset cash --code 50
bx chart add --asset ar --title "Accounts receivable" --code "620"
bx chart add --asset goods --title "Goods for resale"
bx chart add --asset ppe
bx chart set ppe --title "Property, plant, equipment" 
bx chart set ppe --code 01
bx chart add --capital equity
bx chart add --income sales
bx chart add --expense cogs --title "Cost of goods sold"
bx chart add --expense sga --title "Selling, general, and adm. expenses"
bx chart set --retained-earnings "प्रतिधारित कमाई"
bx chart set --retained-earnings re
bx chart add --liability dividend_due
bx chart add --liability ap --title "Accounts payable" --code "621"
bx chart offset sales voids refunds
bx chart offset ppe depreciation
bx chart set depreciation --code 02
bx chart alias --operation invoice --debit ar --credit sales --requires cost
bx chart alias --operation cost --debit cogs --credit goods --requires invoice
bx chart show --json
bx chart show
