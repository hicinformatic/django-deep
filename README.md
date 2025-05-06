
# Django Enhanced Expression Parser

Django Deep est une bibliothèque permettant de créer des filtres SQL complexes à l'aide d'expressions dynamiques dans Django.

## Installation

```bash
pip install django-deep
```

## Utilisation

Exemple d’utilisation de la bibliothèque pour créer une expression de filtrage SQL :

```python
from django_deep import EnhancedExpressionParser

parser = EnhancedExpressionParser()
expression = parser.parse(field1=value1, field2__gte=value2)
```
