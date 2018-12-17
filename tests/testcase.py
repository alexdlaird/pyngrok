import os
import unittest
import shutil

from pyngrok import ngrok
from pyngrok import process


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
