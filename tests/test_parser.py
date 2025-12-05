import pytest
from django.db.models import Count
from django.db import connection as db_connection
from django_deep import DeepParser
from tests.testapp import models
import csv
import logging

logger = logging.getLogger(__name__)


def check_order_by(row, qs, negative=False):
    field = row["field"]
    order = f"-{field}" if negative else field
    check = getattr(qs.order_by(order).last(), field)
    test = getattr(
        DeepParser(queryset=qs, order_enable=True, params={"o": order})
        .get_queryset()
        .last(),
        field,
    )
    logger.debug(f"order: {order}, check: {check}, test: {test}")
    assert test == check


def check_order_by_negative(row, qs):
    check_order_by(row, qs, negative=True)


def check_distinct(qs, test, check):
    initial = qs.count()
    check = check.count()
    test = test.get_queryset().count()
    logger.debug(f"check: {check}, test: {test}")
    assert test == check and check < initial and test < initial


def check_distinct_count(row, qs, negative=False):
    field = row["field"]
    qs = qs.filter(**{f"{field}__isnull": False})
    check = qs.annotate(Count("id"))
    test = DeepParser(queryset=qs, distinct="count")
    check_distinct(qs, test, check)


def check_distinct_bool(row, qs):
    field = row["field"]
    qs = qs.filter(**{f"{field}__isnull": False})
    check = qs.distinct()
    test = DeepParser(queryset=qs, distinct=True)
    check_distinct(qs, test, check)


def check_distinct_field(row, qs):
    if db_connection.vendor != "sqlite":
        field = row["field"]
        qs = qs.filter(**{f"{field}__isnull": False})
        check = qs.values(field).distinct(row["value"])
        test = DeepParser(queryset=qs, distinct=row["value"])
        check_distinct(qs, test, check)
    else:
        logger.warning("Distinct field test is not supported for SQLite, skipping.")


def check_distinct_list(row, qs):
    if db_connection.vendor != "sqlite":
        field = row["field"]
        qs = qs.filter(**{f"{field}__isnull": False})
        values = row["value"].split(":")
        check = qs.values(*values).distinct()
        test = DeepParser(queryset=qs, distinct_list=values)
        check_distinct(qs, test, check)
    else:
        logger.warning("Distinct list test is not supported for SQLite, skipping.")


# Mapping explicite des fonctions de test pour éviter l'utilisation de globals()
TEST_FUNCTIONS = {
    "order_by": check_order_by,
    "order_by_negative": check_order_by_negative,
    "distinct_count": check_distinct_count,
    "distinct": check_distinct_bool,
    "distinct_field": check_distinct_field,
    "distinct_list": check_distinct_list,
}


@pytest.mark.django_db
def test_queryset(setup_data):
    csv_file = "tests/testapp/csv/queryset.csv"
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            logger.info(f"Testing queryset: {row}")
            qs = getattr(models, row.get("model")).objects.all()
            test_name = row["test"]
            test_func = TEST_FUNCTIONS.get(test_name)
            if test_func:
                logger.debug(f"Running test: check_{test_name}")
                test_func(row, qs)
            test_negative_name = f"{test_name}_negative"
            test_negative_func = TEST_FUNCTIONS.get(test_negative_name)
            if test_negative_func:
                logger.debug(f"Running test: check_{test_negative_name}")
                test_negative_func(row, qs)
