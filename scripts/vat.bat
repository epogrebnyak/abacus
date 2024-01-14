bx unlink --yes
bx init
bx chart add asset:cash 
bx chart add income:sales 
bx chart add liability:vat --title "VAT payable"
bx post --debit cash 120 --credit sales 100 --credit vat 20
bx report --all
bx assert vat 20
bx assert cash 120
bx close
bx assert retained_earnings 100