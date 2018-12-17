import time

from pyngrok import ngrok, process
from .testcase import NgrokTestCase


class TestNgrok(NgrokTestCase):
    def test_connect(self):
        # GIVEN
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 0)

        # WHEN
        url = ngrok.connect(5000)
        current_process = ngrok.get_ngrok_process()

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.process.poll())
        self.assertIsNotNone(url)
        self.assertIsNotNone(process.get_process(ngrok.DEFAULT_NGROK_PATH))

    def test_multiple_connections_fails(self):
        # WHEN
        with self.assertRaises(Exception):
            ngrok.connect(5000)
            # time.sleep(1)
            ngrok.connect(5001)
            # time.sleep(1)

    def test_get_tunnels(self):
        # GIVEN
        url = ngrok.connect()
        time.sleep(1)

        # WHEN
        tunnels = ngrok.get_tunnels()

        # THEN
        self.assertEqual(len(tunnels), 2)
        for tunnel in tunnels:
            if tunnel["proto"] == "http":
                self.assertEqual(tunnels[0]["public_url"], url)
                self.assertEqual(tunnels[0]["config"]["addr"], "localhost:80")
            else:
                self.assertEqual(tunnels[1]["proto"], "https")
                self.assertEqual(tunnels[1]["public_url"], url.replace("http", "https"))
                self.assertEqual(tunnels[1]["config"]["addr"], "localhost:80")

    def test_disconnect(self):
        # GIVEN
        url = ngrok.connect()
        time.sleep(1)
        tunnels = ngrok.get_tunnels()
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
        ngrok.connect(5000)
        time.sleep(1)
        p1 = process.get_process(ngrok.DEFAULT_NGROK_PATH).process

        # WHEN
        ngrok.kill()
        time.sleep(1)

        # THEN
        self.assertIsNotNone(p1.poll())
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 0)
