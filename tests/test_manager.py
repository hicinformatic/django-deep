import pytest
from testapp.setup import setup_data, secure_datetime, secure_time
from django_deep import filters
from tests.testapp import models
import csv, logging

logger = logging.getLogger(__name__)


def get_filter_by(filter_type):
    csv_file = 'tests/testapp/csv/filters.csv'
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['filter'] == filter_type:
                yield row


def check_list_filter(row):
    return {f"{row['field']}__in": row['value'].split(',')}


def check_string_filter(row):
    return {f"{row['field']}__in": row['value'].split(',')}


def check_boolean_filter(row):
    return {f"{row['field']}": row['value'].lower() in ['true', '1', 'yes']}


def check_integer_filter(row):
    return {f"{row['field']}": row['value']}


def check_float_filter(row):
    return {f"{row['field']}": row['value']}


def check_decimal_filter(row):
    return {f"{row['field']}": row['value']}


def check_time_filter(row):
    return {f"{row['field']}": row['value']}


def check_date_filter(row):
    return {f"{row['field']}": row['value']}


def get_filters(row_filter, row):
    try:
        fname = f"check_{row_filter}_filter"
        return globals()[fname](row)
    except Exception:
        return {f"{row['field']}": row['value']}


@pytest.mark.django_db
def test_filters(setup_data):
    csv_file = 'tests/testapp/csv/filters.csv'
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            qs = getattr(models, row.get('model')).objects.all()
            row_filter = row.get('filter')
            logger.info("test filter: %s" % row_filter)
            df = filters.deep_filters_association.get(row_filter)
            if row.get('choices'):
                df.choices = row['choices'].split(':')
            if row_filter == 'datetime':
                row['value'] = str(secure_datetime(row['value'], False))
            if row_filter == 'time':
                row['value'] = str(secure_time(row['value']))
            df = df(**row)
            dfm = filters.DeepFilterManager(filters=[df])
            native_filter = get_filters(row_filter, row)
            logging.debug("native filter: %s" % native_filter)
            qs_check = qs.filter(**native_filter)
            qs_test = dfm.apply_filters(queryset=qs, params={row['field']: row['value']})
            assert qs_check.count() == qs_test.count()

