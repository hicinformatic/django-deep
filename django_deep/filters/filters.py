import decimal
import logging
from datetime import date, datetime
from typing import Any, Optional, Union

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_time

logger = logging.getLogger(__name__)


def secure_datetime(
    dt: Union[str, datetime], iso: bool = True
) -> datetime:
    """
    Return timezone-aware datetime.

    If datetime is naive, converts to active timezone.
    """
    if not iso:
        dt = datetime.fromisoformat(dt)
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


def secure_time(t: str) -> Any:
    """Convert time string to timezone-aware time."""
    today = date.today()
    parsed_time = parse_time(t)
    naive_dt = datetime.combine(today, parsed_time)
    aware_dt = secure_datetime(naive_dt)
    return aware_dt.time()


class DeepBaseFilter:
    """Base class for all deep filters."""

    mask: Optional[str] = None
    field: Optional[str] = None
    value: Any = None

    def __init__(self, **extra: Any) -> None:
        for key, value in extra.items():
            if key != "value":
                setter = getattr(self, f"set_key_{key}", None)
                if setter:
                    setter(key, value)
                else:
                    self.set_key_value(key, value)
        self.value = extra["value"]

    def usable(self) -> bool:
        """Check if filter can be used."""
        return self.get_value() is not None

    def set_key_value(self, key: str, value: Any) -> None:
        """Set attribute value."""
        setattr(self, key, value)

    def get_field(self) -> str:
        """Get field name with mask if applicable."""
        return f"{self.field}__{self.mask}" if self.mask else self.field

    def get_value(self) -> Any:
        """Get filter value."""
        return self.value

    def filter(self) -> Q:
        """Apply filter to queryset."""
        if self.usable():
            qgenerate = Q(**{self.get_field(): self.get_value()})
        else:
            qgenerate = Q()
        logger.debug(f"Q generate : {qgenerate}")
        return qgenerate


class DeepStringFilter(DeepBaseFilter):
    """Filter for string equality."""

    def get_value(self) -> str:
        """Convert value to string."""
        value = super().get_value()
        if isinstance(value, str):
            return value
        return str(value)


class DeepBooleanFilter(DeepBaseFilter):
    """Filter for boolean equality."""

    def check_value(self, value: Any) -> Optional[bool]:
        """Convert value to boolean."""
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ("true", "1", "yes"):
                return True
            if value_lower in ("false", "0", "no"):
                return False
        elif isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return bool(value)
        return None

    def usable(self) -> bool:
        """Check if value is boolean."""
        return isinstance(self.get_value(), bool)

    def get_value(self) -> Optional[bool]:
        """Get boolean value."""
        value = super().get_value()
        return self.check_value(value) if value is not None else None


class DeepIntegerFilter(DeepBaseFilter):
    """Filter for integer equality."""

    def get_value(self) -> int:
        """Convert value to integer."""
        return int(super().get_value())


class DeepFloatFilter(DeepBaseFilter):
    """Filter for float equality."""

    def get_value(self) -> Optional[float]:
        """Convert value to float."""
        value = super().get_value()
        if isinstance(value, str):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        return None


class DeepDecimalFilter(DeepBaseFilter):
    """Filter for decimal equality."""

    def get_value(self) -> Optional[decimal.Decimal]:
        """Convert value to Decimal."""
        value = super().get_value()
        if isinstance(value, str):
            return decimal.Decimal(value)
        elif isinstance(value, (int, float)):
            return decimal.Decimal(str(value))
        elif isinstance(value, decimal.Decimal):
            return value
        return None


class DeepDateFilter(DeepBaseFilter):
    """Filter for date equality."""

    secure_date: bool = False

    def get_value(self) -> Any:
        """Get date value, optionally secured."""
        value = super().get_value()
        return secure_datetime(value, False).date() if self.secure_date else value


class DeepTimeFilter(DeepBaseFilter):
    """Filter for time equality."""

    secure_time: bool = False

    def get_value(self) -> Any:
        """Get time value, optionally secured."""
        value = super().get_value()
        return secure_time(value) if self.secure_time else value


class DeepDateTimeFilter(DeepBaseFilter):
    """Filter for datetime equality."""

    secure_datetime: bool = False

    def get_value(self) -> Any:
        """Get datetime value, optionally secured."""
        value = super().get_value()
        return secure_datetime(value, False) if self.secure_datetime else value


class DeepListFilter(DeepBaseFilter):
    """Filter for list equality."""

    mask: str = "in"
    choices: tuple = ()

    def usable(self) -> bool:
        """Check if value is in choices."""
        return (self.get_value() in self.choices) if self.choices else True

    def get_value(self) -> Any:
        """Get list value, filtered by choices if applicable."""
        value = super().get_value()
        if isinstance(value, str):
            value = value.split(",")
        return [v for v in value if v in self.choices] if self.choices else value


class DeepChoiceFilter(DeepBaseFilter):
    """Filter for single choice equality."""

    choices: list = []
    association: dict = {}

    def usable(self) -> bool:
        """Check if value is in choices."""
        return (self.get_value() in self.choices) if self.choices else True

    def get_value(self) -> Any:
        """Get value, mapped through association if applicable."""
        value = super().get_value()
        return self.association.get(value, value)


class DeepMultipleChoiceFilter(DeepBaseFilter):
    """Filter for multiple choice equality."""

    mask: str = "in"
    choices: list = []
    association: dict = {}

    def usable(self) -> bool:
        """Check if value is in choices."""
        return (self.get_value() in self.choices) if self.choices else True

    def get_value(self) -> Any:
        """Get list value, mapped through association if applicable."""
        value = super().get_value()
        if isinstance(value, str):
            value = value.split(",")
        return (
            [self.association.get(v, v) for v in value if v in self.association]
            if self.association
            else value
        )
