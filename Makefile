PYTHON := $(if $(PYTHON_ENV),$(PYTHON_ENV),$(shell command -v python3 || echo /usr/bin/python3))
VENV=venv
ACTIVATE=. $(VENV)/bin/activate
PACKAGE=django_deep-0.1.0-py3-none-any.whl

# Vérifie si c'est Ubuntu/Debian et installe pip/venv système si nécessaire
ensure-system-packages:
	@if [ -f /etc/debian_version ]; then \
		echo ">>> Detected Debian/Ubuntu"; \
		apt-get update && apt-get install -y python3-venv python3-pip; \
	else \
		echo ">>> Not Debian/Ubuntu, skipping system package install"; \
	fi


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

package:
	$(VENV)/bin/python setup.py sdist bdist_wheel

build:
	$(VENV)/bin/python -m build

docker-install:
ifndef CONTAINER
	$(error CONTAINER variable is required, e.g. make docker-install CONTAINER=abcd1234)
endif
	@echo ">>> Copying package to container $(CONTAINER)"
	docker cp dist/$(PACKAGE) $(CONTAINER):/tmp/
	@echo ">>> Installing package inside container $(CONTAINER)"
	docker exec -it $(CONTAINER) pip install /tmp/$(PACKAGE)

docker-uninstall:
ifndef CONTAINER
	$(error CONTAINER variable is required, e.g. make docker-uninstall CONTAINER=abcd1234)
endif
	@echo ">>> Uninstalling package inside container $(CONTAINER)"
	docker exec -it $(CONTAINER) pip uninstall -y $(PACKAGE)

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
