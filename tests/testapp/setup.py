import pytest
import csv
from datetime import datetime, date
from django.utils import timezone
from django.utils.dateparse import parse_time


def secure_datetime(dt, iso=True):
    """
    Retourne un datetime timezone-aware. Si le datetime est naïf, le convertit en timezone active.
    """
    if not iso:
        dt = datetime.fromisoformat(dt)
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


def secure_time(t):
    today = date.today()
    parsed_time = parse_time(t)
    naive_dt = datetime.combine(today, parsed_time)
    aware_dt = secure_datetime(naive_dt)
    return aware_dt.time()


@pytest.fixture
def setup_data(db):
    """
    Remplit la base de données de test avec des données de base.
    """
    from tests.testapp.models import Role, User, Email
    csv_file = 'tests/testapp/csv/db.csv'
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            role, created = Role.objects.get_or_create(name=row['role'])

            data = {}
            #if row['created_at']:
            #    data['created_at'] = secure_datetime(row['created_at'], False).isoformat()
            if row['date_at']:
                data['date_at'] = secure_datetime(row['date_at'], False).date()
            if row['time_at']:
                data['time_at'] = secure_time(row['time_at'])
            user, created = User.objects.get_or_create(username=row['username'], **data)

            Email.objects.get_or_create(email=row['email'], user=user)
            user.roles.add(role)

    roles = Role.objects.all()
    for role in roles:
        role.nb_users = role.roles_to_users.count()
        role.save()


def get_filters_config(filters):
    csv_file = 'tests/testapp/csv/filters.csv'
    with open(csv_file, 'r') as file:
        filters_cfg = {}
        reader = csv.DictReader(file)
        for row in reader:
            if not filters_cfg.get(row.get('field')):
                flt = filters.get(row.get('filter'))
                filters_cfg[row['field']] = flt(**row)
        return filters_cfg
