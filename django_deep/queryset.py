from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.db.models.sql import Query


class MemoryQuerySet(QuerySet):
    """A QuerySet that operates in memory, useful for testing or when the data is already loaded."""

    def __init__(
        self, model=None, data=None, query=None, using=None, hints=None
    ):
        if query is None and model is not None:
            query = Query(model)
        super().__init__(model=model, query=query, using=using, hints=hints)
        self._result_cache = list(data or [])
        self._prefetch_done = True

    def __len__(self):
        return len(self._result_cache)

    def __getitem__(self, k):
        if isinstance(k, slice):
            return self.__class__(
                self.model,
                self._result_cache[k],
                self.query.clone(),
                using=self._db,
                hints=self._hints,
            )
        return self._result_cache[k]

    def _clone(self):
        return self.__class__(
            self.model,
            list(self._result_cache),
            self.query.clone(),
            using=self._db,
            hints=self._hints,
        )

    def all(self):
        return self._clone()

    def count(self):
        return len(self._result_cache)

    def filter(self, *args, **kwargs):
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

    def order_by(self, *fields):
        rslt = self._result_cache
        for field in reversed(fields):
            reverse = False
            if field.startswith('-'):
                reverse = True
                field = field[1:]  # noqa: PLW2901
            rslt = sorted(
                rslt, key=lambda x: getattr(x, field, None), reverse=reverse
            )
        return self.__class__(
            self.model,
            rslt,
            self.query.clone(),
            using=self._db,
            hints=self._hints,
        )

    def get(self, **kwargs):
        rslt = self._result_cache
        for attr, value in kwargs.items():
            rslt = [obj for obj in rslt if getattr(obj, attr) == value]

        if len(rslt) == 1:
            return rslt[0]
        if not rslt:
            raise ObjectDoesNotExist(
                f'{self.model.__name__} matching query does not exist.'
            )
        raise MultipleObjectsReturned(
            f'Multiple {self.model.__name__} objects returned.'
        )
