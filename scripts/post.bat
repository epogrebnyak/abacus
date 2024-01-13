bx chart unlink --yes 
bx ledger unlink --yes
bx post
bx post --help > /dev/null
bx init
bx post --entry asset:cash capital:equity 1000 --title "Initial capital"
bx post --debit asset:ar 120 --credit income:sales 100 --credit liability:vat 20 
bx post --entry cash ar 60 --title "First cash payment"
bx assert cash 1060