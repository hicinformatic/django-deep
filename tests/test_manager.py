import pytest
from testapp.setup import setup_data
from django_deep import filters
from tests.testapp import models
import csv


def get_filter_by(filter_type):
    csv_file = 'tests/testapp/csv/filters.csv'
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['filter'] == filter_type:
                yield row

@pytest.mark.django_db
def test_string_filter(setup_data):
    for row in get_filter_by('string'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{row['field']: row['value']})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()

@pytest.mark.django_db
def test_list_filter(setup_data):
    for row in get_filter_by('list'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{f'{row['field']}__in': row['value'].split(',')})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()

@pytest.mark.django_db
def test_boolean_filter(setup_data):
    for row in get_filter_by('boolean'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{f'{row['field']}__in': row['value'].split(',')})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()


@pytest.mark.django_db
def test_integer_filter(setup_data):
    for row in get_filter_by('integer'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{f'{row['field']}': row['value']})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()


@pytest.mark.django_db
def test_float_filter(setup_data):
    for row in get_filter_by('float'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{f'{row['field']}': row['value']})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()


@pytest.mark.django_db
def test_decimal_filter(setup_data):
    for row in get_filter_by('decimal'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{f'{row['field']}': row['value']})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()



@pytest.mark.django_db
def test_time_filter(setup_data):
    for row in get_filter_by('time'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{f'{row['field']}': row['value']})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()


@pytest.mark.django_db
def test_date_filter(setup_data):
    for row in get_filter_by('date'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{f'{row['field']}': row['value']})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()


@pytest.mark.django_db
def test_datetime_filter(setup_data):
    for row in get_filter_by('datetime'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{f'{row['field']}': row['value']})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()



@pytest.mark.django_db
def test_choice_filter(setup_data):
    for row in get_filter_by('choice'):
        qs = getattr(models, row.get('model')).objects.all()
        f = filters.deep_filters_association.get(row.get('filter'))
        f = f(**row)
        dfm = filters.DeepFilterManager(filters=[f])
        qs2 = qs.filter(**{f'{row['field']}': row['value']})
        qs3 = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
        assert qs2.count() == qs3.count()
