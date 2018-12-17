import json
import os
import uuid

import requests

from pyngrok import process
from pyngrok.installer import get_ngrok_bin
from pyngrok.ngrokexception import NgrokException

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "0.2.0"

BIN_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))
DEFAULT_NGROK_PATH = os.path.join(BIN_DIR, get_ngrok_bin())


# TODO: add logging


def set_auth_token(token, config_path=None):
    process.set_auth_token(token, config_path)


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

    response = _request("{}/api/{}".format(current_process.api_url, "tunnels"), "POST", data=config)

    # TODO: when bind_tls param is added to "options", add check for != "false" here
    if proto == "http":
        response["public_url"] = response["public_url"].replace("https", "http")

    return response["public_url"]


def disconnect(public_url=None, ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    api_url = get_ngrok_process(ngrok_path).api_url

    tunnels = get_tunnels(ngrok_path)
    for tunnel in tunnels:
        if tunnel["public_url"] == public_url:
            _request("{}{}".format(api_url, tunnel["uri"].replace("+", "%20")), "DELETE")


def get_tunnels(ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    if ngrok_path not in process.CURRENT_PROCESSES:
        raise NgrokException("A ngrok process is not running at the given 'ngrok_path'")

    return _request("{}/api/{}".format(get_ngrok_process(ngrok_path).api_url, "tunnels"))["tunnels"]


def kill(ngrok_path=None):
    ngrok_path = ngrok_path if ngrok_path else DEFAULT_NGROK_PATH

    if ngrok_path not in process.CURRENT_PROCESSES:
        raise NgrokException("A ngrok process is not running at the given 'ngrok_path'")

    process.kill_process(ngrok_path)


def _request(uri, method="GET", data=None, params=None):
    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps(data) if data else None

    method = getattr(requests, method.lower())
    response = method(uri, headers=headers, data=data, params=params)

    if str(response.status_code)[0] != '2':
        raise NgrokException(response.text)

    if response.status_code != 204:
        return response.json()
    else:
        return None
