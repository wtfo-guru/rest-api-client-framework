from http import HTTPStatus

import pytest
from pytest_httpserver import HTTPServer

from api_client.exception import ApiClientError
from api_client.request import RestRequest


def test_send_post_request(request_client: RestRequest, httpserver: HTTPServer):
    httpserver.expect_request("/v1/data", method="POST").respond_with_json(
        {"foo": "bar"},
        HTTPStatus.CREATED.value,
    )

    response = request_client.call_endpoint("post_v1_data")
    assert response.status_code == HTTPStatus.CREATED
    assert response.data() == {"foo": "bar"}


# def test_send_post_request_error_code_too_many(
#     request_client: RestRequest,
#     httpserver: HTTPServer,
# ):
#     httpserver.expect_request("/v1/data", method="POST").respond_with_json(
#         {"foo": "bar"},
#         HTTPStatus.TOO_MANY_REQUESTS.value,
#     )

#     with pytest.raises(ApiClientError):  # if it raises an exception response is not set?
#         response = request_client.request("/data", "POST")  # noqa: F841
#         # assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
#         # assert response.data() == {"foo": "bar"}


# def test_send_post_request_with_bad_request(
#     request_client: RestRequest,
#     httpserver: HTTPServer,
# ):
#     httpserver.expect_request("/v1/data", method="POST").respond_with_json(
#         {"foo": "bar"},
#         HTTPStatus.BAD_REQUEST.value,
#     )

#     response = request_client.request("/data", "POST")
#     assert response.status_code == HTTPStatus.BAD_REQUEST
#     assert response.data() == {"foo": "bar"}


# def test_get_request_with_params(request_client: RestRequest, httpserver: HTTPServer):
#     httpserver.expect_request(
#         "/v1/data",
#         method="GET",
#         query_string={"abc": "1", "def": "aaa"},
#     ).respond_with_json({"foo": "bar"})

#     response = request_client.request(
#         "/data",
#         "GET",
#         query_params={"abc": 1, "def": "aaa"},
#     )
#     assert response.data() == {"foo": "bar"}


# def test_get_request_gzipped(
#     request_client: RestRequest,
# ):
#     response = request_client.execute(
#         url="https://httpbin.org/gzip",
#         method="GET",
#         headers={"Accept": "application/json", "Accept-Encoding": "gzip"},
#     )
#     assert response.is_json()
#     assert response.data()["gzipped"]


# def test_delete_request_with_params(
#     request_client: RestRequest,
#     httpserver: HTTPServer,
# ):
#     httpserver.expect_request("/v1/data/id1", method="DELETE").respond_with_json(
#         {"foo": "bar"},
#     )

#     response = request_client.request("/data/id1", "DELETE")
#     assert response.status_code == HTTPStatus.OK
#     assert response.data() == {"foo": "bar"}


# def test_put_request_with_params(request_client: RestRequest, httpserver: HTTPServer):
#     httpserver.expect_request("/v1/data/id1", method="PUT").respond_with_json(
#         {"foo": "bar"},
#     )

#     response = request_client.request("/data/id1", "PUT", {"abc": 123})
#     assert response.status_code == HTTPStatus.OK
#     assert response.data() == {"foo": "bar"}


# def test_post_request_with_image(
#     request_client: RestRequest,
#     image_bytes: bytes,
#     httpserver: HTTPServer,
# ):

#     httpserver.expect_request(
#         "/v1/upload",
#         headers={"Content-Type": "image/png"},
#         data=image_bytes,
#         method="POST",
#     ).respond_with_json({"foo": "bar"})

#     response = request_client.request(
#         "/upload",
#         "POST",
#         image_bytes,
#         headers={"Content-Type": "image/png"},
#     )
#     assert response.status_code == HTTPStatus.OK
#     assert response.data() == {"foo": "bar"}


# def test_get_execute_with_params(request_client: RestRequest, httpserver: HTTPServer):
#     httpserver.expect_request(
#         "/v1/data",
#         method="GET",
#         query_string={"abc": "1", "def": "aaa"},
#     ).respond_with_json({"foo": "bar"})

#     response = request_client.execute(
#         url="http://127.0.0.1:5050/v1/data",
#         method="GET",
#         query_params={"abc": 1, "def": "aaa"},
#     )
#     assert response.data() == {"foo": "bar"}
