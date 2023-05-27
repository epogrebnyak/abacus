# python -m venv .env
source .env/bin/activate
pip install git+https://github.com/epogrebnyak/abacus.git
abacus chart -a cash,goods,ppe -e cogs,sga,rent -cap eq -re re -l dividend_due -i sales -ca sales discounts,cashback net_sales -ca eq treasury_stock free_float -ca ppe depreciation net_ppe