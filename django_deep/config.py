from typing import Final

from django.conf import settings

_idorarg: Final[str] = getattr(settings, "DEEP_IDORARG", "IDorARG")
_filter: Final[list] = getattr(settings, "DEEP_FILTER", ["f", "(", ")"])
_family: Final[list] = getattr(settings, "DEEP_FAMILY", ["(", ")"])
_or: Final[str] = getattr(settings, "DEEP_OR", "~")
_split: Final[str] = getattr(settings, "DEEP_SPLIT", ",")
_negative: Final[str] = getattr(settings, "DEEP_NEGATIVE", "-")

_greater: Final[str] = getattr(settings, "DEEP_GREATER", ">")
_less: Final[str] = getattr(settings, "DEEP_LESS", "<")
_greater_equal: Final[str] = getattr(settings, "DEEP_GREATER_EQUAL", ">=")
_less_equal: Final[str] = getattr(settings, "DEEP_LESS_EQUAL", "<=")

_iexact: Final[str] = getattr(settings, "DEEP_IEXACT", "=")
_exact: Final[str] = getattr(settings, "DEEP_EXACT", "==")
_icontains: Final[str] = getattr(settings, "DEEP_ICONTTAINS", "*")
_contains: Final[str] = getattr(settings, "DEEP_CONTAINS", "**")
