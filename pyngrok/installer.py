import os
import platform
import shutil
import tempfile
import zipfile

from pyngrok.ngrokexception import NgrokException
from future.standard_library import install_aliases

install_aliases()

from urllib.request import urlopen

DARWIN_DOWNLOAD_URL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip"
WINDOWS_DOWNLOAD_URL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip"
LINUX_DARWIN_DOWNLOAD_URL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"


def get_ngrok_bin():
    system = platform.system()
    if system in ["Darwin", "Linux"]:
        return "ngrok"
    elif system == "Windows":  # pragma: no cover
        return "ngrok.exe"
    else:
        raise NgrokException("{} is not supported".format(system))


def install_ngrok(ngrok_path):
    # TODO: add support for outputting "Installing Ngrok ..." to a console
    ngrok_dir = os.path.dirname(ngrok_path)

    if not os.path.exists(ngrok_dir):
        os.mkdir(ngrok_dir)

    system = platform.system()
    if system == "Darwin":
        url = DARWIN_DOWNLOAD_URL
    elif system == "Windows":  # pragma: no cover
        url = WINDOWS_DOWNLOAD_URL
    elif system == "Linux":  # pragma: no cover
        url = LINUX_DARWIN_DOWNLOAD_URL
    else:
        raise NgrokException("{} is not supported".format(system))

    download_path = _download_file(url)
    with zipfile.ZipFile(download_path, "r") as zip_ref:
        zip_ref.extractall(os.path.dirname(ngrok_path))

    os.chmod(ngrok_path, int('777', 8))


def _get_ngrok_path(ngrok_dir):
    ngrok_dir = ngrok_dir if ngrok_dir else tempfile.gettempdir()

    if not os.path.exists(ngrok_dir):
        os.mkdir(ngrok_dir)

    return os.path.join(ngrok_dir, get_ngrok_bin())


def _download_file(url):
    local_filename = url.split("/")[-1]
    response = urlopen(url)
    download_path = os.path.join(tempfile.gettempdir(), local_filename)

    with open(download_path, "wb") as f:
        shutil.copyfileobj(response, f)

    return download_path
