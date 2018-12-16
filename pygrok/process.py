import os
import subprocess
import atexit
import time

from pygrok.installer import get_ngrok_bin, install_ngrok

process = None

def get_process(ngrok_path):
    # TODO: add support for opts
    if not os.path.exists(ngrok_path):
        install_ngrok(ngrok_path)

    if process:
        return process
    else:
        return _start_process(ngrok_path)

def kill_process(ngrok_path):
    if process:
        process.kill()

def _start_process(ngrok_path):
    process = subprocess.Popen([ngrok_path, "start", "--none", "--log=stdout"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    atexit.register(process.terminate)

    # TODO: parse out the URL, in case it doesn't start as the default on 4040, also then removing sleep
    time.sleep(1)

    return process
