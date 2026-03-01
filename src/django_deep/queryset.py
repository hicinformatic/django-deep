from typing import Any, Optional

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Model
from django.db.models.query import QuerySet
from django.db.models.sql import Query


class MemoryQuerySet(QuerySet):
    """
    A QuerySet that operates in memory,
    useful for testing or when the data is already loaded.
    """

    def __init__(
        self,
        model: Optional[Model] = None,
        data: Optional[list] = None,
        query: Optional[Query] = None,
        using: Optional[str] = None,
        hints: Optional[dict] = None,
    ) -> None:
        if query is None and model is not None:
            query = Query(model)
        super().__init__(model=model, query=query, using=using, hints=hints)
        self._result_cache = list(data or [])
        self._prefetch_done = True

    def __len__(self) -> int:
        """Return number of items in result cache."""
        return len(self._result_cache)

    def __getitem__(self, k: int | slice) -> Any:
        """Get item or slice from result cache."""
        if isinstance(k, slice):
            return self.__class__(
                self.model,
                self._result_cache[k],
                self.query.clone(),
                using=self._db,
                hints=self._hints,
            )
        return self._result_cache[k]

    def _clone(self) -> "MemoryQuerySet":
        """Clone queryset with copied result cache."""
        return self.__class__(
            self.model,
            list(self._result_cache),
            self.query.clone(),
            using=self._db,
            hints=self._hints,
        )

    def all(self) -> "MemoryQuerySet":
        """Return all items."""
        return self._clone()

    def count(self) -> int:
        """Return count of items in result cache."""
        return len(self._result_cache)

    def filter(self, *args: Any, **kwargs: Any) -> "MemoryQuerySet":
        """Filter result cache by attribute values."""
        rslt = self._result_cache
        for attr, value in kwargs.items():
            rslt = [obj for obj in rslt if getattr(obj, attr) == value]
        return self.__class__(
            self.model,
            rslt,
            self.query.clone(),
            using=self._db,
            hints=self._hints,
        )

    def order_by(self, *fields: str) -> "MemoryQuerySet":
        """Order result cache by fields."""
        rslt = self._result_cache
        for field in reversed(fields):
            reverse = False
            if field.startswith("-"):
                reverse = True
                field = field[1:]  # noqa: PLW2901
            rslt = sorted(rslt, key=lambda x: getattr(x, field, None), reverse=reverse)
        return self.__class__(
            self.model,
            rslt,
            self.query.clone(),
            using=self._db,
            hints=self._hints,
        )

    def get(self, **kwargs: Any) -> Any:
        """Get single object matching criteria."""
        rslt = self._result_cache
        for attr, value in kwargs.items():
            rslt = [obj for obj in rslt if getattr(obj, attr) == value]

        if len(rslt) == 1:
            return rslt[0]
        if not rslt:
            raise ObjectDoesNotExist(
                f"{self.model.__name__} matching query does not exist."
            )
        raise MultipleObjectsReturned(
            f"Multiple {self.model.__name__} objects returned."
        )
