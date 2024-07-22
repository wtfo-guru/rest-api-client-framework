"""
Module payload for the package api_client of rest-api-client-framework library.

Classes:
    Payload
"""

import json
from typing import Dict, Union

from pydantic import BaseModel

IntStrBool = Union[int, str, bool]
Body = Union[bytes, Dict[str, IntStrBool], BaseModel]


class Payload:
    """Payload class to manage api payloads.

    :param body: Data to send to an API endpoint
    :type body: Body
    """

    _body: Body

    def __init__(self, body: Body):
        """Construct payload object."""
        self._body = body

    @property
    def is_bytes(self) -> bool:
        """Return true if payload type is bytes.

        :return: True if payload is bytes
        :rtype: bool
        """
        return isinstance(self._body, bytes)

    def to_json(self) -> str:
        """Return payload as JSON string.

        :raises ValueError: If payload is bytes type
        :return: JSON string.
        :rtype: str
        """
        if isinstance(self._body, BaseModel):
            return self._body.model_dump_json()
        elif isinstance(self._body, dict):
            return json.dumps(self._body)
        raise ValueError(
            "Payload type {0} cannot be expressed as json.".format(type(self._body)),
        )

    def to_bytes(self) -> bytes:
        """Return payload as bytes.

        :raises ValueError: If payload is not bytes type
        :return: Payload as bytes
        :rtype: bytes
        """
        if isinstance(self._body, bytes):
            return self._body
        raise ValueError(
            "Payload type {0} cannot be expressed as bytes.".format(type(self._body)),
        )
