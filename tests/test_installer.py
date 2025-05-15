__copyright__ = "Copyright (c) 2018-2025 Alex Laird"
__license__ = "MIT"

import os
import socket
import urllib
import urllib.request
from unittest import mock
from urllib.error import HTTPError

from pyngrok import installer, ngrok, conf
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokError, PyngrokNgrokInstallError, PyngrokSecurityError
from pyngrok.installer import PLATFORMS_V3
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
        self.given_file_doesnt_exist(pyngrok_config.config_path)
        default_exists = os.path.exists(conf.DEFAULT_NGROK_CONFIG_PATH)
        self.assertFalse(os.path.exists(pyngrok_config.ngrok_path))
        self.assertFalse(os.path.exists(pyngrok_config.config_path))

        # WHEN
        installer.install_ngrok(pyngrok_config.ngrok_path, pyngrok_config.ngrok_version)
        ngrok_version, pyngrok_version = ngrok.get_version(pyngrok_config=pyngrok_config)

        # THEN
        self.assertTrue(os.path.exists(pyngrok_config.ngrok_path))
        self.assertTrue(ngrok_version.startswith("3"))
        self.assertTrue(os.path.exists(pyngrok_config.config_path))
        # Asserting this way ensures CI validates a lack of a default config path, while running
        # locally one a dev's machine (where the default may exist) will not fail the test
        self.assertEqual(default_exists, os.path.exists(conf.DEFAULT_NGROK_CONFIG_PATH))

    def test_config_provisioned(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v3.config_path)

        # WHEN
        installer.install_default_config(self.pyngrok_config_v3.config_path, {}, self.pyngrok_config_v3.ngrok_version)

        # THEN
        self.assertTrue(os.path.exists(self.pyngrok_config_v3.config_path))

    def test_get_default_v2_config(self):
        # GIVEN
        installer.install_default_config(self.pyngrok_config_v3.config_path,
                                         {},
                                         self.pyngrok_config_v3.ngrok_version,
                                         "2")

        # WHEN
        ngrok_config = installer.get_ngrok_config(self.pyngrok_config_v3.config_path)

        # THEN
        self.assertEqual(2, len(ngrok_config))
        self.assertEqual("2", ngrok_config["version"])
        self.assertEqual("us", ngrok_config["region"])
        self.assertTrue(os.path.exists(self.pyngrok_config_v3.config_path))

    def test_get_default_v3_config(self):
        # GIVEN
        installer.install_default_config(self.pyngrok_config_v3.config_path,
                                         {},
                                         self.pyngrok_config_v3.ngrok_version,
                                         "3")

        # WHEN
        ngrok_config = installer.get_ngrok_config(self.pyngrok_config_v3.config_path)

        # THEN
        self.assertEqual(1, len(ngrok_config))
        self.assertEqual("3", ngrok_config["version"])
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

    @mock.patch("platform.system")
    def test_get_default_ngrok_dir_mac(self, mock_system):
        # GIVEN
        mock_system.return_value = "Darwin"
        user_home = os.path.expanduser("~")

        # WHEN
        default_ngrok_dir = installer.get_default_ngrok_dir()

        # THEN
        self.assertEqual(os.path.join(user_home, "Library", "Application Support", "ngrok"), default_ngrok_dir)

    @mock.patch("platform.system")
    def test_get_default_ngrok_dir_windows(self, mock_system):
        # GIVEN
        mock_system.return_value = "Windows 10"
        user_home = os.path.expanduser("~")

        # WHEN
        default_ngrok_dir = installer.get_default_ngrok_dir()

        # THEN
        self.assertEqual(os.path.join(user_home, "AppData", "Local", "ngrok"), default_ngrok_dir)

    @mock.patch("platform.system")
    def test_get_default_ngrok_dir_unix(self, mock_system):
        # GIVEN
        mock_system.return_value = "Linux"
        user_home = os.path.expanduser("~")

        # WHEN
        default_ngrok_dir = installer.get_default_ngrok_dir()

        # THEN
        self.assertEqual(os.path.join(user_home, ".config", "ngrok"), default_ngrok_dir)

    @mock.patch("platform.system")
    def test_get_ngrok_binary_mac(self, mock_system):
        # GIVEN
        mock_system.return_value = "Darwin"

        # WHEN
        ngrok_bin = installer.get_ngrok_bin()

        # THEN
        self.assertEqual("ngrok", ngrok_bin)

    @mock.patch("platform.system")
    def test_get_system_windows(self, mock_system):
        # GIVEN
        mock_system.return_value = "Windows 10"

        # WHEN
        ngrok_bin = installer.get_ngrok_bin()

        # THEN
        self.assertEqual("ngrok.exe", ngrok_bin)

    @mock.patch("platform.system")
    def test_get_system_linux(self, mock_system):
        # GIVEN
        mock_system.return_value = "Linux"

        # WHEN
        ngrok_bin = installer.get_ngrok_bin()

        # THEN
        self.assertEqual("ngrok", ngrok_bin)

    @mock.patch("platform.system")
    def test_get_system_freebsd(self, mock_system):
        # GIVEN
        mock_system.return_value = "FreeBSD"

        # WHEN
        ngrok_bin = installer.get_ngrok_bin()

        # THEN
        self.assertEqual("ngrok", ngrok_bin)

    @mock.patch("platform.system")
    def test_get_system_cygwin_is_windows(self, mock_system):
        # GIVEN
        mock_system.return_value = "Cygwin NT"

        # WHEN
        ngrok_bin = installer.get_ngrok_bin()

        # THEN
        self.assertEqual("ngrok.exe", ngrok_bin)

    @mock.patch("platform.system")
    def test_get_system_mingw_is_windows(self, mock_system):
        # GIVEN
        mock_system.return_value = "MinGW NT"

        # WHEN
        ngrok_bin = installer.get_ngrok_bin()

        # THEN
        self.assertEqual("ngrok.exe", ngrok_bin)

    @mock.patch("platform.system")
    def test_get_system_unsupported(self, mock_system):
        # GIVEN
        mock_system.return_value = "Solaris"

        # WHEN
        with self.assertRaises(PyngrokNgrokInstallError):
            installer.get_ngrok_bin()

    @mock.patch("platform.system")
    @mock.patch("platform.machine")
    def test_get_ngrok_cdn_url_mac_arm64(self, mock_machine, mock_system):
        # GIVEN
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        # WHEN
        url = installer.get_ngrok_cdn_url("v3")

        # THEN
        self.assertEqual(PLATFORMS_V3["darwin_x86_64_arm"], url)

    @mock.patch("platform.system")
    @mock.patch("platform.machine")
    def test_get_ngrok_cdn_url_windows32(self, mock_machine, mock_system):
        # GIVEN
        mock_system.return_value = "Windows 10"
        mock_machine.return_value = "i386"

        # WHEN
        url = installer.get_ngrok_cdn_url("v3")

        # THEN
        self.assertEqual(PLATFORMS_V3["windows_i386"], url)

    @mock.patch("platform.system")
    @mock.patch("platform.machine")
    def test_get_ngrok_cdn_url_linux_arm64(self, mock_machine, mock_system):
        # GIVEN
        mock_system.return_value = "Linux"
        mock_machine.return_value = "arm aarch64"

        # WHEN
        url = installer.get_ngrok_cdn_url("v3")

        # THEN
        self.assertEqual(PLATFORMS_V3["linux_x86_64_arm"], url)

    @mock.patch("platform.system")
    @mock.patch("platform.machine")
    def test_get_ngrok_cdn_url_freebsd64(self, mock_machine, mock_system):
        # GIVEN
        mock_system.return_value = "FreeBSD"
        mock_machine.return_value = "x86_64"

        # WHEN
        url = installer.get_ngrok_cdn_url("v3")

        # THEN
        self.assertEqual(PLATFORMS_V3["freebsd_x86_64"], url)

    @mock.patch("platform.system")
    @mock.patch("platform.machine")
    def test_get_ngrok_cdn_url_cygwin_is_windows(self, mock_machine, mock_system):
        # GIVEN
        mock_system.return_value = "Cygwin NT"
        mock_machine.return_value = "aarch64"

        # WHEN
        url = installer.get_ngrok_cdn_url("v3")

        # THEN
        self.assertEqual(PLATFORMS_V3["windows_x86_64_arm"], url)

    @mock.patch("platform.system")
    @mock.patch("platform.machine")
    def test_get_ngrok_cdn_url_mingw_is_windows(self, mock_machine, mock_system):
        # GIVEN
        mock_system.return_value = "MinGW NT"
        mock_machine.return_value = "i386"

        # WHEN
        url = installer.get_ngrok_cdn_url("v3")

        # THEN
        self.assertEqual(PLATFORMS_V3["windows_i386"], url)

    def test_ensure_installer_urls_exist_v2(self):
        for key, value in installer.PLATFORMS.items():
            try:
                urllib.request.urlopen(urllib.request.Request(value, method="HEAD"))
            except HTTPError as e:
                if e.status == 404:
                    self.fail("Installer URL returned 404: %s" % value)
                else:
                    raise e

    def test_ensure_installer_urls_exist_v3(self):
        for key, value in installer.PLATFORMS_V3.items():
            try:
                urllib.request.urlopen(urllib.request.Request(value, method="HEAD"))
            except HTTPError as e:
                if e.status == 404:
                    self.fail("Installer URL returned 404: %s" % value)
                else:
                    raise e
