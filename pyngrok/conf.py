import os

from pyngrok.installer import get_ngrok_bin

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "4.1.13"

BIN_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))
DEFAULT_NGROK_PATH = os.path.join(BIN_DIR, get_ngrok_bin())
DEFAULT_CONFIG_PATH = None

DEFAULT_NGROK_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".ngrok2", "ngrok.yml")


class PyngrokConfig:
    """
    An object containing ``pyngrok``'s configuration for interacting with the ``ngrok`` binary. All values are
    optional when it is instantiated, and default values will be used for parameters not passed.

    On import, ``conf.DEFAULT_PYNGROK_CONFIG`` is instantiated to a :class:`~pyngrok.conf.PyngrokConfig` with default values. When ``pyngrok_config`` is
    not passed to methods in :mod:`~pyngrok.ngrok`, this default will be used.

    :var ngrok_path: The path to the ``ngrok`` binary, defaults to the value in
        `conf.DEFAULT_NGROK_PATH <index.html#config-file>`_
    :vartype ngrok_path: str
    :var config_path: The path to the ``ngrok`` config, defaults to ``None`` and ``ngrok`` manages it.
    :vartype config_path: str
    :var auth_token: An authtoken to pass to commands (overrides what is in the config).
    :vartype auth_token: str
    :var region: The region in which ``ngrok`` should start.
    :vartype region: str
    :var monitor_thread: Whether ``ngrok`` should continue to be monitored (for logs, etc.) after it startup
        is complete.
    :vartype monitor_thread: bool
    :var log_event_callback: A callback that will be invoked each time ``ngrok`` emits a log. ``monitor_thread``
        must be set to ``True`` or the function will stop being called after ``ngrok`` finishes starting.
    :vartype log_event_callback: types.FunctionType
    :var startup_timeout: The max number of seconds to wait for ``ngrok`` to start before timing out.
    :vartype startup_timeout: int
    :var max_logs: The max number of logs to store in :class:`~pyngrok.process.NgrokProcess`'s ``logs`` variable.
    :vartype max_logs: int
    :var request_timeout: The max timeout when making requests to ``ngrok``'s API.
    :vartype request_timeout: float
    :var start_new_session: Passed to :py:class:`subprocess.Popen` when launching ``ngrok``. (Python 3 and POSIX only)
    :vartype start_new_session: bool
    """

    def __init__(self,
                 ngrok_path=None,
                 config_path=None,
                 auth_token=None,
                 region=None,
                 monitor_thread=True,
                 log_event_callback=None,
                 startup_timeout=15,
                 max_logs=100,
                 request_timeout=4,
                 start_new_session=False):
        self.ngrok_path = DEFAULT_NGROK_PATH if ngrok_path is None else ngrok_path
        self.config_path = DEFAULT_CONFIG_PATH if config_path is None else config_path
        self.auth_token = auth_token
        self.region = region
        self.monitor_thread = monitor_thread
        self.log_event_callback = log_event_callback
        self.startup_timeout = startup_timeout
        self.max_logs = max_logs
        self.request_timeout = request_timeout
        self.start_new_session = start_new_session


DEFAULT_PYNGROK_CONFIG = PyngrokConfig()
