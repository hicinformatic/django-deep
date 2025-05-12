import pytest
from testapp.setup import setup_data
from django_deep import DeepParser
from tests.testapp.models import Role, User, Email

@pytest.mark.django_db
def test_queryset(setup_data):
    qs = User.objects.all()
    dqs = DeepParser(queryset=qs).get_queryset()
    assert dqs.count() == qs.count()

@pytest.mark.django_db
def test_queryset_order(setup_data):
    qs = User.objects.all().order_by('-username')
    dqs = DeepParser(queryset=qs, order_enable=True, params={'o': '-username'}).get_queryset().last()
    assert qs.last().username == dqs.username

@pytest.mark.django_db
def test_queryset_filters_boolean(setup_data):
    qs = User.objects.filter(is_active=True)
    dqs = DeepParser(queryset=qs, params={'f': 'is_active=False'}).get_queryset()
    assert qs.count() == dqs.count()
