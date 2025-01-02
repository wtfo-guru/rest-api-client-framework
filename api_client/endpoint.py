"""
Request module for the package api_client of rest-api-client-framework library.

Variables:
    SUPPORTED_REQUEST_METHODS
    REQUEST_METHOD_ALIASES

Classes:
    HTTPMethod
    Endpoint
"""

import re
from enum import Enum
from types import MappingProxyType
from typing import List, Optional, Tuple, Union

from pydantic import BaseModel

from api_client.exception import MissingArgumentError, MissingMethodNameError
from api_client.logger import logger
from api_client.payload import IntStrBool

SUPPORTED_REQUEST_METHODS = frozenset(("get", "post", "put", "patch", "delete"))
REQUEST_METHOD_ALIASES = MappingProxyType({"create": "post", "update": "put"})

Flint = Union[int, float]
ReqTimeOut = Union[Tuple[Flint, Flint], Flint]


def multi_urljoin(*parts: str) -> str:
    """Assemble a url from parts.

    :return: The assembled URL string
    :rtype: str
    """
    url = parts[0].strip("/")
    for part in parts[1:]:
        if part:
            if part.startswith("?"):
                url = "{0}{1}".format(url, part.strip("/"))
            else:
                url = "{0}/{1}".format(url, part.strip("/"))
    return url


class HTTPMethod(Enum):
    """HTTPMethod class."""

    GET = "get"
    # HEAD = "head" not needed for apis ??
    DELETE = "delete"
    POST = "post"
    PUT = "put"
    # OPTIONS = "options" not needed for apis ??
    PATCH = "patch"


class Endpoint(BaseModel):
    """
    The Endpoint object contains information to assemble a url to an api endpoint.

    :param `**kwargs`: The keyword arguments to initialize instance variables.
    :ivar name: This is name of the endpoint
    :vartype name: str
    :ivar path: This is is the url relative path
    :vartype path: str
    :ivar request_method: This is request_method type, defaults to None
    :vartype name: HTTPMethod, optional
    :ivar model: This is a pydantic BaseModel to be used for request response
    :vartype name: BaseModel
    :ivar query_parameters: List of query parameters
    :vartype name: List[str]
    """

    name: str
    path: str
    request_method: Optional[HTTPMethod] = None
    model: Optional[type] = None
    query_parameters: Optional[List[str]] = None
    timeout: ReqTimeOut = (6.1, 20)

    def prepare(self, url_root: str, **kwargs: IntStrBool) -> Tuple[str, HTTPMethod]:
        """Prepare the endpoint url.

        :param url_root: The api endpoint root path
        :type url_root: str
        :return: Prepared URL, Request method
        :rtype: Tuple[str, str]
        """
        if self.request_method is None:
            self.request_method = self._method_from_name()  # noqa: WPS601
        # TODO: Research and implement urllib.parse.quote/quote_plus
        query = self._prepare_query(**kwargs)
        path = self._prepare_path(**kwargs)
        # url = "{0}/{1}{2}".format(url_root.rstrip("/"), path.strip("/"), query)
        url = multi_urljoin(url_root, path, query)
        logger.debug("url: {0}".format(url))
        return url, self.request_method

    def _method_from_name(self) -> HTTPMethod:
        """Extract request_method type from the instance name.

        :raises MissingMethodNameError: If request_method type cannot be extracted
            from name.
        :return: The extracted request_method type.
        :rtype: HTTPMethod
        """
        sections = self.name.split("_")
        request_method = sections[0]
        # get aliased request_method if exists
        request_method = REQUEST_METHOD_ALIASES.get(request_method, request_method)
        if request_method not in SUPPORTED_REQUEST_METHODS:
            raise MissingMethodNameError(endpoint_name=self.name)

        # Inferred type from endpoint name.
        return HTTPMethod(request_method)

    def _prepare_query(self, **kwargs: IntStrBool) -> str:
        """Prepare the query from the kwargs.

        :return: Prepared query
        :rtype: str
        """
        if not self.query_parameters:
            return ""
        valors = []
        for key, valor in kwargs.items():
            # since bool is an instance of int, we test it before int
            if isinstance(valor, bool):
                str_val = str(valor).lower()
            elif isinstance(valor, int):
                str_val = str(valor)
            else:
                str_val = valor
            if key in self.query_parameters:
                valors.append("{0}={1}".format(key, str_val))
        return "?{0}".format("&".join(valors))

    def _prepare_path(self, **kwargs: IntStrBool) -> str:
        """Replace path parameters with values.

        :raises MissingArgumentError: If a path variable is not specified in kwargs
        :return: Prepared path
        :rtype: str
        """
        path_parameters = self._path_parameters()
        if path_parameters is None:
            return self.path
        path_kwargs = {}
        for key, valor in kwargs.items():
            if key in path_parameters:
                path_kwargs[key] = valor
        try:
            path = self.path.format(**path_kwargs)
        except KeyError as ex:
            raise MissingArgumentError(str(ex))
        # md = re.search("{([^}]+)}", path)
        # if md:
        #     raise MissingArgumentError(
        #         "Missing path parameter argument: {0}".format(md[1])
        #     )
        return path

    def _path_parameters(self) -> Optional[List[str]]:
        """Extract the path parameters.

        :return: List of path parameters
        :rtype: Optional[List[str]]
        """
        variables = re.findall("({[a-z_]+})", self.path)
        if not variables:
            return None
        path_parameters: List[str] = []
        for parameter in variables:
            path_parameters.append(re.sub("{|}", "", str(parameter)))
        return path_parameters
