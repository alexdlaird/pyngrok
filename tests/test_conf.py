__copyright__ = "Copyright (c) 2018-2025 Alex Laird"
__license__ = "MIT"

import os
import unittest

from pyngrok.conf import PyngrokConfig
from tests.testcase import NgrokTestCase


class TestConf(NgrokTestCase):
    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_auth_token_set_from_env(self):
        # GIVEN
        ngrok_auth_token = os.environ["NGROK_AUTHTOKEN"]

        # WHEN
        pyngrok_config = PyngrokConfig()

        # THEN
        self.assertEqual(ngrok_auth_token, pyngrok_config.auth_token)

    @unittest.skipIf(not os.environ.get("NGROK_API_KEY"), "NGROK_API_KEY environment variable not set")
    def test_api_key_set_from_env(self):
        # GIVEN
        ngrok_api_key = os.environ["NGROK_API_KEY"]

        # WHEN
        pyngrok_config = PyngrokConfig()

        # THEN
        self.assertEqual(ngrok_api_key, pyngrok_config.api_key)
