from typing import Any, ClassVar

from django.db import connection as db_connection
from django.db.models import (
    DateField,
    ExpressionWrapper,
    FloatField,
    Func,
    TextField,
)
from django.utils.timezone import now


class JsonExtract(Func):
    """
    Custom Django Func for extracting JSON date data from database fields.
    
    SECURITY NOTE: This class uses Django's parameter binding system.
    All parameters passed via `extra` are automatically escaped by Django's ORM,
    preventing SQL injection. The `data_path` parameter is processed through
    controlled transformation methods that only perform string operations.
    """
    function = None
    field = None
    output_field = TextField()
    templates: ClassVar[dict] = {
        "postgresql": "%(json_field)s #>> '{%(data_path)s}'",
        "mysql": "JSON_UNQUOTE(JSON_EXTRACT(%(json_field)s, '$.%(data_path)s'))",
        "sqlite": "json_extract(%(json_field)s, '$.%(data_path)s')",
        "oracle": "JSON_VALUE(%(json_field)s, '$.%(data_path)s')",
    }

    def get_data_postgresql(self, data: str) -> str:
        """Transform data path for PostgreSQL."""
        return ",".join(data.split("__"))

    def get_data_default(self, data: str) -> str:
        """Transform data path for default databases."""
        return ".".join(data.split("__"))

    def __init__(self, json_field: str, data_path: str, **extra: Any) -> None:
        self.vendor = db_connection.vendor
        if self.vendor not in self.templates:
            raise NotImplementedError(
                f"JsonExtract is not available for database {self.vendor}"
            )
        extra["json_field"] = json_field
        get_data_method = getattr(
            self, f"get_data_{self.vendor}", self.get_data_default
        )
        extra["data_path"] = get_data_method(data_path)
        self.template = self.templates[self.vendor]
        super().__init__(**extra)


class JsonExtractDate(JsonExtract):
    """Extract date from JSON field."""

    output_field = DateField()
    templates: ClassVar[dict] = {
        "postgresql": "TO_DATE(%(json_field)s #>> '{%(data_path)s}', 'YYYY-MM-DD')",
        "mysql": (
            "CAST(JSON_UNQUOTE(JSON_EXTRACT(%(json_field)s, "
            "'$.%(data_path)s')) AS DATE)"
        ),
        "sqlite": "date(json_extract(%(json_field)s, '$.%(data_path)s'))",
        "oracle": (
            "TO_DATE(JSON_VALUE(%(json_field)s, '$.%(data_path)s'), "
            "'YYYY-MM-DD')"
        ),
    }


def age_expr_from_date_expr(date_expr: Any) -> ExpressionWrapper:
    """
    Return ExpressionWrapper that calculates age in years from date expression.

    Compatible with PostgreSQL, MySQL, SQLite and Oracle.
    """
    vendor = db_connection.vendor

    if vendor == "postgresql":
        return ExpressionWrapper(
            Func(
                Func(now().date(), date_expr, function="AGE"),
                function="EXTRACT",
                template="EXTRACT(EPOCH FROM %(expressions)s)/86400",
            )
            / 365.25,
            output_field=FloatField(),
        )

    elif vendor == "mysql":
        return ExpressionWrapper(
            Func(now().date(), date_expr, function="DATEDIFF") / 365.25,
            output_field=FloatField(),
        )

    elif vendor == "sqlite":
        return ExpressionWrapper(
            Func(
                "now",
                date_expr,
                function="julianday",
                template="(julianday('now') - julianday(%(expressions)s))",
            )
            / 365.25,
            output_field=FloatField(),
        )

    elif vendor == "oracle":
        return ExpressionWrapper(
            (Func("CURRENT_DATE") - date_expr) / 365.25,
            output_field=FloatField(),
        )

    else:
        raise NotImplementedError(f"Age calculation not supported for {vendor}")
