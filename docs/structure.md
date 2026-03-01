## Project Structure

django-deep follows a standard Django app layout with clear separation between parser, manager, subqueries, and functions.

### General Structure

```
django-deep/
├── src/
│   └── django_deep/
│       ├── __init__.py       # Package exports (DeepManager, DeepParser)
│       ├── config.py         # Parser tokens and configuration
│       ├── manager.py        # DeepManager with subquery helpers
│       ├── parser.py         # DeepParser for dynamic filters
│       ├── queryset.py       # MemoryQuerySet for in-memory operations
│       ├── filters/          # Filter definitions for parser
│       │   ├── __init__.py
│       │   ├── filters.py
│       │   └── manager.py
│       ├── functions/        # Database functions
│       │   ├── __init__.py
│       │   └── jsonextract.py
│       └── subqueries/       # Subquery classes
│           ├── __init__.py
│           ├── count_sum.py
│           ├── concatvalues.py
│           ├── jsonagg.py
│           ├── jsonextract.py
│           ├── extractvalues.py
│           └── methodfrom.py
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

### Key Modules

- **manager.py**: DeepManager – subquery factory methods, JsonExtract, auto_related
- **parser.py**: DeepParser – parses string params into Q objects, applies filters/order/distinct
- **subqueries/**: SumSubquery, CountSubquery, JsonAggSubquery, ConcatValuesSubquery, etc.
- **functions/jsonextract.py**: JsonExtract – JSON path extraction (PostgreSQL, MySQL, SQLite, Oracle)

### Package Exports

`src/django_deep/__init__.py`:
- `DeepManager`
- `DeepParser`
- `__version__`
