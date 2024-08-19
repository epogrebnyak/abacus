pytest .
mypy core.py
ruff check . --fix
python example_core.py
python example_ui.py
isort . --float-to-top
black .
 

