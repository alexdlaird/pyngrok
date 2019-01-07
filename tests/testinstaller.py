import os

from mock import mock

from pyngrok import ngrok
from pyngrok.exception import PyngrokNgrokInstallError
from .testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "1.1.3"


class TestNgrok(NgrokTestCase):
    def test_installer(self):
        # GIVEN
        if os.path.exists(ngrok.DEFAULT_NGROK_PATH):
            os.remove(ngrok.DEFAULT_NGROK_PATH)
        self.assertFalse(os.path.exists(ngrok.DEFAULT_NGROK_PATH))

        # WHEN
        ngrok.connect(config_path=self.config_path)

        # THEN
        self.assertTrue(os.path.exists(ngrok.DEFAULT_NGROK_PATH))

    @mock.patch("pyngrok.installer.urlopen")
    def test_installer_download_fails(self, mock_urlopen):
        # GIVEN
        magic_mock = mock.MagicMock()
        magic_mock.getcode.return_value = 500
        mock_urlopen.return_value = magic_mock

        if os.path.exists(ngrok.DEFAULT_NGROK_PATH):
            os.remove(ngrok.DEFAULT_NGROK_PATH)
        self.assertFalse(os.path.exists(ngrok.DEFAULT_NGROK_PATH))

        # WHEN
        with self.assertRaises(PyngrokNgrokInstallError):
            ngrok.connect(config_path=self.config_path)

        # THEN
        self.assertFalse(os.path.exists(ngrok.DEFAULT_NGROK_PATH))
