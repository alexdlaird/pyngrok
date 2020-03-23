import json
import logging
import os
import socket
import sys
import uuid

from future.standard_library import install_aliases

from pyngrok import process
from pyngrok.exception import PyngrokNgrokHTTPError, PyngrokNgrokURLError, PyngrokSecurityError
from pyngrok.installer import get_ngrok_bin, install_ngrok, install_default_config

install_aliases()

from urllib.parse import urlencode
from urllib.request import urlopen, Request, HTTPError, URLError

try:
    from http import HTTPStatus as StatusCodes
except ImportError:  # pragma: no cover
    try:
        from http import client as StatusCodes
    except ImportError:
        import httplib as StatusCodes

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "2.1.2"

logger = logging.getLogger(__name__)

BIN_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))
DEFAULT_NGROK_PATH = os.path.join(BIN_DIR, get_ngrok_bin())
DEFAULT_CONFIG_PATH = None

_DEFAULT_NGROK_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".ngrok2", "ngrok.yml")


class NgrokTunnel:
    """
    An object containing information about an `ngrok` tunnel.

    :var string name: The name of the tunnel.
    :var string proto: A valid `tunnel protocol <https://ngrok.com/docs#tunnel-definitions>`_.
    :var string uri: The tunnel URI, a relative path that can be used to make requests to the `ngrok` web interface.
    :var string public_url: The public `ngrok` URL.
    :var dict config: The config for the tunnel.
    :var dict metrics: Metrics for `the tunnel <https://ngrok.com/docs#list-tunnels>`_.
    """

    def __init__(self, data=None):
        if data is None:
            data = {}

        self.name = data["name"] if data else None
        self.proto = data["proto"] if data else None
        self.uri = data["uri"] if data else None
        self.public_url = data["public_url"] if data else None
        self.config = data["config"] if data else {}
        self.metrics = data["metrics"] if data else None

    def __repr__(self):
        return "<NgrokTunnel: \"{}\" -> \"{}\">".format(self.public_url, self.config["addr"]) if self.config.get(
            "addr", None) else "<pending Tunnel>"

    def __str__(self):  # pragma: no cover
        return "NgrokTunnel: \"{}\" -> \"{}\"".format(self.public_url, self.config["addr"]) if self.config.get(
            "addr", None) else "<pending Tunnel>"


def ensure_ngrok_installed(ngrok_path):
    """
    Ensure `ngrok` is installed at the given path, downloading and installing the binary for
    the current system if not.

    :param ngrok_path: The path to the `ngrok` binary.
    :type ngrok_path: string
    """
    if not os.path.exists(ngrok_path):
        install_ngrok(ngrok_path)

    if not os.path.exists(_DEFAULT_NGROK_CONFIG_PATH):
        install_default_config(_DEFAULT_NGROK_CONFIG_PATH)


def set_auth_token(token, ngrok_path=None, config_path=None):
    """
    Set the `ngrok` auth token in the config file, enabling authenticated features (for instance,
    more concurrent tunnels, custom subdomains, etc.).

    If `ngrok` is not installed at the given path, calling this method will first download
    and install `ngrok`.

    :param token: The auth token to set.
    :type token: string
    :param ngrok_path: A `ngrok` binary override (instead of using `pyngrok`'s).
    :type ngrok_path: string, optional
    :param config_path: A config path override.
    :type config_path: string, optional
    """
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH
    config_path = config_path if config_path else DEFAULT_CONFIG_PATH

    ensure_ngrok_installed(ngrok_path)

    process.set_auth_token(ngrok_path, token, config_path)


def get_ngrok_process(ngrok_path=None, config_path=None, auth_token=None, region=None):
    """
    Retrieve the current `ngrok` process for the given path.

    If `ngrok` is not installed at the given path, calling this method will first download
    and install `ngrok`.

    If `ngrok` is not running, calling this method will start a process for the given path.

    :param ngrok_path: A `ngrok` binary override (instead of using `pyngrok`'s).
    :type ngrok_path: string, optional
    :param config_path: A config path override. Ignored if `ngrok` is already running.
    :type config_path: string, optional
    :param auth_token: An authtoken override. Ignored if `ngrok` is already running.
    :type auth_token: string, optional
    :param region: A region override. Ignored if `ngrok` is already running.
    :type region: string, optional
    :return: The `ngrok` process.
    :rtype: NgrokProcess
    """
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH
    config_path = config_path if config_path else DEFAULT_CONFIG_PATH

    ensure_ngrok_installed(ngrok_path)

    return process.get_process(ngrok_path, config_path, auth_token, region)


def connect(port=80, proto="http", name=None, options=None, ngrok_path=None, config_path=None, timeout=4,
            auth_token=None, region=None):
    """
    Establish a new `ngrok` tunnel to the given port and protocol, returning the connected
    public URL that tunnels to the local port.

    If `ngrok` is not installed at the given path, calling this method will first download
    and install `ngrok`.

    If `ngrok` is not running, calling this method will start a process for the given path.

    :param port: The local port to which to tunnel, defaults to 80.
    :type port: int, optional
    :param proto: The protocol to tunnel, defaults to "http".
    :type proto: string, optional
    :param name: A friendly name for the tunnel.
    :type name: string, optional
    :param options: Parameters passed to `configuration for the ngrok tunnel <https://ngrok.com/docs#tunnel-definitions>`_.
    :type options: dict, optional
    :param ngrok_path: A `ngrok` binary override (instead of using `pyngrok`'s).
    :type ngrok_path: string, optional
    :param config_path: A config path override. Ignored if `ngrok` is already running.
    :type config_path: string, optional
    :param timeout: The request timeout, in seconds.
    :type timeout: float, optional
    :param auth_token: An authtoken override. Ignored if `ngrok` is already running.
    :type auth_token: string, optional
    :param region: A region override. Ignored if `ngrok` is already running.
    :type region: string, optional
    :return: The connected public URL.
    :rtype: string
    """
    if options is None:
        options = {}

    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH
    config_path = config_path if config_path else DEFAULT_CONFIG_PATH

    config = {
        "name": name if name else str(uuid.uuid4()),
        "addr": str(port),
        "proto": proto
    }
    options.update(config)

    api_url = get_ngrok_process(ngrok_path, config_path, auth_token, region).api_url

    logger.debug("Connecting tunnel with options: {}".format(options))

    tunnel = NgrokTunnel(api_request("{}/api/{}".format(api_url, "tunnels"), "POST", data=options, timeout=timeout))

    if proto == "http" and ("bind_tls" not in options or options["bind_tls"] != False):
        tunnel.public_url = tunnel.public_url.replace("https", "http")

    return tunnel.public_url


def disconnect(public_url, ngrok_path=None, config_path=None, timeout=4):
    """
    Disconnect the `ngrok` tunnel for the given URL.

    If `ngrok` is not installed at the given path, calling this method will first download
    and install `ngrok`.

    If `ngrok` is not running, calling this method will start a process for the given path.

    :param public_url: The public URL of the tunnel to disconnect.
    :type public_url: string
    :param ngrok_path: A `ngrok` binary override (instead of using `pyngrok`'s).
    :type ngrok_path: string, optional
    :param config_path: A config path override.
    :type config_path: string, optional
    :param timeout: The request timeout, in seconds.
    :type timeout: float, optional
    """
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    api_url = get_ngrok_process(ngrok_path, config_path).api_url

    tunnels = get_tunnels(ngrok_path)
    for tunnel in tunnels:
        if tunnel.public_url == public_url:
            logger.debug("Disconnecting tunnel: {}".format(tunnel.public_url))

            api_request("{}{}".format(api_url, tunnel.uri.replace("+", "%20")), "DELETE", timeout=timeout)

            break


def get_tunnels(ngrok_path=None, timeout=4):
    """
    Retrieve a list of all active `ngrok` tunnels.

    If `ngrok` is not installed at the given path, calling this method will first download
    and install `ngrok`.

    If `ngrok` is not running, calling this method will start a process for the given path.

    :param ngrok_path: A `ngrok` binary override (instead of using `pyngrok`'s).
    :type ngrok_path: string, optional
    :param timeout: The request timeout, in seconds.
    :type timeout: float, optional
    :return: The currently active `ngrok` tunnels.
    :rtype: list[NgrokTunnel]
    """
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    api_url = get_ngrok_process(ngrok_path).api_url

    tunnels = []
    for tunnel in api_request("{}/api/{}".format(api_url, "tunnels"), timeout=timeout)["tunnels"]:
        tunnels.append(NgrokTunnel(tunnel))

    return tunnels


def kill(ngrok_path=None):
    """
    Terminate the `ngrok` processes, if running, for the given path. This method will not block, it will just issue
    a kill request.

    :param ngrok_path: A `ngrok` binary override (instead of using `pyngrok`'s).
    :type ngrok_path: string, optional
    """
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    process.kill_process(ngrok_path)


def api_request(url, method="GET", data=None, params=None, timeout=4):
    """
    Invoke an API request to the given URI, returning JSON data from the response as a dict.

    :param url: The request URI.
    :type url: string
    :param method: The HTTP method, defaults to "GET".
    :type method: string, optional
    :param data: The request body.
    :type data: dict, optional
    :param params: The URL parameters.
    :type params: list, optional
    :param timeout: The request timeout, in seconds.
    :type timeout: float, optional
    :return: The response from the request.
    :rtype: dict
    """
    if params is None:
        params = []

    if not url.lower().startswith('http'):
        raise PyngrokSecurityError("URL must start with 'http': {}".format(url))

    data = json.dumps(data).encode("utf-8") if data else None

    if params:
        url += "?{}".format(urlencode([(x, params[x]) for x in params]))

    request = Request(url, method=method.upper())
    request.add_header("Content-Type", "application/json")

    logger.debug("Making {} request to {} with data: {}".format(method, url, data))

    try:
        response = urlopen(request, data, timeout)
        response_data = response.read().decode("utf-8")

        status_code = response.getcode()
        logger.debug("Response status code: {}".format(status_code))
        logger.debug("Response: {}".format(response_data))

        if str(status_code)[0] != "2":
            raise PyngrokNgrokHTTPError("ngrok client API returned {}: {}".format(status_code, response_data), url,
                                        status_code, None, request.headers, response_data)
        elif status_code == StatusCodes.NO_CONTENT:
            return None

        return json.loads(response_data)
    except socket.timeout:
        raise PyngrokNgrokURLError("ngrok client exception, URLError: timed out", "timed out")
    except HTTPError as e:
        response_data = e.read().decode("utf-8")

        status_code = e.getcode()
        logger.debug("Response status code: {}".format(status_code))
        logger.debug("Response: {}".format(response_data))

        raise PyngrokNgrokHTTPError("ngrok client exception, API returned {}: {}".format(status_code, response_data),
                                    e.url,
                                    status_code, e.msg, e.hdrs, response_data)
    except URLError as e:
        raise PyngrokNgrokURLError("ngrok client exception, URLError: {}".format(e.reason), e.reason)


def run(args=None):
    """
    Start a blocking `ngrok` process with the default binary and the system's command line args.

    :param args: Arguments to be passed to the `ngrok` process.
    :type args: list, optional
    """
    if args is None:
        args = []

    ensure_ngrok_installed(DEFAULT_NGROK_PATH)

    process.run_process(DEFAULT_NGROK_PATH, args)


def main():
    """
    Entry point for console_scripts.
    """
    run(sys.argv[1:])

    if len(sys.argv) == 1:
        print("\nPYNGROK VERSION:\n   {}".format(__version__))
    elif len(sys.argv) == 2 and sys.argv[1].lstrip("-").lstrip("-") in ["v", "version"]:
        print("pyngrok version {}".format(__version__))


if __name__ == '__main__':
    main()
