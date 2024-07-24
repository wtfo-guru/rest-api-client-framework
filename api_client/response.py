"""
Response module for the package api_client of rest-api-client-framework library.

Classes:
    RestResponse
"""

import io
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Optional

from requests import Response

_JSON = "json"

CONTENT_EXT_MAP = MappingProxyType(
    {
        _JSON: _JSON,
        "png": "png",
        "jpeg": "jpeg",
        "pdf": "pdf",
        "webp": "webp",
    },
)


class RestResponse(io.IOBase):
    """This is a class to handle request responses.

    :param response: request.Response object
    :type response: request.Response
    """

    _headers: Dict[str, str]
    _status_code: int

    def __init__(self, resp: Response) -> None:
        """Construct a RestResponse object."""
        self.response = resp
        self._status_code = resp.status_code
        self.reason = resp.reason
        self._headers = {}
        for kk, vv in resp.headers.items():
            self._headers[str(kk).lower()] = str(vv)

        try:
            self._data = json.loads(resp.content.decode("utf-8"))  # noqa: WPS110
        except ValueError:
            self._data = resp.content  # noqa: WPS110

    @property
    def status_code(self) -> int:
        """Return response status code."""
        return self._status_code

    @property
    def headers(self) -> Dict[str, str]:
        """Returns a dictionary of the response headers."""
        return self._headers

    def is_json(self) -> bool:
        """
        Check that response data is json document.

        :rtype:
            bool
        """
        ct = self.header("content-type")
        if ct is None:
            return False

        return "application/json" in ct

    def header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Return a given response header.

        :param name:
            Header name
        :param default:
            Set default value if header not exists
        :rtype:
            string
        """
        if name not in self._headers:
            return default

        return self._headers[name]

    def data(self) -> Any:  # noqa: WPS110
        """
        Return data downloaded from api.

        :return:
            return data from api
        """
        return self._data

    def save(self, path: str) -> str:  # noqa: WPS210
        """Save response data to file.

        If you set file path without extension method will auto detect output file
        extension from mime type.
        Example you take screenshot and want to save to jpg.
        Set path to:
        1. /tmp/example_1_file_name -> will detect extension from mime type and save
        file to /tmp/example_1_file_name.jpg
        2. /tmp/example_2_file_name.jpg -> extension is in file path so dont detect
        extension from mime and save to /tmp/example_2_file_name.jpg

        :param path: file save path
        :type path: str
        :raises ValueError: if file extension is not set
        :return: saved file path
        :rtype: str
        """
        # find extension
        o_path = Path(path)
        ext = o_path.suffix.lstrip(".")

        add_ext_to_path = False
        if not (ext and ext in {_JSON, "png", "jpg", "pdf", "webp"}):
            content_type = self.header("content-type")
            if content_type is not None:
                ext = CONTENT_EXT_MAP.get(content_type, "")
            add_ext_to_path = True

        if not ext:
            raise ValueError("Unknown file extension to save")

        save_path = path
        if add_ext_to_path:
            save_path = "{0}.{1}".format(path, ext)

        if ext == _JSON:
            with open(save_path, "w") as save_t:
                json.dump(self._data, save_t)
        else:
            with open(save_path, "wb") as save_b:
                save_b.write(self._data)
                save_b.close()

        return save_path
