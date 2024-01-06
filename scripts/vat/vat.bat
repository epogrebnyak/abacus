buh extra unlink --yes
buh init
buh add asset:cash 
buh add income:sales 
buh add liability:vat --title "VAT payable"
buh post-compound --debit cash 120 --credit sales 100 --credit vat 20
buh report -t