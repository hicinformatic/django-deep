from django.conf import settings
import django


def pytest_configure():
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test',
            USE_TZ=True,
            INSTALLED_APPS=[
                'tests',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            MIDDLEWARE=[],
        )
        django.setup()
