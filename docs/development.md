## Development Guidelines

### General Rules

- Default to English for all code artifacts (comments, docstrings, logging, error strings, documentation).
- Keep comments minimal and only when they clarify non-obvious logic.
- Add comments only when they resolve likely ambiguity.

### Simplicity and Dependencies

- **Keep functions simple**: Write the simplest possible functions.
- **Minimize dependencies**: Limit dependencies to the minimum. Use Django's ORM and standard library first.
- **Avoid over-engineering**: Don't add abstractions unless they solve a real problem.

### Code Quality

- **Testing**: Use pytest with pytest-django. Tests go in `tests/`.
- **Type hints**: All public functions and methods must have type hints.
- **Docstrings**: Use Google-style docstrings for public APIs.
- **Linting**: Use ruff. Run `ruff check .` and `ruff format .`

### Commands

```bash
pip install -e ".[dev]"
pytest
ruff check .
ruff format .
```

### Database Support

Subqueries and JsonExtract support:
- **PostgreSQL**: Full support
- **MySQL**: Full support
- **SQLite**: JsonAggSubquery, JsonExtract
- **Oracle**: JsonAggSubquery, JsonExtract

ConcatValuesSubquery: PostgreSQL, MySQL only.

### Security

All subqueries and JsonExtract use Django's parameter binding. Never pass raw SQL or unvalidated user input to field names or paths.
