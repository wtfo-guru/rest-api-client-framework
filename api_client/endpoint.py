import re
from enum import Enum
from typing import Dict, List, Optional, Tuple
from types import MappingProxyType
from urllib.parse import urljoin

from pydantic import BaseModel

from api_client.exception import MissingMethodNameError, MissingArgumentError
from api_client.payload import IntStrBool

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
    query_parameters: Optional[List[str]] = None

    def prepare(self, url_root: str, **kwargs: IntStrBool) -> Tuple[str, str]:
        if self.method is None:
             self.method = self._method_from_name()
        query = self._prepare_query(**kwargs)
        path = self._prepare_path(**kwargs)
        url = urljoin(url_root, path)
        if query:
            url = urljoin(url, query)
        return url, self.method.name

    def _method_from_name(self) -> HTTPMethod:
        sections = self.name.split("_")
        method = sections[0]
        # get aliased method if exists
        method = ALIASES.get(method, method)
        if method not in SUPPORTED_METHODS:
            raise MissingMethodNameError(endpoint_name=self.name)

        # Inferred type from endpoint name.
        return HTTPMethod(method)

    def _prepare_query(self, **kwargs: IntStrBool) -> str:
        if not self.query_parameters:
            return ""
        parameters = []
        for key, val in kwargs.items():
            if isinstance(val, int):
                str_val = str(val)
            elif isinstance(val, bool):
                str_val = str(val).lower()
            else:
                str_val = val
            if key in self.query_parameters:
                parameters.append("{0}={1}".format(key, str_val))
        return "?{0}".format("&".join(parameters))

    def _prepare_path(self, **kwargs: IntStrBool) -> str:
        path_parameters = self._path_parameters()
        if path_parameters is None:
            return self.path
        path_kwargs = {}
        for key, val in kwargs.items():
            if key in path_parameters:
                path_kwargs[key] = val
        path = self.path.format(**path_kwargs)
        md = re.search("{([^}]+)}", path)
        if md:
            raise MissingArgumentError("Missing path parameter argument: {0}".format(md[1]))
        return path


    def _path_parameters(self, path: str) -> Optional[List[str]]:
        """Extract the path parameters.

        Parameters
        ----------
        path : str
            The path with parameters.

        Returns
        -------
        Optional[List[str]]
            List of path parameters.
        """
        params = re.findall("({[a-z_]+})", path)
        if not params:
            return None
        path_parameters: List[str] = []
        for param in params:
            path_parameters.append(re.sub("{|}", "", str(param)))
        return path_parameters

