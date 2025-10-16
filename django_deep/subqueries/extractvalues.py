from django.db import connection as db_connection
from django.conf import settings
from django.db.models import Subquery, Field, CharField, Subquery
from typing import ClassVar


concat_symbol = getattr(settings, 'CONCAT_SYMBOL', '(::)')


class ExtractValueSubquery(Subquery):
    """
    A Django Subquery class to extract the value of a column from the first row of a queryset.
    """

    template: ClassVar[str] = (
        '(SELECT COALESCE(%(field)s, %(default)s) FROM (%(subquery)s) %(name)s LIMIT 1)'
    )

    def __init__(self, queryset, output_field: Field = None, *, field='pk', default=None, **extra):
        """
        Initialize the ExtractValueSubquery.

        :param queryset: The queryset to select from.
        :param output_field: The output field type (e.g., IntegerField, CharField, DateField).
        :param field: The field to extract from the first row.
        :param default: Value to return if no row exists.
        :param extra: Additional parameters.
        """
        extra['field'] = field
        extra['default'] = repr(default) if default is not None else 'NULL'
        extra['name'] = extra.get('name', '_first_value')
        super().__init__(queryset, output_field, **extra)


class ExtractMultipleValuesSubquery(Subquery):
    """
    A Django Subquery class to extract multiple column values from the first row
    of a queryset and concatenate them into a single string.
    """

    template: ClassVar[str] = (
        '(SELECT COALESCE(%(string_concat)s, %(default)s) FROM (%(subquery)s) %(name)s LIMIT 1)'
    )
    output_field = CharField()
    concat: ClassVar[str] = f"'{concat_symbol}'"

    def __init__(self, queryset, output_field=None, *, fields, default=None, **extra):
        """
        :param queryset: The queryset to select from.
        :param output_field: The output field type.
        :param fields: List of fields to concatenate from the first row.
        :param default: Value to return if no row exists.
        :param extra: Additional parameters.
        """
        self.vendor = db_connection.vendor
        # Générer la concaténation des colonnes
        string_concat = f" || {self.concat} || ".join(fields) if self.vendor == 'postgresql' else f"CONCAT({', '.join(fields)})"
        extra['string_concat'] = string_concat
        extra['default'] = repr(default) if default is not None else 'NULL'
        extra['name'] = extra.get('name', '_first_row_concat')
        super().__init__(queryset, output_field or CharField(), **extra)
