PYTHON=python
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
	$(VENV)/bin/pytest

# Vérifie le style du code avec ruff
lint:
	$(VENV)/bin/ruff django_deep/ tests/

# Formatte le code avec black
format:
	$(VENV)/bin/black django_deep/ tests/

# Nettoyage des fichiers temporaires
clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .coverage dist build *.egg-info
