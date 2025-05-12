import pytest
import csv


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
            user, created = User.objects.get_or_create(username=row['username'])
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
