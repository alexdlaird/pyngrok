__copyright__ = "Copyright (c) 2018-2024 Alex Laird"
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
        self.assertTrue(ngrok_auth_token, pyngrok_config.auth_token)
