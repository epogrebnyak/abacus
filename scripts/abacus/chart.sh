abacus chart unlink --yes
abacus chart init
abacus chart add --asset cash ppe
abacus chart name ppe --title "Property, plant, equipment" 
abacus chart promote asset:ar --title "Accounts receivable"
abacus chart add --asset goods --title "Goods for resale"
abacus chart promote capital:equity
abacus chart promote income:sales
abacus chart add --expense cogs --title "Cost of goods sold"
abacus chart promote expense:sga --title "Selling, general, and adm. expenses"
abacus chart add --liability dividend_due ap
abacus chart name ap --title "Accounts payable"
abacus chart offset sales voids refunds
abacus chart promote contra:ppe:depreciation
abacus-extra alias add --operation invoice --debit ar --credit sales
abacus-extra alias add --operation cost --debit cogs --credit goods
abacus chart show --json
abacus chart show
abacus chart set --retained-earnings-account "प्रतिधारित कमाई"
abacus chart set --retained-earnings-account re
abacus chart set --null-account null
abacus chart set --income-summary-account current_profit

