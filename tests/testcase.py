import os
import shutil
import unittest

import yaml

from pyngrok import ngrok
from pyngrok import process

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Alex Laird"
__version__ = "1.3.7"


class NgrokTestCase(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".ngrok2"))
        self.config_path = os.path.join(self.config_dir, "config.yml")
        self.given_config(self.config_path)

    def tearDown(self):
        for p in list(process._current_processes.values()):
            try:
                process.kill_process(p.ngrok_path)
                p.process.wait()
            except OSError:
                pass

        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)

    def given_config(self, config_path, data=""):
        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        if not os.path.exists(config_path):
            open(config_path, "w").close()

        with open(config_path, "r") as config_file:
            config = yaml.safe_load(config_file)
            if config is None:
                config = {}

            config.update(data)

        with open(config_path, "w") as config_file:
            yaml.dump(config, config_file)

    def given_ngrok_installed(self, ngrok_path):
        ngrok.ensure_ngrok_installed(ngrok_path)

    def given_ngrok_not_installed(self, ngrok_path):
        if os.path.exists(ngrok_path):
            os.remove(ngrok_path)
