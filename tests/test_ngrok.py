__copyright__ = "Copyright (c) 2018-2025 Alex Laird"
__license__ = "MIT"

import os
import time
import traceback
import unittest
import uuid
from http import HTTPStatus
from unittest import mock
from urllib.parse import urlparse
from urllib.request import urlopen

import yaml

from pyngrok import __version__, installer, ngrok, process
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokError, PyngrokNgrokError, PyngrokNgrokHTTPError, PyngrokNgrokURLError, \
    PyngrokSecurityError
from scripts.create_test_resources import create_test_resources, generate_name_for_subdomain
from tests.testcase import NgrokTestCase


class TestNgrok(NgrokTestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("NGROK_API_KEY"):
            testcase_config_dir = os.path.normpath(
                os.path.join(os.path.abspath(os.path.dirname(__file__)), ".testcase-ngrok"))
            testcase_config_path = os.path.join(testcase_config_dir, "config.yml")
            testcase_ngrok_path = os.path.join(testcase_config_dir, installer.get_ngrok_bin())
            cls.testcase_pyngrok_config = PyngrokConfig(ngrok_path=testcase_ngrok_path,
                                                        config_path=testcase_config_path)
            cls.given_ngrok_installed(cls.testcase_pyngrok_config)

            # NGROK_HOSTNAME is set when init_test_resources.py is done provisioning test resources, so if it
            # hasn't been set, we need to do that now. When running tests on CI, using the init script can protect
            # against rate limiting, as this allows API resources to be shared across the build matrix.
            if not os.environ.get("NGROK_HOSTNAME"):
                create_test_resources(True)

                cls.reserved_domain_id = os.environ["NGROK_DOMAIN_ID"]
                cls.tcp_edge_reserved_addr_id = os.environ["NGROK_TCP_EDGE_ADDR_ID"]
                cls.http_edge_reserved_domain_id = os.environ["NGROK_HTTP_EDGE_DOMAIN_ID"]
                cls.tls_edge_reserved_domain_id = os.environ["NGROK_TLS_EDGE_DOMAIN_ID"]

            cls.reserved_domain = os.environ["NGROK_DOMAIN"]
            cls.tcp_edge_reserved_addr = os.environ["NGROK_TCP_EDGE_ADDR"]
            cls.tcp_edge_id = os.environ["NGROK_TCP_EDGE_ID"]
            cls.http_edge_reserved_domain = os.environ["NGROK_HTTP_EDGE_DOMAIN"]
            cls.http_edge_id = os.environ["NGROK_HTTP_EDGE_ID"]
            cls.tls_edge_reserved_domain = os.environ["NGROK_TLS_EDGE_DOMAIN"]
            cls.tls_edge_id = os.environ["NGROK_TLS_EDGE_ID"]

    @classmethod
    def tearDownClass(cls):
        # NGROK_HOSTNAME is set when init_test_resources.py is done provisioning test resources, in which case
        # prune_test_resources.py should also be called to clean up test resources after all tests complete. Otherwise,
        # this testcase set up the resources, so it should also tear them down.
        if os.environ.get("NGROK_API_KEY") and not os.environ.get("NGROK_HOSTNAME"):
            try:
                ngrok.api("edges", "https",
                          "delete", cls.http_edge_id,
                          pyngrok_config=cls.testcase_pyngrok_config)
                ngrok.api("edges", "tcp",
                          "delete", cls.http_edge_id,
                          pyngrok_config=cls.testcase_pyngrok_config)
                ngrok.api("edges", "tls",
                          "delete", cls.http_edge_id,
                          pyngrok_config=cls.testcase_pyngrok_config)
                ngrok.api("reserved-domains", "delete", cls.reserved_domain_id,
                          pyngrok_config=cls.testcase_pyngrok_config)
                ngrok.api("reserved-domains", "delete", cls.http_edge_reserved_domain_id,
                          pyngrok_config=cls.testcase_pyngrok_config)
                ngrok.api("reserved-domains", "delete", cls.tls_edge_reserved_domain_id,
                          pyngrok_config=cls.testcase_pyngrok_config)
                ngrok.api("reserved-addrs", "delete", cls.tcp_edge_reserved_addr_id,
                          pyngrok_config=cls.testcase_pyngrok_config)
            except Exception:
                print(traceback.format_exc())
                print("--> An error occurred while cleaning up test resources. Run scripts/prune_test_resources.py to "
                      "finish.")

    @mock.patch("subprocess.call")
    def test_run(self, mock_call):
        # WHEN
        ngrok.run()

        # THEN
        self.assertTrue(mock_call.called)

    @mock.patch("subprocess.call")
    def test_main(self, mock_call):
        # WHEN
        ngrok.main()

        # THEN
        self.assertTrue(mock_call.called)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_connect_v2(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)

        # WHEN
        ngrok_tunnel = ngrok.connect("5000", pyngrok_config=self.pyngrok_config_v2)
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v2)

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertTrue(current_process._monitor_thread.is_alive())
        self.assertIsNone(ngrok_tunnel.id)
        self.assertTrue(ngrok_tunnel.name.startswith("http-5000-"))
        self.assertEqual("http", ngrok_tunnel.proto)
        self.assertEqual("http://localhost:5000", ngrok_tunnel.config["addr"])
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(self.pyngrok_config_v2))
        self.assertIn('http://', ngrok_tunnel.public_url)
        self.assertEqual(len(process._current_processes.keys()), 1)

        # WHEN
        ngrok.kill(self.pyngrok_config_v2)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=self.pyngrok_config_v2)

        # THEN
        self.assertTrue(ngrok_version.startswith("2"))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_connect_v3(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)

        # WHEN
        ngrok_tunnel = ngrok.connect("5000", pyngrok_config=self.pyngrok_config_v3)
        current_process = ngrok.get_ngrok_process(self.pyngrok_config_v3)

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertTrue(current_process._monitor_thread.is_alive())
        self.assertIsNotNone(ngrok_tunnel.id)
        self.assertTrue(ngrok_tunnel.name.startswith("http-5000-"))
        self.assertEqual("https", ngrok_tunnel.proto)
        self.assertEqual("http://localhost:5000", ngrok_tunnel.config["addr"])
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(self.pyngrok_config_v3))
        self.assertIn('https://', ngrok_tunnel.public_url)
        self.assertEqual(len(process._current_processes.keys()), 1)

        # WHEN
        ngrok.kill(self.pyngrok_config_v3)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertTrue(ngrok_version.startswith("3"))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    @unittest.skipIf(not os.environ.get("NGROK_API_KEY"), "NGROK_API_KEY environment variable not set")
    def test_connect_tls(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)

        # WHEN
        ngrok_tunnel = ngrok.connect("443", proto="tls", domain=self.reserved_domain,
                                     terminate_at="upstream",
                                     pooling_enabled=True, pyngrok_config=self.pyngrok_config_v3)
        current_process = ngrok.get_ngrok_process(self.pyngrok_config_v3)

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertTrue(current_process._monitor_thread.is_alive())
        self.assertIsNotNone(ngrok_tunnel.id)
        self.assertTrue(ngrok_tunnel.name.startswith("tls-443-"))
        self.assertEqual("tls", ngrok_tunnel.proto)
        self.assertEqual("tls://localhost:443", ngrok_tunnel.config["addr"])
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(self.pyngrok_config_v3))
        self.assertIn('tls://', ngrok_tunnel.public_url)
        self.assertEqual(len(process._current_processes.keys()), 1)

        # WHEN
        ngrok.kill(self.pyngrok_config_v3)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertTrue(ngrok_version.startswith("3"))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_connect_name(self):
        # WHEN
        ngrok_tunnel = ngrok.connect(name="my-tunnel", pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertEqual(ngrok_tunnel.name, "my-tunnel")
        self.assertEqual("https", ngrok_tunnel.proto)
        self.assertEqual("http://localhost:80", ngrok_tunnel.config["addr"])

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_get_tunnels(self):
        # GIVEN
        url = ngrok.connect(pyngrok_config=self.pyngrok_config_v3).public_url
        time.sleep(1)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)

        # WHEN
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v3)

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        self.assertEqual(len(tunnels), 1)
        self.assertEqual(tunnels[0].proto, "https")
        self.assertEqual(tunnels[0].public_url, url)
        self.assertEqual(tunnels[0].config["addr"], "http://localhost:80")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_bind_tls_both_v2(self):
        # WHEN
        url = ngrok.connect(bind_tls="both", pyngrok_config=self.pyngrok_config_v2).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v2))

        # THEN
        self.assertTrue(url.startswith("http://"))
        self.assertEqual(num_tunnels, 2)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_bind_tls_https_only_v2(self):
        # WHEN
        url = ngrok.connect(bind_tls=True, pyngrok_config=self.pyngrok_config_v2).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v2))

        # THEN
        self.assertTrue(url.startswith("https://"))
        self.assertEqual(num_tunnels, 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_bind_tls_http_only_v2(self):
        # WHEN
        url = ngrok.connect(bind_tls=False, pyngrok_config=self.pyngrok_config_v2).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v2))

        # THEN
        self.assertTrue(url.startswith("http://"))
        self.assertEqual(num_tunnels, 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_schemes_http_v3(self):
        # WHEN
        url = ngrok.connect(schemes=["http"], pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v3))

        # THEN
        self.assertTrue(url.startswith("http://"))
        self.assertEqual(num_tunnels, 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_schemes_https_v3(self):
        # WHEN
        url = ngrok.connect(schemes=["https"], pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v3))

        # THEN
        self.assertTrue(url.startswith("https://"))
        self.assertEqual(num_tunnels, 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_schemes_http_https_v3(self):
        # WHEN
        url = ngrok.connect(schemes=["http", "https"], pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v3))

        # THEN
        self.assertTrue(url.startswith("https://"))
        self.assertEqual(num_tunnels, 2)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_bind_tls_upgraded_to_schemes_v3(self):
        # WHEN
        public_url1 = ngrok.connect(bind_tls="both", pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels1 = len(ngrok.get_tunnels(self.pyngrok_config_v3))
        public_url2 = ngrok.connect(bind_tls=True, pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels2 = len(ngrok.get_tunnels(self.pyngrok_config_v3))
        public_url3 = ngrok.connect(bind_tls=False, pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels3 = len(ngrok.get_tunnels(self.pyngrok_config_v3))

        # THEN
        self.assertTrue(public_url1.startswith("https://"))
        self.assertEqual(num_tunnels1, 2)
        self.assertTrue(public_url2.startswith("https://"))
        self.assertEqual(num_tunnels2, 3)
        self.assertTrue(public_url3.startswith("http://"))
        self.assertEqual(num_tunnels3, 4)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_disconnect_v2(self):
        # GIVEN
        url = ngrok.connect(pyngrok_config=self.pyngrok_config_v2).public_url
        time.sleep(1)
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v2)
        # Two tunnels, as one each was created for "http" and "https"
        self.assertEqual(len(ngrok._current_tunnels.keys()), 2)
        self.assertEqual(len(tunnels), 2)

        # WHEN
        ngrok.disconnect(url, pyngrok_config=self.pyngrok_config_v2)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        time.sleep(1)
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v2)

        # THEN
        # There is still one tunnel left, as we only disconnected the http tunnel
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        self.assertEqual(len(tunnels), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_disconnect_v3(self):
        # GIVEN
        url = ngrok.connect(pyngrok_config=self.pyngrok_config_v3).public_url
        time.sleep(1)
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v3)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        self.assertEqual(len(tunnels), 1)

        # WHEN
        ngrok.disconnect(url, self.pyngrok_config_v3)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)
        time.sleep(1)
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v3)

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)
        self.assertEqual(len(tunnels), 0)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_kill(self):
        # GIVEN
        ngrok.connect("5000", pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)
        ngrok_process = process.get_process(self.pyngrok_config_v3)
        monitor_thread = ngrok_process._monitor_thread
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)

        # WHEN
        ngrok.kill(self.pyngrok_config_v3)
        time.sleep(1)

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)
        self.assertIsNotNone(ngrok_process.proc.poll())
        self.assertFalse(monitor_thread.is_alive())
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assert_no_zombies()

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_api_get_request_success(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        ngrok_tunnel = ngrok.connect(pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)

        # WHEN
        response = ngrok.api_request(f"{current_process.api_url}{ngrok_tunnel.uri}", "GET")

        # THEN
        self.assertEqual(ngrok_tunnel.name, response["name"])
        self.assertEqual(ngrok_tunnel.public_url, response["public_url"])

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_api_request_query_params(self):
        # GIVEN
        tunnel_name = "tunnel (1)"
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        public_url = ngrok.connect(urlparse(current_process.api_url).port, name=tunnel_name,
                                   pyngrok_config=self.pyngrok_config_v3).public_url
        time.sleep(1)

        urlopen(f"{public_url}/api/status").read()
        time.sleep(3)

        # WHEN
        response1 = ngrok.api_request(f"{current_process.api_url}/api/requests/http", "GET")
        response2 = ngrok.api_request(f"{current_process.api_url}/api/requests/http", "GET",
                                      params={"tunnel_name": f"{tunnel_name}"})
        response3 = ngrok.api_request(f"{current_process.api_url}/api/requests/http", "GET",
                                      params={"tunnel_name": "unknown-tunnel"})

        # THEN
        self.assertEqual(len(response1["requests"]), 1)
        self.assertEqual(len(response2["requests"]), 1)
        self.assertEqual(0, len(response3["requests"]))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_api_request_delete_data_updated(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        ngrok.connect(pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v3)
        self.assertEqual(len(tunnels), 1)

        # WHEN
        response = ngrok.api_request(f"{current_process.api_url}{tunnels[0].uri}",
                                     "DELETE")

        # THEN
        self.assertEqual(response, {})
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v3)
        self.assertEqual(len(tunnels), 0)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_api_request_fails(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        bad_data = {
            "name": str(uuid.uuid4()),
            "addr": "8080",
            "proto": "invalid-proto"
        }

        # WHEN
        with self.assertRaises(PyngrokNgrokHTTPError) as cm:
            ngrok.api_request(f"{current_process.api_url}/api/tunnels", "POST", data=bad_data)

        # THEN
        self.assertEqual(HTTPStatus.BAD_REQUEST, cm.exception.status_code)
        self.assertIn("invalid tunnel configuration", str(cm.exception))
        self.assertIn("protocol name", str(cm.exception))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_api_request_timeout(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        ngrok_tunnel = ngrok.connect(pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)

        # WHEN
        with self.assertRaises(PyngrokNgrokURLError) as cm:
            ngrok.api_request(f"{current_process.api_url}{ngrok_tunnel.uri}", "DELETE",
                              timeout=0.0001)

        # THEN
        self.assertIn("timed out", cm.exception.reason)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_regional_tcp_v2(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        subdomain = generate_name_for_subdomain("pyngrok-temp")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v2,
                                                region="au")

        # WHEN
        ngrok_tunnel = ngrok.connect("5000", "tcp", subdomain=subdomain, pyngrok_config=pyngrok_config)
        current_process = ngrok.get_ngrok_process(pyngrok_config)

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(pyngrok_config))
        self.assertEqual("localhost:5000", ngrok_tunnel.config["addr"])
        self.assertIn("tcp://", ngrok_tunnel.public_url)
        self.assertIn(".au.", ngrok_tunnel.public_url)
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_regional_tcp_v3(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                region="au")

        # WHEN
        ngrok_tunnel = ngrok.connect("5000", "tcp", pyngrok_config=pyngrok_config)
        current_process = ngrok.get_ngrok_process(pyngrok_config)

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(pyngrok_config))
        self.assertEqual("localhost:5000", ngrok_tunnel.config["addr"])
        self.assertIn("tcp://", ngrok_tunnel.public_url)
        self.assertIn(".au.", ngrok_tunnel.public_url)
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_auth_v2(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        ngrok_tunnel = ngrok.connect("5000", auth="username:password", pyngrok_config=self.pyngrok_config_v2)
        current_process = ngrok.get_ngrok_process(self.pyngrok_config_v2)

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(self.pyngrok_config_v2))
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_auth_v3(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        ngrok_tunnel1 = ngrok.connect(auth="username:password", pyngrok_config=self.pyngrok_config_v3)
        ngrok_tunnel2 = ngrok.connect("5000", auth=["username:password"], pyngrok_config=self.pyngrok_config_v3)
        ngrok_tunnel3 = ngrok.connect("5001", basic_auth=["username:password"], pyngrok_config=self.pyngrok_config_v3)
        current_process = ngrok.get_ngrok_process(self.pyngrok_config_v3)

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertIsNotNone(ngrok_tunnel1.public_url)
        self.assertIsNotNone(ngrok_tunnel2.public_url)
        self.assertIsNotNone(ngrok_tunnel3.public_url)
        self.assertIsNotNone(process.get_process(self.pyngrok_config_v3))
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_regional_subdomain(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        subdomain = generate_name_for_subdomain("pyngrok-temp")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                region="au")

        # WHEN
        url = ngrok.connect("5000", subdomain=subdomain, pyngrok_config=pyngrok_config).public_url
        current_process = ngrok.get_ngrok_process(pyngrok_config)

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertIsNotNone(url)
        self.assertIsNotNone(process.get_process(pyngrok_config))
        self.assertIn("https://", url)
        self.assertIn(".au.", url)
        self.assertIn(subdomain, url)
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_connect_fileserver(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        ngrok_tunnel = ngrok.connect("file:///", pyngrok_config=self.pyngrok_config_v3)
        current_process = ngrok.get_ngrok_process(self.pyngrok_config_v3)
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v3)

        # THEN
        self.assertEqual(len(tunnels), 1)
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertTrue(current_process._monitor_thread.is_alive())
        self.assertTrue(ngrok_tunnel.name.startswith("http-file-"))
        self.assertEqual("file:///", ngrok_tunnel.config["addr"])
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(self.pyngrok_config_v3))
        self.assertIn('https://', ngrok_tunnel.public_url)
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_disconnect_fileserver_v2(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        url = ngrok.connect("file:///", pyngrok_config=self.pyngrok_config_v2).public_url

        # WHEN
        ngrok.disconnect(url, self.pyngrok_config_v2)
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v2)

        # THEN
        # There is still one tunnel left, as we only disconnected the http tunnel
        self.assertEqual(len(tunnels), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_get_tunnel_fileserver(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        ngrok_tunnel = ngrok.connect("file:///", pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)
        api_url = ngrok.get_ngrok_process(self.pyngrok_config_v3).api_url

        # WHEN
        response = ngrok.api_request(f"{api_url}{ngrok_tunnel.uri}", "GET")

        # THEN
        self.assertEqual(ngrok_tunnel.name, response["name"])
        self.assertTrue(ngrok_tunnel.name.startswith("http-file-"))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_ngrok_tunnel_refresh_metrics(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        ngrok_tunnel = ngrok.connect(urlparse(current_process.api_url).port, pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)
        self.assertEqual(0, ngrok_tunnel.metrics.get("http").get("count"))
        self.assertEqual(ngrok_tunnel.data["metrics"].get("http").get("count"), 0)

        urlopen(f"{ngrok_tunnel.public_url}/api/status").read()
        time.sleep(3)

        # WHEN
        ngrok_tunnel.refresh_metrics()

        # THEN
        self.assertGreater(ngrok_tunnel.metrics.get("http").get("count"), 0)
        self.assertGreater(ngrok_tunnel.data["metrics"].get("http").get("count"), 0)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_tunnel_definitions_v2(self):
        subdomain = generate_name_for_subdomain("pyngrok-temp")

        # GIVEN
        config = {
            "tunnels": {
                "http-tunnel": {
                    "proto": "http",
                    "addr": "8000",
                    "subdomain": subdomain
                },
                "tcp-tunnel": {
                    "proto": "tcp",
                    "addr": "22"
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v2_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v2")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v2,
                                                config_path=config_path)

        # WHEN
        http_tunnel = ngrok.connect(name="http-tunnel", pyngrok_config=pyngrok_config)
        ssh_tunnel = ngrok.connect(name="tcp-tunnel", pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(http_tunnel.name, "http-tunnel (http)")
        self.assertEqual(http_tunnel.config["addr"],
                         f"http://localhost:{config['tunnels']['http-tunnel']['addr']}")
        self.assertEqual(http_tunnel.proto, config["tunnels"]["http-tunnel"]["proto"])
        self.assertEqual(http_tunnel.public_url,
                         f"http://{config['tunnels']['http-tunnel']['subdomain']}.ngrok.io")
        self.assertEqual(ssh_tunnel.name, "tcp-tunnel")
        self.assertEqual(ssh_tunnel.config["addr"],
                         f"localhost:{config['tunnels']['tcp-tunnel']['addr']}")
        self.assertEqual(ssh_tunnel.proto, config["tunnels"]["tcp-tunnel"]["proto"])
        self.assertTrue(ssh_tunnel.public_url.startswith("tcp://"))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_tunnel_definitions_v3(self):
        subdomain = generate_name_for_subdomain("pyngrok-temp")

        # GIVEN
        config = {
            "tunnels": {
                "http-tunnel": {
                    "proto": "http",
                    "addr": "8000",
                    "subdomain": subdomain,
                    "circuit_breaker": 0.5,
                    "oauth": {
                        "provider": "google",
                        "allow_domains": ["pyngrok.com"],
                        "allow_emails": ["email@pyngrok.com"]
                    }
                },
                "tcp-tunnel": {
                    "proto": "tcp",
                    "addr": "22"
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path)

        # WHEN
        http_tunnel = ngrok.connect(name="http-tunnel", pyngrok_config=pyngrok_config)
        ssh_tunnel = ngrok.connect(name="tcp-tunnel", pyngrok_config=pyngrok_config)
        time.sleep(1)
        response_body = urlopen(http_tunnel.public_url).read().decode()

        # THEN
        self.assertEqual(http_tunnel.name, "http-tunnel")
        self.assertEqual(http_tunnel.config["addr"],
                         f"http://localhost:{config['tunnels']['http-tunnel']['addr']}")
        self.assertTrue(http_tunnel.config["addr"].startswith("http://"))
        self.assertEqual(http_tunnel.public_url,
                         f"https://{config['tunnels']['http-tunnel']['subdomain']}.ngrok.io")
        self.assertIn("Sign in - Google Accounts", response_body)
        self.assertEqual(ssh_tunnel.name, "tcp-tunnel")
        self.assertEqual(ssh_tunnel.config["addr"],
                         f"localhost:{config['tunnels']['tcp-tunnel']['addr']}")
        self.assertEqual(ssh_tunnel.proto, config["tunnels"]["tcp-tunnel"]["proto"])
        self.assertTrue(ssh_tunnel.public_url.startswith("tcp://"))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    @unittest.skipIf(not os.environ.get("NGROK_API_KEY"), "NGROK_API_KEY environment variable not set")
    def test_tunnel_definitions_tls(self):
        # GIVEN
        config = {
            "tunnels": {
                "tls-tunnel": {
                    "proto": "tls",
                    "addr": "80",
                    "domain": self.reserved_domain,
                    "terminate_at": "upstream",
                    "pooling_enabled": True
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path)

        # WHEN
        tls_tunnel = ngrok.connect(name="tls-tunnel", pyngrok_config=pyngrok_config)

        # THEN
        self.assertTrue(tls_tunnel.name.startswith("tls-"))
        self.assertEqual(tls_tunnel.config["addr"],
                         f"localhost:{config['tunnels']['tls-tunnel']['addr']}")
        self.assertTrue(tls_tunnel.config["addr"], "localhost:80")
        self.assertEqual(tls_tunnel.name, "tls-tunnel")
        self.assertEqual(tls_tunnel.config["addr"],
                         f"localhost:{config['tunnels']['tls-tunnel']['addr']}")
        self.assertEqual(tls_tunnel.proto, config["tunnels"]["tls-tunnel"]["proto"])
        self.assertTrue(tls_tunnel.public_url, "tls://{domain}".format(domain=self.reserved_domain))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    @unittest.skipIf(not os.environ.get("NGROK_API_KEY"), "NGROK_API_KEY environment variable not set")
    def test_ngrok_edge_http_tunnel_definition(self):
        # GIVEN
        config = {
            "tunnels": {
                "edge-http-tunnel": {
                    "addr": "80",
                    "labels": [
                        "edge={edge_id}".format(edge_id=self.http_edge_id),
                    ]
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path)

        # WHEN
        edge_http_tunnel = ngrok.connect(name="edge-http-tunnel", pyngrok_config=pyngrok_config)
        tunnels = ngrok.get_tunnels(pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(edge_http_tunnel.name, "edge-http-tunnel")
        self.assertEqual(edge_http_tunnel.config["addr"],
                         f"http://localhost:{config['tunnels']['edge-http-tunnel']['addr']}")
        self.assertTrue(edge_http_tunnel.config["addr"].startswith("http://"))
        self.assertEqual(edge_http_tunnel.proto, "https")
        self.assertEqual(edge_http_tunnel.public_url,
                         "https://{domain}:443".format(domain=self.http_edge_reserved_domain))
        self.assertEqual(len(tunnels), 1)
        self.assertEqual(tunnels[0].name, "edge-http-tunnel")
        self.assertEqual(tunnels[0].config["addr"],
                         f"http://localhost:{config['tunnels']['edge-http-tunnel']['addr']}")
        self.assertTrue(tunnels[0].config["addr"].startswith("http://"))
        self.assertEqual(tunnels[0].proto, "https")
        self.assertEqual(tunnels[0].public_url,
                         "https://{domain}:443".format(domain=self.http_edge_reserved_domain))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    @unittest.skipIf(not os.environ.get("NGROK_API_KEY"), "NGROK_API_KEY environment variable not set")
    def test_ngrok_edge_tcp_tunnel_definition(self):
        # GIVEN
        hostname, port = self.tcp_edge_reserved_addr.split(":")
        config = {
            "tunnels": {
                "edge-tcp-tunnel": {
                    "addr": "22",
                    "labels": [
                        "edge={edge_id}".format(edge_id=self.tcp_edge_id),
                    ]
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path)

        # WHEN
        edge_tcp_tunnel = ngrok.connect(name="edge-tcp-tunnel", pyngrok_config=pyngrok_config)
        tunnels = ngrok.get_tunnels(pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(edge_tcp_tunnel.name, "edge-tcp-tunnel")
        self.assertEqual(edge_tcp_tunnel.config["addr"],
                         f"tcp://localhost:{config['tunnels']['edge-tcp-tunnel']['addr']}")
        self.assertTrue(edge_tcp_tunnel.config["addr"].startswith("tcp://"))
        self.assertEqual(edge_tcp_tunnel.proto, "tcp")
        self.assertEqual(edge_tcp_tunnel.public_url, f"tcp://{hostname}:{port}")
        self.assertEqual(len(tunnels), 1)
        self.assertEqual(tunnels[0].name, "edge-tcp-tunnel")
        self.assertEqual(tunnels[0].config["addr"],
                         f"tcp://localhost:{config['tunnels']['edge-tcp-tunnel']['addr']}")
        self.assertTrue(tunnels[0].config["addr"].startswith("tcp://"))
        self.assertEqual(tunnels[0].proto, "tcp")
        self.assertTrue(tunnels[0].public_url, f"tcp://{hostname}:{port}")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    @unittest.skipIf(not os.environ.get("NGROK_API_KEY"), "NGROK_API_KEY environment variable not set")
    def test_ngrok_edge_tls_tunnel_definition(self):
        # GIVEN
        config = {
            "tunnels": {
                "edge-tls-tunnel": {
                    "addr": "443",
                    "labels": [
                        "edge={edge_id}".format(edge_id=self.tls_edge_id),
                    ]
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path)

        # WHEN
        edge_tls_tunnel = ngrok.connect(name="edge-tls-tunnel", pyngrok_config=pyngrok_config)
        tunnels = ngrok.get_tunnels(pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(edge_tls_tunnel.name, "edge-tls-tunnel")
        self.assertEqual(edge_tls_tunnel.config["addr"],
                         f"https://localhost:{config['tunnels']['edge-tls-tunnel']['addr']}")
        self.assertTrue(edge_tls_tunnel.config["addr"].startswith("https://"))
        self.assertEqual(edge_tls_tunnel.proto, "tls")
        self.assertEqual(edge_tls_tunnel.public_url,
                         "tls://{domain}:443".format(domain=self.tls_edge_reserved_domain))
        self.assertEqual(len(tunnels), 1)
        self.assertEqual(tunnels[0].name, "edge-tls-tunnel")
        self.assertEqual(tunnels[0].config["addr"],
                         f"https://localhost:{config['tunnels']['edge-tls-tunnel']['addr']}")
        self.assertTrue(tunnels[0].config["addr"].startswith("https://"))
        self.assertEqual(tunnels[0].proto, "tls")
        self.assertEqual(tunnels[0].public_url,
                         "tls://{domain}:443".format(domain=self.tls_edge_reserved_domain))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    @unittest.skipIf(not os.environ.get("NGROK_API_KEY"), "NGROK_API_KEY environment variable not set")
    def test_bind_tls_and_labels_not_allowed(self):
        # GIVEN
        config = {
            "tunnels": {
                "edge-tunnel": {
                    "addr": "443",
                    "labels": [
                        "edge={edge_id}".format(edge_id=self.tls_edge_id),
                    ]
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path)

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(name="edge-tunnel", bind_tls=True, pyngrok_config=pyngrok_config)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_labels_no_api_key_fails(self):
        # GIVEN
        config = {
            "tunnels": {
                "edge-tunnel": {
                    "addr": "80",
                    "labels": [
                        "edge=edghts_some-id",
                    ]
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path,
                                                api_key=None)
        self.assertIsNone(pyngrok_config.api_key)

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(name="edge-tunnel", pyngrok_config=pyngrok_config)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_ngrok_http_internal_endpoint_pooling(self):
        # WHEN
        internal_http_endpoint = ngrok.connect(proto="http", addr="80", domain="pyngrok.internal",
                                               pooling_enabled=True,
                                               pyngrok_config=self.pyngrok_config_v3)
        tunnels = ngrok.get_tunnels(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertEqual(internal_http_endpoint.config["addr"], "http://localhost:80")
        self.assertTrue(internal_http_endpoint.config["addr"].startswith("http://"))
        self.assertEqual(internal_http_endpoint.proto, "https")
        self.assertEqual(internal_http_endpoint.public_url, "https://pyngrok.internal")
        self.assertEqual(len(tunnels), 1)
        self.assertEqual(tunnels[0].config["addr"], "http://localhost:80")
        self.assertTrue(tunnels[0].config["addr"].startswith("http://"))
        self.assertEqual(tunnels[0].proto, "https")
        self.assertEqual(tunnels[0].public_url, "https://pyngrok.internal")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_ngrok_tls_internal_endpoint_pooling(self):
        # WHEN
        tls_internal_endpoint = ngrok.connect(proto="tls", addr="443", domain="pyngrok.internal",
                                              pooling_enabled=True,
                                              pyngrok_config=self.pyngrok_config_v3)
        tunnels = ngrok.get_tunnels(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertEqual(tls_internal_endpoint.config["addr"], "tls://localhost:443")
        self.assertTrue(tls_internal_endpoint.config["addr"].startswith("tls://"))
        self.assertEqual(tls_internal_endpoint.proto, "tls")
        self.assertEqual(tls_internal_endpoint.public_url, "tls://pyngrok.internal")
        self.assertEqual(len(tunnels), 1)
        self.assertEqual(tunnels[0].config["addr"], "tls://localhost:443")
        self.assertTrue(tunnels[0].config["addr"].startswith("tls://"))
        self.assertEqual(tunnels[0].proto, "tls")
        self.assertEqual(tunnels[0].public_url, "tls://pyngrok.internal")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_tunnel_definitions_pyngrok_default_with_overrides(self):
        subdomain = generate_name_for_subdomain("pyngrok-temp")

        # GIVEN
        config = {
            "tunnels": {
                "pyngrok-default": {
                    "proto": "http",
                    "addr": "8080",
                    "subdomain": subdomain
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        subdomain = generate_name_for_subdomain("pyngrok-temp")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path)

        # WHEN
        ngrok_tunnel1 = ngrok.connect(pyngrok_config=pyngrok_config)
        ngrok_tunnel2 = ngrok.connect("5000", subdomain=subdomain, pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(ngrok_tunnel1.name, "pyngrok-default")
        self.assertEqual(ngrok_tunnel1.config["addr"],
                         f"http://localhost:{config['tunnels']['pyngrok-default']['addr']}")
        self.assertEqual("http", config["tunnels"]["pyngrok-default"]["proto"])
        self.assertEqual(ngrok_tunnel1.public_url,
                         f"https://{config['tunnels']['pyngrok-default']['subdomain']}.ngrok.io")
        self.assertEqual(ngrok_tunnel2.name, "pyngrok-default")
        self.assertEqual(ngrok_tunnel2.config["addr"], "http://localhost:5000")
        self.assertEqual("http", config["tunnels"]["pyngrok-default"]["proto"])
        self.assertIn(subdomain, ngrok_tunnel2.public_url)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_upgrade_ngrok_config_file_v2_to_v3(self):
        # GIVEN
        config_path = os.path.join(self.config_dir, "legacy_config.yml")
        installer.install_default_config(config_path, ngrok_version="v2")
        pyngrok_config_v3 = self.copy_with_updates(self.pyngrok_config_v3,
                                                   config_path=config_path,
                                                   ngrok_version="v3")
        self.given_ngrok_installed(self.pyngrok_config_v3)

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(pyngrok_config=pyngrok_config_v3)

        # GIVEN
        process.capture_run_process(pyngrok_config_v3.ngrok_path,
                                    ["config", "upgrade", "--config", pyngrok_config_v3.config_path])

        # WHEN
        ngrok.connect(pyngrok_config=pyngrok_config_v3)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_full_config_v2_http_tunnel_definitions(self):
        # GIVEN
        config = {
            "version": "2",
            "tunnels": {
                "my-tunnel": {
                    "addr": "5000",
                    "metadata": "metadata",
                    "inspect": False,
                    "proto": "http",
                    "basic_auth": ["auth-token"],
                    "circuit_breaker": 20,
                    "compression": False,
                    "host_header": "host-header",
                    "domain": "pyngrok.com",
                    "ip_restriction": {"allow_cidrs": ["allowed"], "deny_cidrs": ["denied"]},
                    "mutual_tls_cas": __file__,
                    "oauth": {
                        "provider": "google",
                        "allow_domains": ["pyngrok.com"],
                        "allow_emails": ["email@pyngrok.com"]
                    },
                    "proxy_proto": "1",
                    "request_header": {"add": ["req-addition"], "remove": ["req-subtraction"]},
                    "response_header": {"add": ["res-addition"], "remove": ["res-subtraction"]},
                    "schemes": ["https"],
                    # Can't be used in conjunction with "domain", but validated in other tests
                    # "subdomain": "pyngrok",
                    "traffic_policy": {
                        "on_http_request": {"name": "inbound-policy", "expressions": "inbound-policy-expression",
                                            "actions": {"type": "inbound-policy-actions-type",
                                                        "config": "inbound-policy-actions-config"}},
                        "on_http_response": {"name": "outbound-policy", "expressions": "outbound-policy-expression",
                                             "actions": {"type": "outbound-policy-actions-type",
                                                         "config": "outbound-policy-actions-config"}}
                    },
                    "user_agent_filter": {"allow": ["allow-user-agent"], "deny": ["deny-user-agent"]},
                    "verify_webhook": {"provider": "provider", "secret": "secret"},
                    "websocket_tcp_converter": False
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path,
                                                api_key="api-key")

        # WHEN
        # This test ensures the validity of the config (pyngrok will fail with PyngrokNgrokError if the above is
        # invalid), not that the config can start a valid tunnel (thus PyngrokNgrokHTTPError is thrown when pyngrok
        # tries to open the tunnel after ngrok successfully starts, but we can ignore that for this test
        with self.assertRaises(PyngrokNgrokHTTPError):
            ngrok.connect(name="my-tunnel", pyngrok_config=pyngrok_config)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_full_config_v2_tcp_tunnel_definitions(self):
        # GIVEN
        config = {
            "version": "2",
            "tunnels": {
                "my-tunnel": {
                    "addr": "5000",
                    "metadata": "metadata",
                    "inspect": False,
                    "proto": "tcp",
                    "ip_restriction": {"allow_cidrs": ["allowed"], "deny_cidrs": ["denied"]},
                    "proxy_proto": "1",
                    "remote_addr": "2.tcp.ngrok.io:21746",
                    "traffic_policy": {
                        "inbound": {"name": "inbound-policy", "expressions": "inbound-policy-expression",
                                    "actions": {"type": "inbound-policy-actions-type",
                                                "config": "inbound-policy-actions-config"}},
                        "outbound": {"name": "outbound-policy", "expressions": "outbound-policy-expression",
                                     "actions": {"type": "outbound-policy-actions-type",
                                                 "config": "outbound-policy-actions-config"}}
                    }
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path,
                                                api_key="api-key")

        # WHEN
        # This test ensures the validity of the config (pyngrok will fail with PyngrokNgrokError if the above is
        # invalid), not that the config can start a valid tunnel (thus PyngrokNgrokHTTPError is thrown when pyngrok
        # tries to open the tunnel after ngrok successfully starts, but we can ignore that for this test
        with self.assertRaises(PyngrokNgrokHTTPError):
            ngrok.connect(name="my-tunnel", pyngrok_config=pyngrok_config)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_full_config_v2_tls_tunnel_definitions(self):
        # GIVEN
        config = {
            "version": "2",
            "tunnels": {
                "my-tunnel": {
                    "addr": "5000",
                    "metadata": "metadata",
                    "inspect": False,
                    "proto": "tls",
                    # "mutual_tls_cas": __file__,
                    # "crt": __file__,
                    "domain": "pyngrok.com",
                    "ip_restriction": {"allow_cidrs": ["allowed"], "deny_cidrs": ["denied"]},
                    # "key": __file__,
                    "proxy_proto": "1",
                    # Can't be used in conjunction with "domain", but validated in other tests
                    # "subdomain": "pyngrok",
                    "terminate_at": "edge",
                    "traffic_policy": {
                        "inbound": {"name": "inbound-policy", "expressions": "inbound-policy-expression",
                                    "actions": {"type": "inbound-policy-actions-type",
                                                "config": "inbound-policy-actions-config"}},
                        "outbound": {"name": "outbound-policy", "expressions": "outbound-policy-expression",
                                     "actions": {"type": "outbound-policy-actions-type",
                                                 "config": "outbound-policy-actions-config"}}
                    }
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path,
                                                api_key="api-key")

        # WHEN
        # This test ensures the validity of the config (pyngrok will fail with PyngrokNgrokError if the above is
        # invalid), not that the config can start a valid tunnel (thus PyngrokNgrokHTTPError is thrown when pyngrok
        # tries to open the tunnel after ngrok successfully starts, but we can ignore that for this test
        with self.assertRaises(PyngrokNgrokHTTPError):
            ngrok.connect(name="my-tunnel", pyngrok_config=pyngrok_config)

    ################################################################################
    # Tests below this point don't need to start a long-lived ngrok process, they
    # are asserting on pyngrok-specific code or edge cases.
    ################################################################################

    def test_web_addr_false_not_allowed(self):
        # GIVEN
        with open(self.pyngrok_config_v3.config_path, "w") as config_file:
            yaml.dump({"web_addr": False}, config_file)

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(pyngrok_config=self.pyngrok_config_v3)

    def test_log_format_json_not_allowed(self):
        # GIVEN
        with open(self.pyngrok_config_v3.config_path, "w") as config_file:
            yaml.dump({"log_format": "json"}, config_file)

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(pyngrok_config=self.pyngrok_config_v3)

    def test_log_level_warn_not_allowed(self):
        # GIVEN
        with open(self.pyngrok_config_v3.config_path, "w") as config_file:
            yaml.dump({"log_level": "warn"}, config_file)

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(pyngrok_config=self.pyngrok_config_v3)

    def test_labels_param_not_allowed(self):
        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(labels=[])

    def test_api_request_security_error(self):
        # WHEN
        with self.assertRaises(PyngrokSecurityError):
            ngrok.api_request(f"file:{__file__}")

    @mock.patch("pyngrok.process.capture_run_process")
    def test_update(self, mock_capture_run_process):
        ngrok.update(pyngrok_config=self.pyngrok_config_v3)

        self.assertEqual(mock_capture_run_process.call_count, 1)
        self.assertEqual("update", mock_capture_run_process.call_args[0][1][0])

    def test_version(self):
        # WHEN
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertIsNotNone(ngrok_version)
        self.assertEqual(__version__, pyngrok_version)

    def test_set_auth_token_v2(self):
        ngrok.set_auth_token("some-auth-token", pyngrok_config=self.pyngrok_config_v2)
        with open(self.pyngrok_config_v2.config_path, "r") as f:
            contents = f.read()

        # THEN
        self.assertIn("some-auth-token", contents)

    def test_set_auth_token_v3(self):
        # WHEN
        ngrok.set_auth_token("some-auth-token", pyngrok_config=self.pyngrok_config_v3)
        with open(self.pyngrok_config_v3.config_path, "r") as f:
            contents = f.read()

        # THEN
        self.assertIn("some-auth-token", contents)

    @mock.patch("subprocess.check_output")
    def test_set_auth_token_fails(self, mock_check_output):
        # GIVEN
        error_msg = "An error occurred"
        mock_check_output.return_value = error_msg

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            ngrok.set_auth_token("some-auth-token", pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertIn(f": {error_msg}", str(cm.exception))

    def test_set_api_key_v2_fails(self):
        with self.assertRaises(PyngrokError):
            ngrok.set_api_key("some-api-key", pyngrok_config=self.pyngrok_config_v2)

    def test_set_api_key_v3(self):
        # WHEN
        ngrok.set_api_key("some-api-key", pyngrok_config=self.pyngrok_config_v3)
        with open(self.pyngrok_config_v3.config_path, "r") as f:
            contents = f.read()

        # THEN
        self.assertIn("some-api-key", contents)

    @mock.patch("subprocess.check_output")
    def test_set_api_key_fails(self, mock_check_output):
        # GIVEN
        error_msg = "An error occurred"
        mock_check_output.return_value = error_msg

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            ngrok.set_api_key("some-api-key", pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertIn(f": {error_msg}", str(cm.exception))

    @mock.patch('pyngrok.ngrok.api_request')
    @mock.patch('pyngrok.ngrok.get_ngrok_process')
    def test_config_v2_passed_to_api_request(self, mock_get_ngrok_process, mock_api_request):
        # GIVEN
        config = {
            "version": "2",
            "tunnels": {
                "my-tunnel": {
                    "proto": "http",
                    "addr": "8000"
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")

        installer.install_default_config(config_path, config, ngrok_version="v3", config_version="3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                config_path=config_path,
                                                api_key="api-key", )

        expected_options = config["tunnels"]["my-tunnel"].copy()
        expected_options["name"] = "my-tunnel"

        # WHEN
        ngrok.connect(name="my-tunnel", pyngrok_config=pyngrok_config)

        # THEN
        mock_api_request.assert_called_with(f"{mock_get_ngrok_process().api_url}/api/tunnels", method="POST",
                                            data=expected_options, timeout=pyngrok_config.request_timeout)
