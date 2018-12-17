import json
import os
import uuid

from pyngrok import process
from pyngrok.installer import get_ngrok_bin
from pyngrok.ngrokexception import NgrokException
from future.standard_library import install_aliases

install_aliases()

from urllib.parse import urlencode
from urllib.request import urlopen, Request

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "0.3.0"

BIN_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))
DEFAULT_NGROK_PATH = os.path.join(BIN_DIR, get_ngrok_bin())


# TODO: add logging

class NgrokTunnel:
    def __init__(self, data={}):
        self.name = data["name"] if data else None
        self.proto = data["proto"] if data else None
        self.uri = data["uri"] if data else None
        self.public_url = data["public_url"] if data else None
        self.config = data["config"] if data else {}
        self.metrics = data["metrics"] if data else None


def set_auth_token(token, ngrok_path=None, config_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    process.set_auth_token(ngrok_path, token, config_path)


def get_ngrok_process(ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    return process.get_process(ngrok_path)


def connect(port=80, proto="http", name=None, ngrok_path=None, config_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    # TODO: refactor to accept generic "options" that can be passed directly to ngrok command
    config = {
        "name": name if name else str(uuid.uuid4()),
        "addr": str(port),
        "proto": proto
    }

    current_process = process.get_process(ngrok_path, config_path)

    tunnel = NgrokTunnel(_request("{}/api/{}".format(current_process.api_url, "tunnels"), "POST", data=config))

    # TODO: when bind_tls param is added to "options", add check for != "false" here
    if proto == "http":
        tunnel.public_url = tunnel.public_url.replace("https", "http")

    return tunnel.public_url


def disconnect(public_url=None, ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    api_url = get_ngrok_process(ngrok_path).api_url

    tunnels = get_tunnels(ngrok_path)
    for tunnel in tunnels:
        if tunnel.public_url == public_url:
            _request("{}{}".format(api_url, tunnel.uri.replace("+", "%20")), "DELETE")


def get_tunnels(ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    if ngrok_path not in process.CURRENT_PROCESSES:
        raise NgrokException("A ngrok process is not running at the given 'ngrok_path'")

    tunnels = []
    for tunnel in _request("{}/api/{}".format(get_ngrok_process(ngrok_path).api_url, "tunnels"))["tunnels"]:
        tunnels.append(NgrokTunnel(tunnel))

    return tunnels


def kill(ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    if ngrok_path not in process.CURRENT_PROCESSES:
        raise NgrokException("A ngrok process is not running at the given 'ngrok_path'")

    process.kill_process(ngrok_path)


def _request(uri, method="GET", data=None, params=None):
    if not params:
        params = []

    data = json.dumps(data).encode("utf-8") if data else None

    if params:
        uri += "?{}".format(urlencode([(x, params[x]) for x in params]))

    request = Request(uri, method=method.upper())
    request.add_header("Content-Type", "application/json")

    with urlopen(request, data) as response:
        try:
            response_data = response.read().decode('utf-8')

            if str(response.getcode())[0] != '2':
                raise NgrokException(response.text)
            else:
                return json.loads(response_data)
        except:
            return None
