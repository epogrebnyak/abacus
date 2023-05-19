package := "abacus"

# run pytest
test:
  poetry run pytest

# run all tests and checks
grill:
  just test
  just examples
  just lint 
  just ruff
  just mypy
  just md

# run code from README.md
readme:
  cat README.md | npx codedown python | poetry run python 

# run all code examples
examples:
  just readme
  poetry run python readme.py

# run readme.py
md:
  npx prettier . --write

# apply ruff linter
ruff:
  poetry run ruff check . --fix

# type check
mypy:
  poetry run mypy abacus

# use black and isort
lint:  
  poetry run isort .
  poetry run black .

# build and serve docs
docs:
  poetry run mkdocs serve 

# publish docs
docs-publish:
  poetry run mkdocs gh-deploy 

# launch streamlit app (depreciated)
app:
  poetry run streamlit run app/app.py
