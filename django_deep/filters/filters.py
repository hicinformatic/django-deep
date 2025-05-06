from django.db.models import Q
import decimal
from

class DeepBaseFilter:
    """
    Base class for all deep filters.
    """

    mask = None
    field = None

    def __init__(self, **extra):
        for key, value in extra.items():
            if key not in ('self', 'value'):
                getattr(self, f'set_key_{key}', 'set_key_value')(key, value)
        self.value = extra['value']

    def usable(self):
        return (self.get_value() is not None)

    def set_key_value(self, key, value):
        setattr(self, key, value)

    def get_field(self):
        return f'__{self.mask}{self.field}' if self.mask else self.field

    def get_value(self):
        return self.value

    def filter(self):
        """
        Apply the filter to the queryset.
        """
        return Q(**{self.get_field(): self.get_value()}) if self.usable() else Q()


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

    def usable(self):
        use timezone


class DeepTimeFilter(DeepBaseFilter):
    """
    Filter for time equality.
    """

    def usable(self):
        use timezone

class DeepDateTimeFilter(DeepBaseFilter):
    """
    Filter for datetime equality.
    """

    def usable(self):
        use timezone


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
