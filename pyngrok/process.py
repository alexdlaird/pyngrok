import atexit
import logging
import os
import shlex
import subprocess
import sys
import threading
import time

import yaml
from future.standard_library import install_aliases

from pyngrok import conf
from pyngrok.exception import PyngrokNgrokError, PyngrokSecurityError
from pyngrok.installer import validate_config

install_aliases()

from urllib.request import urlopen, Request

try:
    from http import HTTPStatus as StatusCodes
except ImportError:  # pragma: no cover
    try:
        from http import client as StatusCodes
    except ImportError:
        import httplib as StatusCodes

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "4.1.9"

logger = logging.getLogger(__name__)

_current_processes = {}


class NgrokProcess:
    """
    An object containing information about the :code:`ngrok` process.

    :var proc: The child process that is running :code:`ngrok`.
    :vartype proc: subprocess.Popen
    :var pyngrok_config: The :code:`pyngrok` configuration to use with :code:`ngrok`.
    :vartype pyngrok_config: PyngrokConfig
    :var api_url: The API URL for the :code:`ngrok` web interface.
    :vartype api_url: str
    :var logs: A list of the most recent logs from :code:`ngrok`, limited in size to :code:`max_logs`.
    :vartype logs: list[NgrokLog]
    :var startup_error: If :code:`ngrok` startup fails, this will be the log of the failure.
    :vartype startup_error: str
    """

    def __init__(self, proc, pyngrok_config):
        self.proc = proc
        self.pyngrok_config = pyngrok_config

        self.api_url = None
        self.logs = []
        self.startup_error = None

        self._tunnel_started = False
        self._client_connected = False
        self._monitor_thread = None

    def __repr__(self):
        return "<NgrokProcess: \"{}\">".format(self.api_url)

    def __str__(self):  # pragma: no cover
        return "NgrokProcess: \"{}\"".format(self.api_url)

    @staticmethod
    def _line_has_error(log):
        return log.lvl in ["ERROR", "CRITICAL"]

    def _log_startup_line(self, line):
        """
        Parse the given startup log line and use it to manage the startup state
        of the :code:`ngrok` process.

        :param line: The line to be parsed and logged.
        :type line: str
        :return: The parsed log.
        :rtype: NgrokLog
        """
        log = self._log_line(line)

        if log is None:
            return
        elif self._line_has_error(log):
            self.startup_error = log.err
        else:
            # Log `ngrok` startup states as they come in
            if "starting web service" in log.msg and log.addr is not None:
                self.api_url = "http://{}".format(log.addr)
            elif "tunnel session started" in log.msg:
                self._tunnel_started = True
            elif "client session established" in log.msg:
                self._client_connected = True

        return log

    def _log_line(self, line):
        """
        Parse, log, and emit (if :code:`log_event_callback` in :class:`~pyngrok.conf.PyngrokConfig` is registered) the
        given log line.

        :param line: The line to be processed.
        :type line: str
        :return: The parsed log.
        :rtype: NgrokLog
        """
        log = NgrokLog(line)

        if log.line == "":
            return None

        logger.log(getattr(logging, log.lvl), line)
        self.logs.append(log)
        if len(self.logs) > self.pyngrok_config.max_logs:
            self.logs.pop(0)

        if self.pyngrok_config.log_event_callback is not None:
            self.pyngrok_config.log_event_callback(log)

        return log

    def healthy(self):
        """
        Check whether the :code:`ngrok` process has finished starting up and is in a running, healthy state.

        :return: :code:`True` if the :code:`ngrok` process is started, running, and healthy, :code:`False` otherwise.
        :rtype: bool
        """
        if self.api_url is None or \
                not self._tunnel_started or not self._client_connected:
            return False

        if not self.api_url.lower().startswith("http"):
            raise PyngrokSecurityError("URL must start with \"http\": {}".format(self.api_url))

        # Ensure the process is available for requests before registering it as healthy
        request = Request("{}/api/tunnels".format(self.api_url))
        response = urlopen(request)
        if response.getcode() != StatusCodes.OK:
            return False

        return self.proc.poll() is None and \
               self.startup_error is None

    def _monitor_process(self):
        thread = threading.current_thread()

        thread.alive = True
        while thread.alive and self.proc.poll() is None:
            self._log_line(self.proc.stdout.readline())

        self._monitor_thread = None

    def start_monitor_thread(self):
        """
        Start a thread that will monitor the :code:`ngrok` process and its logs until it completes.

        If a monitor thread is already running, nothing will be done.
        """
        if self._monitor_thread is None:
            self._monitor_thread = threading.Thread(target=self._monitor_process)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()

    def stop_monitor_thread(self):
        """
        Set the monitor thread to stop monitoring the :code:`ngrok` process after the next log event. This will not
        necessarily terminate the thread immediately, as the thread may currently be idle, rather it sets a flag
        on the thread telling it to terminate the next time it wakes up.

        This has no impact on the :code:`ngrok` process itself, only :code:`pyngrok`'s monitor of the process and
        its logs.
        """
        if self._monitor_thread is not None:
            self._monitor_thread.alive = False


class NgrokLog:
    """
    An object containing a parsed log from the :code:`ngrok` process.

    :var line: The raw, unparsed log line.
    :vartype line: str
    :var t: The log's ISO 8601 timestamp.
    :vartype t: str
    :var lvl: The log's level.
    :vartype lvl: str
    :var msg: The log's message.
    :vartype msg: str
    :var err: The log's error, if applicable.
    :vartype err: str
    :var addr: The URL, if :code:`obj` is "web".
    :vartype addr: str
    """

    def __init__(self, line):
        self.line = line.strip()
        self.t = None
        self.lvl = "NOTSET"
        self.msg = None
        self.err = None
        self.addr = None

        for i in shlex.split(self.line):
            if "=" not in i:
                continue

            key, value = i.split("=", 1)

            if key == "lvl":
                if not value:
                    value = self.lvl

                value = value.upper()
                if value == "CRIT":
                    value = "CRITICAL"
                elif value in ["ERR", "EROR"]:
                    value = "ERROR"
                elif value == "WARN":
                    value = "WARNING"

                if not hasattr(logging, value):
                    value = self.lvl

            setattr(self, key, value)

    def __repr__(self):
        return "<NgrokLog: t={} lvl={} msg=\"{}\">".format(self.t, self.lvl, self.msg)

    def __str__(self):  # pragma: no cover
        attrs = [attr for attr in dir(self) if not attr.startswith("_") and getattr(self, attr) is not None]
        attrs.remove("line")

        return " ".join("{}=\"{}\"".format(attr, getattr(self, attr)) for attr in attrs)


def set_auth_token(pyngrok_config, token):
    """
    Set the :code:`ngrok` auth token in the config file, enabling authenticated features (for instance,
    more concurrent tunnels, custom subdomains, etc.).

    :param pyngrok_config: The :code:`pyngrok` configuration to use when interacting with the :code:`ngrok` binary.
    :type pyngrok_config: PyngrokConfig
    :param token: The auth token to set.
    :type token: str
    """
    start = [pyngrok_config.ngrok_path, "authtoken", token, "--log=stdout"]
    if pyngrok_config.config_path:
        start.append("--config={}".format(pyngrok_config.config_path))

    result = subprocess.check_output(start)

    if "Authtoken saved" not in str(result):
        raise PyngrokNgrokError("An error occurred when saving the auth token: {}".format(result))


def get_process(pyngrok_config):
    """
    Retrieve the current :code:`ngrok` process for the given config's :code:`ngrok_path`.

    If :code:`ngrok` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param pyngrok_config: The :code:`pyngrok` configuration to use when interacting with the :code:`ngrok` binary.
    :type pyngrok_config: PyngrokConfig
    :return: The :code:`ngrok` process.
    :rtype: NgrokProcess
    """
    if pyngrok_config.ngrok_path in _current_processes:
        # Ensure the process is still running and hasn't been killed externally
        if _current_processes[pyngrok_config.ngrok_path].proc.poll() is None:
            return _current_processes[pyngrok_config.ngrok_path]
        else:
            _current_processes.pop(pyngrok_config.ngrok_path, None)

    return _start_process(pyngrok_config)


def run_process(ngrok_path, args):
    """
    Start a blocking :code:`ngrok` process with the given args.

    :param ngrok_path: The path to the :code:`ngrok` binary.
    :type ngrok_path: str
    :param args: The args to pass to :code:`ngrok`.
    :type args: list[str]
    """
    _ensure_path_ready(ngrok_path)

    start = [ngrok_path] + args
    subprocess.call(start)


def kill_process(ngrok_path):
    """
    Terminate the :code:`ngrok` processes, if running, for the given path. This method will not block, it will just
    issue a kill request.

    :param ngrok_path: The path to the :code:`ngrok` binary.
    :type ngrok_path: str
    """
    if ngrok_path in _current_processes:
        ngrok_process = _current_processes[ngrok_path]

        logger.info("Killing ngrok process: {}".format(ngrok_process.proc.pid))

        try:
            ngrok_process.proc.kill()
            ngrok_process.proc.wait()
        except OSError as e:
            # If the process was already killed, nothing to do but cleanup state
            if e.errno != 3:
                raise e

        _current_processes.pop(ngrok_path, None)
    else:
        logger.debug("\"ngrok_path\" {} is not running a process".format(ngrok_path))


def _ensure_path_ready(ngrok_path):
    """
    Ensure the binary for :code:`ngrok` at the given path is ready to be started, raise a relevant
    exception if not.

    :param ngrok_path: The path to the :code:`ngrok` binary.
    """
    if not os.path.exists(ngrok_path):
        raise PyngrokNgrokError(
            "ngrok binary was not found. Be sure to call \"ngrok.ensure_ngrok_installed()\" first for "
            "\"ngrok_path\": {}".format(ngrok_path))

    if ngrok_path in _current_processes:
        raise PyngrokNgrokError("ngrok is already running for the \"ngrok_path\": {}".format(ngrok_path))


def _validate_config(config_path):
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    if config is not None:
        validate_config(config)


def _terminate_process(process):
    if process is None:
        return

    try:
        process.terminate()
    except OSError:
        logger.debug("ngrok process already terminated: {}".format(process.pid))


def _start_process(pyngrok_config):
    """
    Start a :code:`ngrok` process with no tunnels. This will start the :code:`ngrok` web interface, against
    which HTTP requests can be made to create, interact with, and destroy tunnels.

    :param pyngrok_config: The :code:`pyngrok` configuration to use when interacting with the :code:`ngrok` binary.
    :type pyngrok_config: PyngrokConfig
    :return: The :code:`ngrok` process.
    :rtype: NgrokProcess
    """
    _ensure_path_ready(pyngrok_config.ngrok_path)
    if pyngrok_config.config_path is not None:
        _validate_config(pyngrok_config.config_path)
    else:
        _validate_config(conf.DEFAULT_NGROK_CONFIG_PATH)

    start = [pyngrok_config.ngrok_path, "start", "--none", "--log=stdout"]
    if pyngrok_config.config_path:
        logger.info("Starting ngrok with config file: {}".format(pyngrok_config.config_path))
        start.append("--config={}".format(pyngrok_config.config_path))
    if pyngrok_config.auth_token:
        logger.info("Overriding default auth token")
        start.append("--authtoken={}".format(pyngrok_config.auth_token))
    if pyngrok_config.region:
        logger.info("Starting ngrok in region: {}".format(pyngrok_config.region))
        start.append("--region={}".format(pyngrok_config.region))

    popen_kwargs = {"stdout": subprocess.PIPE, "universal_newlines": True}
    if sys.version_info.major >= 3 and os.name == "posix":
        popen_kwargs.update(start_new_session=pyngrok_config.start_new_session)
    elif pyngrok_config.start_new_session:
        logger.warning("Ignoring start_new_session=True, which requires Python 3 and POSIX")
    proc = subprocess.Popen(start, **popen_kwargs)
    atexit.register(_terminate_process, proc)

    logger.info("ngrok process starting: {}".format(proc.pid))

    ngrok_process = NgrokProcess(proc, pyngrok_config)
    _current_processes[pyngrok_config.ngrok_path] = ngrok_process

    timeout = time.time() + pyngrok_config.startup_timeout
    while time.time() < timeout:
        line = proc.stdout.readline()
        ngrok_process._log_startup_line(line)

        if ngrok_process.healthy():
            logger.info("ngrok process has started: {}".format(ngrok_process.api_url))

            if pyngrok_config.monitor_thread:
                ngrok_process.start_monitor_thread()

            break
        elif ngrok_process.startup_error is not None or \
                ngrok_process.proc.poll() is not None:
            break

    if not ngrok_process.healthy():
        # If the process did not come up in a healthy state, clean up the state
        kill_process(pyngrok_config.ngrok_path)

        if ngrok_process.startup_error is not None:
            raise PyngrokNgrokError("The ngrok process errored on start: {}.".format(ngrok_process.startup_error),
                                    ngrok_process.logs,
                                    ngrok_process.startup_error)
        else:
            raise PyngrokNgrokError("The ngrok process was unable to start.", ngrok_process.logs)

    return ngrok_process
