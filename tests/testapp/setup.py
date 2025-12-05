import csv

import pytest

from django_deep.filters import secure_datetime, secure_time


@pytest.fixture
def setup_data(db):
    """
    Remplit la base de données de test avec des données de base.
    """
    from tests.testapp.models import Role, User, Email

    csv_file = "tests/testapp/csv/db.csv"
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            role, created = Role.objects.get_or_create(name=row["role"])

            data = {}
            if row["created_at"]:
                data["created_at"] = secure_datetime(row["created_at"], False)
            if row["date_at"]:
                data["date_at"] = secure_datetime(row["date_at"], False).date()
            if row["time_at"]:
                data["time_at"] = secure_time(row["time_at"])
            user, created = User.objects.get_or_create(username=row["username"], **data)

            Email.objects.get_or_create(email=row["email"], user=user)
            for i in range(2):  # 2 emails par utilisateur
                Email.objects.get_or_create(
                    user=user, email=f"{user.username}_{i}@example.com"
                )
            user.roles.add(role)

    roles = Role.objects.all()
    for role in roles:
        role.nb_users = role.roles_to_users.count()
        role.save()


def get_filters_config(filters):
    csv_file = "tests/testapp/csv/filters.csv"
    with open(csv_file, "r") as file:
        filters_cfg = {}
        reader = csv.DictReader(file)
        for row in reader:
            if not filters_cfg.get(row.get("field")):
                flt = filters.get(row.get("filter"))
                filters_cfg[row["field"]] = flt(**row)
        return filters_cfg
