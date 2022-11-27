import os
import socket
from unittest import mock

from pyngrok import ngrok, installer
from pyngrok.exception import PyngrokNgrokInstallError, PyngrokSecurityError, PyngrokError
from tests.testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2022, Alex Laird"
__version__ = "5.2.0"


class TestInstaller(NgrokTestCase):
    def test_installer_v2(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v2.ngrok_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v2.ngrok_path))

        # WHEN
        ngrok.connect(pyngrok_config=self.pyngrok_config_v2)
        ngrok.kill(self.pyngrok_config_v2)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=self.pyngrok_config_v2)

        # THEN
        self.assertTrue(os.path.exists(self.pyngrok_config_v2.ngrok_path))
        self.assertTrue(ngrok_version.startswith("2"))

    def test_installer_v3(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v3.ngrok_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v3.ngrok_path))

        # WHEN
        ngrok.connect(pyngrok_config=self.pyngrok_config_v3)
        ngrok.kill(pyngrok_config=self.pyngrok_config_v3)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertTrue(os.path.exists(self.pyngrok_config_v3.ngrok_path))
        self.assertTrue(ngrok_version.startswith("3"))

    def test_config_provisioned(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v2.config_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v2.config_path))

        # WHEN
        ngrok.connect(pyngrok_config=self.pyngrok_config_v2)

        # THEN
        self.assertTrue(os.path.exists(self.pyngrok_config_v2.config_path))

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

        self.given_file_doesnt_exist(self.pyngrok_config_v2.ngrok_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v2.ngrok_path))

        # WHEN
        with self.assertRaises(PyngrokNgrokInstallError):
            ngrok.connect(pyngrok_config=self.pyngrok_config_v2)

        # THEN
        self.assertFalse(os.path.exists(self.pyngrok_config_v2.ngrok_path))

    @mock.patch("pyngrok.installer.urlopen")
    def test_installer_retry(self, mock_urlopen):
        # GIVEN
        mock_urlopen.side_effect = socket.timeout("The read operation timed out")

        self.given_file_doesnt_exist(self.pyngrok_config_v2.ngrok_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v2.ngrok_path))

        # WHEN
        with self.assertRaises(PyngrokNgrokInstallError):
            ngrok.connect(pyngrok_config=self.pyngrok_config_v2)

        # THEN
        self.assertEqual(mock_urlopen.call_count, 4)
        self.assertFalse(os.path.exists(self.pyngrok_config_v2.ngrok_path))

    def test_download_file_security_error(self):
        # WHEN
        with self.assertRaises(PyngrokSecurityError):
            installer._download_file("file:{}".format(__file__), retries=10)

    def test_web_addr_false_not_allowed(self):
        # WHEN
        with self.assertRaises(PyngrokError):
            installer.install_default_config(self.pyngrok_config_v2.config_path, {"web_addr": False})
