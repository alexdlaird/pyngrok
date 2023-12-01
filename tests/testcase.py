import logging
import os
import platform
import shutil
from random import randint

import sys
import unittest
from copy import copy

import psutil
from psutil import AccessDenied, NoSuchProcess

from pyngrok.conf import PyngrokConfig

from pyngrok import ngrok, installer, conf
from pyngrok import process

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "5.2.2"

logger = logging.getLogger(__name__)
ngrok_logger = logging.getLogger("{}.ngrok".format(__name__))


class NgrokTestCase(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".ngrok"))
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        config_v2_path = os.path.join(self.config_dir, "config_v2.yml")
        config_v3_path = os.path.join(self.config_dir, "config_v3.yml")

        ngrok_path_v2 = os.path.join(conf.BIN_DIR, "v2", installer.get_ngrok_bin())
        self.pyngrok_config_v2 = PyngrokConfig(
            ngrok_path=ngrok_path_v2,
            config_path=config_v2_path,
            ngrok_version="v2")

        ngrok_path_v3 = os.path.join(conf.BIN_DIR, "v3", installer.get_ngrok_bin())
        self.pyngrok_config_v3 = PyngrokConfig(ngrok_path=ngrok_path_v3,
                                               config_path=config_v3_path,
                                               ngrok_version="v3")

        conf.DEFAULT_NGROK_CONFIG_PATH = config_v2_path
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
    def create_unique_subdomain():
        return "pyngrok-{}-{}-{}-{}{}-tcp".format(randint(1000000000000000, 9999999999999999), platform.system(),
                                                  platform.python_implementation(), sys.version_info[0],
                                                  sys.version_info[1]).lower()

    @staticmethod
    def copy_with_updates(to_copy, **kwargs):
        copied = copy(to_copy)

        for key, value in kwargs.items():
            copied.__setattr__(key, value)

        return copied

    def assertNoZombies(self):
        try:
            self.assertEqual(0, len(
                list(filter(lambda p: p.name() == "ngrok" and p.status() == "zombie", psutil.process_iter()))))
        except (AccessDenied, NoSuchProcess):
            # Some OSes are flaky on this assertion, but that isn't an indication anything is wrong, so pass
            pass
