chart:
   init
   add --asset cash
   add --asset ar --title "Accounts receivable"
   add --asset goods --title "Inventory (goods for resale)"
   add --asset prepaid_rent --title "Storage facility prepaid rent"
   add --capital equity
   add --liability dividend_due
   add --income sales
   offset sales discounts
   add --expense cogs --title "Cost of goods sold"
   add --expense sga --title "Selling, general and adm. expenses"
   alias --operation invoice --debit ar --credit sales
   alias --operation cost --debit cogs --credit goods
ledger:
   init
ledger post:
   entry --debit cash --credit equity --amount 5000 --title "Initial investment"
   entry --debit goods --credit cash --amount 3500 --title "Acquire goods for cash"
   entry --debit prepaid_rent --credit cash --amount 1200 --title "Prepay rent"
   operation invoice 4300 cost 2500 --title "Issue invoice and register cost of sales"
   entry --debit discounts --credit ar --amount  450 --title "Provide discount"
   entry --debit cash --credit ar --amount 3000 --title "Accept payment"
   entry --debit sga --credit cash --amount  300 --title "Reimburse sales team"
   entry --debit sga --credit prepaid_rent --amount 800 --title "Expense 8 months of rent" --adjust
ledger:
   close
   post-after-close entry --debit re --credit dividend_due --amount 150 --title "Accrue dividend"
report show:
   --balace-sheet
   --income-statement