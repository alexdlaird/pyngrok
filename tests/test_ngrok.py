import os
import unittest

import time
import uuid
from http import HTTPStatus
from unittest import mock
from urllib.parse import urlparse
from urllib.request import urlopen

import yaml

from pyngrok import ngrok, process, installer
from pyngrok.exception import PyngrokNgrokHTTPError, PyngrokNgrokURLError, PyngrokSecurityError, PyngrokError, \
    PyngrokNgrokError
from tests.testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "6.1.0"


class TestNgrok(NgrokTestCase):
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

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_connect_v2(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)
        ngrok.set_auth_token(os.environ["NGROK_AUTHTOKEN"], self.pyngrok_config_v2)

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

    def test_connect_name(self):
        # WHEN
        ngrok_tunnel = ngrok.connect(name="my-tunnel", pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertEqual(ngrok_tunnel.name, "my-tunnel")
        self.assertEqual("https", ngrok_tunnel.proto)
        self.assertEqual("http://localhost:80", ngrok_tunnel.config["addr"])

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

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_bind_tls_both_v2(self):
        # GIVEN
        ngrok.set_auth_token(os.environ["NGROK_AUTHTOKEN"], self.pyngrok_config_v2)

        # WHEN
        url = ngrok.connect(bind_tls="both", pyngrok_config=self.pyngrok_config_v2).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v2))

        # THEN
        self.assertTrue(url.startswith("http"))
        self.assertEqual(num_tunnels, 2)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_bind_tls_https_only_v2(self):
        # GIVEN
        ngrok.set_auth_token(os.environ["NGROK_AUTHTOKEN"], self.pyngrok_config_v2)

        # WHEN
        url = ngrok.connect(bind_tls=True, pyngrok_config=self.pyngrok_config_v2).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v2))

        # THEN
        self.assertTrue(url.startswith("https"))
        self.assertEqual(num_tunnels, 1)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_bind_tls_http_only_v2(self):
        # GIVEN
        ngrok.set_auth_token(os.environ["NGROK_AUTHTOKEN"], self.pyngrok_config_v2)

        # WHEN
        url = ngrok.connect(bind_tls=False, pyngrok_config=self.pyngrok_config_v2).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v2))

        # THEN
        self.assertTrue(url.startswith("http"))
        self.assertEqual(num_tunnels, 1)

    def test_schemes_http_v3(self):
        # WHEN
        url = ngrok.connect(schemes=["http"], pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v3))

        # THEN
        self.assertTrue(url.startswith("http"))
        self.assertEqual(num_tunnels, 1)

    def test_schemes_https_v3(self):
        # WHEN
        url = ngrok.connect(schemes=["https"], pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v3))

        # THEN
        self.assertTrue(url.startswith("https"))
        self.assertEqual(num_tunnels, 1)

    def test_schemes_http_https_v3(self):
        # WHEN
        url = ngrok.connect(schemes=["http", "https"], pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v3))

        # THEN
        self.assertTrue(url.startswith("https"))
        self.assertEqual(num_tunnels, 2)

    def test_bind_tls_upgraded_to_schemes_v3(self):
        # WHEN
        url = ngrok.connect(bind_tls="both", pyngrok_config=self.pyngrok_config_v3).public_url
        num_tunnels = len(ngrok.get_tunnels(self.pyngrok_config_v3))

        # THEN
        self.assertTrue(url.startswith("https"))
        self.assertEqual(num_tunnels, 2)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_disconnect_v2(self):
        # GIVEN
        ngrok.set_auth_token(os.environ["NGROK_AUTHTOKEN"], self.pyngrok_config_v2)
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
        self.assertNoZombies()

    def test_api_get_request_success(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        ngrok_tunnel = ngrok.connect(pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)

        # WHEN
        response = ngrok.api_request("{}{}".format(current_process.api_url, ngrok_tunnel.uri), "GET")

        # THEN
        self.assertEqual(ngrok_tunnel.name, response["name"])
        self.assertTrue(ngrok_tunnel.public_url.startswith("http"))

    def test_api_request_query_params(self):
        # GIVEN
        tunnel_name = "tunnel (1)"
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        public_url = ngrok.connect(urlparse(current_process.api_url).port, name=tunnel_name,
                                   bind_tls=True, pyngrok_config=self.pyngrok_config_v3).public_url
        time.sleep(1)

        urlopen("{}/status".format(public_url)).read()
        time.sleep(3)

        # WHEN
        response1 = ngrok.api_request("{}/api/requests/http".format(current_process.api_url), "GET")
        response2 = ngrok.api_request("{}/api/requests/http".format(current_process.api_url), "GET",
                                      params={"tunnel_name": "{}".format(tunnel_name)})
        response3 = ngrok.api_request("{}/api/requests/http".format(current_process.api_url), "GET",
                                      params={"tunnel_name": "{} (http)".format(tunnel_name)})

        # THEN
        self.assertGreater(len(response1["requests"]), 0)
        self.assertGreater(len(response2["requests"]), 0)
        self.assertEqual(0, len(response3["requests"]))

    def test_api_request_delete_data_updated(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        ngrok.connect(pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v3)
        self.assertEqual(len(tunnels), 1)

        # WHEN
        response = ngrok.api_request("{}{}".format(current_process.api_url, tunnels[0].uri),
                                     "DELETE")

        # THEN
        self.assertEqual(response, {})
        tunnels = ngrok.get_tunnels(self.pyngrok_config_v3)
        self.assertEqual(len(tunnels), 0)

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
            ngrok.api_request("{}/api/tunnels".format(current_process.api_url), "POST", data=bad_data)

        # THEN
        self.assertEqual(HTTPStatus.BAD_REQUEST, cm.exception.status_code)
        self.assertIn("invalid tunnel configuration", str(cm.exception))
        self.assertIn("protocol name", str(cm.exception))

    def test_api_request_timeout(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        ngrok_tunnel = ngrok.connect(pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)

        # WHEN
        with self.assertRaises(PyngrokNgrokURLError) as cm:
            ngrok.api_request("{}{}".format(current_process.api_url, ngrok_tunnel.uri), "DELETE",
                              timeout=0.0001)

        # THEN
        self.assertIn("timed out", cm.exception.reason)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_regional_tcp_v2(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        subdomain = self.create_unique_subdomain()
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v2, auth_token=os.environ["NGROK_AUTHTOKEN"],
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

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_regional_tcp_v3(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, auth_token=os.environ["NGROK_AUTHTOKEN"],
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

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_auth_v2(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v2, auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        ngrok_tunnel = ngrok.connect("5000", auth="username:password", pyngrok_config=pyngrok_config)
        current_process = ngrok.get_ngrok_process(pyngrok_config)

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(pyngrok_config))
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_auth_v3(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        ngrok_tunnel1 = ngrok.connect("5000", auth="username:password", pyngrok_config=pyngrok_config)
        ngrok_tunnel2 = ngrok.connect("5000", basic_auth=["username:password"], pyngrok_config=pyngrok_config)
        current_process = ngrok.get_ngrok_process(pyngrok_config)

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertIsNotNone(ngrok_tunnel1.public_url)
        self.assertIsNotNone(ngrok_tunnel2.public_url)
        self.assertIsNotNone(process.get_process(pyngrok_config))
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_regional_subdomain(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        subdomain = self.create_unique_subdomain()
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, auth_token=os.environ["NGROK_AUTHTOKEN"],
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

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_connect_fileserver(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        ngrok_tunnel = ngrok.connect("file:///", pyngrok_config=pyngrok_config)
        current_process = ngrok.get_ngrok_process(pyngrok_config)
        time.sleep(1)
        tunnels = ngrok.get_tunnels(pyngrok_config)

        # THEN
        self.assertEqual(len(tunnels), 1)
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertTrue(current_process._monitor_thread.is_alive())
        self.assertTrue(ngrok_tunnel.name.startswith("http-file-"))
        self.assertEqual("file:///", ngrok_tunnel.config["addr"])
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(pyngrok_config))
        self.assertIn('https://', ngrok_tunnel.public_url)
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_disconnect_fileserver_v2(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v2, auth_token=os.environ["NGROK_AUTHTOKEN"])
        url = ngrok.connect("file:///", pyngrok_config=pyngrok_config).public_url
        time.sleep(1)

        # WHEN
        ngrok.disconnect(url, pyngrok_config)
        time.sleep(1)
        tunnels = ngrok.get_tunnels(pyngrok_config)

        # THEN
        # There is still one tunnel left, as we only disconnected the http tunnel
        self.assertEqual(len(tunnels), 1)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_get_tunnel_fileserver(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, auth_token=os.environ["NGROK_AUTHTOKEN"])
        ngrok_tunnel = ngrok.connect("file:///", pyngrok_config=pyngrok_config)
        time.sleep(1)
        api_url = ngrok.get_ngrok_process(pyngrok_config).api_url

        # WHEN
        response = ngrok.api_request("{}{}".format(api_url, ngrok_tunnel.uri), "GET")

        # THEN
        self.assertEqual(ngrok_tunnel.name, response["name"])
        self.assertTrue(ngrok_tunnel.name.startswith("http-file-"))

    def test_ngrok_tunnel_refresh_metrics(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        ngrok_tunnel = ngrok.connect(urlparse(current_process.api_url).port, bind_tls=True,
                                     pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)
        self.assertEqual(0, ngrok_tunnel.metrics.get("http").get("count"))
        self.assertEqual(ngrok_tunnel.data["metrics"].get("http").get("count"), 0)

        urlopen("{}/status".format(ngrok_tunnel.public_url)).read()
        time.sleep(3)

        # WHEN
        ngrok_tunnel.refresh_metrics()

        # THEN
        self.assertGreater(ngrok_tunnel.metrics.get("http").get("count"), 0)
        self.assertGreater(ngrok_tunnel.data["metrics"].get("http").get("count"), 0)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_tunnel_definitions_v2(self):
        subdomain = self.create_unique_subdomain()

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
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v2, config_path=config_path,
                                                auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        http_tunnel = ngrok.connect(name="http-tunnel", pyngrok_config=pyngrok_config)
        ssh_tunnel = ngrok.connect(name="tcp-tunnel", pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(http_tunnel.name, "http-tunnel (http)")
        self.assertEqual(http_tunnel.config["addr"],
                         "http://localhost:{}".format(config["tunnels"]["http-tunnel"]["addr"]))
        self.assertEqual(http_tunnel.proto, config["tunnels"]["http-tunnel"]["proto"])
        self.assertEqual(http_tunnel.public_url,
                         "http://{}.ngrok.io".format(config["tunnels"]["http-tunnel"]["subdomain"]))
        self.assertEqual(ssh_tunnel.name, "tcp-tunnel")
        self.assertEqual(ssh_tunnel.config["addr"],
                         "localhost:{}".format(config["tunnels"]["tcp-tunnel"]["addr"]))
        self.assertEqual(ssh_tunnel.proto, config["tunnels"]["tcp-tunnel"]["proto"])
        self.assertTrue(ssh_tunnel.public_url.startswith("tcp://"))

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_tunnel_definitions_v3(self):
        subdomain = self.create_unique_subdomain()

        # GIVEN
        config = {
            "tunnels": {
                "http-tunnel": {
                    "proto": "http",
                    "addr": "8000",
                    "subdomain": subdomain,
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
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, config_path=config_path,
                                                auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        http_tunnel = ngrok.connect(name="http-tunnel", pyngrok_config=pyngrok_config)
        ssh_tunnel = ngrok.connect(name="tcp-tunnel", pyngrok_config=pyngrok_config)
        time.sleep(1)
        response = urlopen(http_tunnel.public_url)
        time.sleep(3)

        # THEN
        self.assertEqual(http_tunnel.name, "http-tunnel")
        self.assertEqual(http_tunnel.config["addr"],
                         "http://localhost:{}".format(config["tunnels"]["http-tunnel"]["addr"]))
        self.assertTrue(http_tunnel.config["addr"].startswith("http://"))
        self.assertEqual(http_tunnel.public_url,
                         "https://{}.ngrok.io".format(config["tunnels"]["http-tunnel"]["subdomain"]))
        self.assertIn("Sign in - Google Accounts", response.read().decode())
        self.assertEqual(ssh_tunnel.name, "tcp-tunnel")
        self.assertEqual(ssh_tunnel.config["addr"],
                         "localhost:{}".format(config["tunnels"]["tcp-tunnel"]["addr"]))
        self.assertEqual(ssh_tunnel.proto, config["tunnels"]["tcp-tunnel"]["proto"])
        self.assertTrue(ssh_tunnel.public_url.startswith("tcp://"))

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    @unittest.skipIf("NGROK_HTTP_EDGE" not in os.environ, "NGROK_HTTP_EDGE environment variable not set")
    @unittest.skipIf("NGROK_TCP_EDGE" not in os.environ, "NGROK_TCP_EDGE environment variable not set")
    @unittest.skipIf("NGROK_API_KEY" not in os.environ, "NGROK_API_KEY environment variable not set")
    @unittest.skipIf("NGROK_HTTP_EDGE_ENDPOINT" not in os.environ,
                     "NGROK_HTTP_EDGE_ENDPOINT environment variable not set")
    @unittest.skipIf("NGROK_TCP_EDGE_ENDPOINT" not in os.environ,
                     "NGROK_TCP_EDGE_ENDPOINT environment variable not set")
    def test_ngrok_v3_cloud_edge_tunnel_definition(self):
        # GIVEN
        config = {
            "tunnels": {
                "edge-http-tunnel": {
                    "addr": "80",
                    "labels": [
                        "edge={}".format(os.environ["NGROK_HTTP_EDGE"]),
                    ]
                },
                "edge-tcp-tunnel": {
                    "addr": "22",
                    "labels": [
                        "edge={}".format(os.environ["NGROK_TCP_EDGE"]),
                    ]
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, config_path=config_path,
                                                auth_token=os.environ["NGROK_AUTHTOKEN"],
                                                api_key=os.environ["NGROK_API_KEY"])

        # WHEN
        edge_http_tunnel = ngrok.connect(name="edge-http-tunnel", pyngrok_config=pyngrok_config)
        edge_tcp_tunnel = ngrok.connect(name="edge-tcp-tunnel", pyngrok_config=pyngrok_config)
        tunnels = sorted(ngrok.get_tunnels(pyngrok_config=pyngrok_config), key=lambda x: x.proto)

        # THEN
        self.assertEqual(edge_http_tunnel.name, "edge-http-tunnel")
        self.assertEqual(edge_http_tunnel.config["addr"],
                         "http://localhost:{}".format(config["tunnels"]["edge-http-tunnel"]["addr"]))
        self.assertTrue(edge_http_tunnel.config["addr"].startswith("http://"))
        self.assertEqual(edge_http_tunnel.proto, "https")
        self.assertEqual(edge_http_tunnel.public_url, os.environ["NGROK_HTTP_EDGE_ENDPOINT"])
        self.assertEqual(edge_tcp_tunnel.name, "edge-tcp-tunnel")
        self.assertEqual(edge_tcp_tunnel.config["addr"],
                         "tcp://localhost:{}".format(config["tunnels"]["edge-tcp-tunnel"]["addr"]))
        self.assertTrue(edge_tcp_tunnel.config["addr"].startswith("tcp://"))
        self.assertEqual(edge_tcp_tunnel.proto, "tcp")
        self.assertEqual(edge_tcp_tunnel.public_url, os.environ["NGROK_TCP_EDGE_ENDPOINT"])
        self.assertEqual(len(tunnels), 2)
        self.assertEqual(tunnels[0].name, "edge-http-tunnel")
        self.assertEqual(tunnels[0].config["addr"],
                         "http://localhost:{}".format(config["tunnels"]["edge-http-tunnel"]["addr"]))
        self.assertTrue(tunnels[0].config["addr"].startswith("http://"))
        self.assertEqual(tunnels[0].proto, "https")
        self.assertEqual(tunnels[0].public_url, os.environ["NGROK_HTTP_EDGE_ENDPOINT"])
        self.assertEqual(tunnels[1].name, "edge-tcp-tunnel")
        self.assertEqual(tunnels[1].config["addr"],
                         "tcp://localhost:{}".format(config["tunnels"]["edge-tcp-tunnel"]["addr"]))
        self.assertTrue(tunnels[1].config["addr"].startswith("tcp://"))
        self.assertEqual(tunnels[1].proto, "tcp")
        self.assertTrue(tunnels[1].public_url, os.environ["NGROK_TCP_EDGE_ENDPOINT"])

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    @unittest.skipIf("NGROK_HTTP_EDGE" not in os.environ, "NGROK_HTTP_EDGE environment variable not set")
    @unittest.skipIf("NGROK_API_KEY" not in os.environ, "NGROK_API_KEY environment variable not set")
    def test_bind_tls_and_labels_not_allowed(self):
        # GIVEN
        config = {
            "tunnels": {
                "edge-tunnel": {
                    "addr": "80",
                    "labels": [
                        "edge={}".format(os.environ["NGROK_HTTP_EDGE"]),
                    ]
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, config_path=config_path,
                                                auth_token=os.environ["NGROK_AUTHTOKEN"],
                                                api_key=os.environ["NGROK_API_KEY"])

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(name="edge-tunnel", bind_tls=True, pyngrok_config=pyngrok_config)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    @unittest.skipIf("NGROK_HTTP_EDGE" not in os.environ, "NGROK_HTTP_EDGE environment variable not set")
    def test_labels_no_api_key_fails(self):
        # GIVEN
        config = {
            "tunnels": {
                "edge-tunnel": {
                    "addr": "80",
                    "labels": [
                        "edge={}".format(os.environ["NGROK_HTTP_EDGE"]),
                    ]
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path, config, ngrok_version="v3")
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, config_path=config_path,
                                                auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(name="edge-tunnel", pyngrok_config=pyngrok_config)

    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_tunnel_definitions_pyngrok_default_with_overrides(self):
        subdomain = self.create_unique_subdomain()

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
        subdomain = self.create_unique_subdomain()
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, config_path=config_path,
                                                auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        ngrok_tunnel1 = ngrok.connect(pyngrok_config=pyngrok_config)
        ngrok_tunnel2 = ngrok.connect("5000", subdomain=subdomain, pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(ngrok_tunnel1.name, "pyngrok-default")
        self.assertEqual(ngrok_tunnel1.config["addr"],
                         "http://localhost:{}".format(config["tunnels"]["pyngrok-default"]["addr"]))
        self.assertEqual("http", config["tunnels"]["pyngrok-default"]["proto"])
        self.assertEqual(ngrok_tunnel1.public_url,
                         "https://{}.ngrok.io".format(config["tunnels"]["pyngrok-default"]["subdomain"]))
        self.assertEqual(ngrok_tunnel2.name, "pyngrok-default")
        self.assertEqual(ngrok_tunnel2.config["addr"], "http://localhost:5000")
        self.assertEqual("http", config["tunnels"]["pyngrok-default"]["proto"])
        self.assertIn(subdomain, ngrok_tunnel2.public_url)

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
            ngrok.api_request("file:{}".format(__file__))

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
        self.assertEqual(ngrok.__version__, pyngrok_version)

    def test_set_auth_token_v2(self):
        ngrok.set_auth_token("807ad30a-73be-48d8", pyngrok_config=self.pyngrok_config_v2)
        with open(self.pyngrok_config_v2.config_path, "r") as f:
            contents = f.read()

        # THEN
        self.assertIn("807ad30a-73be-48d8", contents)

    def test_set_auth_token_v3(self):
        # WHEN
        ngrok.set_auth_token("807ad30a-73be-48d8", pyngrok_config=self.pyngrok_config_v3)
        with open(self.pyngrok_config_v3.config_path, "r") as f:
            contents = f.read()

        # THEN
        self.assertIn("807ad30a-73be-48d8", contents)

    @mock.patch("subprocess.check_output")
    def test_set_auth_token_fails(self, mock_check_output):
        # GIVEN
        error_msg = "An error occurred"
        mock_check_output.return_value = error_msg

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            ngrok.set_auth_token("807ad30a-73be-48d8", pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertIn(": {}".format(error_msg), str(cm.exception))
