import operator
from . import config as cfg
from django.db.models import Count


class DeepParser:
    filters = None
    include = None
    excludes = None
    order = None
    distinct = None
    order_enable = False
    order_base = []
    order_association = {}
    order_authorized = []

    class Param:
        _filters = "f"
        _include = "i"
        _exclude = "x"
        _distinct = "d"
        _order = "o"

    def __init__(self, queryset, params={}, *args, **kwargs):
        self.queryset = queryset
        self.compiled = []
        self.families = []
        self.context = []
        self.filter_idandargs = []
        self.operators = []
        self.idorarg = ""
        self.params = params
        self.filters = {fltr.id: fltr for fltr in kwargs.get(self.Param._filters, [])}
        self.tokens = cfg._filter + cfg._family + [cfg._split, cfg._or]
        self.include = self.execute(params.get(self.Param._include, False))
        self.exclude = self.execute(params.get(self.Param._exclude, False))
        self.order = self.params.get(self.Param._order, kwargs.get("order"))
        self.order_base = kwargs.get("order_base", [])
        self.distinct = kwargs.get("distinct", False)
        self.order_enable = kwargs.get("order_enable", False)
        self.order_association = kwargs.get("order_association", {})
        self.order_authorized = kwargs.get("order_authorized", [])
        self.separator = cfg._split
        self.negative = cfg._negative

    def execute(self, input_str):
        if input_str:
            i = 0
            while i < len(input_str):
                char = input_str[i]
                i += 1
                if char in self.tokens:
                    # Si un filtre commence
                    if char == cfg._filter[0]:
                        if not len(self.context) or self.context[-1] == cfg._family[0]:
                            self.context.append(cfg._filter[0])
                        else:
                            self.concate_idorarg(char)

                    # Ouverture d'un filtre ou d'une famille
                    elif char in {cfg._filter[1], cfg._family[0]}:
                        if (
                            len(self.context)
                            and self.context[-1] == cfg._filter[0]
                            and char == cfg._filter[1]
                        ):
                            self.context[-1] = cfg._filter[0] + cfg._filter[1]
                        elif char == cfg._family[0]:
                            self.context.append(cfg._family[0])
                            self.families.append([])

                    # Fermeture d'un filtre ou d'une famille
                    elif char in {cfg._filter[2], cfg._family[1]}:
                        if len(self.context) and self.context[-1] == cfg._idorarg:
                            self.add_idorarg()

                        if (
                            char == cfg._filter[2]
                            and self.context[-1] == cfg._filter[0] + cfg._filter[1]
                        ):
                            self.context.pop()
                            self.add_filter(self.get_filter_by_idandargs())
                        elif (
                            char == cfg._family[1]
                            and self.context[-1] == cfg._family[0]
                        ):
                            self.add_filter(self.apply_operators(self.families.pop()))
                            self.context.pop()

                    # Séparation des arguments
                    elif char == cfg._split:
                        if len(self.context) and self.context[-1] == cfg._idorarg:
                            self.add_idorarg()

                    # Opérateur logique OR
                    elif char == cfg._or:
                        self.operators.append(operator.or_)

                elif not self.context:
                    raise SyntaxError("Request interpreter needs a starting condition")
                else:
                    self.concate_idorarg(char)

            if self.compiled:
                self.compiled = self.apply_operators(self.compiled)

        if len(self.context):
            raise SyntaxError("Invalid syntax of the request interpreter")

        compiled, self.compiled = self.compiled, []
        return compiled or False

    def add_idorarg(self):
        self.filter_idandargs.append(self.idorarg)
        self.context.pop()
        self.idorarg = ""

    def concate_idorarg(self, char):
        if self.context[-1] != cfg._idorarg:
            self.context.append(cfg._idorarg)
        self.idorarg += char

    def add_filter(self, fltr):
        if fltr:
            (
                self.families[-1].append(fltr)
                if len(self.families)
                else self.compiled.append(fltr)
            )

    def get_filter_by_idandargs(self):
        if len(self.filter_idandargs) and self.filter_idandargs[0] in self.filters:
            fltr = self.filters[self.filter_idandargs[0]]
            fltr.request = self.request
            args = (
                self.filter_idandargs[1]
                if len(self.filter_idandargs) == 2
                else cfg._split.join(self.filter_idandargs[1:])
            )
            self.filter_idandargs = []
            return fltr.sql(self.params, params={fltr.param: args})
        return False

    def apply_operators(self, filters):
        """Applique les opérateurs (AND, OR) sans utiliser `reduce`."""
        if not filters:
            return False

        # Si la liste des opérateurs est vide, on applique un AND par défaut
        operator_func = operator.and_
        result = filters[0]

        # Applique les opérateurs aux filtres
        for i in range(1, len(filters)):
            if self.operators:
                operator_func = self.operators.pop(
                    0
                )  # Prend le prochain opérateur dans la pile
            result = operator_func(result, filters[i])

        return result

    def get_arg_order(self, arg):
        assoc = arg.replace("-", "")
        direc = "-" if arg.startswith("-") else ""
        field = self.order_association.get(assoc, assoc)
        if self.order_authorized:
            if assoc in self.order_authorized:
                return direc + field
        else:
            return direc + field
        return None

    def order_by(self):
        args = []
        if self.order:
            args += [o.replace(".", "__") for o in self.order.split(self.separator)]
        args_base = [arg.replace("-", "") for arg in args]
        if len(self.order_base):
            for ord_base in self.order_base:
                if ord_base.replace("-", "") not in args_base:
                    args.append(ord_base)
        return [
            result for arg in args if (result := self.get_arg_order(arg)) is not None
        ]

    def _apply_include(self):
        if self.include:
            self.queryset = self.queryset.filter(self.include)

    def _apply_exclude(self):
        if self.exclude:
            self.queryset = self.queryset.exclude(self.exclude)

    def _apply_distinct(self):
        if self.distinct:
            if isinstance(self.distinct, str):
                if self.distinct == "count":
                    self.queryset = self.queryset.annotate(Count("id"))
                else:
                    self.queryset = self.queryset.distinct(self.distinct)
            elif isinstance(self.distinct, bool):
                self.queryset = self.queryset.distinct()
            elif isinstance(self.distinct, (list, tuple)):
                self.queryset = self.queryset.distinct(*self.distinct)

    def _apply_ordering(self):
        ob = self.order_by()
        if self.order_enable and ob:
            self.queryset = self.queryset.order_by(*ob)

    def get_queryset(self):
        self._apply_include()
        self._apply_exclude()
        self._apply_distinct()
        self._apply_ordering()
        return self.queryset
