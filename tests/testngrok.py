import time

from pyngrok import ngrok, process
from pyngrok.exception import PyngrokNgrokHTTPError
from .testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "1.1.3"


class TestNgrok(NgrokTestCase):
    def test_connect(self):
        # GIVEN
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 0)

        # WHEN
        url = ngrok.connect(5000, config_path=self.config_path)
        current_process = ngrok.get_ngrok_process()

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.process.poll())
        self.assertIsNotNone(url)
        self.assertIsNotNone(process.get_process(ngrok.DEFAULT_NGROK_PATH))

    def test_multiple_connections_fails(self):
        # WHEN
        with self.assertRaises(PyngrokNgrokHTTPError) as cm:
            ngrok.connect(5000, config_path=self.config_path)
            time.sleep(1)
            ngrok.connect(5001, config_path=self.config_path)
            time.sleep(1)

        # THEN
        self.assertIn("account may not run more than 2 tunnels", cm.exception.args[0].read().decode("utf-8"))

    def test_get_tunnels(self):
        # GIVEN
        url = ngrok.connect(config_path=self.config_path)
        time.sleep(1)

        # WHEN
        tunnels = ngrok.get_tunnels()

        # THEN
        self.assertEqual(len(tunnels), 2)
        for tunnel in tunnels:
            if tunnel.proto == "http":
                self.assertEqual(tunnel.public_url, url)
                self.assertEqual(tunnel.config["addr"], "localhost:80")
            else:
                self.assertEqual(tunnel.proto, "https")
                self.assertEqual(tunnel.public_url, url.replace("http", "https"))
                self.assertEqual(tunnel.config["addr"], "localhost:80")

    def test_disconnect(self):
        # GIVEN
        url = ngrok.connect(config_path=self.config_path)
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
        ngrok.connect(5000, config_path=self.config_path)
        time.sleep(1)
        p1 = process.get_process(ngrok.DEFAULT_NGROK_PATH).process

        # WHEN
        ngrok.kill()
        time.sleep(1)

        # THEN
        self.assertIsNotNone(p1.poll())
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 0)

    def test_set_auth_token(self):
        # WHEN
        ngrok.set_auth_token("807ad30a-73be-48d8", config_path=self.config_path)
        contents = open(self.config_path, "r").read()

        # THEN
        self.assertIn("807ad30a-73be-48d8", contents)
