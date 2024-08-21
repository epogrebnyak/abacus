set -e
isort . --float-to-top
black .
python example_core.py
python example_ui.py
pytest . -q
mypy core.py
ruff check . --fix
 

