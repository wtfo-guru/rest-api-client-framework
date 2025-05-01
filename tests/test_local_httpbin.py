"""
Module test_local_httpbin module for package tests of rest-api-client-framework library.

Functions:
    is_responsive
    httpbin_service
    request_client_http_bin_local
    test_get_request_gzipped_local
"""

import pytest

from tests.conftest import github

pytestmark = pytest.mark.skipif(github(), reason="We are not running locally, Dorothy.")

from typing import List

import requests
from requests.exceptions import ConnectionError
from requests.structures import CaseInsensitiveDict

from api_client.endpoint import Endpoint
from api_client.request import RestRequest


def is_responsive(url: str) -> bool:
    """Test response from http server."""
    responsive = False
    try:
        response = requests.get(url, timeout=(5.0, 3))
        if response.status_code == 200:
            return True
    except ConnectionError:
        responsive = False
    return responsive


@pytest.fixture(scope="module")
def httpbin_service(docker_ip, docker_services) -> str:  # type: ignore[no-untyped-def]
    """Ensure that HTTP service is up and responsive."""
    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("httpbin", 80)
    url = "http://{0}:{1}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: is_responsive(url),
    )
    return url


@pytest.fixture(scope="module")
def request_client_http_bin_local(  # type: ignore[no-untyped-def]
    httpbin_service,
) -> RestRequest:
    """Fixture request client http bin local."""
    endpoints: List[Endpoint] = []
    endpoints.append(Endpoint(name="get_gzip", path="/gzip"))
    return RestRequest(httpbin_service, endpoints, "abc")


def test_get_request_gzipped_local(
    request_client_http_bin_local: RestRequest,
) -> None:
    """Test get request gzipped local."""
    response = request_client_http_bin_local.call_endpoint(
        "get_gzip",
        headers=CaseInsensitiveDict(
            {"Accept": "application/json", "Accept-Encoding": "gzip"}
        ),
    )
    assert response.is_json()
    assert response.data()["gzipped"]
