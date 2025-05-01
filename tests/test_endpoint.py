"""
Module test_endpoint module for package tests of rest-api-client-framework library.

Functions:
    test_endpoint_query_path_parameters
    test_missing_method_name_exception
    test_missing_argument_exception
"""

import re

import pytest

from api_client.endpoint import Endpoint, HTTPMethod
from api_client.exception import (
    MISSING_ARGUMENT_MSG_FMT,
    MissingArgumentError,
    MissingMethodNameError,
)

TT = "f7e12af65cd796d6e149a23faa1571b0"


def test_endpoint_query_path_parameters() -> None:
    """Test endpoint query path parameters."""
    qps = ["token", "enableBlocking"]
    enable_blocking = Endpoint(
        name="enable_blocking",
        path="/settings/{action}",
        request_method=HTTPMethod.GET,
        query_parameters=qps,
    )
    url_root = "http://example.com/api/v3/"
    action = "set"
    url, method = enable_blocking.prepare(
        url_root,
        action="set",
        token=TT,
        enableBlocking=True,
    )
    assert method == HTTPMethod.GET
    assert url == "{0}settings/{1}?{2}={3}&{4}=true".format(
        url_root,
        action,
        qps[0],
        TT,
        qps[1],
    )


def test_missing_method_name_exception() -> None:
    """Test missing method name exception."""
    qps = ["token", "enableBlocking"]
    name = "enable_blocking"
    enable_blocking = Endpoint(
        name=name,
        path="/settings/{action}",
        query_parameters=qps,
    )
    url_root = "http://example.com/api/v3"
    with pytest.raises(MissingMethodNameError) as ex:
        url, method = enable_blocking.prepare(
            url_root,
            action="set",
            token=TT,
            enableBlocking=True,
        )
    assert re.search(".*{0}.*".format(name), ex.value.msg)


def test_missing_argument_exception() -> None:
    """Test missing argument exception."""
    qps = ["token", "enableBlocking"]
    name = "enable_blocking"
    enable_blocking = Endpoint(
        name=name,
        path="/settings/{action}",
        request_method=HTTPMethod.GET,
        query_parameters=qps,
    )
    url_root = "https://example.com/api/v3"
    with pytest.raises(MissingArgumentError) as ex:
        url, method = enable_blocking.prepare(url_root, token=TT, enableBlocking=True)
    assert ex.value.msg == MISSING_ARGUMENT_MSG_FMT.format("'action'")
