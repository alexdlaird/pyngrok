import os
import time
import json

from pygrok.installer import get_ngrok_bin
from pygrok.process import get_process, kill_process
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlencode
from urllib.request import urlopen, Request

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "0.1.0"

BIN_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "bin"))
NGROK_PATH = os.path.join(BIN_DIR, get_ngrok_bin())
TUNNELS = {}

def connect(port=80, proto="http", name=None, ngrok_path=None):
    if ngrok_path is None:
        ngrok_path = NGROK_PATH

    # TODO: add more support for opts (bind_tls, authtoken, etc.)
    config = {
        "name": name if name is not None else "http:{}".format(port),
        "addr": str(port),
        "proto": proto
    }

    get_process(NGROK_PATH)

    response = _api("tunnels", "POST", config)

    TUNNELS[response["public_url"]] = response;

    return response["public_url"]

def disconnect(public_url=None):
  _api.del("tunnels/{}".format(TUNNELS[public_url]["name"]), "DELETE")
  del TUNNELS[public_url]

def get_tunnels():
    tunnels = []
    for tunnel in api("tunnels")["tunnels"]:
        tunnels.append(tunnel)
    return tunnels

def kill(ngrok_path=None):
    if ngrok_path is None:
        ngrok_path = NGROK_PATH

    kill_process(NGROK_PATH)

    TUNNELS = {}

def _api(endpoint, method="GET", data=None, params=[]):
    base_url = "http://127.0.0.1:4040/"
    if params:
        endpoint += "?%s" % urlencode([(x, params[x]) for x in params])
    request = Request("%sapi/%s" % (base_url, endpoint))
    if method != "GET":
        request.get_method = lambda: method
    request.add_header("Content-Type", "application/json")
    response = urlopen(request, json.dumps(data) if data else None)
    try:
        return json.loads(response.read())
    except:
        return None
