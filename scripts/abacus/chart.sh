abacus chart unlink --yes
abacus chart init
abacus chart add-many asset cash ppe
abacus chart add asset:ar --title "Accounts receivable"
abacus chart add asset:goods --title "Goods for resale"
abacus chart name ppe --title "Property, plant, equipment" 
abacus chart add capital:equity
abacus chart add income:sales
abacus chart add expense:cogs --title "Cost of goods sold"
abacus chart add expense:sga --title "Selling, general, and adm. expenses"
abacus chart add liability:dividend_due
abacus chart add liability:ap --title "Accounts payable"
abacus chart add-many contra:sales voids refunds
abacus chart add contra:ppe:depreciation
abacus chart operation invoice --debit ar --credit sales
abacus chart operation cost --debit cogs --credit goods
abacus chart show --json
abacus chart show
abacus chart set --retained-earnings-account "प्रतिधारित कमाई"
abacus chart set --retained-earnings-account re
abacus chart set --null-account null
abacus chart set --income-summary-account current_profit

