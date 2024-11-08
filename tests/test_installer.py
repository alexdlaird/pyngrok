__copyright__ = "Copyright (c) 2018-2024 Alex Laird"
__license__ = "MIT"

import os
import socket
from unittest import mock

from pyngrok import installer, ngrok
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokError, PyngrokNgrokInstallError, PyngrokSecurityError
from tests.testcase import NgrokTestCase


class TestInstaller(NgrokTestCase):
    def test_installer_v2(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v2.ngrok_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v2.ngrok_path))

        # WHEN
        installer.install_ngrok(self.pyngrok_config_v2.ngrok_path, self.pyngrok_config_v2.ngrok_version)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=self.pyngrok_config_v2)

        # THEN
        self.assertTrue(os.path.exists(self.pyngrok_config_v2.ngrok_path))
        self.assertTrue(ngrok_version.startswith("2"))

    def test_installer_v3(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v3.ngrok_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v3.ngrok_path))

        # WHEN
        installer.install_ngrok(self.pyngrok_config_v3.ngrok_path, self.pyngrok_config_v3.ngrok_version)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=self.pyngrok_config_v3)

        # THEN
        self.assertTrue(os.path.exists(self.pyngrok_config_v3.ngrok_path))
        self.assertTrue(ngrok_version.startswith("3"))

    def test_installer_default(self):
        # GIVEN
        ngrok_path = os.path.join(self.config_dir, "default", installer.get_ngrok_bin())
        config_path = os.path.join(self.config_dir, "config_default.yml")

        pyngrok_config = PyngrokConfig(
            ngrok_path=ngrok_path,
            config_path=config_path)
        self.given_file_doesnt_exist(pyngrok_config.ngrok_path)
        self.assertFalse(os.path.exists(pyngrok_config.ngrok_path))

        # WHEN
        installer.install_ngrok(pyngrok_config.ngrok_path, pyngrok_config.ngrok_version)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=pyngrok_config)

        # THEN
        self.assertTrue(os.path.exists(pyngrok_config.ngrok_path))
        self.assertTrue(ngrok_version.startswith("3"))

    def test_config_provisioned(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v3.config_path)
        self.assertFalse(os.path.exists(self.pyngrok_config_v3.config_path))

        # WHEN
        installer.install_default_config(self.pyngrok_config_v3.config_path, {}, self.pyngrok_config_v3.ngrok_version)

        # THEN
        self.assertTrue(os.path.exists(self.pyngrok_config_v3.config_path))

    def test_get_default_config(self):
        # GIVEN
        installer.install_default_config(self.pyngrok_config_v3.config_path, {}, self.pyngrok_config_v3.ngrok_version)

        # WHEN
        ngrok_config = installer.get_ngrok_config(self.pyngrok_config_v3.config_path)

        # THEN
        self.assertEqual(2, len(ngrok_config))
        self.assertEqual("2", ngrok_config["version"])
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
            installer._download_file(f"file:{__file__}", retries=10)

    def test_web_addr_false_not_allowed(self):
        # WHEN
        with self.assertRaises(PyngrokError):
            installer.install_default_config(self.pyngrok_config_v3.config_path, {"web_addr": False})
