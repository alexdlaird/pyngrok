import json
import logging
import os
import socket
import sys
import uuid

from future.standard_library import install_aliases

from pyngrok import process, conf
from pyngrok.exception import PyngrokNgrokHTTPError, PyngrokNgrokURLError, PyngrokSecurityError, PyngrokError
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
__version__ = "4.1.15"

logger = logging.getLogger(__name__)


class NgrokTunnel:
    """
    An object containing information about a ``ngrok`` tunnel.

    :var name: The name of the tunnel.
    :vartype name: str
    :var proto: A valid `tunnel protocol <https://ngrok.com/docs#tunnel-definitions>`_.
    :vartype proto: str
    :var uri: The tunnel URI, a relative path that can be used to make requests to the ``ngrok`` web interface.
    :vartype uri: str
    :var public_url: The public ``ngrok`` URL.
    :vartype public_url: str
    :var config: The config for the tunnel.
    :vartype config: dict
    :var metrics: Metrics for `the tunnel <https://ngrok.com/docs#list-tunnels>`_.
    :vartype metrics: dict
    :var pyngrok_config: The ``pyngrok`` configuration to use with ``ngrok``.
    :vartype pyngrok_config: PyngrokConfig
    :var api_url: The API URL for the ``ngrok`` web interface.
    :vartype api_url: str
    """

    def __init__(self, data=None, pyngrok_config=None, api_url=None):
        if data is None:
            data = {}
        if pyngrok_config is None:
            pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

        self.name = data.get("name")
        self.proto = data.get("proto")
        self.uri = data.get("uri")
        self.public_url = data.get("public_url")
        self.config = data.get("config", {})
        self.metrics = data.get("metrics", {})
        self.pyngrok_config = pyngrok_config
        self.api_url = api_url

    def __repr__(self):
        return "<NgrokTunnel: \"{}\" -> \"{}\">".format(self.public_url, self.config["addr"]) if self.config.get(
            "addr", None) else "<pending Tunnel>"

    def __str__(self):  # pragma: no cover
        return "NgrokTunnel: \"{}\" -> \"{}\"".format(self.public_url, self.config["addr"]) if self.config.get(
            "addr", None) else "<pending Tunnel>"

    def refresh_metrics(self):
        """
        Refresh the metrics from the tunnel.
        """
        if self.api_url is None:
            raise PyngrokError("\"api_url\" was not initialized with this NgrokTunnel, so this method cannot be used.")

        data = api_request("{}{}".format(self.api_url, self.uri), method="GET", data=None,
                           timeout=self.pyngrok_config.request_timeout)

        if "metrics" not in data:
            raise PyngrokError("The ngrok API did not return \"metrics\" in the response")

        self.metrics = data["metrics"]


def ensure_ngrok_installed(ngrok_path):
    """
    Ensure ``ngrok`` is installed at the given path, downloading and installing the binary for
    the current system if not.

    :param ngrok_path: The path to the ``ngrok`` binary.
    :type ngrok_path: str
    """
    if not os.path.exists(ngrok_path):
        install_ngrok(ngrok_path)

    if not os.path.exists(conf.DEFAULT_NGROK_CONFIG_PATH):
        install_default_config(conf.DEFAULT_NGROK_CONFIG_PATH)


def set_auth_token(token, pyngrok_config=None):
    """
    Set the ``ngrok`` auth token in the config file, enabling authenticated features (for instance,
    more concurrent tunnels, custom subdomains, etc.).

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    :param token: The auth token to set.
    :type token: str
    :param pyngrok_config: The ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        defaults to ``conf.DEFAULT_PYNGROK_CONFIG`` (which can be overridden instead,
        `as shown here <index.html#config-file>`_).
    :type pyngrok_config: PyngrokConfig, optional
    """
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    ensure_ngrok_installed(pyngrok_config.ngrok_path)

    process.set_auth_token(pyngrok_config, token)


def get_ngrok_process(pyngrok_config=None):
    """
    Retrieve the current ``ngrok`` process for the given config's ``ngrok_path``.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param pyngrok_config: The ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        defaults to ``conf.DEFAULT_PYNGROK_CONFIG`` (which can be overridden instead,
        `as shown here <index.html#config-file>`_).
    :type pyngrok_config: PyngrokConfig, optional
    :return: The ``ngrok`` process.
    :rtype: NgrokProcess
    """
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    ensure_ngrok_installed(pyngrok_config.ngrok_path)

    return process.get_process(pyngrok_config)


def connect(port="80", proto="http", name=None, options=None, pyngrok_config=None):
    """
    Establish a new ``ngrok`` tunnel for the given protocol to the given port, returning the connected
    public URL that tunnels to the local port.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
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
    :param pyngrok_config: The ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        defaults to ``conf.DEFAULT_PYNGROK_CONFIG`` (which can be overridden instead,
        `as shown here <index.html#config-file>`_).
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

    tunnel = NgrokTunnel(api_request("{}/api/tunnels".format(api_url), method="POST", data=options,
                                     timeout=pyngrok_config.request_timeout),
                         pyngrok_config=pyngrok_config, api_url=api_url)

    if proto == "http" and not options.get("bind_tls", False):
        tunnel.public_url = tunnel.public_url.replace("https", "http")

    return tunnel.public_url


def disconnect(public_url, pyngrok_config=None):
    """
    Disconnect the ``ngrok`` tunnel for the given URL.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param public_url: The public URL of the tunnel to disconnect.
    :type public_url: str
    :param pyngrok_config: The ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        defaults to ``conf.DEFAULT_PYNGROK_CONFIG`` (which can be overridden instead,
        `as shown here <index.html#config-file>`_).
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
    Retrieve a list of active ``ngrok`` tunnels for the given config's ``ngrok_path``.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param pyngrok_config: The ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        defaults to ``conf.DEFAULT_PYNGROK_CONFIG`` (which can be overridden instead,
        `as shown here <index.html#config-file>`_).
    :type pyngrok_config: PyngrokConfig, optional
    :return: The active ``ngrok`` tunnels.
    :rtype: list[NgrokTunnel]
    """
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    api_url = get_ngrok_process(pyngrok_config).api_url

    tunnels = []
    for tunnel in api_request("{}/api/tunnels".format(api_url), method="GET", data=None,
                              timeout=pyngrok_config.request_timeout)["tunnels"]:
        tunnels.append(NgrokTunnel(tunnel, pyngrok_config=pyngrok_config, api_url=api_url))

    return tunnels


def kill(pyngrok_config=None):
    """
    Terminate the ``ngrok`` processes, if running, for the given config's ``ngrok_path``. This method will not
    block, it will just issue a kill request.

    :param pyngrok_config: The ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        defaults to ``conf.DEFAULT_PYNGROK_CONFIG`` (which can be overridden instead,
        `as shown here <index.html#config-file>`_).
    :type pyngrok_config: PyngrokConfig, optional
    """
    if pyngrok_config is None:
        pyngrok_config = conf.DEFAULT_PYNGROK_CONFIG

    process.kill_process(pyngrok_config.ngrok_path)


def api_request(url, method="GET", data=None, params=None, timeout=4):
    """
    Invoke an API request to the given URL, returning JSON data from the response as a dict.

    One use for this method is making requests to ``ngrok`` tunnels:

    .. code-block:: python

        from pyngrok import ngrok

        public_url = ngrok.connect()
        response = ngrok.api_request("{}/some-route".format(public_url),
                                     method="POST", data={"foo": "bar"})

    Another is making requests to the ``ngrok`` API itself:

    .. code-block:: python

        from pyngrok import ngrok

        api_url = ngrok.get_ngrok_process().api_url
        response = ngrok.api_request("{}/api/requests/http".format(api_url),
                                     params={"tunnel_name": "foo"})

    :param url: The request URL.
    :type url: str
    :param method: The HTTP method.
    :type method: str, optional
    :param data: The request body.
    :type data: dict, optional
    :param params: The URL parameters.
    :type params: dict, optional
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
        logger.debug("Response: {}".format(response_data.strip()))

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
        logger.debug("Response: {}".format(response_data.strip()))

        raise PyngrokNgrokHTTPError("ngrok client exception, API returned {}: {}".format(status_code, response_data),
                                    e.url,
                                    status_code, e.msg, e.hdrs, response_data)
    except URLError as e:
        raise PyngrokNgrokURLError("ngrok client exception, URLError: {}".format(e.reason), e.reason)


def run(args=None):
    """
    Ensure ``ngrok`` is installed in the default location, then call :func:`~pyngrok.process.run_process`.

    This method is meant for interacting with ``ngrok`` from the command line and is not necessarily
    compatible with non-blocking API methods. For that, use :mod:`~pyngrok.ngrok`'s interface methods (like
    :func:`~pyngrok.ngrok.connect`), or use :func:`~pyngrok.process.get_process`.

    :param args: Arguments to be passed to the ``ngrok`` process.
    :type args: list[str], optional
    """
    if args is None:
        args = []

    ensure_ngrok_installed(conf.DEFAULT_NGROK_PATH)

    process.run_process(conf.DEFAULT_NGROK_PATH, args)


def main():
    """
    Entry point for the package's ``console_scripts``. This initializes a call from the command
    line and invokes :func:`~pyngrok.ngrok.run`.

    This method is meant for interacting with ``ngrok`` from the command line and is not necessarily
    compatible with non-blocking API methods. For that, use :mod:`~pyngrok.ngrok`'s interface methods (like
    :func:`~pyngrok.ngrok.connect`), or use :func:`~pyngrok.process.get_process`.
    """
    run(sys.argv[1:])

    if len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1].lstrip("-").lstrip("-") == "help":
        print("\nPYNGROK VERSION:\n   {}".format(__version__))
    elif len(sys.argv) == 2 and sys.argv[1].lstrip("-").lstrip("-") in ["v", "version"]:
        print("pyngrok version {}".format(__version__))


if __name__ == "__main__":
    main()
