from pyngrok import ngrok, process
from pyngrok.exception import PyngrokNgrokError
from .testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Alex Laird"
__version__ = "1.3.5"


class TestProcess(NgrokTestCase):
    def test_get_process_no_binary(self):
        # GIVEN
        self.given_ngrok_not_installed(ngrok.DEFAULT_NGROK_PATH)
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            process.get_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)

        # THEN
        self.assertIn("ngrok binary was not found", str(cm.exception))
        self.assertEqual(len(process._current_processes.keys()), 0)

    def test_start_process_multiple_fails(self):
        # GIVEN
        self.given_ngrok_installed(ngrok.DEFAULT_NGROK_PATH)
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        ngrok_process1 = process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)

        # THEN
        self.assertIn("ngrok is already running", str(cm.exception))
        self.assertIsNotNone(ngrok_process1)
        self.assertIsNone(ngrok_process1.process.poll())
        self.assertEqual(ngrok_process1, process.get_process(ngrok.DEFAULT_NGROK_PATH))
        self.assertEqual(len(process._current_processes.keys()), 1)

    def test_start_process_port_in_use(self):
        # GIVEN
        self.given_ngrok_installed(ngrok.DEFAULT_NGROK_PATH)
        self.given_config({"web_addr": "localhost:20"})
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)

        # THEN
        self.assertIn("20: bind: permission denied", str(cm.exception))
        self.assertEqual(len(process._current_processes.keys()), 0)
