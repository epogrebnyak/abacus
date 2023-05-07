package := "abacus"

# run pytest
test:
  poetry run pytest

# run readme.py
readme:
  poetry run python readme.py

# run readme.py
md:
  npx prettier . --write

# apply ruff linter
ruff:
  poetry run ruff check .

# type check
mypy:
  poetry run mypy abacus

# black and isort
lint:  
   black .
   isort .

# build documentation 
docs:
  poetry run sphinx-build -a docs docs/site

# show documentation in browser
show:
  start docs/site/index.html

# publish documentation to Github Pages
pages:
  poetry run ghp-import docs/site 

# create rst source for API documentation
apidoc:
  sphinx-apidoc -o docs src/{{package}}

# launch streamlit app
app:
  poetry run streamlit run app.py
