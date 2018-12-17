import unittest

from pygrok import process


class NgrokTestCase(unittest.TestCase):
    def tearDown(self):
        process.kill_process()
