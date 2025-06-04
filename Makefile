PYTHON := $(or $(PYTHON_ENV),  /usr/bin/python3)
VENV=venv
ACTIVATE=. $(VENV)/bin/activate

# Crée un environnement virtuel et installe les dépendances
venv:
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	$(ACTIVATE) && pip install -U pip setuptools wheel
	$(ACTIVATE) && pip install -e .[dev]

# Installation directe (sans création de venv)
install:
	$(PYTHON) -m pip install -e .[dev]

# Lancer les tests avec pytest
test:
	PYTHONPATH=$(shell pwd) $(VENV)/bin/pytest --ds=tests.settings -o log_cli=true --log-level=DEBUG

# Vérifie le style du code avec ruff
lint:
	$(VENV)/bin/ruff django_deep/ tests/

# Formatte le code avec black
format:
	$(VENV)/bin/black django_deep/ tests/

migrations:
	$(VENV)/bin/python manage.py makemigrations

django-shell:
	$(VENV)/bin/python manage.py shell

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .coverage dist build *.egg-info
