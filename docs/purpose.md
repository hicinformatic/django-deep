## Project Purpose

**django-deep** is a Django library for advanced SQL expressions. It extends Django's ORM with subqueries, JSON extraction, and dynamic filter parsing.

### Core Functionality

1. **DeepManager**:
   - Subquery helpers: `get_sum_sub_query`, `get_count_sub_query`, `get_concat_values_sub_query`, `get_method_from_sub_query`, `get_json_agg_sub_query`
   - `get_json_extract` for JSONField extraction
   - `auto_related` for select_related/prefetch_related optimization

2. **Subqueries**:
   - `SumSubquery` – SUM over a subquery
   - `CountSubquery` – COUNT over a subquery
   - `ConcatValuesSubquery` – Concatenate values (PostgreSQL STRING_AGG, MySQL GROUP_CONCAT)
   - `JsonAggSubquery` – Aggregate as JSON array (PostgreSQL, MySQL, SQLite, Oracle)
   - `MethodFromSubquery` – Custom aggregation via subquery
   - `ExtractValueSubquery`, `ExtractMultipleValuesSubquery` – Extract values from subquery

3. **JsonExtract**:
   - Database-agnostic JSON path extraction
   - Supports PostgreSQL (#>>), MySQL (JSON_EXTRACT), SQLite (json_extract), Oracle (JSON_VALUE)

4. **DeepParser**:
   - Parses dynamic filter expressions from string parameters
   - Params: include (i), exclude (x), order (o), distinct (d)
   - Builds Django Q objects from a custom DSL

5. **MemoryQuerySet**:
   - In-memory queryset for testing

### Use Cases

- Annotate querysets with aggregated subquery data (counts, sums)
- Extract values from JSONFields in database-specific ways
- Build dynamic filters from request parameters
- Optimize queries with subqueries instead of Python loops
