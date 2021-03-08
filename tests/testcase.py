import logging
import os
import platform
import shutil
import sys
import time
import unittest
import uuid
from functools import wraps

import psutil
from psutil import AccessDenied, NoSuchProcess

from pyngrok import ngrok, installer, conf
from pyngrok import process

__author__ = "Alex Laird"
__copyright__ = "Copyright 2021, Alex Laird"
__version__ = "5.0.4"

from pyngrok.exception import PyngrokNgrokError

logger = logging.getLogger(__name__)
ngrok_logger = logging.getLogger("{}.ngrok".format(__name__))


class NgrokTestCase(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".ngrok2"))
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        config_path = os.path.join(self.config_dir, "config.yml")

        conf.DEFAULT_NGROK_CONFIG_PATH = config_path
        self.pyngrok_config = conf.get_default()
        self.pyngrok_config.config_path = conf.DEFAULT_NGROK_CONFIG_PATH

        installer.DEFAULT_RETRY_COUNT = 1

    def tearDown(self):
        for p in list(process._current_processes.values()):
            try:
                process.kill_process(p.pyngrok_config.ngrok_path)
                p.proc.wait()
            except OSError:
                pass

        ngrok._current_tunnels.clear()

        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)

    @staticmethod
    def given_ngrok_installed(pyngrok_config):
        ngrok.install_ngrok(pyngrok_config)

    @staticmethod
    def given_ngrok_not_installed(ngrok_path):
        if os.path.exists(ngrok_path):
            os.remove(ngrok_path)

    def assertNoZombies(self):
        try:
            self.assertEqual(0, len(
                list(filter(lambda p: p.name() == "ngrok" and p.status() == "zombie", psutil.process_iter()))))
        except (AccessDenied, NoSuchProcess):
            # Some OSes are flaky on this assertion, but that isn't an indication anything is wrong, so pass
            pass

    def get_unique_subdomain(self):
        return "pyngrok-{}-{}-{}-{}{}-tcp".format(uuid.uuid4(), platform.system(),
                                                  platform.python_implementation(), sys.version_info[0],
                                                  sys.version_info[1]).lower()


def retry_connection_reset():
    """
    This decorator can be applied to tests that are flaky due to ngrok failing to reconnect the remote session. The EOF
    error is seen when the ngrok remote host says "failed to reconnect session", which may mean ngrok itself is having
    issues (unrelated to the test, retry), or it can be seen when ngrok is throttling connections from the test account
    (too many consecutive or concurrent connections, slow down and retry). In either case, this decorator will apply a
    delay, backoff, and then retry the test.
    """

    def decorator(func):

        @wraps(func)
        def inner(*args, **kwargs):
            delay = 2
            retries = 3
            while retries > 1:
                try:
                    return func(*args, **kwargs)
                except PyngrokNgrokError as e:
                    # Raise the exception if it's not the specific edge case we're looking for
                    if e.ngrok_error != "EOF":
                        raise e

                    logger.warning("ngrok reset our connection, retrying in {} seconds ...".format(delay))
                    time.sleep(delay)

                    retries -= 1
                    delay *= 2

            return func(*args, **kwargs)

        return inner

    return decorator
