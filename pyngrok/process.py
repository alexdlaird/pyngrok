import atexit
import logging
import os
import subprocess
import time

from pyngrok.exception import PyngrokNgrokError

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Alex Laird"
__version__ = "1.3.2"

logger = logging.getLogger(__name__)

CURRENT_PROCESSES = {}


class NgrokProcess:
    """
    An object containing information about the `ngrok` process.

    :var string ngrok_path: The path to the `ngrok` binary used to start this process.
    :var object process: The child process running `ngrok`.
    :var string api_url: The API URL for the `ngrok` web interface.
    """

    def __init__(self, ngrok_path, process, api_url):
        self.ngrok_path = ngrok_path
        self.process = process
        self.api_url = api_url

    def __repr__(self):
        return "<NgrokProcess: \"{}\">".format(self.api_url)

    def __str__(self):  # pragma: no cover
        return "NgrokProcess: \"{}\"".format(self.api_url)


def set_auth_token(ngrok_path, token, config_path=None):
    """
    Set the `ngrok` auth token in the config file, enabling authenticated features (for instance,
    more concurrent tunnels, custom subdomains, etc.).

    :param ngrok_path: The path to the `ngrok` binary.
    :type ngrok_path: string
    :param token: The auth token to set.
    :type token: string
    :param config_path: A config path override.
    :type config_path: string, optional
    """
    start = [ngrok_path, "authtoken", token, "--log=stdout"]
    if config_path:
        start.append("--config={}".format(config_path))

    result = subprocess.check_output(start)

    if "Authtoken saved" not in str(result):
        raise PyngrokNgrokError("An error occurred when saving the auth token: {}".format(result))


def get_process(ngrok_path, config_path=None):
    """
    Retrieve the current `ngrok` process for the given path. If `ngrok` is not currently running for the
    given path, a new process will be started and returned.

    If `ngrok` is not running, calling this method will start a process for the given path.

    :param ngrok_path: The path to the `ngrok` binary.
    :type ngrok_path: string
    :param config_path: A config path override.
    :type config_path: string, optional
    :return: The `ngrok` process.
    :rtype: NgrokProcess
    """
    if ngrok_path in CURRENT_PROCESSES:
        return CURRENT_PROCESSES[ngrok_path]
    else:
        _start_process(ngrok_path, config_path)

        return CURRENT_PROCESSES[ngrok_path]


def run_process(ngrok_path, args):
    """
    Start a blocking `ngrok` process with the given args.

    :param ngrok_path: The path to the `ngrok` binary.
    :type ngrok_path: string
    :param args: The args to pass to `ngrok`.
    :type args: list
    """
    _ensure_path_ready(ngrok_path)

    start = [ngrok_path] + args
    subprocess.call(start)


def kill_process(ngrok_path):
    """
    Terminate any running `ngrok` processes for the given path.

    :param ngrok_path: The path to the `ngrok` binary.
    :type ngrok_path: string
    """
    if ngrok_path in CURRENT_PROCESSES:
        ngrok_process = CURRENT_PROCESSES[ngrok_path]

        logger.debug("Killing ngrok process: {}".format(ngrok_process.process.pid))

        ngrok_process.process.kill()

        del CURRENT_PROCESSES[ngrok_path]


def _ensure_path_ready(ngrok_path):
    """
    Ensure the binary for `ngrok` at the given path is ready to be started, raise a relevant
    exception if not.

    :param ngrok_path: The path to the `ngrok` binary.
    """
    if not os.path.exists(ngrok_path):
        raise PyngrokNgrokError(
            "ngrok binary was not found. Be sure to call `ensure_ngrok_installed()` first for "
            "\"ngrok_path\": {}".format(ngrok_path))

    if ngrok_path in CURRENT_PROCESSES:
        raise PyngrokNgrokError("ngrok is already running for the \"ngrok_path\": {}".format(ngrok_path))


def _terminate_process(process):
    if process is None:
        return

    try:
        process.terminate()
    except OSError:
        logger.info("ngrok process already terminated: {}".format(process.pid))


def _start_process(ngrok_path, config_path=None):
    """
    Start a `ngrok` process with no tunnels. This will start the `ngrok` web interface, against
    which HTTP requests can be made to create, interact with, and destroy tunnels.

    :param ngrok_path: The path to the `ngrok` binary.
    :type ngrok_path: string
    :param config_path: A config path override.
    :type config_path: string, optional
    :return: The `ngrok` process.
    :rtype: NgrokProcess
    """
    _ensure_path_ready(ngrok_path)

    start = [ngrok_path, "start", "--none", "--log=stdout"]
    if config_path:
        logger.debug("Starting ngrok with config file: {}".format(config_path))

        start.append("--config={}".format(config_path))

    process = subprocess.Popen(start, stdout=subprocess.PIPE, universal_newlines=True)
    atexit.register(_terminate_process, process)

    logger.debug("ngrok process started: {}".format(process.pid))

    api_url = None
    tunnel_started = False
    errors = []
    timeout = time.time() + 15
    while time.time() < timeout:
        line = process.stdout.readline()

        if "starting web service" in line:
            api_url = "http://{}".format(line.split("addr=")[1].strip())
        elif "tunnel session started" in line:
            tunnel_started = True
            break
        elif "lvl=error" in line or "lvl=crit" in line:
            errors.append(line.strip())
        elif process.poll() is not None:
            break

    if not api_url or not tunnel_started or len(errors) > 0:
        if len(errors) > 0:
            raise PyngrokNgrokError("The ngrok process was unable to start: {}".format(errors))
        else:
            raise PyngrokNgrokError("The ngrok process was unable to start")

    logger.debug("ngrok web service started: {}".format(api_url))

    ngrok_process = NgrokProcess(ngrok_path, process, api_url)
    CURRENT_PROCESSES[ngrok_path] = ngrok_process

    return ngrok_process
