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
    Pyngrok's configuration for interacting with `ngrok`. All values are optional and will use default values if
    nothing is given.

    :var string ngrok_path: A `ngrok` binary to use (only needed if `pyngrok`'s should not be used).
    :var string config_path: A config path override.
    :var string auth_token: An authtoken override.
    :var string region: A region override.
    :var bool keep_thread_alive: Whether or not the `ngrok` process should continue to be monitored in a separate thread after
        it has finished starting, defaults to True.
    :var function log_func: A callback that will be invoked each time `ngrok` emits a log.
    :var int boot_timeout: The max number of seconds to wait for `ngrok` to start before timing out.
    :var int max_logs: The maximum number of logs to store in NgrokProcess's logs variable.
    :var int request_timeout: The max timeout when making requests to `ngrok`'s API.
    """

    def __init__(self,
                 ngrok_path=DEFAULT_NGROK_PATH,
                 config_path=DEFAULT_CONFIG_PATH,
                 auth_token=None,
                 region=None,
                 keep_thread_alive=True,
                 log_func=None,
                 boot_timeout=15,
                 max_logs=500,
                 request_timeout=4):
        self.ngrok_path = ngrok_path
        self.config_path = config_path
        self.auth_token = auth_token
        self.region = region
        self.keep_thread_alive = keep_thread_alive
        self.log_func = log_func
        self.boot_timeout = boot_timeout
        self.max_logs = max_logs
        self.request_timeout = request_timeout
