"""
Module payload for the package api_client of rest-api-client-framework library.

Classes:
    Payload
"""

import json
from typing import Dict, Optional, Union

from pydantic import BaseModel

IntStrBool = Union[int, str, bool]
Body = Union[str, bytes, Dict[str, IntStrBool], BaseModel]


class Payload:
    """Payload class to manage api payloads.

    :param body: Data to send to an API endpoint
    :type body: Body
    """

    _body: Optional[Body]
    _content_type: Optional[str]

    def __init__(self, body: Body = None, content_type: str = None):
        """Construct payload object."""
        self._body = body
        self._content_type = content_type

    @property
    def content_type(self) -> str:
        if self._content_type is not None:
            return self._content_type
        if self._body is None:
            return "application/json"
        if isinstance(self._body, BaseModel) or isinstance(self._body, dict):
            return "application/json"
        if isinstance(self._body, str):
            return "text/plain"
        raise ValueError(
            "Content-Type cannot be determined for payload type {0}.".format(
                type(self._body),
            ),
        )


    @property
    def is_bytes(self) -> bool:
        """Return true if payload type is bytes.

        :return: True if payload is bytes
        :rtype: bool
        """
        if self._body is None:
            return False
        return isinstance(self._body, bytes)

    def to_json(self) -> Optional[str]:
        """Return payload as JSON string.

        :raises ValueError: If payload is bytes type
        :return: JSON string.
        :rtype: str
        """
        if self._body is not None:
            if isinstance(self._body, BaseModel):
                return self._body.model_dump_json()
            elif isinstance(self._body, dict):
                return json.dumps(self._body)
            raise ValueError(
                "Payload type {0} cannot be expressed as json.".format(
                    type(self._body),
                ),
            )
        return {}

    def to_bytes(self) -> Optional[bytes]:
        """Return payload as bytes.

        :raises ValueError: If payload is not bytes type
        :return: Payload as bytes
        :rtype: bytes
        """
        if self._body is not None:
            if isinstance(self._body, bytes):
                return self._body
            raise ValueError(
                "Payload type {0} cannot be expressed as bytes.".format(type(self._body)),
            )

    def to_text(self) -> Optional[str]:
        """Return payload as bytes.

        :raises ValueError: If payload is not str type
        :return: Payload as text
        :rtype: str
        """
        if self._body is not None:
            if isinstance(self._body, str):
                return self._body
            raise ValueError(
                "Payload type {0} cannot be expressed as text.".format(type(self._body)),
            )
