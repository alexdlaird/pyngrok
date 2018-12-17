import json
import os
import uuid

import requests

from pyngrok.installer import get_ngrok_bin
from pyngrok.process import get_process, kill_process

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "0.1.2"

BIN_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))
NGROK_PATH = os.path.join(BIN_DIR, get_ngrok_bin())

WEB_SERVICE_URLS = {}


# TODO: add logging

def connect(port=80, proto="http", name=None, ngrok_path=None):
    if ngrok_path is None:
        ngrok_path = NGROK_PATH

    # TODO: add more support for opts (bind_tls, authtoken, etc.)
    config = {
        "name": name if name is not None else str(uuid.uuid4()),
        "addr": str(port),
        "proto": proto
    }

    process, url = get_process(ngrok_path)
    WEB_SERVICE_URLS[ngrok_path] = url

    response = _request("{}/api/{}".format(WEB_SERVICE_URLS[ngrok_path], "tunnels"), "POST", data=config)

    if proto == "http":
        response["public_url"] = response["public_url"].replace("https", "http")

    return response["public_url"]


def disconnect(public_url=None, ngrok_path=None):
    if ngrok_path is None:
        ngrok_path = NGROK_PATH

    tunnels = get_tunnels(ngrok_path)
    for tunnel in tunnels:
        if tunnel["public_url"] == public_url:
            _request("{}{}".format(WEB_SERVICE_URLS[ngrok_path], tunnel["uri"].replace("+", "%20")), "DELETE")


def get_tunnels(ngrok_path=None):
    if ngrok_path is None:
        ngrok_path = NGROK_PATH

    if ngrok_path not in WEB_SERVICE_URLS:
        raise Exception("A ngrok process is not running at the given 'ngrok_path'")

    return _request("{}/api/{}".format(WEB_SERVICE_URLS[ngrok_path], "tunnels"))["tunnels"]


def kill(ngrok_path=None):
    if ngrok_path is None:
        ngrok_path = NGROK_PATH

    if ngrok_path not in WEB_SERVICE_URLS:
        raise Exception("A ngrok process is not running at the given 'ngrok_path'")

    kill_process()

    del WEB_SERVICE_URLS[ngrok_path]


def _request(uri, method="GET", data=None, params=None):
    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps(data) if data else None

    method = getattr(requests, method.lower())
    response = method(uri, headers=headers, data=data, params=params)

    if str(response.status_code)[0] != '2':
        raise Exception(response.text)

    if response.status_code != 204:
        return response.json()
    else:
        return None
