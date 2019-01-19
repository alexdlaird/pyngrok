from pyngrok import ngrok, process
from pyngrok.exception import PyngrokNgrokError
from .testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "1.3.0"


class TestProcess(NgrokTestCase):
    def test_start_process_multiple(self):
        # GIVEN
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 0)

        # WHEN
        process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        # TODO: currently this overwrites the key, need to refactor for support
        # process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        current_process = ngrok.get_ngrok_process()

        # THEN
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.process.poll())
        self.assertIsNotNone(process.get_process(ngrok.DEFAULT_NGROK_PATH))
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 1)

    def test_start_process_multiple_fails(self):
        # GIVEN
        self._add_config({"web_addr": "localhost:4040"})
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 0)

        # WHEN
        process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        current_process = ngrok.get_ngrok_process()

        # THEN
        self.assertIn("4040: bind: address already in use", str(cm.exception))
        self.assertIsNotNone(current_process)
        self.assertIsNone(current_process.process.poll())
        self.assertIsNotNone(process.get_process(ngrok.DEFAULT_NGROK_PATH))
        self.assertEqual(len(process.CURRENT_PROCESSES.keys()), 1)
