from django.db.models import Manager
from functions import JsonExtract
from subqueries import (
    ConcatValuesSubquery,
    CountSubquery,
    SumSubquery,
    JsonAggSubquery,
    MethodFromSubquery,
)


class DeepManager(Manager):
    """A custom manager"""

    select_related = ()
    prefetch_related = ()

    # Simplification en regroupant la logique des sous-requêtes dans une méthode générique
    def get_subquery(self, queryset, subquery_class, **extra):
        return subquery_class(queryset, **extra)

    def get_json_extract(self, json_field, data_path):
        return JsonExtract(json_field, data_path)

    def get_prefetch_related(self, prefetch_related):
        return (
            getattr(self, f'prefetch_{pr}', pr) for pr in prefetch_related
        )

    def auto_related(self, **kwargs):
        qs = super().get_queryset()
        select_related = kwargs.get('select_related', self.select_related)
        prefetch_related = kwargs.get('prefetch_related', self.prefetch_related)
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*self.get_prefetch_related(prefetch_related))
        return qs

    # Méthodes spécialisées pour chaque sous-requête
    def get_sum_sub_query(self, queryset, sum_field, **extra):
        return self.get_subquery(queryset, SumSubquery, sum_field=sum_field, **extra)

    def get_count_sub_query(self, queryset, count_field='pk', **extra):
        return self.get_subquery(queryset, CountSubquery, count_field=count_field, **extra)

    def get_concat_values_sub_query(self, queryset, fields, **extra):
        return self.get_subquery(queryset, ConcatValuesSubquery, fields=fields, **extra)

    def get_method_from_sub_query(self, queryset, agg_field, **extra):
        return self.get_subquery(queryset, MethodFromSubquery, agg_field=agg_field, **extra)

    def get_json_agg_sub_query(self, queryset, **extra):
        return self.get_subquery(queryset, JsonAggSubquery, **extra)
