# AI Assistant Contract — django-deep

**Single source of truth for AI-generated work in this repository.**

---

## Project Overview

**django-deep** is a Django library for advanced SQL expressions: subqueries (SUM, COUNT, JsonAgg, ConcatValues), JSON extraction, and dynamic filter parsing.

### Core Functionality

1. **DeepManager** (`manager.py`)
   - Subquery helpers: `get_sum_sub_query`, `get_count_sub_query`, `get_json_agg_sub_query`, `get_concat_values_sub_query`, `get_method_from_sub_query`
   - `get_json_extract` for JSONField extraction
   - `auto_related` for select_related/prefetch_related

2. **DeepParser** (`parser.py`)
   - Parses dynamic filter expressions from string params (i, x, o, d)
   - Builds Django Q objects from custom DSL

3. **Subqueries** (`subqueries/`)
   - SumSubquery, CountSubquery, JsonAggSubquery, ConcatValuesSubquery, MethodFromSubquery, ExtractValueSubquery

4. **JsonExtract** (`functions/jsonextract.py`)
   - JSON path extraction for PostgreSQL, MySQL, SQLite, Oracle

5. **MemoryQuerySet** (`queryset.py`)
   - In-memory queryset for testing

---

## Required Rules

- **Language**: English for code, comments, docstrings, docs
- **Simplicity**: Write the simplest solution that works
- **Minimal dependencies**: Prefer Django ORM and standard library
- **Type hints**: All public APIs must have type hints
- **Docstrings**: Google-style for public classes, methods, functions
- **Testing**: pytest with pytest-django

---

## Project Structure

```
src/django_deep/
├── manager.py      # DeepManager
├── parser.py       # DeepParser
├── queryset.py     # MemoryQuerySet
├── config.py       # Parser config
├── filters/        # Filter definitions
├── functions/      # JsonExtract, etc.
└── subqueries/     # Subquery classes
```

---

## Do Not

- Invent new subquery types or patterns unless explicitly requested
- Pass raw SQL or unvalidated user input to field names
- Hardcode credentials or secrets
- Add dependencies without clear necessity
