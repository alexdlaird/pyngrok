import os
import platform
import time
from unittest import mock
from urllib.parse import urlparse
from urllib.request import urlopen

from pyngrok import process, installer, conf, ngrok
from pyngrok.exception import PyngrokNgrokError
from pyngrok.process import NgrokLog
from tests.testcase import NgrokTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2021, Alex Laird"
__version__ = "5.1.0"


class TestProcess(NgrokTestCase):
    def test_terminate_process(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)
        ngrok_process = process._start_process(self.pyngrok_config)
        monitor_thread = ngrok_process._monitor_thread
        self.assertIsNone(ngrok_process.proc.poll())

        # WHEN
        process._terminate_process(ngrok_process.proc)
        time.sleep(1)

        # THEN
        self.assertIsNotNone(ngrok_process.proc.poll())
        self.assertFalse(monitor_thread.is_alive())

    def test_start_process_port_in_use(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)
        self.assertEqual(len(process._current_processes.keys()), 0)
        ngrok_process = process._start_process(self.pyngrok_config)
        port = urlparse(ngrok_process.api_url).port
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertTrue(ngrok_process._monitor_thread.is_alive())

        ngrok_path2 = os.path.join(conf.BIN_DIR, "2", installer.get_ngrok_bin())
        pyngrok_config2 = self.copy_with_updates(self.pyngrok_config, ngrok_path=ngrok_path2)
        self.given_ngrok_installed(pyngrok_config2)
        config_path2 = os.path.join(self.config_dir, "config2.yml")
        installer.install_default_config(config_path2, {"web_addr": ngrok_process.api_url.lstrip("http://")})
        pyngrok_config2 = self.copy_with_updates(self.pyngrok_config, config_path=config_path2, ngrok_path=ngrok_path2)

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
        self.assertNoZombies()

    def test_process_external_kill(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)
        ngrok_process = process._start_process(self.pyngrok_config)
        monitor_thread = ngrok_process._monitor_thread
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertTrue(ngrok_process._monitor_thread.is_alive())

        # WHEN
        # Kill the process by external means, pyngrok still thinks process is active
        ngrok_process.proc.kill()
        ngrok_process.proc.wait()
        self.assertEqual(len(process._current_processes.keys()), 1)
        time.sleep(1)
        self.assertFalse(monitor_thread.is_alive())

        # THEN
        # Try to kill the process via pyngrok, no error, just update state
        process.kill_process(conf.DEFAULT_NGROK_PATH)
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertFalse(monitor_thread.is_alive())
        self.assertNoZombies()

    def test_process_external_kill_get_process_restart(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)
        ngrok_process1 = process._start_process(self.pyngrok_config)
        monitor_thread1 = ngrok_process1._monitor_thread
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertTrue(ngrok_process1._monitor_thread.is_alive())

        # WHEN
        # Kill the process by external means, pyngrok still thinks process is active
        ngrok_process1.proc.kill()
        ngrok_process1.proc.wait()
        time.sleep(1)
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertFalse(monitor_thread1.is_alive())

        # THEN
        # Try to get process via pyngrok, it has been killed, restart and correct state
        with mock.patch("atexit.register") as mock_atexit:
            ngrok_process2 = process.get_process(self.pyngrok_config)
            self.assertNotEqual(ngrok_process1.proc.pid, ngrok_process2.proc.pid)
            self.assertEqual(len(process._current_processes.keys()), 1)
            self.assertFalse(monitor_thread1.is_alive())
            self.assertTrue(ngrok_process2._monitor_thread.is_alive())

            self.assertTrue(mock_atexit.called)
            self.assertNoZombies()

    def test_multiple_processes_different_binaries(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)
        self.assertEqual(len(process._current_processes.keys()), 0)
        installer.install_default_config(self.pyngrok_config.config_path, {"web_addr": "localhost:4040"})

        ngrok_path2 = os.path.join(conf.BIN_DIR, "2", installer.get_ngrok_bin())
        pyngrok_config2 = self.copy_with_updates(self.pyngrok_config, ngrok_path=ngrok_path2)
        self.given_ngrok_installed(pyngrok_config2)
        config_path2 = os.path.join(self.config_dir, "config2.yml")
        installer.install_default_config(config_path2, {"web_addr": "localhost:4041"})
        pyngrok_config2 = self.copy_with_updates(self.pyngrok_config, config_path=config_path2, ngrok_path=ngrok_path2)

        # WHEN
        ngrok_process1 = process._start_process(self.pyngrok_config)
        ngrok_process2 = process._start_process(pyngrok_config2)

        # THEN
        self.assertEqual(len(process._current_processes.keys()), 2)
        self.assertIsNotNone(ngrok_process1)
        self.assertIsNone(ngrok_process1.proc.poll())
        self.assertTrue(ngrok_process1._monitor_thread.is_alive())
        self.assertTrue(urlparse(ngrok_process1.api_url).port, "4040")
        self.assertIsNotNone(ngrok_process2)
        self.assertIsNone(ngrok_process2.proc.poll())
        self.assertTrue(ngrok_process2._monitor_thread.is_alive())
        self.assertTrue(urlparse(ngrok_process2.api_url).port, "4041")

    def test_multiple_processes_same_binary_fails(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)
        self.assertEqual(len(process._current_processes.keys()), 0)

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

    def test_process_logs(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)

        # WHEN
        ngrok_process = process._start_process(self.pyngrok_config)

        # THEN
        for log in ngrok_process.logs:
            self.assertIsNotNone(log.t)
            self.assertIsNotNone(log.lvl)
            self.assertIsNotNone(log.msg)

    @mock.patch("subprocess.Popen")
    def test_start_new_session(self, mock_popen):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)

        # WHEN
        pyngrok_config = self.copy_with_updates(self.pyngrok_config, start_new_session=True)
        try:
            process._start_process(pyngrok_config=pyngrok_config)
        except TypeError:
            # Since we're mocking subprocess.Popen, this call will ultimately fail, but it gets far enough for us to
            # validate our assertion
            pass

        # THEN
        self.assertTrue(mock_popen.called)
        if os.name == "posix":
            self.assertIn("start_new_session", mock_popen.call_args[1])
        else:
            self.assertNotIn("start_new_session", mock_popen.call_args[1])

    def test_log_event_callback_and_max_logs(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)
        log_event_callback_mock = mock.MagicMock()
        pyngrok_config = self.copy_with_updates(self.pyngrok_config, log_event_callback=log_event_callback_mock,
                                                max_logs=5)

        # WHEN
        ngrok.connect(pyngrok_config=pyngrok_config)
        ngrok_process = ngrok.get_ngrok_process()
        time.sleep(1)

        # THEN
        self.assertGreater(log_event_callback_mock.call_count, len(ngrok_process.logs))
        self.assertEqual(len(ngrok_process.logs), 5)

    def test_no_monitor_thread(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)
        pyngrok_config = self.copy_with_updates(self.pyngrok_config, monitor_thread=False)

        # WHEN
        ngrok.connect(pyngrok_config=pyngrok_config)
        ngrok_process = ngrok.get_ngrok_process()

        # THEN
        self.assertIsNone(ngrok_process._monitor_thread)

    def test_stop_monitor_thread(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config)
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config)
        public_url = ngrok.connect(urlparse(current_process.api_url).port, bind_tls=True,
                                   pyngrok_config=self.pyngrok_config).public_url
        ngrok_process = ngrok.get_ngrok_process()
        monitor_thread = ngrok_process._monitor_thread

        # WHEN
        time.sleep(1)
        self.assertTrue(monitor_thread.is_alive())
        ngrok_process.stop_monitor_thread()
        # Make a request to the tunnel to force a log through, which will allow the thread to trigger its own teardown
        urlopen("{}/status".format(public_url)).read()
        time.sleep(1)

        # THEN
        self.assertFalse(monitor_thread.is_alive())
        self.assertIsNone(ngrok_process._monitor_thread)
        self.assertTrue(ngrok_process.pyngrok_config.monitor_thread)

    @mock.patch("subprocess.Popen")
    def test_retry_session_connection_failure(self, mock_proc_readline):
        # GIVEN
        log_line = "lvl=eror msg=\"some error\" err=EOF"
        mock_proc_readline.return_value.stdout.readline.side_effect = [log_line, log_line, log_line]
        pyngrok_config = self.copy_with_updates(self.pyngrok_config)
        self.given_ngrok_installed(pyngrok_config)

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(pyngrok_config)

        # THEN
        self.assertIsNotNone(cm)
        self.assertEqual(cm.exception.ngrok_logs[-1].msg, "some error")
        self.assertEqual(cm.exception.ngrok_error, "EOF")
        self.assertEqual(mock_proc_readline.call_count, 1)
        self.assertEqual(len(process._current_processes.keys()), 0)

    ################################################################################
    # Tests below this point don't need to start a long-lived ngrok process, they
    # are asserting on pyngrok-specific code or edge cases.
    ################################################################################

    def test_get_process_no_binary(self):
        # GIVEN
        self.given_ngrok_not_installed(conf.DEFAULT_NGROK_PATH)
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            process.get_process(self.pyngrok_config)

        # THEN
        self.assertIn("ngrok binary was not found", str(cm.exception))
        self.assertEqual(len(process._current_processes.keys()), 0)

    def test_log_parsing(self):
        # WHEN
        ngrok_log = NgrokLog("lvl=INFO msg=Test")
        # THEN
        self.assertEqual(ngrok_log.lvl, "INFO")
        self.assertEqual(ngrok_log.msg, "Test")

        # WHEN
        ngrok_log = NgrokLog("lvl=WARN msg=Test=Test")
        # THEN
        self.assertEqual(ngrok_log.lvl, "WARNING")
        self.assertEqual(ngrok_log.msg, "Test=Test")

        # WHEN
        ngrok_log = NgrokLog("lvl=WARN msg=\"Test=Test with spaces\"")
        # THEN
        self.assertEqual(ngrok_log.lvl, "WARNING")
        self.assertEqual(ngrok_log.msg, "Test=Test with spaces")

        # WHEN
        ngrok_log = NgrokLog("lvl=ERR no_msg")
        # THEN
        self.assertEqual(ngrok_log.lvl, "ERROR")
        self.assertIsNone(ngrok_log.msg)

        # WHEN
        ngrok_log = NgrokLog("lvl=CRIT")
        # THEN
        self.assertEqual(ngrok_log.lvl, "CRITICAL")
        self.assertIsNone(ngrok_log.msg)

        # WHEN
        ngrok_log = NgrokLog("lvl=")
        # THEN
        self.assertEqual(ngrok_log.lvl, "NOTSET")

        # WHEN
        ngrok_log = NgrokLog("key=val")
        # THEN
        self.assertEqual(ngrok_log.lvl, "NOTSET")

        # WHEN
        ngrok_log = NgrokLog("lvl=FAKE")
        # THEN
        self.assertEqual(ngrok_log.lvl, "NOTSET")
