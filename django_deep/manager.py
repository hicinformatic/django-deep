from typing import Any

from django.db.models import Manager, QuerySet

from .functions import JsonExtract
from .subqueries import (
    ConcatValuesSubquery,
    CountSubquery,
    JsonAggSubquery,
    MethodFromSubquery,
    SumSubquery,
)


class DeepManager(Manager):
    """Custom manager with subquery and JSON extraction support."""

    select_related: tuple = ()
    prefetch_related: tuple = ()

    def get_subquery(
        self, queryset: QuerySet, subquery_class: type, **extra: Any
    ) -> Any:
        """Generic method to create subqueries."""
        return subquery_class(queryset, **extra)

    def get_json_extract(self, json_field: str, data_path: str) -> JsonExtract:
        """Create JsonExtract expression."""
        return JsonExtract(json_field, data_path)

    def get_prefetch_related(self, prefetch_related: tuple) -> Any:
        """Get prefetch related configuration."""
        return (getattr(self, f"prefetch_{pr}", pr) for pr in prefetch_related)

    def auto_related(self, **kwargs: Any) -> QuerySet:
        """Apply select_related and prefetch_related optimizations."""
        qs = super().get_queryset()
        select_related = kwargs.get("select_related", self.select_related)
        prefetch_related = kwargs.get("prefetch_related", self.prefetch_related)
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*self.get_prefetch_related(prefetch_related))
        return qs

    def get_sum_sub_query(
        self, queryset: QuerySet, sum_field: str, **extra: Any
    ) -> Any:
        """Create SumSubquery."""
        return self.get_subquery(queryset, SumSubquery, sum_field=sum_field, **extra)

    def get_count_sub_query(
        self, queryset: QuerySet, count_field: str = "pk", **extra: Any
    ) -> Any:
        """Create CountSubquery."""
        return self.get_subquery(
            queryset, CountSubquery, count_field=count_field, **extra
        )

    def get_concat_values_sub_query(
        self, queryset: QuerySet, fields: list, **extra: Any
    ) -> Any:
        """Create ConcatValuesSubquery."""
        return self.get_subquery(
            queryset, ConcatValuesSubquery, fields=fields, **extra
        )

    def get_method_from_sub_query(
        self, queryset: QuerySet, agg_field: str, **extra: Any
    ) -> Any:
        """Create MethodFromSubquery."""
        return self.get_subquery(
            queryset,
            MethodFromSubquery,
            agg_field=agg_field,
            **extra,
        )

    def get_json_agg_sub_query(self, queryset: QuerySet, **extra: Any) -> Any:
        """Create JsonAggSubquery."""
        return self.get_subquery(queryset, JsonAggSubquery, **extra)
