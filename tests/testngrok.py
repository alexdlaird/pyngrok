import os
import platform
import sys
import time
import uuid

import mock

from pyngrok import ngrok, process
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokNgrokHTTPError, PyngrokNgrokURLError, PyngrokSecurityError
from .testcase import NgrokTestCase

try:
    from http import HTTPStatus as StatusCodes
except ImportError:
    try:
        from http import client as StatusCodes
    except ImportError:
        import httplib as StatusCodes

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "4.0.0"


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

        # WHEN
        url = ngrok.connect(5000, pyngrok_config=self.pyngrok_config)
        current_process = ngrok.get_ngrok_process()

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.proc.poll())
        self.assertTrue(current_process._monitor_thread.is_alive())
        self.assertIsNotNone(url)
        self.assertIsNotNone(process.get_process(self.pyngrok_config))
        self.assertIn('http://', url)
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
        url = ngrok.connect(pyngrok_config=self.pyngrok_config)
        time.sleep(1)

        # WHEN
        tunnels = ngrok.get_tunnels()

        # THEN
        self.assertEqual(len(tunnels), 2)
        for tunnel in tunnels:
            if tunnel.proto == "http":
                self.assertEqual(tunnel.public_url, url)
                self.assertEqual(tunnel.config["addr"], "http://localhost:80")
            else:
                self.assertEqual(tunnel.proto, "https")
                self.assertEqual(tunnel.public_url, url.replace("http", "https"))
                self.assertEqual(tunnel.config["addr"], "http://localhost:80")

    def test_disconnect(self):
        # GIVEN
        url = ngrok.connect(pyngrok_config=self.pyngrok_config)
        time.sleep(1)
        tunnels = ngrok.get_tunnels()
        # Two tunnels, as one each was created for "http" and "https"
        self.assertEqual(len(tunnels), 2)

        # WHEN
        ngrok.disconnect(url)
        time.sleep(1)
        tunnels = ngrok.get_tunnels()

        # THEN
        # There is still one tunnel left, as we only disconnected the http tunnel
        self.assertEqual(len(tunnels), 1)

    def test_kill(self):
        # GIVEN
        ngrok.connect(5000, pyngrok_config=self.pyngrok_config)
        time.sleep(1)
        ngrok_process = process.get_process(self.pyngrok_config)
        monitor_thread = ngrok_process._monitor_thread

        # WHEN
        ngrok.kill()
        time.sleep(1)

        # THEN
        self.assertIsNotNone(ngrok_process.proc.poll())
        self.assertFalse(monitor_thread.is_alive())
        self.assertEqual(len(process._current_processes.keys()), 0)

    def test_set_auth_token(self):
        # WHEN
        ngrok.set_auth_token("807ad30a-73be-48d8", pyngrok_config=self.pyngrok_config)
        contents = open(self.pyngrok_config.config_path, "r").read()

        # THEN
        self.assertIn("807ad30a-73be-48d8", contents)

    def test_api_get_request_success(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        ngrok.connect(pyngrok_config=self.pyngrok_config)
        time.sleep(1)
        tunnel = ngrok.get_tunnels()[0]

        # WHEN
        response = ngrok.api_request("{}{}".format(current_process.api_url, tunnel.uri.replace("+", "%20")), "GET")

        # THEN
        self.assertEqual(tunnel.name, response["name"])

    def test_api_request_delete_data_updated(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        ngrok.connect(pyngrok_config=self.pyngrok_config)
        time.sleep(1)
        tunnels = ngrok.get_tunnels()
        self.assertEqual(len(tunnels), 2)

        # WHEN
        response = ngrok.api_request("{}{}".format(current_process.api_url, tunnels[0].uri.replace("+", "%20")),
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
            ngrok.api_request("{}/api/{}".format(current_process.api_url, "tunnels"), "POST", data=bad_options)

        # THEN
        self.assertEqual(StatusCodes.BAD_REQUEST, cm.exception.status_code)
        self.assertIn("invalid tunnel configuration", str(cm.exception))
        self.assertIn("protocol name", str(cm.exception))

    def test_api_request_timeout(self):
        # GIVEN
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        ngrok.connect(pyngrok_config=self.pyngrok_config)
        time.sleep(1)
        tunnels = ngrok.get_tunnels()

        # WHEN
        with self.assertRaises(PyngrokNgrokURLError) as cm:
            ngrok.api_request("{}{}".format(current_process.api_url, tunnels[0].uri.replace("+", "%20")), "DELETE",
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
        pyngrok_config = PyngrokConfig(auth_token=os.environ["NGROK_AUTHTOKEN"], region="au")

        # WHEN
        url = ngrok.connect(5000, "tcp", options={"subdomain": subdomain}, pyngrok_config=pyngrok_config)
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
        pyngrok_config = PyngrokConfig(auth_token=os.environ["NGROK_AUTHTOKEN"], region="au")

        # WHEN
        url = ngrok.connect(5000, options={"subdomain": subdomain}, pyngrok_config=pyngrok_config)
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
