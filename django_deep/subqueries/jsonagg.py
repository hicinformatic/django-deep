from typing import ClassVar

from django.db import connection as db_connection
from django.db.models import JSONField, Subquery


class JsonAggSubquery(Subquery):
    """A Django Subquery class to aggregate JSON values from a queryset."""

    template = (
        '(SELECT %(vendor_method)s AS %(name)s FROM (%(subquery)s) subquery)'
    )
    templates: ClassVar[dict] = {
        'postgresql': 'json_agg(subquery)',
        'mysql': 'JSON_ARRAYAGG(subquery)',
        'sqlite': 'json_group_array(subquery)',
        'oracle': 'JSON_ARRAYAGG(subquery)',
    }

    def __init__(self, queryset, **extra):
        """
        Initialize the JsonAggSubquery with the given queryset.
        :param queryset: The queryset to aggregate JSON values from.
        :param extra: Additional parameters.
        """
        self.vendor = db_connection.vendor
        if self.vendor not in self.templates:
            raise NotImplementedError(
                f'JsonAggSubquery is not implemented for {self.vendor}'
            )
        extra['vendor_method'] = self.templates[self.vendor]
        extra['name'] = extra.get('name', '_json_data')
        super().__init__(queryset, output_field=JSONField(), **extra)
