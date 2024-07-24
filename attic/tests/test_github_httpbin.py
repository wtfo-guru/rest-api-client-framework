import os

import pytest

py_test_mark = pytest.mark.skipif(
    os.getenv("GITHUB_ENV") is None, reason="We are not running on GitHub, Dorothy."
)

from typing import List

from api_client.endpoint import Endpoint
from api_client.request import RestRequest


@pytest.fixture(scope="module")
def request_client_http_bin_github() -> RestRequest:
    endpoints: List[Endpoint] = []
    endpoints.append(Endpoint(name="get_gzip", path="/gzip"))
    return RestRequest("http://httpbin:8000", endpoints, "abc")


def test_get_request_gzipped_github(request_client_http_bin_github: RestRequest):
    response = test_get_request_gzipped_github.call_endpoint(
        "get_gzip",
        headers={"Accept": "application/json", "Accept-Encoding": "gzip"},
    )
    assert response.is_json()
    assert response.data()["gzipped"]
