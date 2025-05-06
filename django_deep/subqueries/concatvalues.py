from typing import ClassVar

from django.db import connection as db_connection
from django.db.models import CharField, Subquery


class ConcatValuesSubquery(Subquery):
    """A Django Subquery class to concatenate values from a queryset."""

    templates: ClassVar[dict] = {
        'postgresql': "(SELECT STRING_AGG(%(string_contact)s, ',') FROM (%(subquery)s) %(name)s)",
        'mysql': '(SELECT GROUP_CONCAT(%(string_contact)s) FROM (%(subquery)s) %(name)s)',
    }
    template_ifnull: ClassVar[str] = 'COALESCE(%s, %s)'
    concat: ClassVar[str] = "'(::)'"
    output_field = CharField()

    def raise_not_implemented(self, conf):
        raise NotImplementedError(
            f'ConcatValuesSubquery {conf} is not implemented for {self.vendor}'
        )

    def ifnull(self, field, **extra):
        if field in extra.get('null', []):
            return self.template_ifnull % (
                field,
                extra.get(f'{field}_ifnull', '0'),
            )
        return field

    def get_concat(self, fields, **extra):
        fs = [self.ifnull(field, **extra) for field in fields]
        fs = f'|{self.concat}|'.join(fs).split('|')
        return f'CONCAT({", ".join(fs)})'

    def get_postgresql_concat(self, fields, **extra):
        return f'||{self.concat}||'.join([
            self.ifnull(field, **extra) for field in fields
        ])

    def get_oracle_concat(self, fields, **extra):
        return f'||{self.concat}||'.join([
            self.ifnull(field, **extra) for field in fields
        ])

    def get_mysql_concat(self, fields, **extra):
        return self.get_concat(fields, **extra)

    def get_sqlite_concat(self, fields, **extra):
        return self.get_concat(fields, **extra)

    def __init__(self, queryset, output_field=None, *, fields, **extra):
        """
        Initialize the ConcatValuesSubquery with the given queryset and fields.
        :param queryset: The queryset to concatenate values from.
        :param output_field: The output field type.
        :param fields: The fields to concatenate.
        :param extra: Additional parameters.
        """
        self.vendor = db_connection.vendor
        getm = f'get_{self.vendor}_concat'
        if hasattr(self, getm):
            extra['string_contact'] = getattr(self, getm)(fields, **extra)
        else:
            self.raise_not_implemented(getm)
        extra['name'] = extra.get('name', '_concat')
        self.concat = extra.get('concat', self.concat)
        super().__init__(queryset, output_field, **extra)

    def as_sql(self, compiler, connection, template=None, **extra_context):
        self.template = self.templates.get(self.vendor)
        if not self.template:
            self.raise_not_implemented('template')
        sql, params = super().as_sql(compiler, connection, template=self.template, **extra_context)
        return sql, params


def split_concat(stats, fields, **kwargs):
    """Split and concatenate stats with fields."""
    if stats:
        concat = kwargs.get('concat', '(::)')
        separator = kwargs.get('separator', ',')
        total = kwargs.get('total', 'total')
        return [
            {
                field: int(s[idx]) if field == total else s[idx]
                for idx, field in enumerate(fields)
            }
            for stat in stats.split(separator)
            for s in [stat.split(concat)]
        ]
    return stats
