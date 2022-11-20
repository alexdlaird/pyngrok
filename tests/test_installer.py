import os
import socket
from unittest import mock

from pyngrok import ngrok, installer, conf
from pyngrok.exception import PyngrokNgrokInstallError, PyngrokSecurityError, PyngrokError
from tests.testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2022, Alex Laird"
__version__ = "5.2.0"


class TestInstaller(NgrokTestCase):
    def test_installer(self):
        # GIVEN
        if os.path.exists(conf.DEFAULT_NGROK_PATH):
            os.remove(conf.DEFAULT_NGROK_PATH)
        self.assertFalse(os.path.exists(conf.DEFAULT_NGROK_PATH))

        # WHEN
        ngrok.connect(pyngrok_config=self.pyngrok_config)
        ngrok.kill(self.pyngrok_config)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=self.pyngrok_config)

        # THEN
        self.assertTrue(os.path.exists(conf.DEFAULT_NGROK_PATH))
        self.assertTrue(ngrok_version.startswith("3"))

    def test_installer_v2(self):
        # GIVEN
        if os.path.exists(conf.DEFAULT_NGROK_PATH):
            os.remove(conf.DEFAULT_NGROK_PATH)
        self.assertFalse(os.path.exists(conf.DEFAULT_NGROK_PATH))
        pyngrok_config = self.copy_with_updates(self.pyngrok_config, ngrok_version="2")

        # WHEN
        ngrok.connect(pyngrok_config=pyngrok_config)
        ngrok.kill(self.pyngrok_config)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=pyngrok_config)

        # THEN
        self.assertTrue(os.path.exists(conf.DEFAULT_NGROK_PATH))
        self.assertTrue(ngrok_version.startswith("2"))

    def test_config_provisioned(self):
        # GIVEN
        if os.path.exists(self.pyngrok_config.config_path):
            os.remove(self.pyngrok_config.config_path)
        self.assertFalse(os.path.exists(self.pyngrok_config.config_path))

        # WHEN
        ngrok.connect(pyngrok_config=self.pyngrok_config)

        # THEN
        self.assertTrue(os.path.exists(self.pyngrok_config.config_path))

    ################################################################################
    # Tests below this point don't need to start a long-lived ngrok process, they
    # are asserting on pyngrok-specific code or edge cases.
    ################################################################################

    @mock.patch("pyngrok.installer.urlopen")
    def test_installer_download_fails(self, mock_urlopen):
        # GIVEN
        magic_mock = mock.MagicMock()
        magic_mock.getcode.return_value = 500
        mock_urlopen.return_value = magic_mock

        if os.path.exists(conf.DEFAULT_NGROK_PATH):
            os.remove(conf.DEFAULT_NGROK_PATH)
        self.assertFalse(os.path.exists(conf.DEFAULT_NGROK_PATH))

        # WHEN
        with self.assertRaises(PyngrokNgrokInstallError):
            ngrok.connect(pyngrok_config=self.pyngrok_config)

        # THEN
        self.assertFalse(os.path.exists(conf.DEFAULT_NGROK_PATH))

    @mock.patch("pyngrok.installer.urlopen")
    def test_installer_retry(self, mock_urlopen):
        # GIVEN
        mock_urlopen.side_effect = socket.timeout("The read operation timed out")

        if os.path.exists(conf.DEFAULT_NGROK_PATH):
            os.remove(conf.DEFAULT_NGROK_PATH)
        self.assertFalse(os.path.exists(conf.DEFAULT_NGROK_PATH))

        # WHEN
        with self.assertRaises(PyngrokNgrokInstallError):
            ngrok.connect(pyngrok_config=self.pyngrok_config)

        # THEN
        self.assertEqual(mock_urlopen.call_count, 4)
        self.assertFalse(os.path.exists(conf.DEFAULT_NGROK_PATH))

    def test_download_file_security_error(self):
        # WHEN
        with self.assertRaises(PyngrokSecurityError):
            installer._download_file("file:{}".format(__file__), retries=10)

    def test_web_addr_false_not_allowed(self):
        # WHEN
        with self.assertRaises(PyngrokError):
            installer.install_default_config(self.pyngrok_config.config_path, {"web_addr": False})
