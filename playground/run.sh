set -e
isort . --float-to-top
black .
ruff check . --fix
python example_core.py
python example_ui.py
python readme.py
pytest . -q
mypy core.py
mypy ui.py
 

