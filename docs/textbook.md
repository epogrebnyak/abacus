# Textbook examples

## Joan Robinson law office

> From "Accounting Principles" by Weygandt, Kimmel and Kieso (ed 12, p. 31).

Joan Robinson opens her own law office on July 1, 2017.
During the first month of operations, the following transactions occurred.

1. Joan invested $11,000 in cash in the law practice.
2. Paid $800 for July rent on offi ce space.
3. Purchased equipment on account $3,000.
4. Performed legal services to clients for cash $1,500.
5. Borrowed $700 cash from a bank on a note payable.
6. Performed legal services for client on account $2,000.
7. Paid monthly expenses: salaries and wages $500, utilities $300, and advertising $100.
8. Joan withdrew $1,000 cash for personal use.

Solution: [click here](https://raw.githubusercontent.com/epogrebnyak/abacus/main/scripts/textbook/joan.bat).

## Yazici Advertising

> From "Intermediate Accounting. IFRS Edition" by Weygandt, Kimmel and Warfiled.
> Illustration 3-10 to 3-20.

Solution: [click here](https://raw.githubusercontent.com/epogrebnyak/abacus/main/scripts/textbook/yazici.bat).

## AccountingCoach.com

Direct Delivery sample transactions 1-6 from [accountingcoach.com](https://www.accountingcoach.com/accounting-basics/explanation/5).

=== "Result"

    ```
                        Balance sheet
    Assets                 20260  Capital              20180
      Cash                  4810    Common stock       20000
      Vehicles             14000    Retained earnings    180
      Prepaid insurance     1200  Liabilities             80
      Accounts receivable    250    Accounts payable      80
    Total                  20260  Total                20260

                        Income Statement
    Income                                               260
      Services                                           260
    Expenses                                              80
      Temporary help agency                               80
    Current profit                                       180
    ```

=== "Command line"

    ```bash
    abacus extra unlink --yes
    abacus init
    abacus post asset:cash capital:common_stock 20000 --title "1. Owner's investment"
    abacus post asset:vehicles cash             14000 --title "2. Purchased vehicle"
    abacus post asset:prepaid_insurance cash     1200 --title "3. Bought insurance"
    abacus post cash income:services               10 --title "4. Accepted cash for provided services"
    abacus post asset:ar services                 250 --title "5. Provided services on account"
    abacus post expense:agency liability:ap        80 --title "6. Purchased services on account"
    abacus close
    abacus name ar "Accounts receivable"
    abacus name ap "Accounts payable"
    abacus name agency "Temporary help agency"
    abacus report --all
    ```
