"""
Module test_with_httpbin module for package tests of rest-api-client-framework library.

Functions:
    test_send_post_request
    test_send_post_request_error_code_too_many
    test_send_post_request_with_bad_request
    test_get_request_with_params
    test_delete_request_with_params
    test_put_request_with_params
    test_post_request_with_image
"""

import pytest
import unittest

class HttpBinLocalTest(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setUp(self, docker_ip, docker_services):
        """Ensure that HTTP service is up and responsive."""

        # `port_for` takes a container port and returns the corresponding host port
        port = docker_services.port_for("httpbin", 80)
        url = "http://{}:{}".format(docker_ip, port)
        docker_services.wait_until_responsive(
            timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
        )
        return url

    def tearDown(self):
        self.widget.dispose()
