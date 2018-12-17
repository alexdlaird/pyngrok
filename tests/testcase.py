import unittest

from pyngrok import ngrok
from pyngrok import process


class NgrokTestCase(unittest.TestCase):
    def tearDown(self):
        process.kill_process(ngrok.DEFAULT_NGROK_PATH)
