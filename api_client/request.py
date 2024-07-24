"""
Request module for the package api_client of rest-api-client-framework library.

Classes:
    ExecutionMode
    EndpointNotFoundError
    RestRequest
"""

from enum import Enum
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import requests
from requests.structures import CaseInsensitiveDict

from api_client.constants import VERSION
from api_client.endpoint import Endpoint, HTTPMethod, ReqTimeOut
from api_client.exception import ApiClientError
from api_client.payload import IntStrBool, Payload
from api_client.response import RestResponse

# from urllib.parse import urljoin


_CONTENT_TYPE_KEY = "Content-Type"

Headers = CaseInsensitiveDict[str]


class ExecutionMode(Enum):
    """ExecutionMode class."""

    SYNC = "SYNC"  # noqa: WPS115
    ASYNC = "ASYNC"  # noqa: WPS115


class EndpointNotFoundError(Exception):
    """Endpoint not found in RestRequest class."""


class RestRequest:  # noqa: WPS214
    """Class to handle rest api requests.

    :param endpoint: Endpoint or list of Endpoints for the request object
    :type endpoint: Union[Endpoint, List[Endpoint]]
    :param api_root: server api host, defaults to "http://api.example.com"
    :type api_root: _type_, optional
    :param user_agent: client user agent, defaults to "rest-api-client-framework"
    :type user_agent: Optional[str]
    :param api_key: api authorization
    :type api_key: Optional[str], default to None
    """

    _endpoints: Dict[str, Endpoint]

    def __init__(
        self,
        api_root: str,
        endpoints: Union[Endpoint, List[Endpoint]],
        user_agent: str = "rest-api-client-framework",
        api_key: Optional[str] = None,
    ) -> None:
        """Construct a RestRequest object."""
        self._endpoints = {}
        if isinstance(endpoints, Endpoint):
            self._register_endpoint(endpoints)
        else:
            self._register_endpoints(endpoints)
        self.api_root = api_root
        self.user_agent = user_agent
        self.api_key = api_key

        self.version = VERSION

    def call_endpoint(
        self,
        name: str,
        payload: Optional[Payload] = None,
        headers: Optional[Headers] = None,
        mode: ExecutionMode = ExecutionMode.SYNC,
        **kwargs: IntStrBool,
    ) -> RestResponse:
        """Call endpoint.

        :param name: Endpoint name
        :type name: str
        :param payload: Payload to send, defaults to None
        :type payload: Optional[Payload], optional
        :param headers: Headers to send, defaults to None
        :type headers: Optional[Headers], optional
        :param mode: Sync or async, defaults to ExecutionMode.SYNC
        :type mode: ExecutionMode, optional
        :raises EndpointNotFoundError: If endpoint not found
        :raises NotImplementedError: If mode is async
        :return: The RestResponse object
        :rtype: RestResponse
        """
        endpoint: Optional[Endpoint] = self._endpoints.get(name, None)
        if endpoint is None:
            raise EndpointNotFoundError("Endpoint '{0}' not found.".format(name))
        url, method = endpoint.prepare(self.api_root, **kwargs)

        if payload is None:
            payload = Payload()
        heads = self._prepare_headers(payload, headers)
        if mode == ExecutionMode.SYNC:
            return self._send_request(url, method, heads, endpoint.timeout, payload)
        raise NotImplementedError("Async request is not implemented yet!")

    def _register_endpoints(self, endpoints: List[Endpoint]) -> None:
        """Register Endpoints.

        :param endpoints: Endpoints to register
        :type endpoints: List[Endpoint]
        """
        for ep in endpoints:
            self._register_endpoint(ep)

    def _register_endpoint(self, endpoint: Endpoint) -> None:
        """Register Endpoint.

        :param endpoint: Endpoint to register
        :type endpoint: Endpoint
        :raises KeyError: If endpoint is already registered
        """
        if endpoint.name in self._endpoints:
            raise KeyError("Endpoint name {0} already exists.".format(endpoint.name))
        self._endpoints[endpoint.name] = endpoint

    def _send_request(
        self,
        url: str,
        method: HTTPMethod,
        headers: Headers,
        timeout: ReqTimeOut,
        payload: Optional[Payload] = None,
        **kwargs: Any,
    ) -> RestResponse:
        """Send a request.

        :param method: Request method
        :type method: str
        :param url: The url to send the request
        :type url: str
        :return: The request response
        :rtype: RestResponse
        """
        return self._execute(method, url, timeout, headers, payload, **kwargs)

    def _execute(  # noqa: C901, WPS238, WPS231
        self,
        method: HTTPMethod,
        url: str,
        timeout: ReqTimeOut,
        headers: Headers,
        payload: Optional[Payload],
    ) -> RestResponse:
        if payload is None:
            payload = Payload({})

        # run request
        try:
            if method == HTTPMethod.GET:
                req = requests.request(
                    method.name,
                    url,
                    timeout=timeout,
                    headers=headers,
                )
            else:
                if "json" in headers[_CONTENT_TYPE_KEY]:
                    req = requests.request(
                        method.name,
                        url,
                        json=payload.to_json(),
                        timeout=timeout,
                        headers=headers,
                    )
                elif payload.is_text:
                    req = requests.request(
                        method.name,
                        url,
                        data=payload.to_text(),
                        timeout=timeout,
                        headers=headers,
                    )
                elif payload.is_bytes:
                    req = requests.request(
                        method.name,
                        url,
                        data=payload.to_bytes(),
                        timeout=timeout,
                        headers=headers,
                    )
                else:
                    # Cannot generate the request from given parameters
                    msg = """Cannot prepare a request message for provided
                             arguments. Please check that your arguments match
                             declared content type."""
                    raise ApiClientError(status=0, reason=msg)

        except Exception as ex:
            msg = "{0}\n{1}".format(type(ex).__name__, str(ex))
            raise ApiClientError(status=0, reason=msg)

        response = RestResponse(req)

        self._check_response(response)

        return response

    # def info(self) -> RestResponse:  # noqa: WPS110
    #     """Get info about account.

    #     :return: Info about free requests etc.
    #     :rtype: RestResponse
    #     """
    #     return self.request("info", "GET", {})

    def _check_response(self, response: RestResponse) -> None:
        """Check the response status code.

        :param response: _description_
        :type response: _type_
        :raises ApiClientError: _description_
        """
        if HTTPStatus.OK <= response.status_code < HTTPStatus.BAD_REQUEST:
            return
        raise ApiClientError(response=response)

    @classmethod
    def _add_key_if_missing(
        cls,
        headers: Headers,
        key: str,
        header: Optional[str],
    ) -> None:
        """Add the value to the map if it doesn't already exist.

        :param headers: Request headers
        :type headers: Headers
        :param key: Header key
        :type key: str
        :param header: Header value
        :type header: str
        """
        if key not in headers:
            if header is None:
                raise ValueError(
                    "header '{0}' cannot be None.".format(key),
                )
            headers[key] = header

    def _prepare_headers(
        self,
        payload: Payload,
        headers: Optional[Headers] = None,
    ) -> Headers:
        """Prepare headers.

        :param payload: The Payload object
        :type payload: Payload
        :param headers: Request headers, defaults to None
        :type headers: Optional[Headers], optional
        :return: Prepared request headers
        :rtype: Headers
        """
        heads: Headers
        if headers is None:
            initial_headers: Dict[str, str] = {}
            heads = Headers(initial_headers)
        else:
            heads = headers.copy()
        if self.api_key:
            self._add_key_if_missing(
                heads,
                "Authorization",
                "Bearer {0}".format(self.api_key),
            )
        self._add_key_if_missing(heads, _CONTENT_TYPE_KEY, payload.content_type)
        self._add_key_if_missing(
            heads,
            "User-Agent",
            "{0} {1}".format(self.user_agent, self.version),
        )
        self._add_key_if_missing(heads, "Accept-Encoding", "gzip")
        return heads
