import pytest
from .setup import setup_data
from tests import models
import csv


def check_result(qst, format, result):
    """
    Vérifie si le résultat de la requête correspond à la valeur attendue.
    """
    if format == 'count':
        check = qst.count()
    elif format == 'len':
        check = len(qst)

    if check == result:
        print(f"Test passed for {qst.model} with result {result} and format {format}")
    else:
        raise AssertionError(f"Expected {result} but got {check} for {qst.model} with format {format}")


@pytest.mark.django_db
def test_filters(setup_data):
    csv_file = 'tests/filters.csv'
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            mdl = getattr(models, row['model'])
            qst = mdl.objects.all()
            flt = getattr(mdl, row['filter'])(field=row['field'], value=row['value'])
            qst = qst.filter(flt.filter())
            check_result(qst, row['format'], row['result'])


@pytest.mark.django_db
def test_filtermanager(setup_data):
    """
    Teste le gestionnaire de filtres.
    """
