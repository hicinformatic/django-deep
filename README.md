# django-deep

Django library for advanced SQL expressions: subqueries (SUM, COUNT, JsonAgg, ConcatValues), JSON extraction, and dynamic filter parsing.

## Features

- **DeepManager** – Custom manager with subquery helpers (`get_sum_sub_query`, `get_count_sub_query`, `get_json_agg_sub_query`, `get_concat_values_sub_query`, `get_method_from_sub_query`) and `JsonExtract` for JSON fields
- **DeepParser** – Parses dynamic filter expressions from string parameters (include, exclude, order, distinct) to build Django Q objects
- **Subqueries** – `SumSubquery`, `CountSubquery`, `JsonAggSubquery`, `ConcatValuesSubquery`, `MethodFromSubquery`, `ExtractValueSubquery`
- **JsonExtract** – Database-agnostic JSON field extraction (PostgreSQL, MySQL, SQLite, Oracle)
- **MemoryQuerySet** – In-memory queryset for testing

## Installation

```bash
pip install django-deep
```

## Quick start

```python
from django.db import models
from django.db.models import OuterRef
from django_deep import DeepManager

class Order(models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class Customer(models.Model):
    name = models.CharField(max_length=255)
    objects = DeepManager()
    name = models.CharField(max_length=255)
    objects = DeepManager()

# Annotate with subqueries
Customer.objects.annotate(
    order_count=Customer.objects.get_count_sub_query(
        Order.objects.filter(customer_id=OuterRef("pk"))
    ),
    order_sum=Customer.objects.get_sum_sub_query(
        Order.objects.filter(customer_id=OuterRef("pk")), sum_field="total"
    ),
)
```

## Subqueries

```python
from django.db.models import OuterRef
from django_deep import DeepManager

# SumSubquery
qs.annotate(total=manager.get_sum_sub_query(Order.objects.filter(...), "total"))

# CountSubquery
qs.annotate(cnt=manager.get_count_sub_query(Order.objects.filter(...)))

# JsonAggSubquery (PostgreSQL, MySQL, SQLite, Oracle)
qs.annotate(items=manager.get_json_agg_sub_query(RelatedModel.objects.filter(...)))
```

## JsonExtract

```python
from django_deep.functions import JsonExtract

# Extract from JSONField
Model.objects.annotate(
    value=JsonExtract("metadata", "path__to__field")
)
```

## Dynamic filters (DeepParser)

Parse include/exclude/order from request params:

```python
parser = DeepParser(queryset, params={"i": "field__filter:value", "o": "name"})
compiled = parser.execute(params.get("i"))
if compiled:
    qs = queryset.filter(compiled)
qs = parser.get_queryset()
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
ruff format .
```

## License

GPL-3.0-or-later — see the `LICENSE` file.
