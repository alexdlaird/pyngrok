__copyright__ = "Copyright (c) 2018-2026 Alex Laird"
__license__ = "MIT"

import os
import time
import unittest
from unittest import mock
from urllib.parse import urlparse
from urllib.request import urlopen

from pyngrok import installer, ngrok, process
from pyngrok.exception import PyngrokError
from tests.testcase import NgrokTestCase


class TestNgrokEndpoints(NgrokTestCase):
    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_connect_endpoint(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(ngrok._current_endpoints.keys()), 0)

        # WHEN
        endpoint = ngrok.connect_endpoint(upstream="http://localhost:5000",
                                          pyngrok_config=self.pyngrok_config)
        current_process = ngrok.get_ngrok_process(self.pyngrok_config)

        # THEN
        self.assertEqual(len(ngrok._current_endpoints.keys()), 1)
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertTrue(current_process._monitor_thread.is_alive())
        self.assertIsNotNone(endpoint.name)
        self.assertEqual(endpoint.upstream.get("url"), "http://localhost:5000")
        self.assertIsNotNone(endpoint.url)
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_connect_endpoint_upstream_dict(self):
        # WHEN
        endpoint = ngrok.connect_endpoint(upstream={"url": "http://localhost:5000", "protocol": "http1"},
                                          pyngrok_config=self.pyngrok_config)

        # THEN
        self.assertEqual(endpoint.upstream.get("url"), "http://localhost:5000")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_connect_endpoint_with_pooling(self):
        # WHEN
        endpoint = ngrok.connect_endpoint(upstream="http://localhost:80",
                                          url="https://pyngrok.internal",
                                          pooling_enabled=True,
                                          pyngrok_config=self.pyngrok_config)

        # THEN
        self.assertEqual(endpoint.url, "https://pyngrok.internal")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_get_endpoints(self):
        # GIVEN
        created_endpoint = ngrok.connect_endpoint(upstream="http://localhost:5000",
                                                  pyngrok_config=self.pyngrok_config)
        time.sleep(1)
        self.assertEqual(len(ngrok._current_endpoints.keys()), 1)

        # WHEN
        endpoints = ngrok.get_endpoints(self.pyngrok_config)

        # THEN
        self.assertEqual(len(ngrok._current_endpoints.keys()), 1)
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0].name, created_endpoint.name)
        self.assertEqual(endpoints[0].upstream.get("url"), "http://localhost:5000")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_disconnect_endpoint(self):
        # GIVEN
        endpoint = ngrok.connect_endpoint(upstream="http://localhost:5000",
                                          pyngrok_config=self.pyngrok_config)
        time.sleep(1)
        self.assertEqual(len(ngrok._current_endpoints.keys()), 1)

        # WHEN
        ngrok.disconnect_endpoint(endpoint.name, self.pyngrok_config)

        # THEN
        self.assertEqual(len(ngrok._current_endpoints.keys()), 0)
        time.sleep(1)
        self.assertEqual(len(ngrok.get_endpoints(self.pyngrok_config)), 0)

    def test_disconnect_endpoint_when_ngrok_not_running(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN (must not raise, must not start ngrok)
        ngrok.disconnect_endpoint("does-not-exist", self.pyngrok_config)

        # THEN
        self.assertEqual(len(process._current_processes.keys()), 0)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_disconnect_endpoint_unknown_name_is_noop(self):
        # GIVEN
        ngrok.connect_endpoint(upstream="http://localhost:5000", pyngrok_config=self.pyngrok_config)

        # WHEN (must not raise)
        ngrok.disconnect_endpoint("some-name-that-isnt-running", self.pyngrok_config)

        # THEN
        self.assertEqual(len(ngrok.get_endpoints(self.pyngrok_config)), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_kill_clears_endpoints_and_tunnels(self):
        # GIVEN
        ngrok.connect("5000", pyngrok_config=self.pyngrok_config)
        ngrok.connect_endpoint(upstream="http://localhost:6000", pyngrok_config=self.pyngrok_config)
        time.sleep(1)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        self.assertEqual(len(ngrok._current_endpoints.keys()), 1)

        # WHEN
        ngrok.kill(self.pyngrok_config)
        time.sleep(1)

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)
        self.assertEqual(len(ngrok._current_endpoints.keys()), 0)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_ngrok_endpoint_refresh_metrics(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        upstream = f"http://localhost:{urlparse(current_process.api_url).port}"
        endpoint = ngrok.connect_endpoint(upstream=upstream, pyngrok_config=self.pyngrok_config)
        time.sleep(1)

        urlopen(f"{endpoint.url}/api/status").read()
        time.sleep(3)

        # WHEN
        endpoint.refresh_metrics()

        # THEN
        self.assertGreater(endpoint.metrics.get("http", {}).get("count", 0), 0)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_endpoint_definitions(self):
        # GIVEN
        config = {
            "endpoints": [
                {"name": "my-endpoint", "upstream": {"url": "http://localhost:8000"}}
            ]
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3", config_version="3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config,
                                                config_path=config_path)

        # WHEN
        endpoint = ngrok.connect_endpoint(name="my-endpoint", pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(endpoint.name, "my-endpoint-api")
        self.assertEqual(endpoint.upstream.get("url"), "http://localhost:8000")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_endpoint_definitions_pyngrok_default(self):
        # GIVEN
        config = {
            "endpoints": [
                {"name": "pyngrok-default", "upstream": {"url": "http://localhost:8080"}}
            ]
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3", config_version="3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config,
                                                config_path=config_path)

        # WHEN
        endpoint = ngrok.connect_endpoint(pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(endpoint.name, "pyngrok-default-api")
        self.assertEqual(endpoint.upstream.get("url"), "http://localhost:8080")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_endpoint_definitions_pyngrok_default_with_overrides(self):
        # GIVEN
        config = {
            "endpoints": [
                {"name": "pyngrok-default", "upstream": {"url": "http://localhost:8080"}}
            ]
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3", config_version="3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config,
                                                config_path=config_path)

        # WHEN
        endpoint = ngrok.connect_endpoint(upstream="http://localhost:9090", pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(endpoint.name, "pyngrok-default-api")
        self.assertEqual(endpoint.upstream.get("url"), "http://localhost:9090")

    @mock.patch("pyngrok.ngrok.api_request")
    @mock.patch("pyngrok.ngrok.get_ngrok_process")
    def test_connect_endpoint_posts_to_endpoints_api(self, mock_get_ngrok_process, mock_api_request):
        # GIVEN
        mock_get_ngrok_process.return_value.api_url = "http://localhost:4040"
        mock_api_request.return_value = {
            "name": "my-endpoint-api",
            "url": "https://my.ngrok.dev",
            "upstream": {"url": "http://localhost:8000"}
        }

        # WHEN
        ngrok.connect_endpoint(upstream="http://localhost:8000", name="my-endpoint",
                               pyngrok_config=self.pyngrok_config)

        # THEN
        call_args, call_kwargs = mock_api_request.call_args
        self.assertEqual(call_args[0], "http://localhost:4040/api/endpoints")
        self.assertEqual(call_kwargs["method"], "POST")
        self.assertEqual(call_kwargs["data"]["upstream"], {"url": "http://localhost:8000"})
        self.assertEqual(call_kwargs["data"]["name"], "my-endpoint")

    @mock.patch("pyngrok.ngrok.api_request")
    @mock.patch("pyngrok.ngrok.get_ngrok_process")
    def test_connect_endpoint_from_config_posts_expected_options(self, mock_get_ngrok_process, mock_api_request):
        # GIVEN
        config = {
            "endpoints": [
                {"name": "my-endpoint", "upstream": {"url": "http://localhost:8000"}}
            ]
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3", config_version="3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config,
                                                config_path=config_path)
        mock_get_ngrok_process.return_value.api_url = "http://localhost:4040"
        mock_api_request.return_value = {
            "name": "my-endpoint-api",
            "url": "https://my.ngrok.dev",
            "upstream": config["endpoints"][0]["upstream"]
        }

        expected_options = {
            "upstream": {"url": "http://localhost:8000"},
            "name": "my-endpoint-api",
        }

        # WHEN
        ngrok.connect_endpoint(name="my-endpoint", pyngrok_config=pyngrok_config)

        # THEN
        mock_api_request.assert_called_with("http://localhost:4040/api/endpoints", method="POST",
                                            data=expected_options, timeout=pyngrok_config.request_timeout)

    def test_ngrok_endpoint_repr(self):
        # GIVEN
        endpoint = ngrok.NgrokEndpoint(
            {"name": "my-endpoint", "url": "https://my.ngrok.dev",
             "upstream": {"url": "http://localhost:8000"}},
            self.pyngrok_config, "http://localhost:4040")

        # THEN
        self.assertIn("my.ngrok.dev", repr(endpoint))
        self.assertIn("localhost:8000", repr(endpoint))

    def test_ngrok_endpoint_pending_repr(self):
        # GIVEN
        endpoint = ngrok.NgrokEndpoint({}, self.pyngrok_config, "http://localhost:4040")

        # THEN
        self.assertEqual("<pending Endpoint>", repr(endpoint))

    def test_ngrok_endpoint_uri_falls_back_to_name(self):
        # GIVEN
        endpoint = ngrok.NgrokEndpoint({"name": "my-endpoint"}, self.pyngrok_config,
                                       "http://localhost:4040")

        # THEN
        self.assertEqual("/api/endpoints/my-endpoint", endpoint.uri)

    @mock.patch("pyngrok.ngrok.api_request")
    def test_refresh_metrics_raises_when_missing(self, mock_api_request):
        # GIVEN
        endpoint = ngrok.NgrokEndpoint({"name": "my-endpoint"}, self.pyngrok_config,
                                       "http://localhost:4040")
        mock_api_request.return_value = {"name": "my-endpoint"}

        # WHEN / THEN
        with self.assertRaises(PyngrokError):
            endpoint.refresh_metrics()
