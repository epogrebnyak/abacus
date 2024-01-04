cx extra unlink --yes
cx init
cx add asset:cash 
cx add income:sales 
cx add liability:vat --title "VAT payable"
cx post-compound --debit cash 120 --credit sales 100 --credit vat 20
cx report -t