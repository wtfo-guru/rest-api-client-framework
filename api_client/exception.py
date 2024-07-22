"""
Exception module for the package api_client of rest-api-client-framework library.

Classes:
    PathParamSubError
    MissingMethodNameError
    ApiError
"""

from http import HTTPStatus
from typing import Optional, Union

from api_client.response import RestResponse

MISSING_ARGUMENT_MSG_FMT = """
The path parameter {0} was not substituted.
"""

MISSING_METHOD_MSG_FMT = """
Missing method name for endpoint {0}.
Pass it as an argument or declare it in the format:

- get_your_resource_name
- post_something
- put_asd
- patch_another
- delete_snake_case
"""


class MissingArgumentError(Exception):
    """Path parameter substitution failed."""

    def __init__(self, arg: str):
        """Construct a MissingArgumentError exception.

        Parameters
        ----------
        arg : str
            The name of the path parameter not substituted.
        """
        self.msg = MISSING_ARGUMENT_MSG_FMT.format(arg)


class MissingMethodNameError(Exception):
    """HTTP Method is missing from endpoint."""

    def __init__(self, endpoint_name: str):
        """Construct a MissingMethodName exception.

        Parameters
        ----------
        endpoint_name : str
            The name of the missing endpoint.
        """
        self.msg = MISSING_METHOD_MSG_FMT.format(endpoint_name)


class ApiError(Exception):
    """ApiError class.

    :param status: status code, defaults to None
    :type status: Optional[Union[HTTPStatus, int]], optional
    :param reason: reason for the exception, defaults to None
    :type reason: Optional[str], optional
    :param response: RestResponse object, defaults to None
    :type response: Optional[RestResponse], optional
    """

    status: int
    reason: str
    response: Optional[RestResponse]

    def __init__(
        self,
        status: Optional[Union[HTTPStatus, int]] = None,
        reason: Optional[str] = None,
        response: Optional[RestResponse] = None,
    ) -> None:
        """Construct aa ApiError object."""
        if response:
            self.status = response.status_code
            self.reason = response.reason
            self.response = response
        else:
            self.response = None
            if isinstance(status, HTTPStatus):
                self.status = status.value
                self.reason = status.description
            else:
                self.status = 0 if status is None else int(status)
                self.reason = "Unknown" if reason is None else reason

    def __str__(self) -> str:
        """Compose error messages for exception."""
        error_message = "({0})\nReason: {1}\n".format(self.status, self.reason)
        if self.response:
            if self.response.headers:
                error_message += "HTTP response headers: {0}\n".format(
                    self.response.headers,
                )

            body = self.response.data()
            if body:
                error_message += "HTTP response body: {0}\n".format(str(body))

        return error_message
