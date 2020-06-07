import os
import shutil
import unittest

from pyngrok import ngrok, installer
from pyngrok import process

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "4.0.0"

from pyngrok.config import PyngrokConfig


class NgrokTestCase(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".ngrok2"))
        config_path = os.path.join(self.config_dir, "config.yml")

        ngrok._DEFAULT_NGROK_CONFIG_PATH = config_path

        self.pyngrok_config = PyngrokConfig(config_path=config_path)

        installer.DEFAULT_RETRY_COUNT = 1

    def tearDown(self):
        for p in list(process._current_processes.values()):
            try:
                process.kill_process(p.ngrok_path)
                p.proc.wait()
            except OSError:
                pass

        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)

    @staticmethod
    def given_ngrok_installed(ngrok_path):
        ngrok.ensure_ngrok_installed(ngrok_path)

    @staticmethod
    def given_ngrok_not_installed(ngrok_path):
        if os.path.exists(ngrok_path):
            os.remove(ngrok_path)
