import logging
import os
import platform
import shutil
import tempfile
import zipfile

from future.standard_library import install_aliases

from pyngrok.ngrokexception import NgrokException

install_aliases()

from urllib.request import urlopen

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "1.0.0"

logger = logging.getLogger(__name__)

DARWIN_DOWNLOAD_URL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip"
WINDOWS_DOWNLOAD_URL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip"
LINUX_DARWIN_DOWNLOAD_URL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"


def get_ngrok_bin():
    system = platform.system()
    if system in ["Darwin", "Linux"]:
        return "ngrok"
    elif system == "Windows":  # pragma: no cover
        return "ngrok.exe"
    else:  # pragma: no cover
        raise NgrokException("'{}' is not a supported platform".format(system))


def install_ngrok(ngrok_path):
    logger.debug("Binary not found at {}, installing ngrok ...".format(ngrok_path))

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
    else:  # pragma: no cover
        raise NgrokException("'{}' is not a supported platform".format(system))

    try:
        download_path = _download_file(url)

        with zipfile.ZipFile(download_path, "r") as zip_ref:
            logger.debug("Extracting ngrok binary ...".format(url))
            zip_ref.extractall(os.path.dirname(ngrok_path))

        os.chmod(ngrok_path, int('777', 8))
    except Exception as e:
        raise NgrokException("An error occurred while downloading ngrok from {}: {}".format(url, e))


def _download_file(url):
    logger.debug("Download ngrok from {} ...".format(url))

    local_filename = url.split("/")[-1]
    response = urlopen(url)
    download_path = os.path.join(tempfile.gettempdir(), local_filename)

    with open(download_path, "wb") as f:
        shutil.copyfileobj(response, f)

    return download_path
