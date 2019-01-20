from pyngrok import ngrok, process
from pyngrok.exception import PyngrokNgrokError
from .testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "1.3.0"


class TestProcess(NgrokTestCase):
    def test_start_process_multiple_fails(self):
        # TODO: refactor this test so no assertion is raised and multiple instances of the same bin are allowed
        # GIVEN
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 0)

        # WHEN
        ngrok_process1 = process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        with self.assertRaises(PyngrokNgrokError) as cm:
            ngrok_process2 = process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)

        # THEN
        self.assertIsNotNone(ngrok_process1)
        # self.assertIsNotNone(ngrok_process2)
        # self.assertEqual(ngrok_process2, ngrok.get_ngrok_process())
        self.assertIsNone(ngrok_process1.process.poll())
        # self.assertIsNone(ngrok_process2.process.poll())
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 1)

    def test_start_process_multiple_port_defined_fails(self):
        # GIVEN
        self._add_config({"web_addr": "localhost:4040"})
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 0)

        # WHEN
        ngrok_process1 = process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        with self.assertRaises(PyngrokNgrokError) as cm:
            ngrok_process2 = process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)

        # THEN
        self.assertIsNotNone(ngrok_process1)
        self.assertEqual(ngrok_process1, ngrok.get_ngrok_process())
        self.assertIsNone(ngrok_process1.process.poll())

        # TODO: after above test is refactored and raised exception removed, uncomment this
        # self.assertIn("4040: bind: address already in use", str(cm.exception))
        # self.assertIsNotNone(ngrok_process2)
        # self.assertEqual(ngrok_process2, ngrok.get_ngrok_process())
        # self.assertIsNone(ngrok_process2.process.poll())
        self.assertIsNotNone(process.get_process(ngrok.DEFAULT_NGROK_PATH))
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 1)
