from django.core.exceptions import PermissionDenied
from django.db.models import Q


class DeepFilterManager:
    """
    A manager for handling and applying filters to querysets.

    This class provides functionality to activate filters based on params parameters,
    check for mandatory filters, and apply active filters to a queryset.

    Attributes:
    ----------
    filters : list
        A list of filter instances to be applied.
    mandatory_filters : list
        A list of mandatory filter names that must be present in the params.

    Methods:
    -------
    activate_filter(params, filter_instance)
        Activates a filter based on params parameters.
    apply_negation(filter_instance)
        Applies negation logic to a filter.
    check_mandatory_filters(params)
        Checks if all mandatory filters are present in the params.
    get_active_filters(params)
        Returns a list of active filters based on the params.
    apply_filters(queryset, params)
        Applies all active filters to a queryset.
    """

    def __init__(self, filters=None, mandatory_filters=None):
        """
        Initialise le gestionnaire de filtres.

        :param filters: Liste des instances de filtres à appliquer
        :param mandatory_filters: Liste des noms de filtres obligatoires
        """
        self.filters = filters or []
        self.mandatory_filters = mandatory_filters or []

    def activate_filter(self, params, filter_instance):
        """
        Active un filtre en fonction du paramètre dans l'URL.
        Le filtre est activé si le paramètre existe et n'est pas None.
        Si l'opérateur `-=` est trouvé dans la valeur, il marque le filtre comme négatif.
        """
        param_name = filter_instance.field
        filter_value = params.get(param_name)

        # Vérification de la négation avec `-=` dans l'URL
        negate = False
        if filter_value and filter_value.startswith('-='):
            negate = True
            filter_value = filter_value[
                2:
            ]  # Enlever le "-=" pour obtenir la valeur réelle

        if filter_value:
            # Créer une nouvelle instance du filtre avec la valeur à filtrer
            activated_filter = filter_instance.__class__(
                field=filter_instance.field, value=filter_value
            )

            # Si c'est une négation, on ajuste le filtre pour appliquer la logique inverse
            if negate:
                activated_filter = self.apply_negation(activated_filter)

            return activated_filter
        return None

    def apply_negation(self, filter_instance):
        """
        Applique la logique de négation sur un filtre.
        Utilise le ~ pour inverser l'effet du filtre dans le ORM de Django.
        """
        # Ici, on suppose que `filter_instance.filter()` retourne un Q object
        return Q(~filter_instance.filter())

    def check_mandatory_filters(self, params):
        """Vérifie si tous les filtres obligatoires sont présents dans la requête."""
        for mandatory_filter in self.mandatory_filters:
            param_name = {mandatory_filter}
            if not params.get(param_name):
                raise PermissionDenied(f"Le filtre obligatoire '{mandatory_filter}' est manquant.")
        return True

    def get_active_filters(self, params):
        """Retourne une liste des filtres activés en fonction des paramètres présents dans la requête."""
        # Vérifier que les filtres obligatoires sont présents avant d'activer les autres
        self.check_mandatory_filters(params)

        active_filters = []
        print(self.filters)
        for filter_instance in self.filters:
            activated_filter = self.activate_filter(params, filter_instance)
            if activated_filter:
                active_filters.append(activated_filter)
        return active_filters

    def apply_filters(self, queryset, params):
        """Applique tous les filtres activés à un queryset."""
        active_filters = self.get_active_filters(params)
        for filter_instance in active_filters:
            queryset = queryset.filter(filter_instance.filter())
        return queryset
