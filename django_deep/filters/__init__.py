from .manager import DeepFilterManager
from .filters import (
    DeepBaseFilter,
    DeepStringFilter,
    DeepBooleanFilter,
    DeepIntegerFilter,
    DeepDateTimeFilter,
    DeepDateFilter,
    DeepTimeFilter,
    DeepDecimalFilter,
    DeepFloatFilter,
    DeepListFilter,
    DeepChoiceFilter,
)

deep_filters_association = {
    'string': DeepStringFilter,
    'boolean': DeepBooleanFilter,
    'integer': DeepIntegerFilter,
    'float': DeepFloatFilter,
    'decimal': DeepDecimalFilter,
    'date': DeepDateFilter,
    'time': DeepTimeFilter,
    'datetime': DeepDateTimeFilter,
    'list': DeepListFilter,
    'choice': DeepChoiceFilter,
}
