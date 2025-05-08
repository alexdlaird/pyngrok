__copyright__ = "Copyright (c) 2018-2025 Alex Laird"
__license__ = "MIT"

import os
import time
import unittest
from urllib.parse import urlparse
from urllib.request import urlopen

from pyngrok import ngrok, agent
from tests.testcase import NgrokTestCase


class TestAgent(NgrokTestCase):
    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_captured_requests(self):
        # GIVEN
        tunnel_name = "my-tunnel"
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        public_url = ngrok.connect(urlparse(current_process.api_url).port, name=tunnel_name,
                                   pyngrok_config=self.pyngrok_config_v3).public_url
        time.sleep(1)

        urlopen(f"{public_url}/api/status").read()
        time.sleep(3)

        # WHEN
        response1 = agent.get_requests(pyngrok_config=self.pyngrok_config_v3)
        response2 = agent.get_requests({"tunnel_name": "unknown-tunnel"}, self.pyngrok_config_v3)

        # THEN
        self.assertEqual(1, len(response1))
        self.assertIsNotNone(1, len(response1[0].uri))
        self.assertIsNotNone(response1[0].id)
        self.assertIsNotNone(response1[0].uri)
        self.assertIsNotNone(response1[0].duration)
        self.assertIsNotNone(response1[0].request)
        self.assertIsNotNone(response1[0].response)
        self.assertEqual(tunnel_name, response1[0].tunnel_name)
        self.assertEqual(0, len(response2))

        # WHEN
        response3 = agent.get_request(response1[0].id, pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertEqual(response3.id, response3.id)
        self.assertEqual(response3.uri, response3.uri)
        self.assertEqual(response3.duration, response3.duration)
        self.assertEqual(response3.request, response3.request)
        self.assertEqual(response3.response, response3.response)
        self.assertEqual(tunnel_name, response3.tunnel_name)

        # WHEN
        agent.replay_request(response1[0].id, pyngrok_config=self.pyngrok_config_v3)
        response4 = sorted(agent.get_requests(pyngrok_config=self.pyngrok_config_v3), key=lambda x: x.id)

        # THEN
        self.assertEqual(2, len(response4))
        self.assertEqual(response1[0].id, response4[0].id)
        self.assertEqual(response1[0].uri, response4[0].uri)
        self.assertEqual(response1[0].duration, response4[0].duration)
        self.assertIsNotNone(response4[0].request)
        self.assertIsNotNone(response4[0].response)
        self.assertEqual(tunnel_name, response4[0].tunnel_name)
        self.assertNotEqual(response1[0].id, response4[1].id)
        self.assertNotEqual(response1[0].uri, response4[1].uri)
        self.assertNotEqual(response1[0].duration, response4[1].duration)
        self.assertIsNotNone(response4[1].request)
        self.assertIsNotNone(response4[1].response)
        self.assertEqual(tunnel_name, response4[1].tunnel_name)

        # WHEN
        agent.delete_requests(pyngrok_config=self.pyngrok_config_v3)
        response5 = agent.get_requests(pyngrok_config=self.pyngrok_config_v3)

        self.assertEqual(0, len(response5))

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_get_agent_status(self):
        # GIVEN
        ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        time.sleep(1)

        response = agent.get_agent_status(self.pyngrok_config_v3)

        # THEN
        self.assertEqual("online", response.status)
        self.assertIsNotNone(response.agent_version)
        self.assertIsNotNone(response.uri)
