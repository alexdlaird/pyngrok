import os
import shutil
import unittest

import yaml

from pyngrok import ngrok
from pyngrok import process

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Alex Laird"
__version__ = "1.3.1"


class NgrokTestCase(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".ngrok2"))
        self.config_path = os.path.join(self.config_dir, "config.yml")
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
        open(self.config_path, "w").close()

    def tearDown(self):
        process.kill_process(ngrok.DEFAULT_NGROK_PATH)
        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)

    def given_config(self, new_configs):
        with open(self.config_path, "r") as config_file:
            config = yaml.safe_load(config_file)
            if config is None:
                config = {}

            config.update(new_configs)

        with open(self.config_path, "w") as config_file:
            yaml.dump(config, config_file)

    def given_ngrok_installed(self, ngrok_path):
        ngrok.ensure_ngrok_installed(ngrok_path)

    def given_ngrok_not_installed(self, ngrok_path):
        if os.path.exists(ngrok_path):
            os.remove(ngrok_path)
