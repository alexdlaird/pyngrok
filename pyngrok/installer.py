import logging
import os
import platform
import shutil
import tempfile
import zipfile

from future.standard_library import install_aliases

from pyngrok.exception import PyngrokNgrokInstallError

install_aliases()

from urllib.request import urlopen

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Alex Laird"
__version__ = "1.3.0"

logger = logging.getLogger(__name__)

DARWIN_DOWNLOAD_URL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip"
WINDOWS_DOWNLOAD_URL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip"
LINUX_DARWIN_DOWNLOAD_URL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"


def get_ngrok_bin():
    """
    Retrieve the `ngrok` command for the current system.

    :return: The `ngrok` command.
    :rtype: string
    """
    system = platform.system()
    if system in ["Darwin", "Linux"]:
        return "ngrok"
    elif system == "Windows":  # pragma: no cover
        return "ngrok.exe"
    else:  # pragma: no cover
        raise PyngrokNgrokInstallError("\"{}\" is not a supported platform".format(system))


def install_ngrok(ngrok_path):
    """
    Download and install `ngrok` for the current system in the given location.

    :param ngrok_path: The path to where the `ngrok` binary will be downloaded.
    :type ngrok_path: string
    """
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
        raise PyngrokNgrokInstallError("\"{}\" is not a supported platform".format(system))

    try:
        download_path = _download_file(url)

        with zipfile.ZipFile(download_path, "r") as zip_ref:
            logger.debug("Extracting ngrok binary to {} ...".format(download_path))
            zip_ref.extractall(os.path.dirname(ngrok_path))

        os.chmod(ngrok_path, int("777", 8))
    except Exception as e:
        raise PyngrokNgrokInstallError("An error occurred while downloading ngrok from {}: {}".format(url, e))


def _download_file(url):
    logger.debug("Download ngrok from {} ...".format(url))

    local_filename = url.split("/")[-1]
    response = urlopen(url)

    status_code = response.getcode()
    logger.debug("Response status code: {}".format(status_code))

    if status_code != 200:
        return None

    download_path = os.path.join(tempfile.gettempdir(), local_filename)

    with open(download_path, "wb") as f:
        shutil.copyfileobj(response, f)

    return download_path
