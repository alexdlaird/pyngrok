__copyright__ = "Copyright (c) 2018-2025 Alex Laird"
__license__ = "MIT"

import os
from unittest import mock

from pyngrok.conf import PyngrokConfig
from tests.testcase import NgrokTestCase


class TestConf(NgrokTestCase):
    def test_auth_token_set_from_env(self):
        # GIVEN
        ngrok_auth_token = "some-auth-token"

        # WHEN
        with mock.patch.dict(os.environ, {"NGROK_AUTHTOKEN": ngrok_auth_token}):
            pyngrok_config = PyngrokConfig()

        # THEN
        self.assertEqual(ngrok_auth_token, pyngrok_config.auth_token)

    def test_api_key_set_from_env(self):
        # GIVEN
        ngrok_api_key = "some-api-key"

        # WHEN
        with mock.patch.dict(os.environ, {"NGROK_API_KEY": ngrok_api_key}):
            pyngrok_config = PyngrokConfig()

        # THEN
        self.assertEqual(ngrok_api_key, pyngrok_config.api_key)
