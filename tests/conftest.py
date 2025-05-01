"""
Module conftest module for package tests of rest-api-client-framework library.

Functions:
    github
    foo_bar
    image_bytes
    httpserver_listen_address
    request_client
    response
    response_image
"""

import os

os.environ["REST_API_CLIENT_FRAMEWORK_TESTING"] = "Yes"
os.environ["REST_API_CLIENT_FRAMEWORK_LOG_LEVEL"] = "DEBUG"

import base64
from http import HTTPStatus
from typing import Dict, List

import pytest
from requests import Response
from requests.structures import CaseInsensitiveDict

from api_client.endpoint import Endpoint, HTTPMethod
from api_client.request import RestRequest

EXAMPLE_IMAGE = (
    "/9j/4AAQSkZJRgABAQEASABIAAD/4gxYSUNDX1BST0ZJTEUAAQEAAAxITGlubwIQAABtbnRyUkdCIFhZ"
    "WiAHzgACAAkABgAxAABhY3NwTVNGVAAAAABJRUMgc1JHQgAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLUhQ"
    "ICAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABFjcHJ0AAABUAAA"
    "ADNkZXNjAAABhAAAAGx3dHB0AAAB8AAAABRia3B0AAACBAAAABRyWFlaAAACGAAAABRnWFlaAAACLAAA"
    "ABRiWFlaAAACQAAAABRkbW5kAAACVAAAAHBkbWRkAAACxAAAAIh2dWVkAAADTAAAAIZ2aWV3AAAD1AAA"
    "ACRsdW1pAAAD+AAAABRtZWFzAAAEDAAAACR0ZWNoAAAEMAAAAAxyVFJDAAAEPAAACAxnVFJDAAAEPAAA"
    "CAxiVFJDAAAEPAAACAx0ZXh0AAAAAENvcHlyaWdodCAoYykgMTk5OCBIZXdsZXR0LVBhY2thcmQgQ29t"
    "cGFueQAAZGVzYwAAAAAAAAASc1JHQiBJRUM2MTk2Ni0yLjEAAAAAAAAAAAAAABJzUkdCIElFQzYxOTY2"
    "LTIuMQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWFlaIAAA"
    "AAAAAPNRAAEAAAABFsxYWVogAAAAAAAAAAAAAAAAAAAAAFhZWiAAAAAAAABvogAAOPUAAAOQWFlaIAAA"
    "AAAAAGKZAAC3hQAAGNpYWVogAAAAAAAAJKAAAA+EAAC2z2Rlc2MAAAAAAAAAFklFQyBodHRwOi8vd3d3"
    "LmllYy5jaAAAAAAAAAAAAAAAFklFQyBodHRwOi8vd3d3LmllYy5jaAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABkZXNjAAAAAAAAAC5JRUMgNjE5NjYtMi4xIERlZmF1bHQg"
    "UkdCIGNvbG91ciBzcGFjZSAtIHNSR0IAAAAAAAAAAAAAAC5JRUMgNjE5NjYtMi4xIERlZmF1bHQgUkdC"
    "IGNvbG91ciBzcGFjZSAtIHNSR0IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZGVzYwAAAAAAAAAsUmVmZXJl"
    "bmNlIFZpZXdpbmcgQ29uZGl0aW9uIGluIElFQzYxOTY2LTIuMQAAAAAAAAAAAAAALFJlZmVyZW5jZSBW"
    "aWV3aW5nIENvbmRpdGlvbiBpbiBJRUM2MTk2Ni0yLjEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHZp"
    "ZXcAAAAAABOk/gAUXy4AEM8UAAPtzAAEEwsAA1yeAAAAAVhZWiAAAAAAAEwJVgBQAAAAVx/nbWVhcwAA"
    "AAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAo8AAAACc2lnIAAAAABDUlQgY3VydgAAAAAAAAQAAAAABQAK"
    "AA8AFAAZAB4AIwAoAC0AMgA3ADsAQABFAEoATwBUAFkAXgBjAGgAbQByAHcAfACBAIYAiwCQAJUAmgCf"
    "AKQAqQCuALIAtwC8AMEAxgDLANAA1QDbAOAA5QDrAPAA9gD7AQEBBwENARMBGQEfASUBKwEyATgBPgFF"
    "AUwBUgFZAWABZwFuAXUBfAGDAYsBkgGaAaEBqQGxAbkBwQHJAdEB2QHhAekB8gH6AgMCDAIUAh0CJgIv"
    "AjgCQQJLAlQCXQJnAnECegKEAo4CmAKiAqwCtgLBAssC1QLgAusC9QMAAwsDFgMhAy0DOANDA08DWgNm"
    "A3IDfgOKA5YDogOuA7oDxwPTA+AD7AP5BAYEEwQgBC0EOwRIBFUEYwRxBH4EjASaBKgEtgTEBNME4QTw"
    "BP4FDQUcBSsFOgVJBVgFZwV3BYYFlgWmBbUFxQXVBeUF9gYGBhYGJwY3BkgGWQZqBnsGjAadBq8GwAbR"
    "BuMG9QcHBxkHKwc9B08HYQd0B4YHmQesB78H0gflB/gICwgfCDIIRghaCG4IggiWCKoIvgjSCOcI+wkQ"
    "CSUJOglPCWQJeQmPCaQJugnPCeUJ+woRCicKPQpUCmoKgQqYCq4KxQrcCvMLCwsiCzkLUQtpC4ALmAuw"
    "C8gL4Qv5DBIMKgxDDFwMdQyODKcMwAzZDPMNDQ0mDUANWg10DY4NqQ3DDd4N+A4TDi4OSQ5kDn8Omw62"
    "DtIO7g8JDyUPQQ9eD3oPlg+zD88P7BAJECYQQxBhEH4QmxC5ENcQ9RETETERTxFtEYwRqhHJEegSBxIm"
    "EkUSZBKEEqMSwxLjEwMTIxNDE2MTgxOkE8UT5RQGFCcUSRRqFIsUrRTOFPAVEhU0FVYVeBWbFb0V4BYD"
    "FiYWSRZsFo8WshbWFvoXHRdBF2UXiReuF9IX9xgbGEAYZRiKGK8Y1Rj6GSAZRRlrGZEZtxndGgQaKhpR"
    "GncanhrFGuwbFBs7G2MbihuyG9ocAhwqHFIcexyjHMwc9R0eHUcdcB2ZHcMd7B4WHkAeah6UHr4e6R8T"
    "Hz4faR+UH78f6iAVIEEgbCCYIMQg8CEcIUghdSGhIc4h+yInIlUigiKvIt0jCiM4I2YjlCPCI/AkHyRN"
    "JHwkqyTaJQklOCVoJZclxyX3JicmVyaHJrcm6CcYJ0kneierJ9woDSg/KHEooijUKQYpOClrKZ0p0CoC"
    "KjUqaCqbKs8rAis2K2krnSvRLAUsOSxuLKIs1y0MLUEtdi2rLeEuFi5MLoIuty7uLyQvWi+RL8cv/jA1"
    "MGwwpDDbMRIxSjGCMbox8jIqMmMymzLUMw0zRjN/M7gz8TQrNGU0njTYNRM1TTWHNcI1/TY3NnI2rjbp"
    "NyQ3YDecN9c4FDhQOIw4yDkFOUI5fzm8Ofk6Njp0OrI67zstO2s7qjvoPCc8ZTykPOM9Ij1hPaE94D4g"
    "PmA+oD7gPyE/YT+iP+JAI0BkQKZA50EpQWpBrEHuQjBCckK1QvdDOkN9Q8BEA0RHRIpEzkUSRVVFmkXe"
    "RiJGZ0arRvBHNUd7R8BIBUhLSJFI10kdSWNJqUnwSjdKfUrESwxLU0uaS+JMKkxyTLpNAk1KTZNN3E4l"
    "Tm5Ot08AT0lPk0/dUCdQcVC7UQZRUFGbUeZSMVJ8UsdTE1NfU6pT9lRCVI9U21UoVXVVwlYPVlxWqVb3"
    "V0RXklfgWC9YfVjLWRpZaVm4WgdaVlqmWvVbRVuVW+VcNVyGXNZdJ114XcleGl5sXr1fD19hX7NgBWBX"
    "YKpg/GFPYaJh9WJJYpxi8GNDY5dj62RAZJRk6WU9ZZJl52Y9ZpJm6Gc9Z5Nn6Wg/aJZo7GlDaZpp8WpI"
    "ap9q92tPa6dr/2xXbK9tCG1gbbluEm5rbsRvHm94b9FwK3CGcOBxOnGVcfByS3KmcwFzXXO4dBR0cHTM"
    "dSh1hXXhdj52m3b4d1Z3s3gReG54zHkqeYl553pGeqV7BHtje8J8IXyBfOF9QX2hfgF+Yn7CfyN/hH/l"
    "gEeAqIEKgWuBzYIwgpKC9INXg7qEHYSAhOOFR4Wrhg6GcobXhzuHn4gEiGmIzokziZmJ/opkisqLMIuW"
    "i/yMY4zKjTGNmI3/jmaOzo82j56QBpBukNaRP5GokhGSepLjk02TtpQglIqU9JVflcmWNJaflwqXdZfg"
    "mEyYuJkkmZCZ/JpomtWbQpuvnByciZz3nWSd0p5Anq6fHZ+Ln/qgaaDYoUehtqImopajBqN2o+akVqTH"
    "pTilqaYapoum/adup+CoUqjEqTepqaocqo+rAqt1q+msXKzQrUStuK4trqGvFq+LsACwdbDqsWCx1rJL"
    "ssKzOLOutCW0nLUTtYq2AbZ5tvC3aLfguFm40blKucK6O7q1uy67p7whvJu9Fb2Pvgq+hL7/v3q/9cBw"
    "wOzBZ8Hjwl/C28NYw9TEUcTOxUvFyMZGxsPHQce/yD3IvMk6ybnKOMq3yzbLtsw1zLXNNc21zjbOts83"
    "z7jQOdC60TzRvtI/0sHTRNPG1EnUy9VO1dHWVdbY11zX4Nhk2OjZbNnx2nba+9uA3AXcit0Q3ZbeHN6i"
    "3ynfr+A24L3hROHM4lPi2+Nj4+vkc+T85YTmDeaW5x/nqegy6LzpRunQ6lvq5etw6/vshu0R7ZzuKO60"
    "70DvzPBY8OXxcvH/8ozzGfOn9DT0wvVQ9d72bfb794r4Gfio+Tj5x/pX+uf7d/wH/Jj9Kf26/kv+3P9t"
    "////2wCEAAIDAwMEAwQFBQQGBgYGBggIBwcICA0JCgkKCQ0TDA4MDA4MExEUEQ8RFBEeGBUVGB4jHRwd"
    "IyolJSo1MjVFRVwBAgMDAwQDBAUFBAYGBgYGCAgHBwgIDQkKCQoJDRMMDgwMDgwTERQRDxEUER4YFRUY"
    "HiMdHB0jKiUlKjUyNUVFXP/AABEIACAAIAMBIgACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQID"
    "BAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNi"
    "coIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeI"
    "iYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz"
    "9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQF"
    "ITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpT"
    "VFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrC"
    "w8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/APw6j09tQuorbTrS"
    "WSRhwv33f3wBgD9Kw7i1ubdts0TRtuZSGGCCh2sCPUHg1+h2sW2o+HdNtv7Fhht53mXD7Sdqsp5cqcnG"
    "NpbtXzT4h0bVL+eeSWGAtdSv5EsB+Sa4iXLYByR5q8cn7wrCFZOVhxu03bS9r+Z23wW1rTZr1tF1KKOW"
    "KVjLa+ZghJlGSOf7wGfqK+1NV8caHp0DJBtnZB1B2Qpj1bv+FfkZpl5JZX1vcoquY2DBW6N7H2rW1HVt"
    "W1WUefMzjPyxKMIPoo/rWkqalK/4HQqjSsvvPoWw1jxT4vtNRRfm8m4hnhcRYhWJfleLB4KgfNjvzXvX"
    "h3wVHrPhq+luNZCywwj7JHbQLBbQTRtujmbJJOGHYgY4xXzL4113UNO1RZNI1OS3t5Y4lmghkby45IDl"
    "VIAAKchgOhOc1q6n4ufTP7PvdIVreG/iSa4to9wTgkTRseAVDZ44xn0NccoSai4pK+qJTgr3V7P8Tg/H"
    "OjmC7i1BLfyY74yGSH/n3u4jtuIOp6N8y+qnisHwxfrbyEiztriWMkiOeHzkfPTcmRnHUehFdj4ktdaX"
    "RRcGO6WxvLwygTKc+ekZHGQCCY+x64rxiN2ilWQdBww9QetehDWGvoTfW6P/2Q=="
)


def github() -> bool:
    """Test if running in github workflow."""
    return os.getenv("GITHUB_ENV") is not None


@pytest.fixture
def foo_bar() -> Dict[str, str]:
    """Fixture foo_bar."""
    return {"foo": "bar"}


@pytest.fixture
def image_bytes() -> bytes:
    """Fixture image_bytes."""
    return base64.b64decode(EXAMPLE_IMAGE)


@pytest.fixture(scope="session")
def httpserver_listen_address() -> tuple[str, int]:
    """Fixture httpserver_listen_address."""
    return ("127.0.0.1", 5050)


@pytest.fixture
def request_client() -> RestRequest:
    """Fixture request_client."""
    endpoints: List[Endpoint] = []
    endpoints.append(Endpoint(name="post_v1_data", path="/v1/data"))
    endpoints.append(
        Endpoint(
            name="get_v1_data",
            path="/v1/data",
            query_parameters=["abcd", "efgh"],
        ),
    )
    endpoints.append(Endpoint(name="delete_v1_data", path="/v1/data/{id}"))
    endpoints.append(Endpoint(name="put_v1_data", path="/v1/data/{id}"))
    endpoints.append(
        Endpoint(
            name="wtf_upload",
            path="/{version}/upload",
            request_method=HTTPMethod.POST,
        ),
    )
    return RestRequest("http://127.0.0.1:5050", endpoints, "abc")


@pytest.fixture
def response() -> Response:
    """Fixture response."""
    rr = Response()
    rr._content = '{"foo": "bar"}'.encode("utf-8")  # noqa: WPS437
    rr.status_code = HTTPStatus.OK
    rr.headers = CaseInsensitiveDict(
        {"Content-Type": "application/json", "Accept": "application/gzip"}
    )

    return rr


@pytest.fixture
def response_image() -> Response:
    """Fixture response_image."""
    rr = Response()
    rr._content = base64.b64decode(EXAMPLE_IMAGE)  # noqa: WPS437
    rr.status_code = HTTPStatus.OK
    rr.headers = CaseInsensitiveDict({"Content-Type": "image/png"})

    return rr
