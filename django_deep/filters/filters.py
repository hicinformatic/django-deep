from django.db.models import Q
import decimal
from datetime import datetime, date
from django.utils import timezone
from django.utils.dateparse import parse_time


def secure_datetime(dt, iso=True):
    """
    Retourne un datetime timezone-aware. Si le datetime est naïf, le convertit en timezone active.
    """
    if not iso:
        dt = datetime.fromisoformat(dt)
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


def secure_time(t):
    today = date.today()
    parsed_time = parse_time(t)
    naive_dt = datetime.combine(today, parsed_time)
    aware_dt = secure_datetime(naive_dt)
    return aware_dt.time()


class DeepBaseFilter:
    """
    Base class for all deep filters.
    """
    mask = None
    field = None

    def __init__(self, **extra):
        for key, value in extra.items():
            if key not in ('self', 'value'):
                if hasattr(self,  f'set_key_{key}'):
                    getattr(self, f'set_key_{key}')(key, value)
                else:
                    self.set_key_value(key, value)
        self.value = extra['value']

    def usable(self):
        return (self.get_value() is not None)

    def set_key_value(self, key, value):
        setattr(self, key, value)

    def get_field(self):
        return f'{self.field}__{self.mask}' if self.mask else self.field

    def get_value(self):
        return self.value

    def filter(self):
        """
        Apply the filter to the queryset.
        """
        test = Q(**{self.get_field(): self.get_value()}) if self.usable() else Q()
        print("Q used", test)
        return test


class DeepStringFilter(DeepBaseFilter):
    """
    Filter for string equality.
    """

    def get_value(self):
        value = super().get_value()
        if isinstance(value, str):
            return value
        return str(value)


class DeepBooleanFilter(DeepBaseFilter):
    """
    Filter for equality.
    """

    def get_value(self):
        value = super().get_value()
        if isinstance(value, str):
            return True if value.lower() in ('true', '1') else False
        return bool(value)


class DeepIntegerFilter(DeepBaseFilter):
    """
    Filter for integer equality.
    """

    def get_value(self):
        return int(super().get_value())


class DeepFloatFilter(DeepBaseFilter):
    """
    Filter for float equality.
    """

    def get_value(self):
        return float(super().get_value())


class DeepDecimalFilter(DeepBaseFilter):
    """
    Filter for decimal equality.
    """

    def get_value(self):
        return decimal.Decimal(super().get_value())


class DeepDateFilter(DeepBaseFilter):
    """
    Filter for date equality.
    """

    def get_value(self):
        value = super().get_value()
        return secure_datetime(value, False).date()


class DeepTimeFilter(DeepBaseFilter):
    """
    Filter for time equality.
    """
    def get_value(self):
        value = super().get_value()
        return secure_time(value)


class DeepDateTimeFilter(DeepBaseFilter):
    """
    Filter for datetime equality.
    """

    def get_value(self):
        value = super().get_value()
        return secure_datetime(value, False).date()


class DeepListFilter(DeepBaseFilter):
    """
    Filter for list equality.
    """
    mask = 'in'
    authorized = ()

    def get_value(self):
        value = super().get_value()
        if isinstance(value, str):
            value = value.split(',')
        return [v for v in value if v in self.authorized] if len(self.authorized) else value


class DeepChoiceFilter(DeepBaseFilter):
    """
    Filter for list equality.
    """
    choices = []
    association = {}

    def usable(self):
        return (self.get_value() in self.choices)

    def get_value(self):
        value = super().get_value()
        return self.association.get(value, value)


class DeepMultipleChoiceFilter(DeepBaseFilter):
    """
    Filter for list equality.
    """
    mask = 'in'
    choices = []
    association = {}

    def usable(self):
        return (self.get_value() in self.choices)

    def get_value(self):
        value = super().get_value()
        if isinstance(value, str):
            value = value.split(',')
        return [self.association.get(v, v) for v in value if v in self.association] if len(self.association) else value
