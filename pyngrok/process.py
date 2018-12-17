import atexit
import os
import subprocess
import time

from pyngrok.installer import install_ngrok

process = None


def get_process(ngrok_path=None):
    # TODO: add support for opts
    if process:
        return process
    elif ngrok_path is not None:
        if not os.path.exists(ngrok_path):
            install_ngrok(ngrok_path)

        _start_process(ngrok_path)

        return process
    else:
        raise Exception("A ngrok process is not already running, so 'ngrok_path' must be provided")


def kill_process():
    global process

    if process:
        process[0].kill()

        if hasattr(atexit, 'unregister'):
            atexit.unregister(process[0].terminate)

    process = None


def _start_process(ngrok_path):
    global process

    ngrok_proc = subprocess.Popen([ngrok_path, "start", "--none", "--log=stdout"], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, universal_newlines=True)
    atexit.register(ngrok_proc.terminate)

    url = None
    started = False
    t_end = time.time() + 15
    while time.time() < t_end:
        line = ngrok_proc.stdout.readline()

        if "starting web service" in line:
            url = "http://{}".format(line.split("addr=")[1].strip())
        elif "tunnel session started" in line:
            started = True
            break
        elif ngrok_proc.poll() is not None:
            # TODO: process died, find a useful error and report it
            break

    if url is None or not started:
        raise Exception("The ngrok process was unable to start")

    process = ngrok_proc, url
