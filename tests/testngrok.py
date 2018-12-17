import time

from pyngrok import ngrok, process
from .testcase import NgrokTestCase


class TestNgrok(NgrokTestCase):
    def test_connect(self):
        # GIVEN
        self.assertIsNone(process.process)

        # WHEN
        url = ngrok.connect(5000)
        p1 = process.get_process()[0]

        # THEN
        self.assertIsNone(p1.poll())
        self.assertIsNotNone(url)
        self.assertIsNotNone(process.process)
        self.assertIsNotNone(process.get_process())

    def test_multiple_connections_fails(self):
        # WHEN
        with self.assertRaises(Exception):
            ngrok.connect(5000)
            time.sleep(1)
            ngrok.connect(5001)
            time.sleep(1)

    def test_get_tunnels(self):
        # GIVEN
        url = ngrok.connect()
        time.sleep(1)

        # WHEN
        tunnels = ngrok.get_tunnels()

        # THEN
        self.assertTrue(len(tunnels), 1)
        self.assertTrue(tunnels[0]["proto"], "http")
        self.assertTrue(tunnels[0]["public_url"], url)
        self.assertTrue(tunnels[0]["config"]["addr"], "localhost:80")

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
        p1 = process.get_process()[0]

        # WHEN
        ngrok.kill()
        time.sleep(1)

        # THEN
        self.assertIsNotNone(p1.poll())
        self.assertIsNone(process.process)
