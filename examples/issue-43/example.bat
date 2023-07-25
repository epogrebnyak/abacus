bx erase --chart
bx chart add--asset cash || exit /b
bx chart add--asset ar --title "Accounts receivable"  || exit /b
bx chart offset ar bad_debt  || exit /b
bx chart title bad_debt "Allowance for bad debts"  || exit /b
bx chart add--asset inventory  || exit /b
bx chart add--expense cogs --title "Cost of goods sold"  || exit /b 
bx chart add--expense sga --title "Selling expenses"  || exit /b
bx chart add--capital equity   || exit /b
bx chart add--retained-earnings re  || exit /b
bx chart add--income sales  || exit /b
bx chart offset sales discounts voids  || exit /b
bx chart show || exit /b

bx operation set capitalize --debit cash --credit equity --describe "shareholder funds"  || exit /b
bx operation set acquire-goods --debit inventory --credit cash --describe "acquired goods for cash"  || exit /b
bx operation set invoice --debit ar --credit sales --describe "invoice" --requires cost  || exit /b
bx operation set cost --debit cogs --credit inventory --describe "cost of sales"  || exit /b
bx operation set discount --debit discounts --credit ar --describe "provided discount"  || exit /b
bx operation set accept-payment --debit cash --credit ar --describe "accepted cash payment"  || exit /b
bx operation set salary --debit sga --credit cash --describe "paid salary in cash"  || exit /b
bx operation show  || exit /b

bx ledger start  || exit /b
bx post operation -t "Initial investment" capitalize 1000   || exit /b
bx post operation -t "Purchased goods for resale" acquire-goods 500   || exit /b
bx post operation -t "Sales contract #1" invoice 440 discount 40 cost 250  || exit /b
bx post operation -t "Cash payment on sales contract #1" accept-payment 200 || exit /b
bx post operation -t "Sales contract #2" invoice 300 cost 120 accept-payment 300   || exit /b
bx post operation -t "Sales team remuneration" salary 150   || exit /b
bx post entry -t "Unrecoverable debt on sales contract #1" --debit ar --credit bad_debt --amount 100   || exit /b
bx ledger close  || exit /b
bx ledger list --close || exit /b
bx ledger list --business || exit /b

bx report --balance-sheet
bx report --income-statement
bx accounts
bx account cash
bx assert cash 850