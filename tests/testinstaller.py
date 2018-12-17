import os

from pyngrok import ngrok
from .testcase import NgrokTestCase


class TestNgrok(NgrokTestCase):
    def test_installer(self):
        # GIVEN
        if os.path.exists(ngrok.DEFAULT_NGROK_PATH):
            os.remove(ngrok.DEFAULT_NGROK_PATH)
        self.assertFalse(os.path.exists(ngrok.DEFAULT_NGROK_PATH))

        # WHEN
        ngrok.connect(5000)

        # THEN
        self.assertTrue(os.path.exists(ngrok.DEFAULT_NGROK_PATH))
