import os
import socket
import unittest
from unittest import mock

from pyngrok import ngrok, installer, conf
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokNgrokInstallError, PyngrokSecurityError, PyngrokError
from tests.testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "6.1.0"


class TestInstaller(NgrokTestCase):
    @unittest.skipIf("NGROK_AUTHTOKEN" not in os.environ, "NGROK_AUTHTOKEN environment variable not set")
    def test_installer_v2(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v2.ngrok_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v2.ngrok_path))

        # WHEN
        ngrok.set_auth_token(os.environ["NGROK_AUTHTOKEN"], self.pyngrok_config_v2)
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

    def test_installer_default(self):
        # GIVEN
        ngrok_path = os.path.join(conf.BIN_DIR, "default", installer.get_ngrok_bin())
        config_path = os.path.join(self.config_dir, "config_default.yml")

        pyngrok_config = PyngrokConfig(
            ngrok_path=ngrok_path,
            config_path=config_path)
        self.given_file_doesnt_exist(pyngrok_config.ngrok_path)
        self.assertFalse(os.path.exists(pyngrok_config.ngrok_path))

        # WHEN
        ngrok.connect(pyngrok_config=pyngrok_config)
        ngrok.kill(pyngrok_config)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=pyngrok_config)

        # THEN
        self.assertTrue(os.path.exists(pyngrok_config.ngrok_path))
        self.assertTrue(ngrok_version.startswith("3"))

    def test_config_provisioned(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v3.config_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v3.config_path))

        # WHEN
        ngrok.connect(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertTrue(os.path.exists(self.pyngrok_config_v3.config_path))

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

        self.given_file_doesnt_exist(self.pyngrok_config_v3.ngrok_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v3.ngrok_path))

        # WHEN
        with self.assertRaises(PyngrokNgrokInstallError):
            ngrok.connect(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertFalse(os.path.exists(self.pyngrok_config_v3.ngrok_path))

    @mock.patch("pyngrok.installer.urlopen")
    def test_installer_retry(self, mock_urlopen):
        # GIVEN
        mock_urlopen.side_effect = socket.timeout("The read operation timed out")

        self.given_file_doesnt_exist(self.pyngrok_config_v3.ngrok_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v3.ngrok_path))

        # WHEN
        with self.assertRaises(PyngrokNgrokInstallError):
            ngrok.connect(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertEqual(mock_urlopen.call_count, 4)
        self.assertFalse(os.path.exists(self.pyngrok_config_v3.ngrok_path))

    def test_download_file_security_error(self):
        # WHEN
        with self.assertRaises(PyngrokSecurityError):
            installer._download_file("file:{}".format(__file__), retries=10)

    def test_web_addr_false_not_allowed(self):
        # WHEN
        with self.assertRaises(PyngrokError):
            installer.install_default_config(self.pyngrok_config_v3.config_path, {"web_addr": False})
