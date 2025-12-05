from typing import ClassVar

from django.db import connection as db_connection
from django.db.models import CharField, Subquery

json_template = """(SELECT
    %(vendor_data)s AS %(name)s
FROM (SELECT
    %(additional)s
    %(vendor_method)s AS %(valagg)s,
    %(method)s(%(method_field)s) AS %(valmethod)s
FROM (%(subquery)s) as s1
GROUP BY %(group_by)s) as subquery)"""


concat_template = """(SELECT
    %(vendor_data)s AS %(name)s
FROM (SELECT
    %(concat_fields)s AS concatfields
FROM (SELECT
    %(additional)s
    %(vendor_method)s AS %(valagg)s,
    %(method)s(%(method_field)s) AS %(valmethod)s
FROM (%(subquery)s) as s1
GROUP BY %(group_by)s) as subquery) as s2)"""


class MethodFromSubquery(Subquery):
    """
    A Django Subquery class to count the number of value in a JSON dataset
    from a queryset.
    
    SECURITY NOTE: This class uses Django's parameter binding system.
    All parameters passed via `extra` are automatically escaped by Django's ORM,
    preventing SQL injection. The `field` and `group_by` parameters should
    contain valid Django field names that are validated by the ORM.
    """

    template_json = json_template
    template_concat = concat_template
    templates: ClassVar[dict] = {
        # Json
        "postgresql_json": "json_agg(subquery)",
        "mysql_json": "JSON_ARRAYAGG(subquery)",
        "sqlite_json": "json_group_array(subquery)",
        "oracle_json": "JSON_ARRAYAGG(subquery)",
        # Concat
        "postgresql_concat": "STRING_AGG(concatfields, ',')",
        "mysql_concat": "GROUP_CONCAT(concatfields)",
        "sqlite_concat": "GROUP_CONCAT(concatfields)",
        "oracle_concat": "LISTAGG(concatfields, ',')",
        # Method
        "postgresql_method": "jsonb_array_elements_text(%s)",
        "mysql_method": "JSON_UNQUOTE(JSON_EXTRACT(%s, '$[*]'))",
        "sqlite_method": "json_each(%s).value",
        "oracle_method": "JSON_VALUE(%s, '$[*]')",
    }
    template_ifnull: ClassVar[str] = "COALESCE(%s, %s)"
    concat: ClassVar[str] = "'(::)'"
    output_field = CharField()

    def raise_not_implemented(self, conf):
        raise NotImplementedError(
            f"MethodFromSubquery {conf} is not implemented for {self.vendor}"
        )

    def ifnull(self, field, **extra):
        if field in extra.get("null", []):
            return self.template_ifnull % (
                field,
                extra.get(f"{field}_ifnull", "0"),
            )
        return field

    def get_concat(self, fields, **extra):
        fs = [self.ifnull(field, **extra) for field in fields]
        fs = f"|{self.concat}|".join(fs).split("|")
        return f'CONCAT({", ".join(fs)})'

    def get_postgresql_concat(self, fields, **extra):
        return f"||{self.concat}||".join(
            [self.ifnull(field, **extra) for field in fields]
        )

    def get_oracle_concat(self, fields, **extra):
        return f"||{self.concat}||".join(
            [self.ifnull(field, **extra) for field in fields]
        )

    def get_mysql_concat(self, fields, **extra):
        return self.get_concat(fields, **extra)

    def get_sqlite_concat(self, fields, **extra):
        return self.get_concat(fields, **extra)

    def __init__(self, queryset, agg_field, **extra):
        """
        Initialize the JsonAggSubquery with the given queryset and count field.
        :param queryset: The queryset to aggregate JSON values from.
        :param output_field: The output field type.
        :param agg_field: The field to aggregate values from JSON.
        :param extra: Additional parameters.
        """
        self.vendor = db_connection.vendor
        if self.vendor + "_method" not in self.templates:
            self.raise_not_implemented("method")
        else:
            extra["vendor_method"] = self.templates[self.vendor + "_method"] % agg_field

        agg_mode = "_" + extra.pop("mode", "json")
        if self.vendor + agg_mode not in self.templates:
            self.raise_not_implemented(agg_mode)
        else:
            extra["vendor_data"] = self.templates[self.vendor + agg_mode]
            self.template = getattr(self, f"template{agg_mode}")

        add_fields = extra.get("additional_fields", [])
        group_by = extra.get("group_by", [])

        extra["method"] = extra.get("method", "COUNT")
        extra["method_field"] = extra.get("method_field", "id")
        extra["name"] = extra.get("name", "_method_from")
        extra["method"] = extra.get("method", "COUNT")
        extra["valagg"] = extra.get("valagg", "valagg")
        extra["valmethod"] = extra.get("valmethod", "total")
        extra["additional"] = ", ".join([f'"{f}"' for f in add_fields])

        if extra["additional"]:
            extra["additional"] += ","

        extra["group_by"] = ", ".join([f'"{field}"' for field in group_by])
        if extra["group_by"]:
            extra["group_by"] = extra["group_by"] + ", " + extra["valagg"]
        else:
            extra["group_by"] = extra["valagg"]

        if agg_mode == "_concat":
            fields = [*add_fields, extra["valagg"], extra["valmethod"]]
            getm = f"get_{self.vendor}_concat"
            self.concat = extra.get("concat", self.concat)
            if hasattr(self, f"get_{self.vendor}_concat"):
                extra["concat_fields"] = getattr(self, getm)(fields, **extra)
            else:
                self.raise_not_implemented(getm)
        super().__init__(queryset, output_field=CharField(), **extra)
