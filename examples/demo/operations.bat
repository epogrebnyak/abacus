bx operation set capitalize --debit cash --credit equity --describe "shareholder funds" || exit /b
bx operation set acquire-goods --debit goods --credit cash --describe "acquired goods for cash"
bx operation set invoice --debit ar --credit sales --describe "invoice" --requires cost
bx operation set cost --debit cogs --credit goods --describe "cost of sales"
bx operation set discount --debit discounts --credit ar --describe "provided discount"
bx operation set accept-payment --debit cash --credit ar --describe "accepted cash payment"
bx operation set salary --debit sga --credit cash --describe "paid salary in cash"
bx operation show