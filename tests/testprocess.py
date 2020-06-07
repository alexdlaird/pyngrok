import os
import platform
import time

from future.standard_library import install_aliases
from mock import mock

from pyngrok import process, installer, conf
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokNgrokError
from .testcase import NgrokTestCase

install_aliases()

from urllib.parse import urlparse

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "4.0.0"


class TestProcess(NgrokTestCase):
    def test_terminate_process(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config.ngrok_path)
        ngrok_process = process._start_process(self.pyngrok_config)
        ngrok_thread = process._ngrok_threads[conf.DEFAULT_NGROK_PATH]
        self.assertIsNone(ngrok_process.proc.poll())

        # WHEN
        process._terminate_process(ngrok_process.proc)
        time.sleep(1)

        # THEN
        self.assertIsNotNone(ngrok_process.proc.poll())
        self.assertFalse(ngrok_thread.is_alive())

    def test_get_process_no_binary(self):
        # GIVEN
        self.given_ngrok_not_installed(conf.DEFAULT_NGROK_PATH)
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(process._ngrok_threads.keys()), 0)

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            process.get_process(self.pyngrok_config)

        # THEN
        self.assertIn("ngrok binary was not found", str(cm.exception))
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(process._ngrok_threads.keys()), 0)

    def test_start_process_port_in_use(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config.ngrok_path)
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(process._ngrok_threads.keys()), 0)
        ngrok_process = process._start_process(self.pyngrok_config)
        port = urlparse(ngrok_process.api_url).port
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertEqual(len(process._ngrok_threads.keys()), 1)

        ngrok_path2 = os.path.join(conf.BIN_DIR, "2", installer.get_ngrok_bin())
        self.given_ngrok_installed(ngrok_path2)
        config_path2 = os.path.join(self.config_dir, "config2.yml")
        installer.install_default_config(config_path2, {"web_addr": ngrok_process.api_url.lstrip("http://")})
        pyngrok_config2 = PyngrokConfig(ngrok_path=ngrok_path2, config_path=config_path2)

        error = None
        retries = 0
        while error is None and retries < 10:
            time.sleep(1)

            # WHEN
            with self.assertRaises(PyngrokNgrokError) as cm:
                process._start_process(pyngrok_config2)

            error = cm.exception.ngrok_error
            retries += 1

        # THEN
        self.assertIsNotNone(error)
        if platform.system() == "Windows":
            self.assertIn("{}: bind: Only one usage of each socket address".format(port), cm.exception.ngrok_error)
        else:
            self.assertIn("{}: bind: address already in use".format(port), str(cm.exception.ngrok_error))
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertEqual(len(process._ngrok_threads.keys()), 1)

    def test_process_external_kill(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config.ngrok_path)
        ngrok_process = process._start_process(self.pyngrok_config)
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertEqual(len(process._ngrok_threads.keys()), 1)

        # WHEN
        # Kill the process by external means, pyngrok still thinks process is active
        ngrok_process.proc.kill()
        ngrok_process.proc.wait()
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertEqual(len(process._ngrok_threads.keys()), 1)

        # Try to kill the process via pyngrok, no error, just update state
        process.kill_process(conf.DEFAULT_NGROK_PATH)
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(process._ngrok_threads.keys()), 0)

    def test_process_external_kill_get_process_restart(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config.ngrok_path)
        ngrok_process1 = process._start_process(self.pyngrok_config)
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertEqual(len(process._ngrok_threads.keys()), 1)

        # WHEN
        # Kill the process by external means, pyngrok still thinks process is active
        ngrok_process1.proc.kill()
        ngrok_process1.proc.wait()
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertEqual(len(process._ngrok_threads.keys()), 1)

        # THEN
        # Try to get process via pyngrok, it has been killed, restart and correct state
        with mock.patch("atexit.register") as mock_atexit:
            ngrok_process2 = process.get_process(self.pyngrok_config)
            self.assertNotEqual(ngrok_process1.proc.pid, ngrok_process2.proc.pid)
            self.assertEqual(len(process._current_processes.keys()), 1)
            self.assertEqual(len(process._ngrok_threads.keys()), 1)

            mock_atexit.assert_called()

    def test_multiple_processes_different_binaries(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config.ngrok_path)
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(process._ngrok_threads.keys()), 0)
        installer.install_default_config(self.pyngrok_config.config_path, {"web_addr": "localhost:4040"})

        ngrok_path2 = os.path.join(conf.BIN_DIR, "2", installer.get_ngrok_bin())
        self.given_ngrok_installed(ngrok_path2)
        config_path2 = os.path.join(self.config_dir, "config2.yml")
        installer.install_default_config(config_path2, {"web_addr": "localhost:4041"})
        pyngrok_config2 = PyngrokConfig(ngrok_path=ngrok_path2, config_path=config_path2)

        # WHEN
        ngrok_process1 = process._start_process(self.pyngrok_config)
        ngrok_thread1 = process._ngrok_threads[self.pyngrok_config.ngrok_path]
        ngrok_process2 = process._start_process(pyngrok_config2)
        ngrok_thread2 = process._ngrok_threads[pyngrok_config2.ngrok_path]

        # THEN
        self.assertEqual(len(process._current_processes.keys()), 2)
        self.assertEqual(len(process._ngrok_threads.keys()), 2)
        self.assertIsNotNone(ngrok_process1)
        self.assertIsNone(ngrok_process1.proc.poll())
        self.assertTrue(ngrok_thread1.is_alive())
        self.assertTrue(urlparse(ngrok_process1.api_url).port, "4040")
        self.assertIsNotNone(ngrok_process2)
        self.assertIsNone(ngrok_process2.proc.poll())
        self.assertTrue(ngrok_thread2.is_alive())
        self.assertTrue(urlparse(ngrok_process2.api_url).port, "4041")

    def test_multiple_processes_same_binary_fails(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config.ngrok_path)
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertEqual(len(process._ngrok_threads.keys()), 0)

        # WHEN
        ngrok_process1 = process._start_process(self.pyngrok_config)
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(self.pyngrok_config)

        # THEN
        self.assertIn("ngrok is already running", str(cm.exception))
        self.assertIsNotNone(ngrok_process1)
        self.assertIsNone(ngrok_process1.proc.poll())
        self.assertEqual(ngrok_process1, process.get_process(self.pyngrok_config))
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertEqual(len(process._ngrok_threads.keys()), 1)

    def test_logs(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config.ngrok_path)

        # WHEN
        ngrok_process = process._start_process(self.pyngrok_config)

        # THEN
        for log in ngrok_process.logs:
            self.assertIsNotNone(log.t)
            self.assertIsNotNone(log.lvl)
            self.assertIsNotNone(log.msg)
