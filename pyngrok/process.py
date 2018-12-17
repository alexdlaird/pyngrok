import atexit
import logging
import os
import subprocess
import time

from pyngrok.installer import install_ngrok
from pyngrok.ngrokexception import NgrokException

logger = logging.getLogger(__name__)

CURRENT_PROCESSES = {}


class NgrokProcess:
    def __init__(self, ngrok_path, process, api_url):
        self.ngrok_path = ngrok_path
        self.process = process
        self.api_url = api_url


def set_auth_token(ngrok_path, token, config_path=None):
    start = [ngrok_path, "authtoken", token, "--log=stdout"]
    if config_path:
        start.append("--config={}".format(config_path))

    result = subprocess.check_output(start)

    if "Authtoken saved" not in str(result):
        raise NgrokException(result)


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
        ngrok_process = CURRENT_PROCESSES[ngrok_path]

        logger.debug("Killing ngrok process: {}".format(ngrok_process.process.pid))

        ngrok_process.process.kill()

        if hasattr(atexit, 'unregister'):
            atexit.unregister(ngrok_process.process.terminate)

        del CURRENT_PROCESSES[ngrok_path]


def _start_process(ngrok_path, config_path=None):
    start = [ngrok_path, "start", "--none", "--log=stdout"]
    if config_path:
        logger.debug("Starting ngrok with config file: {}".format(config_path))

        start.append("--config={}".format(config_path))

    process = subprocess.Popen(start, stdout=subprocess.PIPE, universal_newlines=True)
    atexit.register(process.terminate)

    logger.debug("ngrok process started: {}".format(process.pid))

    api_url = None
    tunnel_started = False
    errors = []
    timeout = time.time() + 15
    while time.time() < timeout:
        line = process.stdout.readline()

        if "starting web service" in line:
            api_url = "http://{}".format(line.split("addr=")[1].strip())
        elif "tunnel session started" in line:
            tunnel_started = True
            break
        elif "lvl=error" in line or "lvl=crit" in line:
            errors.append(line)
        elif process.poll() is not None:
            break

    if not api_url or not tunnel_started or len(errors) > 0:
        if len(errors) > 0:
            raise NgrokException(errors)
        else:
            raise NgrokException("The ngrok process was unable to start")

    logger.debug("ngrok web service started: {}".format(api_url))

    CURRENT_PROCESSES[ngrok_path] = NgrokProcess(ngrok_path, process, api_url)
