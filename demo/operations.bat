bx operation set capitalize --debit cash --credit equity --title "shareholder funds"
bx operation set acquire-goods --debit inventory --credit cash --title "acquired goods for cash"
bx operation set invoice --debit ar --credit sales --title "invoice" --requires cost
bx operation set cost --debit cogs --credit inventory --title "cost of sales"
bx operation set discount --debit discounts --credit ar --title "provided discount"
bx operation set accept-payment --debit cash --credit ar --title "accepted cash payment"
bx operation set salary --debit sga --credit cash --title "paid salary in cash"
bx operation show