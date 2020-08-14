import json
import logging
import os
import socket
import sys
import uuid

from future.standard_library import install_aliases

from pyngrok import process, conf
from pyngrok.exception import PyngrokNgrokHTTPError, PyngrokNgrokURLError, PyngrokSecurityError
from pyngrok.installer import install_ngrok, install_default_config

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
__version__ = "4.1.10"

logger = logging.getLogger(__name__)


class NgrokTunnel:
    """
    An object containing information about a :code:`ngrok` tunnel.

    :var name: The name of the tunnel.
    :vartype name: str
    :var proto: A valid `tunnel protocol <https://ngrok.com/docs#tunnel-definitions>`_.
    :vartype proto: str
    :var uri: The tunnel URI, a relative path that can be used to make requests to the :code:`ngrok` web interface.
    :vartype uri: str
    :var public_url: The public :code:`ngrok` URL.
    :vartype public_url: str
    :var config: The config for the tunnel.
    :vartype config: dict
    :var metrics: Metrics for `the tunnel <https://ngrok.com/docs#list-tunnels>`_.
    :vartype metrics: dict
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
    Ensure :code:`ngrok` is installed at the given path, downloading and installing the binary for
    the current system if not.

    :param ngrok_path: The path to the :code:`ngrok` binary.
    :type ngrok_path: str
    """
    if not os.path.exists(ngrok_path):
        install_ngrok(ngrok_path)

    if not os.path.exists(conf.DEFAULT_NGROK_CONFIG_PATH):
        install_default_config(conf.DEFAULT_NGROK_CONFIG_PATH)


def set_auth_token(token, pyngrok_config=None):
    """
    Set the :code:`ngrok` auth token in the config file, enabling authenticated features (for instance,
    more concurrent tunnels, custom subdomains, etc.).

    If :code:`ngrok` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s :code:`ngrok_path`, calling this method
    will first download and install :code:`ngrok`.

    :param token: The auth token to set.
    :type token: str
    :param pyngrok_config: The :code:`pyngrok` configuration to use when interacting with the :code:`ngrok` binary.
    :type pyngrok_config: PyngrokConfig, optional
    """
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    ensure_ngrok_installed(pyngrok_config.ngrok_path)

    process.set_auth_token(pyngrok_config, token)


def get_ngrok_process(pyngrok_config=None):
    """
    Retrieve the current :code:`ngrok` process for the given config's :code:`ngrok_path`.

    If :code:`ngrok` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s :code:`ngrok_path`, calling this method
    will first download and install :code:`ngrok`.

    If :code:`ngrok` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param pyngrok_config: The :code:`pyngrok` configuration to use when interacting with the :code:`ngrok` binary.
    :type pyngrok_config: PyngrokConfig, optional
    :return: The :code:`ngrok` process.
    :rtype: NgrokProcess
    """
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    ensure_ngrok_installed(pyngrok_config.ngrok_path)

    return process.get_process(pyngrok_config)


def connect(port="80", proto="http", name=None, options=None, pyngrok_config=None):
    """
    Establish a new :code:`ngrok` tunnel to the given port and protocol, returning the connected
    public URL that tunnels to the local port.

    If :code:`ngrok` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s :code:`ngrok_path`, calling this method
    will first download and install :code:`ngrok`.

    If :code:`ngrok` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param port: The local port to which the tunnel will forward traffic, defaults to "80". Can also be
        a `local directory or network address <https://ngrok.com/docs#http-file-urls>`_.
    :type port: str, optional
    :param proto: The protocol to tunnel, defaults to "http".
    :type proto: str, optional
    :param name: A friendly name for the tunnel.
    :type name: str, optional
    :param options: Parameters passed to `configuration for the ngrok
        tunnel <https://ngrok.com/docs#tunnel-definitions>`_.
    :type options: dict[str, str], optional
    :param pyngrok_config: The :code:`pyngrok` configuration to use when interacting with the :code:`ngrok` binary.
    :type pyngrok_config: PyngrokConfig, optional
    :return: The connected public URL.
    :rtype: str
    """
    if options is None:
        options = {}
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    port = str(port)
    if not name:
        if not port.startswith("file://"):
            name = "{}-{}-{}".format(proto, port, uuid.uuid4())
        else:
            name = "{}-file-{}".format(proto, uuid.uuid4())

    config = {
        "name": name,
        "addr": port,
        "proto": proto
    }
    options.update(config)

    api_url = get_ngrok_process(pyngrok_config).api_url

    logger.debug("Connecting tunnel with options: {}".format(options))

    tunnel = NgrokTunnel(api_request("{}/api/{}".format(api_url, "tunnels"), method="POST", data=options,
                                     timeout=pyngrok_config.request_timeout))

    if proto == "http" and not options.get("bind_tls", False):
        tunnel.public_url = tunnel.public_url.replace("https", "http")

    return tunnel.public_url


def disconnect(public_url, pyngrok_config=None):
    """
    Disconnect the :code:`ngrok` tunnel for the given URL.

    If :code:`ngrok` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s :code:`ngrok_path`, calling this method
    will first download and install :code:`ngrok`.

    If :code:`ngrok` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param public_url: The public URL of the tunnel to disconnect.
    :type public_url: str
    :param pyngrok_config: The :code:`pyngrok` configuration to use when interacting with the :code:`ngrok` binary.
    :type pyngrok_config: PyngrokConfig, optional
    """
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    api_url = get_ngrok_process(pyngrok_config).api_url

    tunnels = get_tunnels(pyngrok_config)
    for tunnel in tunnels:
        if tunnel.public_url == public_url:
            logger.debug("Disconnecting tunnel: {}".format(tunnel.public_url))

            api_request("{}{}".format(api_url, tunnel.uri), method="DELETE",
                        timeout=pyngrok_config.request_timeout)

            break


def get_tunnels(pyngrok_config=None):
    """
    Retrieve a list of active :code:`ngrok` tunnels for the given config's :code:`ngrok_path`.

    If :code:`ngrok` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s :code:`ngrok_path`, calling this method
    will first download and install :code:`ngrok`.

    If :code:`ngrok` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param pyngrok_config: The :code:`pyngrok` configuration to use when interacting with the :code:`ngrok` binary.
    :type pyngrok_config: PyngrokConfig, optional
    :return: The active :code:`ngrok` tunnels.
    :rtype: list[NgrokTunnel]
    """
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    api_url = get_ngrok_process(pyngrok_config).api_url

    tunnels = []
    for tunnel in api_request("{}/api/{}".format(api_url, "tunnels"), method="GET", data=None,
                              timeout=pyngrok_config.request_timeout)["tunnels"]:
        tunnels.append(NgrokTunnel(tunnel))

    return tunnels


def kill(pyngrok_config=None):
    """
    Terminate the :code:`ngrok` processes, if running, for the given config's :code:`ngrok_path`. This method will not
    block, it will just issue a kill request.

    :param pyngrok_config: The :code:`pyngrok` configuration to use when interacting with the :code:`ngrok` binary.
    :type pyngrok_config: PyngrokConfig, optional
    """
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    process.kill_process(pyngrok_config.ngrok_path)


def api_request(url, method="GET", data=None, params=None, timeout=4):
    """
    Invoke an API request to the given URI, returning JSON data from the response as a dict.

    :param url: The request URL.
    :type url: str
    :param method: The HTTP method.
    :type method: str, optional
    :param data: The request body.
    :type data: dict, optional
    :param params: The URL parameters.
    :type params: list[str], optional
    :param timeout: The request timeout, in seconds.
    :type timeout: float, optional
    :return: The response from the request.
    :rtype: dict
    """
    if params is None:
        params = []

    if not url.lower().startswith("http"):
        raise PyngrokSecurityError("URL must start with \"http\": {}".format(url))

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
    Start a blocking :code:`ngrok` process with the default binary and the passed args.

    :param args: Arguments to be passed to the :code:`ngrok` process.
    :type args: list[str], optional
    """
    if args is None:
        args = []

    ensure_ngrok_installed(conf.DEFAULT_NGROK_PATH)

    process.run_process(conf.DEFAULT_NGROK_PATH, args)


def main():
    """
    Entry point for the package's :code:`console_scripts`.
    """
    run(sys.argv[1:])

    if len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1].lstrip("-").lstrip("-") == "help":
        print("\nPYNGROK VERSION:\n   {}".format(__version__))
    elif len(sys.argv) == 2 and sys.argv[1].lstrip("-").lstrip("-") in ["v", "version"]:
        print("pyngrok version {}".format(__version__))


if __name__ == "__main__":
    main()
