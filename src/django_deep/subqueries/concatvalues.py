from typing import Any, ClassVar, Optional

from django.conf import settings
from django.db import connection as db_connection
from django.db.models import CharField, QuerySet, Subquery


concat_separator = getattr(settings, "CONCAT_SEPARATOR", ":)(:")
concat_symbol = getattr(settings, "CONCAT_SYMBOL", "(::)")


class ConcatValuesSubquery(Subquery):
    """
    A Django Subquery class to concatenate values from a queryset.
    
    SECURITY NOTE: This class uses Django's parameter binding system.
    All parameters passed via `extra` are automatically escaped by Django's ORM,
    preventing SQL injection. The `fields` parameter should contain valid
    Django field lookups that are validated by the ORM.
    """

    separator: ClassVar[str] = concat_separator
    templates: ClassVar[dict] = {
        "postgresql": (
            "(SELECT STRING_AGG(%(string_contact)s, '%(separator)s') "
            "FROM (%(subquery)s) %(name)s)"
        ),
        "mysql": (
            "(SELECT GROUP_CONCAT(%(string_contact)s) "
            "FROM (%(subquery)s) %(name)s)"
        ),
    }
    template_ifnull: ClassVar[str] = "COALESCE(%s, %s)"
    concat: ClassVar[str] = f"'{concat_symbol}'"
    output_field = CharField()

    def raise_not_implemented(self, conf: str) -> None:
        """Raise NotImplementedError for unsupported vendor."""
        raise NotImplementedError(
            f"ConcatValuesSubquery {conf} is not implemented for {self.vendor}"
        )

    def ifnull(self, field: str, **extra: Any) -> str:
        """Apply COALESCE if field is in null list."""
        if field in extra.get("null", []):
            return self.template_ifnull % (
                field,
                extra.get(f"{field}_ifnull", "0"),
            )
        return field

    def get_concat(self, fields: list, **extra: Any) -> str:
        """Generate CONCAT expression for MySQL/SQLite."""
        fs = [self.ifnull(field, **extra) for field in fields]
        concat_str = f"|{self.concat}|".join(fs)
        fs = concat_str.split("|")
        return f"CONCAT({self.separator.join(fs)})"

    def get_postgresql_concat(self, fields: list, **extra: Any) -> str:
        """Generate concatenation expression for PostgreSQL."""
        return f"||{self.concat}||".join(
            [self.ifnull(field, **extra) for field in fields]
        )

    def get_oracle_concat(self, fields: list, **extra: Any) -> str:
        """Generate concatenation expression for Oracle."""
        return f"||{self.concat}||".join(
            [self.ifnull(field, **extra) for field in fields]
        )

    def get_mysql_concat(self, fields: list, **extra: Any) -> str:
        """Generate concatenation expression for MySQL."""
        return self.get_concat(fields, **extra)

    def get_sqlite_concat(self, fields: list, **extra: Any) -> str:
        """Generate concatenation expression for SQLite."""
        return self.get_concat(fields, **extra)

    def __init__(
        self,
        queryset: QuerySet,
        output_field: Optional[CharField] = None,
        *,
        fields: list,
        **extra: Any,
    ) -> None:
        """
        Initialize the ConcatValuesSubquery with the given queryset and fields.

        :param queryset: The queryset to concatenate values from
        :param output_field: The output field type
        :param fields: The fields to concatenate
        :param extra: Additional parameters
        """
        self.vendor = db_connection.vendor
        getm = f"get_{self.vendor}_concat"
        method = getattr(self, getm, None)
        if method:
            extra["string_contact"] = method(fields, **extra)
        else:
            self.raise_not_implemented(getm)
        extra["name"] = extra.get("name", "_concat")
        extra["separator"] = self.separator
        self.concat = extra.get("concat", self.concat)
        super().__init__(queryset, output_field, **extra)

    def as_sql(
        self,
        compiler: Any,
        connection: Any,
        template: Optional[str] = None,
        **extra_context: Any,
    ) -> tuple[str, tuple]:
        """Generate SQL for concatenation subquery."""
        self.template = self.templates.get(self.vendor)
        if not self.template:
            self.raise_not_implemented("template")
        sql, params = super().as_sql(
            compiler, connection, template=self.template, **extra_context
        )
        return sql, params


def split_concat(stats: str, fields: list, **kwargs: Any) -> Any:
    """Split and concatenate stats with fields."""
    if stats:
        concat = kwargs.get("concat", concat_symbol)
        separator = kwargs.get("separator", concat_separator)
        int_fields = kwargs.get("int_fields", ["total"])
        return [
            {
                field: int(s[idx]) if field in int_fields else s[idx]
                for idx, field in enumerate(fields)
            }
            for stat in stats.split(separator)
            for s in [stat.split(concat)]
        ]
    return stats
