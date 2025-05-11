__copyright__ = "Copyright (c) 2018-2024 Alex Laird"
__license__ = "MIT"

import os
import platform
import time
import unittest
from unittest import mock
from urllib.parse import urlparse
from urllib.request import urlopen

from pyngrok import installer, ngrok, process
from pyngrok.exception import PyngrokNgrokError
from pyngrok.process import NgrokLog
from tests.testcase import NgrokTestCase


class TestProcess(NgrokTestCase):
    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_terminate_process(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v3)
        ngrok_process = process._start_process(self.pyngrok_config_v3)
        monitor_thread = ngrok_process._monitor_thread
        self.assertIsNone(ngrok_process.proc.poll())

        # WHEN
        process._terminate_process(ngrok_process.proc)
        time.sleep(1)

        # THEN
        self.assertIsNotNone(ngrok_process.proc.poll())
        self.assertFalse(monitor_thread.is_alive())

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_start_process_port_in_use_v2(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v2)
        self.assertEqual(len(process._current_processes.keys()), 0)
        ngrok_process = process._start_process(self.pyngrok_config_v2)
        port = urlparse(ngrok_process.api_url).port
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertTrue(ngrok_process._monitor_thread.is_alive())

        ngrok_path_v2_2 = os.path.join(self.config_dir, "v2_2", installer.get_ngrok_bin())
        pyngrok_config_v2_2 = self.copy_with_updates(self.pyngrok_config_v2,
                                                     ngrok_path=ngrok_path_v2_2)
        self.given_ngrok_installed(pyngrok_config_v2_2)
        config_path_v2_2 = os.path.join(self.config_dir, "config_v2_2.yml")
        installer.install_default_config(config_path_v2_2, {"web_addr": ngrok_process.api_url.lstrip("http://")},
                                         ngrok_version="v2")
        pyngrok_config_v2_2 = self.copy_with_updates(self.pyngrok_config_v2,
                                                     config_path=config_path_v2_2,
                                                     ngrok_path=ngrok_path_v2_2)

        time.sleep(3)

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(pyngrok_config_v2_2)

        # THEN
        self.assertIsNotNone(cm.exception)
        if platform.system() == "Windows":
            self.assertIn(f"{port}: bind: Only one usage of each socket address", cm.exception.ngrok_error)
        else:
            self.assertIn(f"{port}: bind: address already in use", str(cm.exception.ngrok_error))
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assert_no_zombies()

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_start_process_port_in_use_v3(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v3)
        self.assertEqual(len(process._current_processes.keys()), 0)
        ngrok_process = process._start_process(self.pyngrok_config_v3)
        port = urlparse(ngrok_process.api_url).port
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assertTrue(ngrok_process._monitor_thread.is_alive())

        ngrok_path_v3_2 = os.path.join(self.config_dir, "v3_2", installer.get_ngrok_bin())
        pyngrok_config_v3_2 = self.copy_with_updates(self.pyngrok_config_v3,
                                                     ngrok_path=ngrok_path_v3_2)
        self.given_ngrok_installed(pyngrok_config_v3_2)
        config_path_v3_2 = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path_v3_2, {"web_addr": ngrok_process.api_url.lstrip("http://")},
                                         ngrok_version="v3")
        pyngrok_config_v3_2 = self.copy_with_updates(self.pyngrok_config_v3,
                                                     config_path=config_path_v3_2,
                                                     ngrok_path=ngrok_path_v3_2)

        time.sleep(3)

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(pyngrok_config_v3_2)

        # THEN
        self.assertIsNotNone(cm.exception.ngrok_error)
        if platform.system() == "Windows":
            self.assertIn(f"{port}: bind: Only one usage of each socket address", cm.exception.ngrok_error)
        else:
            self.assertIn(f"{port}: bind: address already in use", str(cm.exception.ngrok_error))
        self.assertEqual(len(process._current_processes.keys()), 1)
        self.assert_no_zombies()

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_process_external_kill(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v3)
        ngrok_process1 = process._start_process(self.pyngrok_config_v3)
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
        # Try to kill the process via pyngrok, no error, just update state
        process.kill_process(self.pyngrok_config_v3.ngrok_path)
        self.assertEqual(len(process._current_processes.keys()), 0)
        self.assertFalse(monitor_thread1.is_alive())
        self.assert_no_zombies()

        # THEN
        # Try to get process via pyngrok, it has been killed, restart and correct state
        with mock.patch("atexit.register") as mock_atexit:
            ngrok_process2 = process.get_process(self.pyngrok_config_v3)
            self.assertNotEqual(ngrok_process1.proc.pid, ngrok_process2.proc.pid)
            self.assertEqual(len(process._current_processes.keys()), 1)
            self.assertFalse(monitor_thread1.is_alive())
            self.assertTrue(ngrok_process2._monitor_thread.is_alive())

            self.assertTrue(mock_atexit.called)
            self.assert_no_zombies()

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_multiple_processes_different_binaries(self):
        # GIVEN
        self.assertEqual(len(process._current_processes.keys()), 0)

        self.given_ngrok_installed(self.pyngrok_config_v2)
        config_path_v2_1 = os.path.join(self.config_dir, "config_v2_1.yml")
        installer.install_default_config(config_path_v2_1, {"web_addr": "localhost:4040"}, ngrok_version="v2")
        pyngrok_config_v2_1 = self.copy_with_updates(self.pyngrok_config_v2,
                                                     config_path=config_path_v2_1,
                                                     ngrok_path=self.pyngrok_config_v2.ngrok_path)

        ngrok_path_v2_2 = os.path.join(self.config_dir, "v2_2", installer.get_ngrok_bin())
        pyngrok_config_v2_2 = self.copy_with_updates(self.pyngrok_config_v2,
                                                     ngrok_path=ngrok_path_v2_2)
        self.given_ngrok_installed(pyngrok_config_v2_2)
        config_path_v2_2 = os.path.join(self.config_dir, "config_v2_2.yml")
        installer.install_default_config(config_path_v2_2, {"web_addr": "localhost:4041"}, ngrok_version="v2")
        pyngrok_config_v2_2 = self.copy_with_updates(self.pyngrok_config_v2,
                                                     config_path=config_path_v2_2,
                                                     ngrok_path=ngrok_path_v2_2)

        self.given_ngrok_installed(self.pyngrok_config_v3)
        config_path_v3_1 = os.path.join(self.config_dir, "config_v3_1.yml")
        installer.install_default_config(config_path_v3_1, {"web_addr": "localhost:4042"}, ngrok_version="v3")
        pyngrok_config_v3_1 = self.copy_with_updates(self.pyngrok_config_v3,
                                                     config_path=config_path_v3_1,
                                                     ngrok_path=self.pyngrok_config_v3.ngrok_path)

        ngrok_path_v3_2 = os.path.join(self.config_dir, "v3_2", installer.get_ngrok_bin())
        pyngrok_config_v3_2 = self.copy_with_updates(self.pyngrok_config_v3,
                                                     ngrok_path=ngrok_path_v3_2)
        self.given_ngrok_installed(pyngrok_config_v3_2)
        config_path_v3_2 = os.path.join(self.config_dir, "config_v3_2.yml")
        installer.install_default_config(config_path_v3_2, {"web_addr": "localhost:4043"}, ngrok_version="v3")
        pyngrok_config_v3_2 = self.copy_with_updates(self.pyngrok_config_v3,
                                                     config_path=config_path_v3_2,
                                                     ngrok_path=ngrok_path_v3_2)

        # WHEN
        ngrok_process1 = process._start_process(pyngrok_config_v2_1)
        ngrok_process2 = process._start_process(pyngrok_config_v2_2)
        ngrok_process3 = process._start_process(pyngrok_config_v3_1)
        ngrok_process4 = process._start_process(pyngrok_config_v3_2)

        # THEN
        self.assertEqual(len(process._current_processes.keys()), 4)
        self.assertIsNotNone(ngrok_process1)
        self.assertIsNone(ngrok_process1.proc.poll())
        self.assertTrue(ngrok_process1._monitor_thread.is_alive())
        self.assertTrue(urlparse(ngrok_process1.api_url).port, "4040")
        self.assertIsNotNone(ngrok_process2)
        self.assertIsNone(ngrok_process2.proc.poll())
        self.assertTrue(ngrok_process2._monitor_thread.is_alive())
        self.assertTrue(urlparse(ngrok_process2.api_url).port, "4041")
        self.assertIsNotNone(ngrok_process3)
        self.assertIsNone(ngrok_process3.proc.poll())
        self.assertTrue(ngrok_process3._monitor_thread.is_alive())
        self.assertTrue(urlparse(ngrok_process3.api_url).port, "4042")
        self.assertIsNotNone(ngrok_process4)
        self.assertIsNone(ngrok_process4.proc.poll())
        self.assertTrue(ngrok_process4._monitor_thread.is_alive())
        self.assertTrue(urlparse(ngrok_process4.api_url).port, "4043")

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_multiple_processes_same_binary_fails_v2(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v2)
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        ngrok_process1 = process._start_process(self.pyngrok_config_v2)
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(self.pyngrok_config_v2)

        # THEN
        self.assertIn("ngrok is already running", str(cm.exception))
        self.assertIsNotNone(ngrok_process1)
        self.assertIsNone(ngrok_process1.proc.poll())
        self.assertEqual(ngrok_process1, process.get_process(self.pyngrok_config_v2))
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_multiple_processes_same_binary_fails_v3(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v3)
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        ngrok_process1 = process._start_process(self.pyngrok_config_v3)
        with self.assertRaises(PyngrokNgrokError) as cm:
            process._start_process(self.pyngrok_config_v3)

        # THEN
        self.assertIn("ngrok is already running", str(cm.exception))
        self.assertIsNotNone(ngrok_process1)
        self.assertIsNone(ngrok_process1.proc.poll())
        self.assertEqual(ngrok_process1, process.get_process(self.pyngrok_config_v3))
        self.assertEqual(len(process._current_processes.keys()), 1)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_process_logs(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v3)

        # WHEN
        ngrok_process = process._start_process(self.pyngrok_config_v3)

        # THEN
        for log in ngrok_process.logs:
            self.assertIsNotNone(log.t)
            self.assertIsNotNone(log.lvl)
            self.assertIsNotNone(log.msg)

    @mock.patch("subprocess.Popen")
    def test_start_new_session(self, mock_popen):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v3)

        # WHEN
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                start_new_session=True)
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

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_log_event_callback_and_max_logs(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v3)
        log_event_callback_mock = mock.MagicMock()
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3, log_event_callback=log_event_callback_mock,
                                                max_logs=5)

        # WHEN
        ngrok.connect(pyngrok_config=pyngrok_config)
        ngrok_process = ngrok.get_ngrok_process(pyngrok_config)
        time.sleep(1)

        # THEN
        self.assertGreater(log_event_callback_mock.call_count, len(ngrok_process.logs))
        self.assertEqual(len(ngrok_process.logs), 5)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_no_monitor_thread(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v3)
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3,
                                                monitor_thread=False)

        # WHEN
        ngrok.connect(pyngrok_config=pyngrok_config)
        ngrok_process = ngrok.get_ngrok_process(pyngrok_config)

        # THEN
        self.assertIsNone(ngrok_process._monitor_thread)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_stop_monitor_thread(self):
        # GIVEN
        self.given_ngrok_installed(self.pyngrok_config_v3)
        current_process = ngrok.get_ngrok_process(pyngrok_config=self.pyngrok_config_v3)
        public_url = ngrok.connect(urlparse(current_process.api_url).port,
                                   pyngrok_config=self.pyngrok_config_v3).public_url
        ngrok_process = ngrok.get_ngrok_process(self.pyngrok_config_v3)
        monitor_thread = ngrok_process._monitor_thread

        # WHEN
        time.sleep(1)
        self.assertTrue(monitor_thread.is_alive())
        ngrok_process.stop_monitor_thread()
        # Make a request to the tunnel to force a log through, which will allow the thread to trigger its own teardown
        urlopen(f"{public_url}/status").read()
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
        pyngrok_config = self.copy_with_updates(self.pyngrok_config_v3)
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

    def test_start_process_no_binary(self):
        # GIVEN
        self.given_file_doesnt_exist(self.pyngrok_config_v3.ngrok_path)
        self.assertEqual(len(process._current_processes.keys()), 0)

        # WHEN
        with self.assertRaises(PyngrokNgrokError) as cm:
            process.get_process(self.pyngrok_config_v3)

        # THEN
        self.assertIn("ngrok binary was not found", str(cm.exception))
        self.assertEqual(len(process._current_processes.keys()), 0)

    def test_log_parsing(self):
        # GIVEN
        log_line = ("t=2024-03-08T08:45:07-0600 lvl=info msg=\"starting web service\" "
                    "obj=web addr=127.0.0.1:4040 allow_hosts=[]")
        # WHEN
        ngrok_log = NgrokLog(log_line)
        # THEN
        self.assertEqual(ngrok_log.line, log_line)
        self.assertEqual(ngrok_log.t, "2024-03-08T08:45:07-0600")
        self.assertEqual(ngrok_log.lvl, "INFO")
        self.assertEqual(ngrok_log.msg, "starting web service")
        self.assertEqual(ngrok_log.obj, "web")
        self.assertEqual(ngrok_log.addr, "127.0.0.1:4040")

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
        ngrok_log = NgrokLog("lvl=WARN msg=\"Test=This is Tom's test\"")
        # THEN
        self.assertEqual(ngrok_log.lvl, "WARNING")
        self.assertEqual(ngrok_log.msg, "Test=This is Tom's test")

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

        # WHEN
        ngrok_log = NgrokLog("t=123456789")
        # THEN
        self.assertEqual(ngrok_log.t, "123456789")
