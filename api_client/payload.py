"""Top-level module cli for __PROJECT__."""

from typing import Dict, Union

from pydantic import BaseModel

IntStrBool = Union[int, str, bool]
Body = Union[bytes, Dict[str, IntStrBool], BaseModel]


class Payload:
    """Payload class to manage api payloads.

    :param body: Data to send to an API endpoint
    :type body: Body
    """

    body: Body

    def __init__(self, body: Body):
        """_summary_

        :param body: _description_
        :type body: Body
        """
        self.body = body
