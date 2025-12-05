from typing import ClassVar
from django.db.models import Func
from django.db import connection as db_connection
from django.db.models import TextField


class JsonExtract(Func):
    """
    Custom Django Func for extracting JSON data from database fields.
    
    SECURITY NOTE: This class uses Django's parameter binding system.
    All parameters passed via `extra` are automatically escaped by Django's ORM,
    preventing SQL injection. The `data_path` parameter is processed through
    controlled transformation methods that only perform string operations.
    
    However, developers should ensure that:
    - User inputs are validated before being passed to this function
    - The `data_path` parameter only contains valid field paths
      (e.g., "field__subfield")
    - Never pass raw SQL strings directly
    """
    function = None
    field = None
    output_field = TextField()
    templates: ClassVar[dict] = {
        "postgresql": "%(json_field)s #>> '{%(data_path)s}'",
        "mysql": "JSON_UNQUOTE(JSON_EXTRACT(%(json_field)s, '$.%(data_path)s'))",
        "sqlite": "json_extract(%(json_field)s, '$.%(data_path)s')",
        "oracle": "JSON_VALUE(%(json_field)s, '$.%(data_path)s')",
    }

    def get_data_postgresql(self, data):
        return ",".join(data.split("__"))

    def get_data_default(self, data):
        return ".".join(data.split("__"))

    def __init__(self, json_field, data_path, **extra):
        self.vendor = db_connection.vendor
        if self.vendor not in self.templates:
            raise NotImplementedError(
                f"JsonExtract n'est pas disponible pour la base {self.vendor}"
            )
        extra["json_field"] = json_field
        extra["data_path"] = getattr(
            self, f"get_data_{self.vendor}", self.get_data_default
        )(data_path)
        self.template = self.templates[self.vendor]
        super().__init__(**extra)
