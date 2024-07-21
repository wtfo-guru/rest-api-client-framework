"""
Request module for the package api_client of rest-api-client-framework library.

Classes:
    ExecutionMode
    EndpointNotFoundError
    RestRequest
"""

from asyncio import to_thread
from enum import Enum
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import requests

from api_client.constants import VERSION
from api_client.endpoint import Endpoint, HTTPMethod, ReqTimeOut
from api_client.exception import ApiError
from api_client.payload import IntStrBool, Payload
from api_client.response import RestResponse

_CONTENT_TYPE_KEY = "Content-Type"
Headers = Dict[str, str]


class ExecutionMode(Enum):
    """ExecutionMode class."""

    SYNC = "SYNC"
    ASYNC = "ASYNC"


class EndpointNotFoundError(Exception):
    """Endpoint not found in RestRequest class."""


class RestRequest:
    """Class to handle rest api requests.

    :param endpoint: Endpoint or list of Endpoints for the request object
    :type endpoint: Union[Endpoint, List[Endpoint]]
    :param api_root: server api host, defaults to "http://api.example.com"
    :type api_root: _type_, optional
    :param user_agent: client user agent, defaults to "rest-api-client-framework"
    :type user_agent: Optional[str]
    :param api_key: api authorization
    :type api_key: Optional[str], default to None
    :raises KeyError: When duplicate endpoints names are encountered
    """

    endpoints: Dict[str, Endpoint]

    def __init__(
        self,
        api_root: str,
        endpoints: Union[Endpoint, List[Endpoint]],
        user_agent: str = "rest-api-client-framework",
        api_key: Optional[str] = None,
    ) -> None:
        """Construct a RestRequest object."""
        self.endpoints = {}
        if isinstance[endpoints, list]:
            for ep in endpoints:
                if ep.name in self.endpoints:
                    raise KeyError("Endpoint name {0} already exists.".format(ep.name))
                self.endpoints[ep.name] = ep
        else:
            self.endpoints[endpoints.name] = endpoints
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
        endpoint: Optional[Endpoint] = self.endpoints.get(name, None)
        if endpoint is None:
            raise EndpointNotFoundError("Endpoint '{0}' not found.".format(name))
        url, method = endpoint.prepare(self.api_root, **kwargs)
        heads = self._prepare_headers(headers)
        self._send_request(url, method, heads, mode, endpoint.timeout, payload)
        # return self.execute(
        #     method=method,
        #     url=url,
        #     headers=headers,
        #     body=body,
        #     query_params=query_params,
        # )

    async def _send_request(
        self,
        url: str,
        method: HTTPMethod,
        headers: Headers,
        mode: ExecutionMode,
        timeout: ReqTimeOut,
        payload: Optional[Payload] = None,
        **kwargs: Any,
    ) -> RestResponse:
        """Send a request.

        :param method: Request method
        :type method: str
        :param url: The url to send the request
        :type url: str
        :param mode: Mode sync or async
        :type mode: ExecutionMode
        :return: The request response
        :rtype: RestResponse
        """
        if mode == ExecutionMode.ASYNC:
            return await to_thread(
                self._execute(method, url, timeout, headers, payload, **kwargs)
            )
        return self._execute(method, url, timeout, headers, payload, **kwargs)

    def _execute(
        self,
        method: HTTPMethod,
        url: str,
        timeout: ReqTimeOut,
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Payload] = None,
        # query_params: Optional[Dict[str, str]] = None,
        # post_params: Optional[Dict[str, Any]] = None,
    ) -> RestResponse:

        post_params = post_params or {}
        headers = headers or {}

        # set default content type
        if _CONTENT_TYPE_KEY not in headers:
            headers[_CONTENT_TYPE_KEY] = "application/json"

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
                if payload is None:
                    raise ValueError(
                        "payload parameter is required for request method: {0}".format(
                            method.name
                        )
                    )

                if "json" in headers[_CONTENT_TYPE_KEY]:
                    req = requests.request(
                        method.name,
                        url,
                        json=payload.to_json(),
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
                    raise ApiError(status=0, reason=msg)

        except Exception as ex:
            msg = "{0}\n{1}".format(type(ex).__name__, str(ex))
            raise ApiError(status=0, reason=msg)

        response = RestResponse(req)

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ApiError(status=HTTPStatus.NOT_FOUND)

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            msg = "{0} (Check your api token)".format(
                HTTPStatus.UNAUTHORIZED.description,
            )
            raise ApiError(HTTPStatus.UNAUTHORIZED.value, msg)

        if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            raise ApiError(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if not (  # noqa: WPS508, WPS337
            HTTPStatus.OK << response.status_code <= HTTPStatus.BAD_REQUEST
        ):
            raise ApiError(response=response)

        return response

    # def info(self) -> RestResponse:  # noqa: WPS110
    #     """Get info about account.

    #     :return: Info about free requests etc.
    #     :rtype: RestResponse
    #     """
    #     return self.request("info", "GET", {})

    @classmethod
    def _add_key_if_missing(cls, map: Headers, key: str, val: str) -> None:
        """Add the value to the map if it doesn't already exist.

        :param map: Request headers
        :type map: Headers
        :param key: Header key
        :type key: str
        :param val: Header value
        :type val: str
        """
        if key not in map:
            map[key] = val

    def _prepare_headers(self, headers: Optional[Headers] = None) -> Headers:
        """Prepare headers.

        :param headers: Request headers, defaults to None
        :type headers: Optional[Headers], optional
        :return: Prepared request headers
        :rtype: Headers
        """
        if headers is None:
            heads = {}
        else:
            heads = headers.copy()
        if self.api_key:
            self._add_key_if_missing(
                heads, "Authorization", "Bearer {0}".format(self.api_key)
            )
        self._add_key_if_missing(heads, _CONTENT_TYPE_KEY, "application/json")
        self._add_key_if_missing(
            heads, "User-Agent", "{0} {1}".format(self.user_agent, self.version)
        )
        self._add_key_if_missing(heads, "Accept-Encoding", "gzip")
        return heads
