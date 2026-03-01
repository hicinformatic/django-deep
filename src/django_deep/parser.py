import operator
from typing import Any, Optional

from django.db.models import Count, QuerySet

from . import config as cfg


class DeepParser:
    """Parser for dynamic filter expressions."""

    filters: Optional[dict] = None
    include: Optional[Any] = None
    excludes: Optional[Any] = None
    order: Optional[str] = None
    distinct: Optional[Any] = None
    order_enable: bool = False
    order_base: list = []
    order_association: dict = {}
    order_authorized: list = []

    class Param:
        """Parameter keys for parser configuration."""

        _filters: str = "f"
        _include: str = "i"
        _exclude: str = "x"
        _distinct: str = "d"
        _order: str = "o"

    def __init__(
        self,
        queryset: QuerySet,
        params: Optional[dict] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.queryset = queryset
        self.compiled = []
        self.families = []
        self.context = []
        self.filter_idandargs = []
        self.operators = []
        self.idorarg = ""
        self.params = params or {}
        self.filters = {fltr.id: fltr for fltr in kwargs.get(self.Param._filters, [])}
        self.tokens = cfg._filter + cfg._family + [cfg._split, cfg._or]
        self.include = self.execute(self.params.get(self.Param._include, False))
        self.exclude = self.execute(self.params.get(self.Param._exclude, False))
        self.order = self.params.get(self.Param._order, kwargs.get("order"))
        self.order_base = kwargs.get("order_base", [])
        self.distinct = kwargs.get("distinct", False)
        self.order_enable = kwargs.get("order_enable", False)
        self.order_association = kwargs.get("order_association", {})
        self.order_authorized = kwargs.get("order_authorized", [])
        self.separator = cfg._split

    def execute(self, input_str: Optional[str]) -> Any:
        """Parse input string and build filter expressions."""
        if input_str:
            for char in input_str:
                if char in self.tokens:
                    if char == cfg._filter[0]:
                        if not self.context or self.context[-1] == cfg._family[0]:
                            self.context.append(cfg._filter[0])
                        else:
                            self.concate_idorarg(char)

                    elif char in {cfg._filter[1], cfg._family[0]}:
                        if (
                            self.context
                            and self.context[-1] == cfg._filter[0]
                            and char == cfg._filter[1]
                        ):
                            self.context[-1] = cfg._filter[0] + cfg._filter[1]
                        elif char == cfg._family[0]:
                            self.context.append(cfg._family[0])
                            self.families.append([])

                    elif char in {cfg._filter[2], cfg._family[1]}:
                        if self.context and self.context[-1] == cfg._idorarg:
                            self.add_idorarg()

                        if (
                            char == cfg._filter[2]
                            and self.context
                            and self.context[-1] == cfg._filter[0] + cfg._filter[1]
                        ):
                            self.context.pop()
                            self.add_filter(self.get_filter_by_idandargs())
                        elif (
                            char == cfg._family[1]
                            and self.context
                            and self.context[-1] == cfg._family[0]
                        ):
                            self.add_filter(self.apply_operators(self.families.pop()))
                            self.context.pop()

                    elif char == cfg._split:
                        if self.context and self.context[-1] == cfg._idorarg:
                            self.add_idorarg()

                    elif char == cfg._or:
                        self.operators.append(operator.or_)

                elif not self.context:
                    raise SyntaxError("Request interpreter needs a starting condition")
                else:
                    self.concate_idorarg(char)

            if self.compiled:
                self.compiled = self.apply_operators(self.compiled)

        if self.context:
            raise SyntaxError("Invalid syntax of the request interpreter")

        compiled, self.compiled = self.compiled, []
        return compiled or False

    def add_idorarg(self) -> None:
        """Add current idorarg to filter_idandargs and reset."""
        self.filter_idandargs.append(self.idorarg)
        self.context.pop()
        self.idorarg = ""

    def concate_idorarg(self, char: str) -> None:
        """Append character to current idorarg."""
        if self.context[-1] != cfg._idorarg:
            self.context.append(cfg._idorarg)
        self.idorarg += char

    def add_filter(self, fltr: Any) -> None:
        """Add filter to compiled list or current family."""
        if fltr:
            if self.families:
                self.families[-1].append(fltr)
            else:
                self.compiled.append(fltr)

    def get_filter_by_idandargs(self) -> Any:
        if (
            self.filter_idandargs
            and self.filter_idandargs[0] in self.filters
        ):
            fltr = self.filters[self.filter_idandargs[0]]
            args = (
                self.filter_idandargs[1]
                if len(self.filter_idandargs) == 2
                else cfg._split.join(self.filter_idandargs[1:])
            )
            self.filter_idandargs = []
            return fltr.sql(self.params, params={fltr.param: args})
        return False

    def apply_operators(self, filters: list) -> Any:
        """Apply logical operators (AND, OR) to filters."""
        if not filters:
            return False

        operator_func = operator.and_
        result = filters[0]

        for filter_item in filters[1:]:
            if self.operators:
                operator_func = self.operators.pop(0)
            result = operator_func(result, filter_item)

        return result

    def get_arg_order(self, arg: str) -> Optional[str]:
        """Get order field from argument with direction."""
        assoc = arg.replace("-", "")
        direc = "-" if arg.startswith("-") else ""
        field = self.order_association.get(assoc, assoc)
        if not self.order_authorized or assoc in self.order_authorized:
            return direc + field
        return None

    def order_by(self) -> list:
        args = []
        if self.order:
            args += [o.replace(".", "__") for o in self.order.split(self.separator)]
        args_base = [arg.replace("-", "") for arg in args]
        if self.order_base:
            for ord_base in self.order_base:
                if ord_base.replace("-", "") not in args_base:
                    args.append(ord_base)
        return [
            result for arg in args if (result := self.get_arg_order(arg)) is not None
        ]

    def _apply_include(self) -> None:
        """Apply include filters to queryset."""
        if self.include:
            self.queryset = self.queryset.filter(self.include)

    def _apply_exclude(self) -> None:
        """Apply exclude filters to queryset."""
        if self.exclude:
            self.queryset = self.queryset.exclude(self.exclude)

    def _apply_distinct(self) -> None:
        """Apply distinct to queryset."""
        if not self.distinct:
            return
        if isinstance(self.distinct, str):
            if self.distinct == "count":
                self.queryset = self.queryset.annotate(Count("id"))
            else:
                self.queryset = self.queryset.distinct(self.distinct)
        elif isinstance(self.distinct, bool):
            self.queryset = self.queryset.distinct()
        elif isinstance(self.distinct, (list, tuple)):
            self.queryset = self.queryset.distinct(*self.distinct)

    def _apply_ordering(self) -> None:
        """Apply ordering to queryset."""
        ob = self.order_by()
        if self.order_enable and ob:
            self.queryset = self.queryset.order_by(*ob)

    def get_queryset(self) -> QuerySet:
        self._apply_include()
        self._apply_exclude()
        self._apply_distinct()
        self._apply_ordering()
        return self.queryset
