from typing import ClassVar

from django.db.models import PositiveIntegerField, Subquery


class SumSubquery(Subquery):
    """A Django Subquery class to sum the values from a queryset."""

    template: ClassVar[str] = (
        '(SELECT COALESCE(SUM(%(sum_field)s), 0) FROM (%(subquery)s) %(name)s)'
    )
    output_field = PositiveIntegerField()

    def __init__(self, queryset, output_field=None, *, sum_field, **extra):
        """
        Initialize the SumSubquery with the given queryset and sum field.
        :param queryset: The queryset to sum values from.
        :param output_field: The output field type.
        :param sum_field: The field to sum values from.
        :param extra: Additional parameters.
        """
        extra['sum_field'] = sum_field
        extra['name'] = extra.get('name', '_sum')
        super().__init__(queryset, output_field, **extra)


class CountSubquery(Subquery):
    """A Django Subquery class to count the number of rows from a queryset."""

    template: ClassVar[str] = (
        '(SELECT COALESCE(Count(%(count_field)s), 0) FROM (%(subquery)s) %(name)s)'
    )
    output_field = PositiveIntegerField()

    def __init__(
        self, queryset, output_field=None, *, count_field='pk', **extra
    ):
        """
        Initialize the JsonAggSubquery with the given queryset and count field.
        :param queryset: The queryset to aggregate JSON values from.
        :param output_field: The output field type.
        :param count_field: The field to count values from.
        :param extra: Additional parameters.
        """
        extra['count_field'] = count_field
        extra['name'] = extra.get('name', '_count')
        super().__init__(queryset, output_field, **extra)
