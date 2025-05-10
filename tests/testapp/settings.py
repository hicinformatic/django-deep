import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEBUG=True,
SECRET_KEY='test'
USE_TZ=True
INSTALLED_APPS=[
    'django_deep',
    'tests.testapp',
]

DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}



#import django
#def pytest_configure():
#    if not settings.configured:
#        settings.configure(
#            DEBUG=True,
#            SECRET_KEY='test',
#            USE_TZ=True,
#            INSTALLED_APPS=[
#                'django_deep',
#                'tests.testapp',
#            ],
#            DATABASES={
#                'default': {
#                    'ENGINE': 'django.db.backends.sqlite3',
#                    'NAME': ':memory:',
#                }
#            },
#            MIDDLEWARE=[],
#        )
#        django.setup()
