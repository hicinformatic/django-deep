from typing import Any, Optional

from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet


class DeepFilterManager:
    """
    Manager for handling and applying filters to querysets.

    Provides functionality to activate filters based on params, check for
    mandatory filters, and apply active filters to a queryset.
    """

    def __init__(
        self,
        filters: Optional[list] = None,
        mandatory_filters: Optional[list] = None,
    ):
        """
        Initialize the filter manager.

        :param filters: List of filter instances to apply
        :param mandatory_filters: List of mandatory filter names
        """
        self.filters = filters or []
        self.mandatory_filters = mandatory_filters or []

    def activate_filter(
        self, params: dict, filter_instance: Any
    ) -> Optional[Any]:
        """
        Activate a filter based on URL parameter.

        Filter is activated if parameter exists and is not None.
        If `-=` operator is found in value, marks filter as negated.
        """
        param_name = filter_instance.field
        filter_value = params.get(param_name)

        negate = filter_value and filter_value.startswith("-=")
        if negate:
            filter_value = filter_value[2:]

        if filter_value:
            activated_filter = filter_instance.__class__(
                field=filter_instance.field, value=filter_value
            )

            if negate:
                activated_filter = self.apply_negation(activated_filter)

            return activated_filter
        return None

    def apply_negation(self, filter_instance: Any) -> Q:
        """
        Apply negation logic to a filter.

        Uses ~ operator to invert filter effect in Django ORM.
        """
        return Q(~filter_instance.filter())

    def check_mandatory_filters(self, params: dict) -> bool:
        """Check if all mandatory filters are present in request."""
        for mandatory_filter in self.mandatory_filters:
            if not params.get(mandatory_filter):
                raise PermissionDenied(
                    f"Mandatory filter '{mandatory_filter}' is missing."
                )
        return True

    def get_active_filters(self, params: dict) -> list:
        """
        Return list of activated filters based on request parameters.
        """
        self.check_mandatory_filters(params)

        active_filters = []
        for filter_instance in self.filters:
            activated_filter = self.activate_filter(params, filter_instance)
            if activated_filter:
                active_filters.append(activated_filter)
        return active_filters

    def apply_filters(self, queryset: QuerySet, params: dict) -> QuerySet:
        """Apply all activated filters to a queryset."""
        active_filters = self.get_active_filters(params)
        if active_filters:
            combined_filter = Q()
            for filter_instance in active_filters:
                combined_filter &= filter_instance.filter()
            queryset = queryset.filter(combined_filter)
        return queryset
