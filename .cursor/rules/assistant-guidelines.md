# Cursor Rules for Django Deep

## Language and Framework
- Always respond in French
- Use Django best practices and conventions
- Follow PEP 8 for Python code style
- Use type hints when appropriate

## Project Context
Django Deep est une bibliothèque permettant de créer des filtres SQL complexes à l'aide d'expressions dynamiques dans Django. Le projet se concentre sur :
- Le parsing d'expressions pour générer des requêtes SQL
- Les sous-requêtes (subqueries) : concatvalues, count_sum, extractvalues, jsonagg, jsonextract, methodfrom
- Les filtres et managers personnalisés
- Les fonctions d'extraction JSON

## Code Style
- Use black for code formatting (line length: 88)
- Use ruff for linting
- Prefer f-strings over .format() or % formatting
- Use pathlib.Path instead of os.path when possible
- Prefer list/dict comprehensions when readable
- Use type hints for function parameters and return types
- Keep comments minimal - only add comments to resolve ambiguity
- All comments and docstrings must be in English

## Django ORM Specific
- Use Django ORM instead of raw SQL when possible
- Use select_related() and prefetch_related() to optimize queries
- Use F() expressions for database-level operations
- Use Q objects for complex queries
- Always use migrations for schema changes
- Use get_object_or_404() instead of try/except for single objects

## Parser and Expression Handling
- When parsing expressions, validate input carefully
- Handle edge cases in expression parsing (empty values, None, special characters)
- Use Django's field lookup syntax (field__lookup) when appropriate
- Ensure expressions are properly escaped to prevent SQL injection
- Document complex parsing logic with clear comments

## Subqueries and Aggregations
- Optimize subqueries to avoid N+1 query problems
- Use annotations and aggregations when possible
- Consider using select_related/prefetch_related
- Use bulk operations (bulk_create, bulk_update) when appropriate
- Avoid loading unnecessary data with .values() or .only()

## JSON Extraction
- Validate JSON structure before extraction
- Handle missing keys gracefully with default values
- Use COALESCE or default values for nullable JSON fields
- Document JSON path syntax clearly

## Performance
- Optimize database queries (avoid N+1 queries)
- Use annotations and aggregations when possible
- Consider using select_related/prefetch_related
- Use bulk operations (bulk_create, bulk_update) when appropriate
- Profile complex queries to identify bottlenecks

## Security
- Never trust user input - always validate and sanitize
- Use Django's built-in security features (CSRF, XSS protection)
- Use parameterized queries (Django ORM handles this)
- Never commit secrets or API keys to version control
- Use environment variables for sensitive configuration
- Validate and escape all expressions before parsing

## Testing
- Write tests for new features, especially parser logic
- Use pytest and pytest-django for testing
- Test edge cases and error conditions
- Test with various expression formats and edge cases
- Use factories (factory_boy) for test data when appropriate
- Test subquery performance with realistic data volumes

## Documentation
- Write docstrings for functions and classes
- Use clear, descriptive variable and function names
- Add comments for complex parsing logic
- Document expression syntax and supported lookups
- Keep README.md up to date with examples

## Git
- Write clear, descriptive commit messages
- Use conventional commits format when possible
- Keep commits focused and atomic

## Error Handling
- Use specific exception types
- Provide meaningful error messages for parsing errors
- Log errors appropriately
- Don't swallow exceptions silently
- Return helpful error messages when expressions are invalid

## Code Organization
- Keep functions small and focused
- Use Django apps to organize related functionality
- Separate parser logic from query building
- Use managers and querysets for complex queries
- Group related subqueries in the subqueries module

## Dependencies
- Keep dependencies up to date
- Use requirements.txt or pyproject.toml for dependencies
- Pin versions for production
- Document why each dependency is needed

## Expression Parser Specific
- Support Django's field lookup syntax (field__lookup)
- Handle nested lookups (field__related__lookup)
- Support Q objects for complex queries
- Validate field names against model fields
- Handle special cases (isnull, in, range, etc.)

## Subquery Specific
- Ensure subqueries are properly correlated
- Use OuterRef for correlated subqueries
- Optimize subqueries to avoid unnecessary joins
- Document subquery parameters clearly
- Handle NULL values appropriately in aggregations

