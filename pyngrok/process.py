import atexit
import logging
import os
import subprocess
import time

from pyngrok.exception import PyngrokNgrokError

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.4.3"

logger = logging.getLogger(__name__)

_current_processes = {}


class NgrokProcess:
    """
    An object containing information about the `ngrok` process.

    :var string ngrok_path: The path to the `ngrok` binary used to start this process.
    :var string config_path: The path to the `ngrok` config used.
    :var object proc: The child `subprocess.Popen <https://docs.python.org/3/library/subprocess.html#subprocess.Popen>`_ that is running `ngrok`.
    :var string api_url: The API URL for the `ngrok` web interface.
    """

    def __init__(self, ngrok_path, config_path, proc, api_url):
        self.ngrok_path = ngrok_path
        self.config_path = config_path
        self.proc = proc
        self.api_url = api_url

        # Legacy, maintained for backwards compatibility, but use should be avoided as it shadows the module name.
        self.process = proc

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
    if ngrok_path in _current_processes:
        # Ensure the process is still running and hasn't been killed externally
        if _current_processes[ngrok_path].process.poll() is None:
            return _current_processes[ngrok_path]
        else:
            _current_processes.pop(ngrok_path, None)

    return _start_process(ngrok_path, config_path)


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
    Terminate the `ngrok` processes, if running, for the given path. This method will not block, it will just issue
    a kill request.

    :param ngrok_path: The path to the `ngrok` binary.
    :type ngrok_path: string
    """
    if ngrok_path in _current_processes:
        ngrok_process = _current_processes[ngrok_path]

        logger.info("Killing ngrok process: {}".format(ngrok_process.process.pid))

        try:
            ngrok_process.process.kill()
        except OSError as e:
            # If the process was already killed, nothing to do but cleanup state
            if e.errno != 3:
                raise e

        _current_processes.pop(ngrok_path, None)
    else:
        logger.debug("\"ngrok_path\" {} is not running a process".format(ngrok_path))


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

    if ngrok_path in _current_processes:
        raise PyngrokNgrokError("ngrok is already running for the \"ngrok_path\": {}".format(ngrok_path))


def _terminate_process(process):
    if process is None:
        return

    try:
        process.terminate()
    except OSError:
        logger.debug("ngrok process already terminated: {}".format(process.pid))


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
        logger.info("Starting ngrok with config file: {}".format(config_path))

        start.append("--config={}".format(config_path))

    process = subprocess.Popen(start, stdout=subprocess.PIPE, universal_newlines=True)
    atexit.register(_terminate_process, process)

    logger.info("ngrok process started: {}".format(process.pid))

    api_url = None
    tunnel_started = False
    errors = []
    timeout = time.time() + 15
    while time.time() < timeout:
        line = process.stdout.readline()
        logger.debug(line)

        if "starting web service" in line:
            api_url = "http://{}".format(line.split("addr=")[1].strip())
        elif "tunnel session started" in line:
            tunnel_started = True
            break
        elif "lvl=error" in line or "lvl=crit" in line or ("err=" in line and "err=nil" not in line):
            errors.append(line.strip())
        elif process.poll() is not None:
            break

    if not api_url or not tunnel_started or len(errors) > 0:
        raise PyngrokNgrokError("The ngrok process was unable to start.", errors)

    logger.info("ngrok web service started: {}".format(api_url))

    ngrok_process = NgrokProcess(ngrok_path, config_path, process, api_url)
    _current_processes[ngrok_path] = ngrok_process

    return ngrok_process
