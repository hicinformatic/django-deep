from typing import Any, ClassVar

from django.db import connection as db_connection
from django.db.models import JSONField, QuerySet, Subquery


class JsonAggSubquery(Subquery):
    """
    A Django Subquery class to aggregate JSON values from a queryset.
    
    SECURITY NOTE: This class uses Django's parameter binding system.
    All parameters passed via `extra` are automatically escaped by Django's ORM,
    preventing SQL injection.
    """

    template: ClassVar[str] = (
        "(SELECT %(vendor_method)s AS %(name)s FROM (%(subquery)s) subquery)"
    )
    templates: ClassVar[dict] = {
        "postgresql": "json_agg(subquery)",
        "mysql": "JSON_ARRAYAGG(subquery)",
        "sqlite": "json_group_array(subquery)",
        "oracle": "JSON_ARRAYAGG(subquery)",
    }

    def __init__(self, queryset: QuerySet, **extra: Any) -> None:
        """
        Initialize the JsonAggSubquery with the given queryset.

        :param queryset: The queryset to aggregate JSON values from
        :param extra: Additional parameters
        """
        self.vendor = db_connection.vendor
        vendor_method = self.templates.get(self.vendor)
        if not vendor_method:
            raise NotImplementedError(
                f"JsonAggSubquery is not implemented for {self.vendor}"
            )
        extra["vendor_method"] = vendor_method
        extra["name"] = extra.get("name", "_json_data")
        super().__init__(queryset, output_field=JSONField(), **extra)
