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
from api_client.endpoint import Endpoint
from api_client.exception import ApiError
from api_client.payload import IntStrBool, Payload
from api_client.response import RestResponse

_CONTENT_TYPE_KEY = "Content-Type"
Flint = Union[int, float]
ReqTimeOut = Union[Tuple[Flint, Flint], Flint]


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
        self, name: str, *args: IntStrBool, payload: Payload, **kwargs: IntStrBool
    ) -> RestResponse:
        endpoint: Optional[Endpoint] = self.endpoints.get(name, None)
        if endpoint is None:
            raise EndpointNotFoundError("Endpoint '{0}' not found.".format(name))

    def request(
        self,
        endpoint: Endpoint,
        payload: Optional[Payload] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> RestResponse:
        """_summary_

        :param endpoint: Endpoint to request
        :type endpoint: Endpoint
        :param payload: The request payload, defaults to None
        :type payload: Optional[Payload], optional
        :param headers: The request headers, defaults to None
        :type headers: Optional[Dict[str, str]], optional
        :return: The request response
        :rtype: RestResponse
        """
        if headers is None:
            headers = {}

        if self.api_key:
            headers["Authorization"] = "Bearer {0}".format(self.api_key)
        if _CONTENT_TYPE_KEY not in headers:
            headers[_CONTENT_TYPE_KEY] = "application/json"
        headers["User-Agent"] = "{0} {1}".format(self.user_agent, self.version)
        headers["Accept-Encoding"] = "gzip"

        method, url = endpoint.prepare(self.api_root)

        return self.execute(
            method=method,
            url=url,
            headers=headers,
            body=body,
            query_params=query_params,
        )

    async def send_request_async(
        self, method: str, url: str, **kwargs: Any,
    ) -> RestResponse:
        """Send an asynchronous request.

        :param method: Request method
        :type method: str
        :param url: The url to send the request
        :type url: str
        :return: The request response
        :rtype: RestResponse
        """
        return await to_thread(requests.request(method, url, **kwargs))

    def send_request(
        self, method, url: str, mode: ExecutionMode, **kwargs: Any,
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
            return self.send_request_async(method, url, **kwargs)
        return requests.request(method, url, **kwargs)

    def execute(  # noqa: WPS234, WPS231, WPS210, WPS211, C901, WPS238
        self,
        method: str,
        url: str,
        query_params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[bytes, Dict[str, Any]]] = None,
        post_params: Optional[Dict[str, Any]] = None,
        timeout: ReqTimeOut = (6.1, 20),
    ) -> RestResponse:
        """
        Execute raw request to server.

        :param method:
            Http method
        :param url:
            Absolute url https://example.com
        :param query_params:
            Dict with with query params
        :param headers:
            Dict with headers
        :param body:
            Raw body for post query
        :param post_params:
            When send application/x-www-form query set this attribute
        :param request_timeout:
            Timeout in seconds
        :return: RestResponse
        """
        # get method
        method = method.upper()
        assert method in {  # noqa: S101
            "GET",
            "HEAD",
            "DELETE",
            "POST",
            "PUT",
            "PATCH",
            "OPTIONS",
        }

        if post_params and body:
            raise ValueError(
                "body parameter cannot be used with post_params parameter.",
            )

        post_params = post_params or {}
        headers = headers or {}

        # set default content type
        if _CONTENT_TYPE_KEY not in headers:
            headers[_CONTENT_TYPE_KEY] = "application/json"

        # run request
        try:
            # For `POST`, `PUT`, `PATCH`, `OPTIONS`, `DELETE`
            if method in {"POST", "PUT", "PATCH", "OPTIONS", "DELETE"}:

                if query_params:
                    url = "{0}?{1}".format(url, query_params)

                if "json" in headers[_CONTENT_TYPE_KEY]:
                    req = requests.request(
                        method,
                        url,
                        json=body,
                        timeout=timeout,
                        headers=headers,
                    )
                elif (  # noqa: WPS337
                    headers[_CONTENT_TYPE_KEY] == "application/x-www-form-urlencoded"
                ):  # noqa: E501
                    req = requests.request(
                        method,
                        url,
                        params=post_params,
                        timeout=timeout,
                        headers=headers,
                    )
                elif headers[_CONTENT_TYPE_KEY] == "multipart/form-data":
                    # must del headers['Content-Type'], or the correct
                    # Content-Type which generated by urllib3 will be
                    # overwritten.
                    headers.pop(_CONTENT_TYPE_KEY)
                    req = requests.request(
                        method,
                        url,
                        params=post_params,
                        timeout=timeout,
                        headers=headers,
                    )
                # Pass a `string` parameter directly in the body to support
                # other content types than Json when `body` argument is
                # provided in serialized form

                elif isinstance(body, bytes):
                    req = requests.request(
                        method,
                        url,
                        data=body,
                        timeout=timeout,
                        headers=headers,
                    )
                else:
                    # Cannot generate the request from given parameters
                    msg = """Cannot prepare a request message for provided
                             arguments. Please check that your arguments match
                             declared content type."""
                    raise ApiError(status=0, reason=msg)
            # For `GET`, `HEAD`
            else:
                req = requests.request(
                    method,
                    url,
                    params=query_params,
                    timeout=timeout,
                    headers=headers,
                )

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

    def info(self) -> RestResponse:  # noqa: WPS110
        """Get info about account.

        :return: Info about free requests etc.
        :rtype: RestResponse
        """
        return self.request("info", "GET", {})
