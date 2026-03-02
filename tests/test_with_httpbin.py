"""
Module test_local_httpbin module for package tests of rest-api-client-framework library.

Functions:
    request_client_http_bin_github
    test_get_request_gzipped_github
"""

import socket
from typing import List

import pytest
from requests.structures import CaseInsensitiveDict

from api_client.endpoint import Endpoint
from api_client.request import RestRequest
from tests.conftest import github

# pytestmark = pytest.mark.skipif(not github(), reason="We are not on GitHub, Dorothy.")


@pytest.fixture(scope="module")
def request_client_http_bin_github() -> RestRequest:
    """Fixture request client http bin github."""
    endpoints: List[Endpoint] = []
    endpoints.append(Endpoint(name="get_gzip", path="/gzip"))
    if github():
        httpbin_addr = "http://127.0.0.1:8000"
    else:
        ip = socket.gethostbyname("devops-vm.metaorg.com")
        httpbin_addr = "http://{0}:8080".format(ip)
    return RestRequest(httpbin_addr, endpoints, "abc")


def test_get_request_gzipped_github(
    request_client_http_bin_github: RestRequest,
) -> None:
    """Test get request gzipped github."""
    response = request_client_http_bin_github.call_endpoint(
        "get_gzip",
        headers=CaseInsensitiveDict(
            {"Accept": "application/json", "Accept-Encoding": "gzip"}
        ),
    )
    assert response.is_json()
    assert response.data()["gzipped"]
