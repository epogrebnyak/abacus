abacus chart unlink --yes
abacus chart init
abacus chart add asset:cash 
abacus chart add asset:ar --title "Accounts receivable"
abacus chart add asset:goods --title "Goods for resale"
abacus chart add asset:ppe
abacus chart name ppe --title "Property, plant, equipment" 
abacus chart add capital:equity
abacus chart add income:sales
abacus chart add expense:cogs --title "Cost of goods sold"
abacus chart add expense:sga --title "Selling, general, and adm. expenses"
abacus chart add liability:dividend_due
abacus chart add liability:ap --title "Accounts payable"
abacus chart add-many contra:sales:voids contra:sales:refunds
abacus chart add contra:ppe:depreciation
abacus chart show --json
abacus chart show
abacus chart set --re "प्रतिधारित कमाई"
abacus chart set --re re
abacus chart set --null null
abacus chart set --isa current_profit

