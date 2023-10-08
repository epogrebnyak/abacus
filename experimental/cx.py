script = """cx new "Joan Law Office (Weygandt, ed 12, p. 31)"
cx post --debit asset:cash               --credit capital:equity --amount 11000
cx post --debit expense:rent             --credit cash           --amount 800
cx post --debit asset:equipment          --credit cash           --amount 3000
cx post --debit cash                     --credit income:sales   --amount 1500
cx post --debit cash                     --credit liability:note --amount 700
cx post --debit asset:ar                 --credit sales          --amount 2000
cx post --debit expense:salaries         --credit cash           --amount 2000
cx post --debit expense:utilities        --credit cash           --amount 300
cx post --debit expense:ads              --credit cash           --amount 100
cx post --debit contra:equity:withdrawal --credit cash           --amount 1000
cx name ar "Accounts receivable"
cx chart
cx report --balance-sheet
cx report --income-statement"""
#cx report --changes-in-equity
#cx report --cash-flow
#cx report --trial-balance

docstring = """Usage:
  cx new <title>
  cx post --debit <debit_account> --credit <credit_account> --amount <amount>
  cx name <account> <title>
  cx chart
  cx report --balance-sheet
  cx report --income-statement
"""

from docopt import docopt
for line in script.split("\n"):
    #print(line)
    #print(docopt(docstring, argv=line.split()))
    pass

# split the same way as you would do with command line
line = 'cx new "Joan Law Office (Weygandt, ed 12, p. 31)"'

