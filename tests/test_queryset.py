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


def check_distinct_count(row, qs, negative=False):
    field = row["field"]
    qs = qs.filter(**{f"{field}__isnull": False})
    initial = qs.count()
    check = qs.annotate(Count("id")).count()
    test = DeepParser(queryset=qs, distinct="count").get_queryset().count()
    logger.debug(f"distinct: {field}, initial: {initial}, check: {check}, test: {test}")
    assert test == check and check < initial and test < initial


def check_distinct(row, qs):
    field = row["field"]
    qs = qs.filter(**{f"{field}__isnull": False})
    initial = qs.count()
    check = qs.distinct().count()
    test = DeepParser(queryset=qs, distinct=True).get_queryset().count()
    logger.debug(f"distinct: {field}, initial: {initial}, check: {check}, test: {test}")
    assert test == check and check < initial and test < initial


def check_distinct_field(row, qs):
    if db_connection.vendor != "sqlite":
        field = row["field"]
        qs = qs.filter(**{f"{field}__isnull": False})
        initial = qs.count()
        check = qs.values(field).distinct(row["value"]).count()
        test = DeepParser(queryset=qs, distinct=row["value"]).get_queryset().count()
        logger.debug(
            f"distinct: {field}, initial: {initial}, check: {check}, test: {test}"
        )
        assert test == check and check < initial and test < initial
    else:
        logger.warning("Distinct field test is not supported for SQLite, skipping.")


def check_distinct_list(row, qs):
    if db_connection.vendor != "sqlite":
        field = row["field"]
        qs = qs.filter(**{f"{field}__isnull": False})
        initial = qs.count()
        values = row["value"].split(":")
        check = qs.values(*values).distinct().count()
        test = DeepParser(queryset=qs, distinct_list=values).get_queryset().count()
        logger.debug(
            f"distinct: {field}, initial: {initial}, check: {check}, test: {test}"
        )
        assert test == check and check < initial and test < initial
    else:
        logger.warning("Distinct list test is not supported for SQLite, skipping.")


# Explicit mapping of test functions to avoid using globals()
TEST_FUNCTIONS = {
    "order_by": check_order_by,
    "order_by_negative": check_order_by_negative,
    "distinct_count": check_distinct_count,
    "distinct": check_distinct,
    "distinct_field": check_distinct_field,
    "distinct_list": check_distinct_list,
}


@pytest.mark.django_db
def test_queryset(setup_data):
    csv_file = "tests/testapp/csv/queryset.csv"
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
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
