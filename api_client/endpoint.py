from enum import Enum
from typing import Dict, List, Optional, Tuple
from types import MappingProxyType

from pydantic import BaseModel

from api_client.exception import MissingMethodNameError

SUPPORTED_METHODS = frozenset(("get", "post", "put", "patch", "delete"))
ALIASES = MappingProxyType({"create": "post", "update": "put"})

class HTTPMethod(Enum):
    """HTTPMethod class."""

    GET = "get"
    DELETE = "delete"
    POST = "post"
    PUT = "put"
    PATCH = "patch"


class Endpoint(BaseModel):
    """Endpoint class."""

    name: str
    path: str
    method: Optional[HTTPMethod] = None
    model: Optional[type] = None
    query_parameters: Optional[Dict[str, str]] = None
    path_parameters: Optional[List[str]] = None

    def prepare(self) -> Tuple[str, str]:
        if not self.method:
             self.method = self._method_from_name()

    def _method_from_name(self) -> HTTPMethod:
        sections = self.name.split("_")
        method = sections[0]
        # get aliased method if exists
        method = ALIASES.get(method, method)
        if method not in SUPPORTED_METHODS:
            raise MissingMethodNameError(endpoint_name=self.name)

        # Inferred type from endpoint name.
        return HTTPMethod(method)
