set -e
isort . --float-to-top
black .
python example_mini.py
python example_ui.py
python readme.py
pytest . -q
ruff check . --fix
mypy core.py
mypy ui.py
wc -l core.py ui.py
 

