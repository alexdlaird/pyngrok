import json
import logging
import os
import uuid

from future.standard_library import install_aliases

from pyngrok import process
from pyngrok.installer import get_ngrok_bin
from pyngrok.ngrokexception import NgrokException

install_aliases()

from urllib.parse import urlencode
from urllib.request import urlopen, Request

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "0.3.2"

logger = logging.getLogger(__name__)

BIN_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))
DEFAULT_NGROK_PATH = os.path.join(BIN_DIR, get_ngrok_bin())


class NgrokTunnel:
    def __init__(self, data=None):
        if data is None:
            data = {}

        self.name = data["name"] if data else None
        self.proto = data["proto"] if data else None
        self.uri = data["uri"] if data else None
        self.public_url = data["public_url"] if data else None
        self.config = data["config"] if data else {}
        self.metrics = data["metrics"] if data else None


def set_auth_token(token, ngrok_path=None, config_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    process.ensure_ngrok_installed(ngrok_path)

    process.set_auth_token(ngrok_path, token, config_path)


def get_ngrok_process(ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    return process.get_process(ngrok_path)


def connect(port=80, proto="http", name=None, options=None, ngrok_path=None, config_path=None):
    if options is None:
        options = {}

    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    config = {
        "name": name if name else str(uuid.uuid4()),
        "addr": str(port),
        "proto": proto
    }
    options.update(config)

    current_process = process.get_process(ngrok_path, config_path)

    logger.debug("Connecting tunnel with options: {}".format(options))

    tunnel = NgrokTunnel(_request("{}/api/{}".format(current_process.api_url, "tunnels"), "POST", data=options))

    if proto == "http" and ("bind_tls" not in options or options["bind_tls"] != False):
        tunnel.public_url = tunnel.public_url.replace("https", "http")

    return tunnel.public_url


def disconnect(public_url=None, ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    api_url = get_ngrok_process(ngrok_path).api_url

    tunnels = get_tunnels(ngrok_path)
    for tunnel in tunnels:
        if tunnel.public_url == public_url:
            logger.debug("Disconnecting tunnel: {}".format(tunnel.public_url))

            _request("{}{}".format(api_url, tunnel.uri.replace("+", "%20")), "DELETE")


def get_tunnels(ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    if ngrok_path not in process.CURRENT_PROCESSES:
        raise NgrokException("ngrok is not running for the 'ngrok_path': {}".format(ngrok_path))

    tunnels = []
    for tunnel in _request("{}/api/{}".format(get_ngrok_process(ngrok_path).api_url, "tunnels"))["tunnels"]:
        tunnels.append(NgrokTunnel(tunnel))

    return tunnels


def kill(ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    if ngrok_path not in process.CURRENT_PROCESSES:
        raise NgrokException("ngrok is not running for the 'ngrok_path': {}".format(ngrok_path))

    process.kill_process(ngrok_path)


def _request(uri, method="GET", data=None, params=None):
    if not params:
        params = []

    data = json.dumps(data).encode("utf-8") if data else None

    if params:
        uri += "?{}".format(urlencode([(x, params[x]) for x in params]))

    request = Request(uri, method=method.upper())
    request.add_header("Content-Type", "application/json")

    logger.debug("Making {} request to {} with data: {}".format(method, uri, data))

    with urlopen(request, data) as response:
        try:
            response_data = response.read().decode('utf-8')

            status_code = response.getcode()
            logger.debug("Response status code: {}".format(status_code))
            logger.debug("Response: {}".format(response_data))

            if str(status_code)[0] != '2':
                raise NgrokException("ngrok client API return {}: {}".format(status_code, response_data))
            elif status_code == 204:
                return None
            else:
                return json.loads(response_data)
        except Exception as e:
            logger.debug("Request exception: {}".format(e))

            return None
