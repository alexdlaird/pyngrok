import os
import platform
import sys
import time
import uuid

import mock
import yaml

from future.standard_library import install_aliases

from pyngrok import ngrok, process, conf, installer
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokNgrokHTTPError, PyngrokNgrokURLError, PyngrokSecurityError, PyngrokError
from .testcase import NgrokTestCase

install_aliases()

from urllib.parse import urlparse
from urllib.request import urlopen

try:
    from http import HTTPStatus as StatusCodes
except ImportError:
    try:
        from http import client as StatusCodes
    except ImportError:
        import httplib as StatusCodes

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "5.0.0"


class TestNgrok(NgrokTestCase):
    @mock.patch("subprocess.call")
    def test_run(self, mock_call):
        # WHEN
        ngrok.run()

        # THEN
        mock_call.assert_called_once()

    @mock.patch("subprocess.call")
    def test_main(self, mock_call):
        # WHEN
        ngrok.main()

        # THEN
        mock_call.assert_called_once()

    def test_connect(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)

        # WHEN
        ngrok_tunnel = ngrok.connect(5000, pyngrok_config=self.pyngrok_config)
        current_process = ngrok.get_ngrok_process()

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertTrue(current_process._monitor_thread.is_alive())
        self.assertIsNotNone(ngrok_tunnel.name)
        self.assertIsNotNone(ngrok_tunnel.public_url)
        self.assertIsNotNone(process.get_process(self.pyngrok_config))
        self.assertIn('http://', ngrok_tunnel.public_url)
        self.assertEqual(len(process._current_processes.keys()), 1)

    def test_multiple_connections_fails(self):
        # WHEN
        with self.assertRaises(PyngrokNgrokHTTPError) as cm:
            ngrok.connect(5000, pyngrok_config=self.pyngrok_config)
            time.sleep(1)
            ngrok.connect(5001, pyngrok_config=self.pyngrok_config)
            time.sleep(1)

        # THEN
        self.assertEqual(502, cm.exception.status_code)
        self.assertIn("account may not run more than 2 tunnels", str(cm.exception))

    def test_get_tunnels(self):
        # GIVEN
        url = ngrok.connect(pyngrok_config=self.pyngrok_config).public_url
        time.sleep(1)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)

        # WHEN
        tunnels = ngrok.get_tunnels()
        self.assertEqual(len(ngrok._current_tunnels.keys()), 2)

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 2)
        self.assertEqual(len(tunnels), 2)
        for tunnel in tunnels:
            if tunnel.proto == "http":
                self.assertEqual(tunnel.public_url, url)
                self.assertEqual(tunnel.config["addr"], "http://localhost:80")
            else:
                self.assertEqual(tunnel.proto, "https")
                self.assertEqual(tunnel.public_url, url.replace("http", "https"))
                self.assertEqual(tunnel.config["addr"], "http://localhost:80")

    def test_bind_tls_https(self):
        # WHEN
        url = ngrok.connect(pyngrok_config=self.pyngrok_config, options={"bind_tls": True}).public_url

        # THEN
        self.assertTrue(url.startswith("https"))

    def test_disconnect(self):
        # GIVEN
        url = ngrok.connect(pyngrok_config=self.pyngrok_config).public_url
        time.sleep(1)
        tunnels = ngrok.get_tunnels()
        # Two tunnels, as one each was created for "http" and "https"
        self.assertEqual(len(ngrok._current_tunnels.keys()), 2)
        self.assertEqual(len(tunnels), 2)

        # WHEN
        ngrok.disconnect(url)
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        time.sleep(1)
        tunnels = ngrok.get_tunnels()

        # THEN
        # There is still one tunnel left, as we only disconnected the http tunnel
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)
        self.assertEqual(len(tunnels), 1)

    def test_kill(self):
        # GIVEN
        ngrok.connect(5000, pyngrok_config=self.pyngrok_config)
        time.sleep(1)
        ngrok_process = process.get_process(self.pyngrok_config)
        monitor_thread = ngrok_process._monitor_thread
        self.assertEqual(len(ngrok._current_tunnels.keys()), 1)

        # WHEN
        ngrok.kill()
        time.sleep(1)

        # THEN
        self.assertEqual(len(ngrok._current_tunnels.keys()), 0)
        self.assertIsNotNone(ngrok_process.proc.poll())
        self.assertFalse(monitor_thread.is_alive())
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertNoZombies()

    def test_set_auth_token(self):
        # WHEN
        ngrok.set_auth_token("807ad30a-73be-48d8", pyngrok_config=self.pyngrok_config)
        with open(self.pyngrok_config.config_path, "r") as f:
            contents = f.read()

        # THEN
        self.assertIn("807ad30a-73be-48d8", contents)

    def test_api_get_request_success(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        ngrok.connect()
        time.sleep(1)
        tunnel = ngrok.get_tunnels()[0]

        # WHEN
        response = ngrok.api_request("{}{}".format(current_process.api_url, tunnel.uri), "GET")

        # THEN
        self.assertEqual(tunnel.name, response["name"])

    def test_api_request_query_params(self):
        # GIVEN
        tunnel_name = "tunnel (1)"
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        public_url = ngrok.connect(urlparse(current_process.api_url).port, name=tunnel_name,
                                   options={"bind_tls": True}).public_url
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
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        ngrok.connect()
        time.sleep(1)
        tunnels = ngrok.get_tunnels()
        self.assertEqual(len(tunnels), 2)

        # WHEN
        response = ngrok.api_request("{}{}".format(current_process.api_url, tunnels[0].uri),
                                     "DELETE")

        # THEN
        self.assertIsNone(response)
        tunnels = ngrok.get_tunnels()
        self.assertEqual(len(tunnels), 1)

    def test_api_request_fails(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        bad_options = {
            "name": str(uuid.uuid4()),
            "addr": "8080",
            "proto": "invalid-proto"
        }

        # WHEN
        with self.assertRaises(PyngrokNgrokHTTPError) as cm:
            ngrok.api_request("{}/api/tunnels".format(current_process.api_url), "POST", data=bad_options)

        # THEN
        self.assertEqual(StatusCodes.BAD_REQUEST, cm.exception.status_code)
        self.assertIn("invalid tunnel configuration", str(cm.exception))
        self.assertIn("protocol name", str(cm.exception))

    def test_api_request_timeout(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        ngrok.connect()
        time.sleep(1)
        tunnels = ngrok.get_tunnels()

        # WHEN
        with self.assertRaises(PyngrokNgrokURLError) as cm:
            ngrok.api_request("{}{}".format(current_process.api_url, tunnels[0].uri), "DELETE",
                              timeout=0.0001)

        # THEN
        self.assertIn("timed out", cm.exception.reason)

    def test_api_request_security_error(self):
        # WHEN
        with self.assertRaises(PyngrokSecurityError):
            ngrok.api_request("file:{}".format(__file__))

    def test_regional_tcp(self):
        if "NGROK_AUTHTOKEN" not in os.environ:
            self.skipTest("NGROK_AUTHTOKEN environment variable not set")

        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        subdomain = "pyngrok-{}-{}-{}{}-tcp".format(platform.system(), platform.python_implementation(),
                                                    sys.version_info[0], sys.version_info[1]).lower()
        pyngrok_config = PyngrokConfig(config_path=conf.DEFAULT_NGROK_CONFIG_PATH,
                                       auth_token=os.environ["NGROK_AUTHTOKEN"], region="au")

        # WHEN
        url = ngrok.connect(5000, "tcp", options={"subdomain": subdomain}, pyngrok_config=pyngrok_config).public_url
        current_process = ngrok.get_ngrok_process()

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertIsNotNone(url)
        self.assertIsNotNone(process.get_process(pyngrok_config))
        self.assertIn("tcp://", url)
        self.assertIn(".au.", url)
        self.assertEqual(len(process._current_processes.keys()), 1)

    def test_regional_subdomain(self):
        if "NGROK_AUTHTOKEN" not in os.environ:
            self.skipTest("NGROK_AUTHTOKEN environment variable not set")

        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        subdomain = "pyngrok-{}-{}-{}{}-http".format(platform.system(), platform.python_implementation(),
                                                     sys.version_info[0], sys.version_info[1]).lower()
        pyngrok_config = PyngrokConfig(config_path=conf.DEFAULT_NGROK_CONFIG_PATH,
                                       auth_token=os.environ["NGROK_AUTHTOKEN"], region="au")

        # WHEN
        url = ngrok.connect(5000, options={"subdomain": subdomain}, pyngrok_config=pyngrok_config).public_url
        current_process = ngrok.get_ngrok_process()

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertIsNotNone(url)
        self.assertIsNotNone(process.get_process(pyngrok_config))
        self.assertIn("http://", url)
        self.assertIn(".au.", url)
        self.assertIn(subdomain, url)
        self.assertEqual(len(process._current_processes.keys()), 1)

    def test_web_addr_false_not_allowed(self):
        # GIVEN
        with open(self.pyngrok_config.config_path, "w") as config_file:
            yaml.dump({"web_addr": False}, config_file)

        # WHEN
        with self.assertRaises(PyngrokError) as e:
            ngrok.connect(pyngrok_config=self.pyngrok_config)

    def test_log_format_json_not_allowed(self):
        # GIVEN
        with open(self.pyngrok_config.config_path, "w") as config_file:
            yaml.dump({"log_format": "json"}, config_file)

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(pyngrok_config=self.pyngrok_config)

    def test_log_level_warn_not_allowed(self):
        # GIVEN
        with open(self.pyngrok_config.config_path, "w") as config_file:
            yaml.dump({"log_level": "warn"}, config_file)

        # WHEN
        with self.assertRaises(PyngrokError):
            ngrok.connect(pyngrok_config=self.pyngrok_config)

    def test_connect_fileserver(self):
        if "NGROK_AUTHTOKEN" not in os.environ:
            self.skipTest("NGROK_AUTHTOKEN environment variable not set")

        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = PyngrokConfig(config_path=conf.DEFAULT_NGROK_CONFIG_PATH,
                                       auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        url = ngrok.connect("file:///", pyngrok_config=pyngrok_config).public_url
        current_process = ngrok.get_ngrok_process()
        time.sleep(1)
        tunnels = ngrok.get_tunnels()

        # THEN
        self.assertEqual(len(tunnels), 2)
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertTrue(current_process._monitor_thread.is_alive())
        self.assertIsNotNone(url)
        self.assertIsNotNone(process.get_process(self.pyngrok_config))
        self.assertIn('http://', url)
        self.assertEqual(len(process._current_processes.keys()), 1)

        # WHEN
        ngrok.disconnect(url)
        time.sleep(1)
        tunnels = ngrok.get_tunnels()

        # THEN
        # There is still one tunnel left, as we only disconnected the http tunnel
        self.assertEqual(len(tunnels), 1)

    def test_disconnect_fileserver(self):
        if "NGROK_AUTHTOKEN" not in os.environ:
            self.skipTest("NGROK_AUTHTOKEN environment variable not set")

        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = PyngrokConfig(config_path=conf.DEFAULT_NGROK_CONFIG_PATH,
                                       auth_token=os.environ["NGROK_AUTHTOKEN"])
        url = ngrok.connect("file:///", pyngrok_config=pyngrok_config).public_url
        time.sleep(1)
        tunnel = ngrok.get_tunnels()[0]
        api_url = ngrok.get_ngrok_process(pyngrok_config).api_url

        # WHEN
        ngrok.disconnect(url)
        time.sleep(1)
        tunnels = ngrok.get_tunnels()

        # THEN
        # There is still one tunnel left, as we only disconnected the http tunnel
        self.assertEqual(len(tunnels), 1)

    def test_get_tunnel_fileserver(self):
        if "NGROK_AUTHTOKEN" not in os.environ:
            self.skipTest("NGROK_AUTHTOKEN environment variable not set")

        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)
        pyngrok_config = PyngrokConfig(config_path=conf.DEFAULT_NGROK_CONFIG_PATH,
                                       auth_token=os.environ["NGROK_AUTHTOKEN"])
        ngrok.connect("file:///", pyngrok_config=pyngrok_config)
        time.sleep(1)
        tunnel = ngrok.get_tunnels()[0]
        api_url = ngrok.get_ngrok_process(pyngrok_config).api_url

        # WHEN
        response = ngrok.api_request("{}{}".format(api_url, tunnel.uri), "GET")

        # THEN
        self.assertEqual(tunnel.name, response["name"])
        self.assertIn("file", tunnel.name)

    def test_ngrok_tunnel_refresh_metrics(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        ngrok_tunnel = ngrok.connect(urlparse(current_process.api_url).port, options={"bind_tls": True})
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

    def test_version(self):
        # WHEN
        ngrok_version, pyngrok_version = ngrok.get_version()

        # THEN
        self.assertIsNotNone(ngrok_version)
        self.assertEqual(ngrok.__version__, pyngrok_version)

    def test_tunnel_definitions(self):
        if "NGROK_AUTHTOKEN" not in os.environ:
            self.skipTest("NGROK_AUTHTOKEN environment variable not set")

        # GIVEN
        config = {
            "tunnels": {
                "config-tunnel": {
                    "proto": "http",
                    "addr": "8000",
                    "subdomain": "pyngrok1"
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config2.yml")
        installer.install_default_config(config_path, config)
        pyngrok_config = PyngrokConfig(config_path=config_path,
                                       auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        ngrok_tunnel = ngrok.connect(name="config-tunnel", pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(ngrok_tunnel.name, "config-tunnel (http)")
        self.assertEqual(ngrok_tunnel.config["addr"],
                         "http://localhost:{}".format(config["tunnels"]["config-tunnel"]["addr"]))
        self.assertEqual(ngrok_tunnel.proto, config["tunnels"]["config-tunnel"]["proto"])
        self.assertEqual(ngrok_tunnel.public_url,
                         "http://{}.ngrok.io".format(config["tunnels"]["config-tunnel"]["subdomain"]))

    def test_tunnel_definitions_pyngrok_default(self):
        if "NGROK_AUTHTOKEN" not in os.environ:
            self.skipTest("NGROK_AUTHTOKEN environment variable not set")

        # GIVEN
        config = {
            "tunnels": {
                "pyngrok-default": {
                    "proto": "http",
                    "addr": "8080",
                    "subdomain": "pyngrok2"
                }
            }
        }
        config_path = os.path.join(self.config_dir, "config2.yml")
        installer.install_default_config(config_path, config)
        pyngrok_config = PyngrokConfig(config_path=config_path,
                                       auth_token=os.environ["NGROK_AUTHTOKEN"])

        # WHEN
        ngrok_tunnel = ngrok.connect(pyngrok_config=pyngrok_config)

        # THEN
        self.assertEqual(ngrok_tunnel.name, "pyngrok-default (http)")
        self.assertEqual(ngrok_tunnel.config["addr"],
                         "http://localhost:{}".format(config["tunnels"]["pyngrok-default"]["addr"]))
        self.assertEqual(ngrok_tunnel.proto, config["tunnels"]["pyngrok-default"]["proto"])
        self.assertEqual(ngrok_tunnel.public_url,
                         "http://{}.ngrok.io".format(config["tunnels"]["pyngrok-default"]["subdomain"]))
