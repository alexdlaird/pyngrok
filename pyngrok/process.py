import atexit
import os
import subprocess
import time

from pyngrok.installer import install_ngrok
from pyngrok.ngrokexception import NgrokException

CURRENT_PROCESSES = {}


class Process:
    def __init__(self, ngrok_path, process, api_url):
        self.ngrok_path = ngrok_path
        self.process = process
        self.api_url = api_url


def set_auth_token(ngrok_path, token, config_path=None):
    start = [ngrok_path, "authtoken", token]
    if config_path:
        start.append("--config={}".format(config_path))

    subprocess.Popen(config_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).wait()


def get_process(ngrok_path, config_path=None):
    if ngrok_path in CURRENT_PROCESSES:
        return CURRENT_PROCESSES[ngrok_path]
    else:
        if not os.path.exists(ngrok_path):
            install_ngrok(ngrok_path)

        _start_process(ngrok_path, config_path)

        return CURRENT_PROCESSES[ngrok_path]


def kill_process(ngrok_path):
    if ngrok_path in CURRENT_PROCESSES:
        CURRENT_PROCESSES[ngrok_path].process.kill()

        if hasattr(atexit, 'unregister'):
            atexit.unregister(CURRENT_PROCESSES[ngrok_path].process.terminate)

        del CURRENT_PROCESSES[ngrok_path]


def _start_process(ngrok_path, config_path=None):
    start = [ngrok_path, "start", "--none", "--log=stdout"]
    if config_path:
        start.append("--config={}".format(config_path))

    process = subprocess.Popen(start, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    atexit.register(process.terminate)

    api_url = None
    tunnel_started = False
    timeout = time.time() + 15
    while time.time() < timeout:
        line = process.stdout.readline()

        if "starting web service" in line:
            api_url = "http://{}".format(line.split("addr=")[1].strip())
        elif "tunnel session started" in line:
            tunnel_started = True
            break
        elif process.poll() is not None:
            # TODO: process died, report a useful error here
            break

    if not api_url or not tunnel_started:
        raise NgrokException("The ngrok process was unable to start")

    CURRENT_PROCESSES[ngrok_path] = Process(ngrok_path, process, api_url)
