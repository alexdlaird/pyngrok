import os

from future.standard_library import install_aliases
from mock import mock

from pyngrok import ngrok, process
from pyngrok.exception import PyngrokNgrokError
from .testcase import NgrokTestCase

install_aliases()

from urllib.parse import urlparse

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Alex Laird"
__version__ = "1.3.8"


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

    def test_start_process_port_in_use(self):
        # GIVEN
        self.given_ngrok_installed(ngrok.DEFAULT_NGROK_PATH)
        self.assertEqual(len(process._current_processes.keys()), 0)
        ngrok_process = process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        port = urlparse(ngrok_process.api_url).port
        self.assertEqual(len(process._current_processes.keys()), 1)

        ngrok_path2 = os.path.join(ngrok.BIN_DIR, "2", ngrok.get_ngrok_bin())
        self.given_ngrok_installed(ngrok_path2)
        config_path2 = os.path.join(self.config_dir, "config2.yml")
        self.given_config(config_path2, {"web_addr": ngrok_process.api_url.lstrip("http://")})

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(ngrok_path2, config_path=config_path2)

        # THEN
        self.assertIn("{}: bind: address already in use".format(port), str(cm.exception.ngrok_errors))
        self.assertEqual(len(process._current_processes.keys()), 1)

    def test_process_external_kill(self):
        # GIVEN
        self.given_ngrok_installed(ngrok.DEFAULT_NGROK_PATH)
        ngrok_process = process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        self.assertEqual(len(process._current_processes.keys()), 1)

        # WHEN
        # Kill the process by external means, pyngrok still thinks process is active
        ngrok_process.process.kill()
        ngrok_process.process.wait()
        self.assertEqual(len(process._current_processes.keys()), 1)

        # Try to kill the process via pyngrok, no error, just update state
        process.kill_process(ngrok.DEFAULT_NGROK_PATH)
        self.assertEqual(len(process._current_processes.keys()), 0)

    def test_process_external_kill_get_process_restart(self):
        # GIVEN
        self.given_ngrok_installed(ngrok.DEFAULT_NGROK_PATH)
        ngrok_process1 = process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        self.assertEqual(len(process._current_processes.keys()), 1)

        # WHEN
        # Kill the process by external means, pyngrok still thinks process is active
        ngrok_process1.process.kill()
        ngrok_process1.process.wait()
        self.assertEqual(len(process._current_processes.keys()), 1)

        # THEN
        # Try to get process via pyngrok, it has been killed, restart and correct state
        with mock.patch("atexit.register") as mock_atexit:
            ngrok_process2 = process.get_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
            self.assertNotEqual(ngrok_process1.process.pid, ngrok_process2.process.pid)
            self.assertEqual(len(process._current_processes.keys()), 1)

            mock_atexit.assert_called_once()

    def test_multiple_processes_different_binaries(self):
        # GIVEN
        self.given_ngrok_installed(ngrok.DEFAULT_NGROK_PATH)
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.given_config(self.config_path, {"web_addr": "localhost:4040"})

        ngrok_path2 = os.path.join(ngrok.BIN_DIR, "2", ngrok.get_ngrok_bin())
        self.given_ngrok_installed(ngrok_path2)
        config_path2 = os.path.join(self.config_dir, "config2.yml")
        self.given_config(config_path2, {"web_addr": "localhost:4041"})

        # WHEN
        ngrok_process1 = process._start_process(ngrok.DEFAULT_NGROK_PATH, config_path=self.config_path)
        ngrok_process2 = process._start_process(ngrok_path2, config_path=config_path2)

        # THEN
        self.assertEqual(len(process._current_processes.keys()), 2)
        self.assertIsNotNone(ngrok_process1)
        self.assertIsNone(ngrok_process1.process.poll())
        self.assertTrue("4040" in ngrok_process1.api_url)
        self.assertIsNotNone(ngrok_process2)
        self.assertIsNone(ngrok_process2.process.poll())
        self.assertTrue("4041" in ngrok_process2.api_url)

    def test_multiple_processes_same_binary_fails(self):
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
