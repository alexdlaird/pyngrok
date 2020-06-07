__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "4.0.0"

import os

from pyngrok.installer import get_ngrok_bin

BIN_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))
DEFAULT_NGROK_PATH = os.path.join(BIN_DIR, get_ngrok_bin())
DEFAULT_CONFIG_PATH = None


class PyngrokConfig:
    """
    An object containing Pyngrok's configuration for interacting with the `ngrok` binary. All values are optional when
    instantiating an object, and default values will be used instead for that parameter.

    :var ngrok_path: A `ngrok` binary override.
    :vartype ngrok_path: str
    :var config_path: A config path override.
    :vartype config_path: str
    :var auth_token: An authtoken override.
    :vartype auth_token: str
    :var region: A region override.
    :vartype region: str
    :var keep_thread_alive: Whether or not the `ngrok` process should continue to be monitored in a separate thread
        after it has finished starting.
    :vartype keep_thread_alive: bool
    :var log_func: A callback that will be invoked each time `ngrok` emits a log. `keep_thread_alive` must be
        True for the function to continue to be called after `ngrok` finishes starting.
    :vartype log_func: function
    :var boot_timeout: The max number of seconds to wait for `ngrok` to start before timing out.
    :vartype boot_timeout: int
    :var max_logs: The max number of logs to store in NgrokProcess's logs variable.
    :vartype max_logs: int
    :var request_timeout: The max timeout when making requests to `ngrok`'s API.
    :vartype request_timeout: float
    """

    def __init__(self,
                 ngrok_path=None,
                 config_path=None,
                 auth_token=None,
                 region=None,
                 keep_thread_alive=True,
                 log_func=None,
                 boot_timeout=15,
                 max_logs=500,
                 request_timeout=4):
        self.ngrok_path = DEFAULT_NGROK_PATH if ngrok_path is None else ngrok_path
        self.config_path = DEFAULT_CONFIG_PATH if config_path is None else config_path
        self.auth_token = auth_token
        self.region = region
        self.keep_thread_alive = keep_thread_alive
        self.log_func = log_func
        self.boot_timeout = boot_timeout
        self.max_logs = max_logs
        self.request_timeout = request_timeout
