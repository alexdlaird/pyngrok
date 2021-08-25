import json
import logging
import os
import socket
import sys
import uuid
from http import HTTPStatus
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from pyngrok import process, conf, installer
from pyngrok.exception import PyngrokNgrokHTTPError, PyngrokNgrokURLError, PyngrokSecurityError, PyngrokError

__author__ = "Alex Laird"
__copyright__ = "Copyright 2021, Alex Laird"
__version__ = "5.1.0"

logger = logging.getLogger(__name__)

_current_tunnels = {}


class NgrokTunnel:
    """
    An object containing information about a ``ngrok`` tunnel.

    :var data: The original tunnel data.
    :vartype data: dict
    :var name: The name of the tunnel.
    :vartype name: str
    :var proto: The protocol of the tunnel.
    :vartype proto: str
    :var uri: The tunnel URI, a relative path that can be used to make requests to the ``ngrok`` web interface.
    :vartype uri: str
    :var public_url: The public ``ngrok`` URL.
    :vartype public_url: str
    :var config: The config for the tunnel.
    :vartype config: dict
    :var metrics: Metrics for `the tunnel <https://ngrok.com/docs#list-tunnels>`_.
    :vartype metrics: dict
    :var pyngrok_config: The ``pyngrok`` configuration to use when interacting with the ``ngrok``.
    :vartype pyngrok_config: PyngrokConfig
    :var api_url: The API URL for the ``ngrok`` web interface.
    :vartype api_url: str
    """

    def __init__(self, data, pyngrok_config, api_url):
        self.data = data

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
        Get the latest metrics for the tunnel and update the ``metrics`` variable.
        """
        logger.info("Refreshing metrics for tunnel: {}".format(self.public_url))

        data = api_request("{}{}".format(self.api_url, self.uri), method="GET",
                           timeout=self.pyngrok_config.request_timeout)

        if "metrics" not in data:
            raise PyngrokError("The ngrok API did not return \"metrics\" in the response")

        self.data["metrics"] = data["metrics"]
        self.metrics = self.data["metrics"]


def install_ngrok(pyngrok_config=None):
    """
    Download, install, and initialize ``ngrok`` for the given config. If ``ngrok`` and its default
    config is already installed, calling this method will do nothing.

    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    if not os.path.exists(pyngrok_config.ngrok_path):
        installer.install_ngrok(pyngrok_config.ngrok_path)

    # If no config_path is set, ngrok will use its default path
    if pyngrok_config.config_path is not None:
        config_path = pyngrok_config.config_path
    else:
        config_path = conf.DEFAULT_NGROK_CONFIG_PATH

    # Install the config to the requested path
    if not os.path.exists(config_path):
        installer.install_default_config(config_path)

    # Install the default config, even if we don't need it this time, if it doesn't already exist
    if conf.DEFAULT_NGROK_CONFIG_PATH != config_path and \
            not os.path.exists(conf.DEFAULT_NGROK_CONFIG_PATH):
        installer.install_default_config(conf.DEFAULT_NGROK_CONFIG_PATH)


def set_auth_token(token, pyngrok_config=None):
    """
    Set the ``ngrok`` auth token in the config file, enabling authenticated features (for instance,
    more concurrent tunnels, custom subdomains, etc.).

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    :param token: The auth token to set.
    :type token: str
    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    install_ngrok(pyngrok_config)

    process.set_auth_token(pyngrok_config, token)


def get_ngrok_process(pyngrok_config=None):
    """
    Get the current ``ngrok`` process for the given config's ``ngrok_path``.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    Use :func:`~pyngrok.process.is_process_running` to check if a process is running without also implicitly
    installing and starting it.

    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    :return: The ``ngrok`` process.
    :rtype: NgrokProcess
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    install_ngrok(pyngrok_config)

    return process.get_process(pyngrok_config)


def connect(addr=None, proto=None, name=None, pyngrok_config=None, **options):
    """
    Establish a new ``ngrok`` tunnel for the given protocol to the given port, returning an object representing
    the connected tunnel.

    If a `tunnel definition in ngrok's config file <https://ngrok.com/docs#tunnel-definitions>`_ matches the given
    ``name``, it will be loaded and used to start the tunnel. When ``name`` is ``None`` and a "pyngrok-default" tunnel
    definition exists in ``ngrok``'s config, it will be loaded and use. Any ``kwargs`` passed as ``options`` will
    override properties from the loaded tunnel definition.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    .. note::

        ``ngrok``'s default behavior for ``http`` when no additional properties are passed is to open *two* tunnels,
        one ``http`` and one ``https``. This method will return a reference to the ``http`` tunnel in this case. If
        only a single tunnel is needed, pass ``bind_tls=True`` and a reference to the ``https`` tunnel will be returned.

    :param addr: The local port to which the tunnel will forward traffic, or a
        `local directory or network address <https://ngrok.com/docs#http-file-urls>`_, defaults to "80".
    :type addr: str, optional
    :param proto: A valid `tunnel protocol <https://ngrok.com/docs#tunnel-definitions>`_, defaults to "http".
    :type proto: str, optional
    :param name: A friendly name for the tunnel, or the name of a `ngrok tunnel definition <https://ngrok.com/docs#tunnel-definitions>`_
        to be used.
    :type name: str, optional
    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    :param options: Remaining ``kwargs`` are passed as `configuration for the ngrok
        tunnel <https://ngrok.com/docs#tunnel-definitions>`_.
    :type options: dict, optional
    :return: The created ``ngrok`` tunnel.
    :rtype: NgrokTunnel
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    if pyngrok_config.config_path is not None:
        config_path = pyngrok_config.config_path
    else:
        config_path = conf.DEFAULT_NGROK_CONFIG_PATH

    if os.path.exists(config_path):
        config = installer.get_ngrok_config(config_path)
    else:
        config = {}

    # If a "pyngrok-default" tunnel definition exists in the ngrok config, use that
    tunnel_definitions = config.get("tunnels", {})
    if not name and "pyngrok-default" in tunnel_definitions:
        name = "pyngrok-default"

    # Use a tunnel definition for the given name, if it exists
    if name and name in tunnel_definitions:
        tunnel_definition = tunnel_definitions[name]

        addr = tunnel_definition.get("addr") if not addr else addr
        proto = tunnel_definition.get("proto") if not proto else proto
        # Use the tunnel definition as the base, but override with any passed in options
        tunnel_definition.update(options)
        options = tunnel_definition

    addr = str(addr) if addr else "80"
    if not proto:
        proto = "http"

    if not name:
        if not addr.startswith("file://"):
            name = "{}-{}-{}".format(proto, addr, uuid.uuid4())
        else:
            name = "{}-file-{}".format(proto, uuid.uuid4())

    logger.info("Opening tunnel named: {}".format(name))

    config = {
        "name": name,
        "addr": addr,
        "proto": proto
    }
    options.update(config)

    api_url = get_ngrok_process(pyngrok_config).api_url

    logger.debug("Creating tunnel with options: {}".format(options))

    tunnel = NgrokTunnel(api_request("{}/api/tunnels".format(api_url), method="POST", data=options,
                                     timeout=pyngrok_config.request_timeout),
                         pyngrok_config, api_url)

    if proto == "http" and options.get("bind_tls", "both") == "both":
        tunnel = NgrokTunnel(api_request("{}{}%20%28http%29".format(api_url, tunnel.uri), method="GET",
                                         timeout=pyngrok_config.request_timeout),
                             pyngrok_config, api_url)

    _current_tunnels[tunnel.public_url] = tunnel

    return tunnel


def disconnect(public_url, pyngrok_config=None):
    """
    Disconnect the ``ngrok`` tunnel for the given URL, if open.

    :param public_url: The public URL of the tunnel to disconnect.
    :type public_url: str
    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    # If ngrok is not running, there are no tunnels to disconnect
    if not process.is_process_running(pyngrok_config.ngrok_path):
        return

    api_url = get_ngrok_process(pyngrok_config).api_url

    if public_url not in _current_tunnels:
        get_tunnels(pyngrok_config)

        # One more check, if the given URL is still not in the list of tunnels, it is not active
        if public_url not in _current_tunnels:
            return

    tunnel = _current_tunnels[public_url]

    logger.info("Disconnecting tunnel: {}".format(tunnel.public_url))

    api_request("{}{}".format(api_url, tunnel.uri), method="DELETE",
                timeout=pyngrok_config.request_timeout)

    _current_tunnels.pop(public_url, None)


def get_tunnels(pyngrok_config=None):
    """
    Get a list of active ``ngrok`` tunnels for the given config's ``ngrok_path``.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    :return: The active ``ngrok`` tunnels.
    :rtype: list[NgrokTunnel]
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    api_url = get_ngrok_process(pyngrok_config).api_url

    _current_tunnels.clear()
    for tunnel in api_request("{}/api/tunnels".format(api_url), method="GET",
                              timeout=pyngrok_config.request_timeout)["tunnels"]:
        ngrok_tunnel = NgrokTunnel(tunnel, pyngrok_config, api_url)
        _current_tunnels[ngrok_tunnel.public_url] = ngrok_tunnel

    return list(_current_tunnels.values())


def kill(pyngrok_config=None):
    """
    Terminate the ``ngrok`` processes, if running, for the given config's ``ngrok_path``. This method will not
    block, it will just issue a kill request.

    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    process.kill_process(pyngrok_config.ngrok_path)

    _current_tunnels.clear()


def get_version(pyngrok_config=None):
    """
    Get a tuple with the ``ngrok`` and ``pyngrok`` versions.

    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    :return: A tuple of ``(ngrok_version, pyngrok_version)``.
    :rtype: tuple
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    ngrok_version = process.capture_run_process(pyngrok_config.ngrok_path, ["--version"]).split("version ")[1]

    return ngrok_version, __version__


def update(pyngrok_config=None):
    """
    Update ``ngrok`` for the given config's ``ngrok_path``, if an update is available.

    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    :return: The result from the ``ngrok`` update.
    :rtype: str
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    return process.capture_run_process(pyngrok_config.ngrok_path, ["update"])


def api_request(url, method="GET", data=None, params=None, timeout=4):
    """
    Invoke an API request to the given URL, returning JSON data from the response.

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
        logger.debug("Response {}: {}".format(status_code, response_data.strip()))

        if str(status_code)[0] != "2":
            raise PyngrokNgrokHTTPError("ngrok client API returned {}: {}".format(status_code, response_data), url,
                                        status_code, None, request.headers, response_data)
        elif status_code == HTTPStatus.NO_CONTENT:
            return None

        return json.loads(response_data)
    except socket.timeout:
        raise PyngrokNgrokURLError("ngrok client exception, URLError: timed out", "timed out")
    except HTTPError as e:
        response_data = e.read().decode("utf-8")

        status_code = e.getcode()
        logger.debug("Response {}: {}".format(status_code, response_data.strip()))

        raise PyngrokNgrokHTTPError("ngrok client exception, API returned {}: {}".format(status_code, response_data),
                                    e.url,
                                    status_code, e.msg, e.hdrs, response_data)
    except URLError as e:
        raise PyngrokNgrokURLError("ngrok client exception, URLError: {}".format(e.reason), e.reason)


def run(args=None, pyngrok_config=None):
    """
    Ensure ``ngrok`` is installed at the default path, then call :func:`~pyngrok.process.run_process`.

    This method is meant for interacting with ``ngrok`` from the command line and is not necessarily
    compatible with non-blocking API methods. For that, use :mod:`~pyngrok.ngrok`'s interface methods (like
    :func:`~pyngrok.ngrok.connect`), or use :func:`~pyngrok.process.get_process`.

    :param args: Arguments to be passed to the ``ngrok`` process.
    :type args: list[str], optional
    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :type pyngrok_config: PyngrokConfig, optional
    """
    if args is None:
        args = []
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    install_ngrok(pyngrok_config)

    process.run_process(pyngrok_config.ngrok_path, args)


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
