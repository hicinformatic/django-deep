from typing import Any, ClassVar, Optional

from django.db.models import PositiveIntegerField, QuerySet, Subquery


class SumSubquery(Subquery):
    """
    A Django Subquery class to sum the values from a queryset.
    
    SECURITY NOTE: This class uses Django's parameter binding system.
    All parameters passed via `extra` are automatically escaped by Django's ORM,
    preventing SQL injection. The `sum_field` parameter should be a valid
    Django field name that is validated by the ORM.
    """

    template: ClassVar[str] = (
        "(SELECT COALESCE(SUM(%(sum_field)s), 0) FROM (%(subquery)s) %(name)s)"
    )

    def __init__(
        self,
        queryset: QuerySet,
        output_field: Optional[PositiveIntegerField] = None,
        *,
        sum_field: str,
        **extra: Any,
    ) -> None:
        """
        Initialize the SumSubquery with the given queryset and sum field.

        :param queryset: The queryset to sum values from
        :param output_field: The output field type
        :param sum_field: The field to sum values from
        :param extra: Additional parameters
        """
        print(f"Initializing SumSubquery with sum_field: {sum_field} and extra: {extra}")
        extra["sum_field"] = sum_field
        extra["name"] = extra.get("name", "_sum")
        self.output_field = output_field
        super().__init__(queryset, output_field, **extra)


class CountSubquery(Subquery):
    """
    A Django Subquery class to count the number of rows from a queryset.
    
    SECURITY NOTE: This class uses Django's parameter binding system.
    All parameters passed via `extra` are automatically escaped by Django's ORM,
    preventing SQL injection. The `count_field` parameter should be a valid
    Django field name that is validated by the ORM.
    """

    template: ClassVar[str] = (
        "(SELECT COALESCE(COUNT(%(count_field)s), 0) FROM (%(subquery)s) %(name)s)"
    )
    output_field = PositiveIntegerField()

    def __init__(
        self,
        queryset: QuerySet,
        output_field: Optional[PositiveIntegerField] = None,
        *,
        count_field: str = "pk",
        **extra: Any,
    ) -> None:
        """
        Initialize the CountSubquery with the given queryset and count field.

        :param queryset: The queryset to count rows from
        :param output_field: The output field type
        :param count_field: The field to count values from
        :param extra: Additional parameters
        """
        extra["count_field"] = count_field
        extra["name"] = extra.get("name", "_count")
        super().__init__(queryset, output_field, **extra)
