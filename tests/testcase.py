__copyright__ = "Copyright (c) 2018-2024 Alex Laird"
__license__ = "MIT"

import logging
import os
import shutil
import unittest
from copy import copy

import psutil
from psutil import AccessDenied, NoSuchProcess

from pyngrok import conf, installer, ngrok, process
from pyngrok.conf import PyngrokConfig

logger = logging.getLogger(__name__)
ngrok_logger = logging.getLogger(f"{__name__}.ngrok")


class NgrokTestCase(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".ngrok"))
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        config_v2_path = os.path.join(self.config_dir, "config_v2.yml")

        conf.DEFAULT_NGROK_CONFIG_PATH = config_v2_path
        conf.DEFAULT_NGROK_PATH = os.path.join(config_v2_path, installer.get_ngrok_bin())

        config_v3_path = os.path.join(self.config_dir, "config_v3.yml")

        ngrok_path_v2 = os.path.join(self.config_dir, "v2", installer.get_ngrok_bin())
        self.pyngrok_config_v2 = PyngrokConfig(
            ngrok_path=ngrok_path_v2,
            config_path=config_v2_path,
            ngrok_version="v2")

        ngrok_path_v3 = os.path.join(self.config_dir, "v3", installer.get_ngrok_bin())
        self.pyngrok_config_v3 = PyngrokConfig(ngrok_path=ngrok_path_v3,
                                               config_path=config_v3_path,
                                               ngrok_version="v3")

        conf.set_default(self.pyngrok_config_v2)

        # ngrok's CDN can be flaky, so make sure its flakiness isn't reflect in our CI/CD test runs
        installer.DEFAULT_RETRY_COUNT = 3

    def tearDown(self):
        for p in list(process._current_processes.values()):
            try:
                process.kill_process(p.pyngrok_config.ngrok_path)
                p.proc.wait()
            except OSError:
                pass

        ngrok._current_tunnels.clear()

        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)

    @staticmethod
    def given_ngrok_installed(pyngrok_config):
        ngrok.install_ngrok(pyngrok_config)

    @staticmethod
    def given_file_doesnt_exist(path):
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def copy_with_updates(to_copy, **kwargs):
        copied = copy(to_copy)

        for key, value in kwargs.items():
            copied.__setattr__(key, value)

        return copied

    def assert_no_zombies(self):
        try:
            self.assertEqual(0, len(
                list(filter(lambda p: p.name() == "ngrok" and p.status() == "zombie", psutil.process_iter()))))
        except (AccessDenied, NoSuchProcess):
            # Some OSes are flaky on this assertion, but that isn't an indication anything is wrong, so pass
            pass
