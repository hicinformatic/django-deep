from django.conf import settings

# Définition des délimiteurs et opérateurs
_idorarg = getattr(settings, "DEEP_IDORARG", "IDorARG")  # Identifiant ou argument
_filter = getattr(
    settings, "DEEP_FILTER", ["f", "(", ")"]
)  # Délimiteurs pour les filtres
_family = getattr(
    settings, "DEEP_FAMILY", ["(", ")"]
)  # Délimiteurs pour les familles de filtres
_or = getattr(settings, "DEEP_OR", "~")  # Opérateur logique OR
_split = getattr(settings, "DEEP_SPLIT", ",")  # Séparateur pour diviser les arguments
_negative = getattr(
    settings, "DEEP_NEGATIVE", "-"
)  # Préfixe pour indiquer une condition négative

# Opérateurs de comparaison (1 caractère pour faciliter le parsing)
_greater = getattr(settings, "DEEP_GREATER", ">")  # Supérieur strict
_less = getattr(settings, "DEEP_LESS", "<")  # Inférieur strict
_greater_equal = getattr(settings, "DEEP_GREATER_EQUAL", ">=")  # Supérieur ou égal
_less_equal = getattr(settings, "DEEP_LESS_EQUAL", "<=")  # Inférieur ou égal

# Opérateurs de correspondance textuelle
_iexact = getattr(settings, "DEEP_IEXACT", "=")  # Égalité sans tenir compte de la casse
_exact = getattr(settings, "DEEP_EXACT", "==")  # Égalité stricte
_icontains = getattr(
    settings, "DEEP_ICONTTAINS", "*"
)  # Contient sans tenir compte de la casse
_contains = getattr(
    settings, "DEEP_CONTAINS", "**"
)  # Contient avec prise en compte de la casse
