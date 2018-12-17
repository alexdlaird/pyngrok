import json
import os
import uuid

from future.standard_library import install_aliases

from pygrok.installer import get_ngrok_bin
from pygrok.process import get_process, kill_process

install_aliases()

from urllib.parse import urlencode
from urllib.request import urlopen, Request

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "0.1.0"

BIN_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))
NGROK_PATH = os.path.join(BIN_DIR, get_ngrok_bin())
TUNNELS = {}

# TODO: clean this up, it's not great practice
WEB_SERVICE_URL = None


# TODO: add logging

def connect(port, proto="http", name=None, ngrok_path=None):
    global WEB_SERVICE_URL

    if ngrok_path is None:
        ngrok_path = NGROK_PATH

    # TODO: add more support for opts (bind_tls, authtoken, etc.)
    config = {
        "name": name if name is not None else str(uuid.uuid4()),
        "addr": str(port),
        "proto": proto
    }

    process, url = get_process(ngrok_path)
    WEB_SERVICE_URL = url

    response = _api("tunnels", "POST", data=config)

    if proto == "http":
        response["name"] += " (http)"
        response["public_url"] = response["public_url"].replace("https", "http")
        response["proto"] = "http"
        response["uri"] += "+%28http%29"

    TUNNELS[response["public_url"]] = response

    return response["public_url"]


# TODO: implement manual disconnect (current impl is not properly disconnecting http tunnels
# def disconnect(public_url=None):
#     _api(TUNNELS[public_url]["uri"][5:], "DELETE")
#     del TUNNELS[public_url]


def get_tunnels():
    tunnels = []
    for tunnel in _api("tunnels")["tunnels"]:
        tunnels.append(tunnel)
    return tunnels


def kill():
    global WEB_SERVICE_URL, TUNNELS

    kill_process()

    WEB_SERVICE_URL = None
    TUNNELS = {}


def _api(endpoint, method="GET", data=None, params=None):
    if params is None:
        params = []

    if params:
        endpoint += "?%s" % urlencode([(x, params[x]) for x in params])
    data = urlencode(data).encode() if data else None
    request = Request("%sapi/%s" % (WEB_SERVICE_URL, endpoint))
    if method != "GET":
        request.get_method = lambda: method
    request.add_header("Content-Type", "application/json")
    response = urlopen(request, data)
    try:
        return json.loads(response.read().decode("utf-8"))
    except:
        return None
