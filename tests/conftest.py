# filepath: /home/cd001/Projects/django-deep/django-deep/tests/conftest.py
import pytest
import django
from django.conf import settings

@pytest.fixture(scope="session", autouse=True)
def setup_django():
    if not settings.configured:
        settings.configure(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "django.contrib.sessions",
            ],
            AUTH_USER_MODEL="auth.User",
        )
    django.setup()
