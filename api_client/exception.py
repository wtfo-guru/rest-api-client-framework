"""
Exception module for the package api_client of rest-api-client-framework library.

Classes:
    ApiException
"""

from http import HTTPStatus
from typing import Optional, Union

from api_client.response import RestResponse


class ApiException(Exception):
    """ApiException class."""

    status: int
    reason: str
    response: Optional[RestResponse]

    def __init__(
        self,
        status: Optional[Union[HTTPStatus, int]] = None,
        reason: Optional[str] = None,
        response: Optional[RestResponse] = None,
    ) -> None:
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
        """Custom error messages for exception"""
        error_message = "({0})\n" "Reason: {1}\n".format(self.status, self.reason)
        if self.response:
            if self.response.headers:
                error_message += "HTTP response headers: {0}\n".format(
                    self.response.headers
                )

            body = self.response.data()
            if body:
                error_message += "HTTP response body: {0}\n".format(str(body))

        return error_message
