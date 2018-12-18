import os

from pyngrok import ngrok
from .testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "1.0.0"


class TestNgrok(NgrokTestCase):
    def test_installer(self):
        # GIVEN
        if os.path.exists(ngrok.DEFAULT_NGROK_PATH):
            os.remove(ngrok.DEFAULT_NGROK_PATH)
        self.assertFalse(os.path.exists(ngrok.DEFAULT_NGROK_PATH))

        # WHEN
        ngrok.connect(5000, config_path=self.config_path)

        # THEN
        self.assertTrue(os.path.exists(ngrok.DEFAULT_NGROK_PATH))
