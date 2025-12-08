from typing import Any, ClassVar, Optional

from django.conf import settings
from django.db import connection as db_connection
from django.db.models import CharField, Field, QuerySet, Subquery


concat_symbol = getattr(settings, "CONCAT_SYMBOL", "(::)")


class ExtractValueSubquery(Subquery):
    """
    A Django Subquery class to extract the value of a column
    from the first row of a queryset.
    
    SECURITY NOTE: This class uses Django's parameter binding system.
    All parameters passed via `extra` are automatically escaped by Django's ORM,
    preventing SQL injection. The `field` parameter should be a valid
    Django field name that is validated by the ORM.
    """

    template: ClassVar[str] = (
        "(SELECT COALESCE(%(field)s, %(default)s) FROM (%(subquery)s) %(name)s LIMIT 1)"
    )

    def __init__(
        self,
        queryset: QuerySet,
        output_field: Optional[Field] = None,
        *,
        field: str = "pk",
        default: Any = None,
        **extra: Any,
    ) -> None:
        """
        Initialize the ExtractValueSubquery.

        :param queryset: The queryset to select from
        :param output_field: The output field type
            (e.g., IntegerField, CharField, DateField)
        :param field: The field to extract from the first row
        :param default: Value to return if no row exists
        :param extra: Additional parameters
        """
        extra["field"] = field
        extra["default"] = repr(default) if default is not None else "NULL"
        extra["name"] = extra.get("name", "_first_value")
        super().__init__(queryset, output_field, **extra)


class ExtractMultipleValuesSubquery(Subquery):
    """
    A Django Subquery class to extract multiple column values
    from the first row of a queryset and concatenate them into a single string.
    
    SECURITY NOTE: This class uses Django's parameter binding system.
    All parameters passed via `extra` are automatically escaped by Django's ORM,
    preventing SQL injection. The `fields` parameter should contain valid
    Django field names that are validated by the ORM.
    """

    template: ClassVar[str] = (
        "(SELECT COALESCE(%(string_concat)s, %(default)s) "
        "FROM (%(subquery)s) %(name)s LIMIT 1)"
    )
    output_field = CharField()
    concat: ClassVar[str] = f"'{concat_symbol}'"

    def __init__(
        self,
        queryset: QuerySet,
        output_field: Optional[CharField] = None,
        *,
        fields: list,
        default: Any = None,
        **extra: Any,
    ) -> None:
        """
        Initialize ExtractMultipleValuesSubquery.

        :param queryset: The queryset to select from
        :param output_field: The output field type
        :param fields: List of fields to concatenate from the first row
        :param default: Value to return if no row exists
        :param extra: Additional parameters
        """
        self.vendor = db_connection.vendor
        if self.vendor == "postgresql":
            string_concat = f" || {self.concat} || ".join(fields)
        else:
            string_concat = f"CONCAT({', '.join(fields)})"
        extra["string_concat"] = string_concat
        extra["default"] = repr(default) if default is not None else "NULL"
        extra["name"] = extra.get("name", "_first_row_concat")
        super().__init__(queryset, output_field or CharField(), **extra)
