"""
Exception module for the package api_client of rest-api-client-framework library.

Classes:
    ApiException
"""

from typing import Optional

from requests import Response


class ApiException(Exception):
    """ApiException class."""

    status: Optional[int]
    reason: Optional[str]
    response: Optional[Response]

    def __init__(
        self,
        status: Optional[int] = None,
        reason: Optional[str] = None,
        http_resp: Optional[Response] = None,
    ) -> None:

        if http_resp:
            self.status = http_resp.status_code
            self.reason = http_resp.reason
        else:
            self.status = status
            self.reason = reason
        self.response = http_resp

    def __str__(self) -> str:
        """Custom error messages for exception"""
        error_message = "({0})\n" "Reason: {1}\n".format(self.status, self.reason)
        if self.response:
            if self.response.headers:
                error_message += "HTTP response headers: {0}\n".format(
                    self.response.headers
                )

            body = self.response.text
            if body:
                error_message += "HTTP response body: {0}\n".format(body)

        return error_message
