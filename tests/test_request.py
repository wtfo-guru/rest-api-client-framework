from http import HTTPStatus
from types import MappingProxyType
from typing import Dict

import pytest
from pytest_httpserver import HTTPServer

from api_client.exception import ApiClientError
from api_client.payload import Payload
from api_client.request import RestRequest

FOO_BAR = MappingProxyType({"foo": "bar"})


def test_send_post_request(
    request_client: RestRequest,
    httpserver: HTTPServer,
    foo_bar: Dict[str, str],
) -> None:
    httpserver.expect_request("/v1/data", method="POST").respond_with_json(
        foo_bar,
        HTTPStatus.CREATED.value,
    )

    response = request_client.call_endpoint("post_v1_data")
    assert response.status_code == HTTPStatus.CREATED
    assert response.data() == FOO_BAR


def test_send_post_request_error_code_too_many(
    request_client: RestRequest,
    httpserver: HTTPServer,
    foo_bar: Dict[str, str],
) -> None:
    httpserver.expect_request("/v1/data", method="POST").respond_with_json(
        foo_bar,
        HTTPStatus.TOO_MANY_REQUESTS.value,
    )

    with pytest.raises(ApiClientError) as ex:
        response = request_client.call_endpoint("post_v1_data")
    assert ex.value.reason == (
        """The user has sent too many requests in a given"""
        """ amount of time ("rate limiting")"""
    )


def test_send_post_request_with_bad_request(
    request_client: RestRequest,
    httpserver: HTTPServer,
    foo_bar: Dict[str, str],
) -> None:
    httpserver.expect_request("/v1/data", method="POST").respond_with_json(
        {"foo": "bar"},
        HTTPStatus.BAD_REQUEST.value,
    )
    with pytest.raises(ApiClientError) as ex:
        response = request_client.call_endpoint("post_v1_data")
    assert ex.value.reason == "Bad request syntax or unsupported method"


def test_get_request_with_params(
    request_client: RestRequest,
    httpserver: HTTPServer,
    foo_bar: Dict[str, str],
) -> None:
    httpserver.expect_request(
        "/v1/data",
        method="GET",
        query_string={"abcd": "1", "efgh": "aaa"},
    ).respond_with_json(foo_bar)

    response = request_client.call_endpoint("get_v1_data", abcd="1", efgh="aaa")
    assert response.data() == FOO_BAR


def test_delete_request_with_params(
    request_client: RestRequest,
    httpserver: HTTPServer,
    foo_bar: Dict[str, str],
) -> None:
    httpserver.expect_request("/v1/data/id1", method="DELETE").respond_with_json(
        foo_bar,
    )

    # response = request_client.request("/data/id1", "DELETE")
    response = request_client.call_endpoint("delete_v1_data", id="id1")
    assert response.status_code == HTTPStatus.OK
    assert response.data() == FOO_BAR


def test_put_request_with_params(
    request_client: RestRequest,
    httpserver: HTTPServer,
    foo_bar: Dict[str, str],
) -> None:
    httpserver.expect_request("/v1/data/id1", method="PUT").respond_with_json(
        {"foo": "bar"},
    )

    response = request_client.call_endpoint("put_v1_data", id="id1")
    assert response.status_code == HTTPStatus.OK
    assert response.data() == {"foo": "bar"}


def test_post_request_with_image(
    request_client: RestRequest,
    image_bytes: bytes,
    httpserver: HTTPServer,
    foo_bar: Dict[str, str],
) -> None:

    httpserver.expect_request(
        "/v1/upload",
        headers={"Content-Type": "image/png"},
        data=image_bytes,
        method="POST",
    ).respond_with_json(foo_bar)

    payload = Payload(image_bytes)
    headers = {"Content-Type": "image/png"}
    response = request_client.call_endpoint(
        "wtf_upload",
        payload,
        headers,
        version="v1",
    )
    assert response.status_code == HTTPStatus.OK
    assert response.data() == FOO_BAR
