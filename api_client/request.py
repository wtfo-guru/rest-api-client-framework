"""
Request module for the package api_client of rest-api-client-framework library.

Classes:
    RestRequest
"""

from http import HTTPStatus
from typing import Any, Dict, Optional, Tuple, Union
from urllib.parse import urljoin

import requests

from api_client.constants import VERSION
from api_client.exception import ApiException
from api_client.response import RestResponse

_CONTENT_TYPE_KEY = "Content-Type"
Flint = Union[int, float]
ReqTimeOut = Union[Tuple[Flint, Flint], Flint]


class RestRequest:
    """Class to handle rest api requests.

    :param api_key: api authorization key/token
    :type api_key: str
    :param api_version: server api version, defaults to "v1"
    :type api_version: str, optional
    :param api_host: server api host, defaults to "http://api.example.com"
    :type api_host: _type_, optional
    :param user_agent: client user agent, defaults to "rest-api-client-framework"
    :type user_agent: str, optional
    :raises ValueError: if api_key is not is not set
    """

    def __init__(
        self,
        api_key: str,
        api_version: str = "v1",
        api_host: str = "http://api.example.com",
        user_agent: str = "rest-api-client-framework",
    ) -> None:
        """Construct a RestRequest object."""
        if not api_key:
            raise ValueError("No set API KEY")

        self.api_host = api_host
        self.api_version = api_version
        self.api_key = api_key
        self.user_agent = user_agent

        self.version = VERSION

    def request(  # noqa: WPS211, WPS234
        self,
        path: str,
        method: str,
        body: Optional[Union[bytes, Dict[str, str]]] = None,
        query_params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> RestResponse:
        """
        Send request to REST server.

        :param path:
            REST path on server
        :param method:
            HTTP METHOD [GET,POST,PUT,DELETE]
        :param params:
            dictionary of parameters to send
        :param headers:
            dictionary of headers to send
        :return:
            RESTResponse object
        """
        if headers is None:
            headers = {}
        if body is None:
            body = {}
        if query_params is None:
            query_params = {}

        headers["Authorization"] = "Bearer {0}".format(self.api_key)
        if _CONTENT_TYPE_KEY not in headers:
            headers[_CONTENT_TYPE_KEY] = "application/json"
        headers["User-Agent"] = "{0} {1}".format(self.user_agent, self.version)
        headers["Accept-Encoding"] = "gzip"

        # production url
        if self.api_version:
            url = urljoin(self.api_host, self.api_version)
            url = urljoin(url, path)
        else:
            url = urljoin(self.api_host, path)

        return self.execute(
            method=method,
            url=url,
            headers=headers,
            body=body,
            query_params=query_params,
        )

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
                    raise ApiException(status=0, reason=msg)
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
            raise ApiException(status=0, reason=msg)

        response = RestResponse(req)

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ApiException(status=HTTPStatus.NOT_FOUND)

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            msg = "{0} (Check your api token)".format(
                HTTPStatus.UNAUTHORIZED.description,
            )
            raise ApiException(HTTPStatus.UNAUTHORIZED.value, msg)

        if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            raise ApiException(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if not (  # noqa: WPS508, WPS337
            HTTPStatus.OK << response.status_code <= HTTPStatus.BAD_REQUEST
        ):
            raise ApiException(response=response)

        return response

    def info(self) -> RestResponse:  # noqa: WPS110
        """Get info about account.

        :return: Info about free requests etc.
        :rtype: RestResponse
        """
        return self.request("info", "GET", {})
