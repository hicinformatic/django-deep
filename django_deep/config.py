# Définition des délimiteurs et opérateurs
_idorarg = 'IDorARG'   # Identifiant ou argument
_filter = ['f', '(', ')']  # Délimiteurs pour les filtres
_family = ['(', ')']    # Délimiteurs pour les familles de filtres
_or = '~'  # Opérateur logique OR
_split = ','  # Séparateur pour diviser les arguments
_negative = '-'  # Préfixe pour indiquer une condition négative

# Opérateurs de comparaison (1 caractère pour faciliter le parsing)
_greater = '>'   # Supérieur strict
_less = '<'      # Inférieur strict
_greater_equal = '>='  # Supérieur ou égal
_less_equal = '<='     # Inférieur ou égal

# Opérateurs de correspondance textuelle
_iexact = '='     # Égalité sans tenir compte de la casse
_exact = '=='     # Égalité stricte
_icontains = '*'  # Contient sans tenir compte de la casse
_contains = '**'  # Contient avec prise en compte de la casse
