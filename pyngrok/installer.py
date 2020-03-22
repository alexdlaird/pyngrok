import logging
import os
import platform
import shutil
import socket
import sys
import tempfile
import time
import zipfile

import yaml
from future.standard_library import install_aliases

from pyngrok.exception import PyngrokNgrokInstallError, PyngrokSecurityError

install_aliases()

from urllib.request import urlopen

try:
    from http import HTTPStatus as StatusCodes
except ImportError:  # pragma: no cover
    try:
        from http import client as StatusCodes
    except ImportError:
        import httplib as StatusCodes

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "2.1.1"

logger = logging.getLogger(__name__)

CDN_URL_PREFIX = "https://bin.equinox.io/c/4VmDzA7iaHb/"
PLATFORMS = {
    'darwin_x86_64': CDN_URL_PREFIX + "ngrok-stable-darwin-amd64.zip",
    'darwin_i386': CDN_URL_PREFIX + "ngrok-stable-darwin-386.zip",
    'windows_x86_64': CDN_URL_PREFIX + "ngrok-stable-windows-amd64.zip",
    'windows_i386': CDN_URL_PREFIX + "ngrok-stable-windows-386.zip",
    'linux_x86_64_arm': CDN_URL_PREFIX + "ngrok-stable-linux-arm64.zip",
    'linux_i386_arm': CDN_URL_PREFIX + "ngrok-stable-linux-arm.zip",
    'linux_i386': CDN_URL_PREFIX + "ngrok-stable-linux-386.zip",
    'linux_x86_64': CDN_URL_PREFIX + "ngrok-stable-linux-amd64.zip",
    'freebsd_x86_64': CDN_URL_PREFIX + "ngrok-stable-freebsd-amd64.zip",
    'freebsd_i386': CDN_URL_PREFIX + "ngrok-stable-freebsd-386.zip",
    'cygwin_x86_64': CDN_URL_PREFIX + "ngrok-stable-windows-amd64.zip",
}
DEFAULT_DOWNLOAD_TIMEOUT = 6
DEFAULT_RETRY_COUNT = 0


def get_ngrok_bin():
    """
    Retrieve the `ngrok` command for the current system.

    :return: The `ngrok` command.
    :rtype: string
    """
    system = platform.system()
    if system in ["Darwin", "Linux"]:
        return "ngrok"
    elif system == "Windows" or "cygwin" in system.lower():  # pragma: no cover
        return "ngrok.exe"
    else:  # pragma: no cover
        raise PyngrokNgrokInstallError("\"{}\" is not a supported platform".format(system))


def install_ngrok(ngrok_path, timeout=None):
    """
    Download and install `ngrok` for the current system in the given location.

    :param ngrok_path: The path to where the `ngrok` binary will be downloaded.
    :type ngrok_path: string
    :param timeout: The request timeout, in seconds.
    :type timeout: float, optional
    """
    timeout = timeout if timeout else DEFAULT_DOWNLOAD_TIMEOUT

    logger.debug("Binary not found at {}, installing ngrok ...".format(ngrok_path))

    ngrok_dir = os.path.dirname(ngrok_path)

    if not os.path.exists(ngrok_dir):
        os.makedirs(ngrok_dir)

    arch = "x86_64" if sys.maxsize > 2 ** 32 else "i386"
    if platform.uname()[4].startswith("arm") or platform.uname()[4].startswith("aarch64"):
        arch += "_arm"
    system = platform.system().lower()
    if "cygwin" in system:
        system = "cygwin"
    
    plat = system + "_" + arch
    try:
        url = PLATFORMS[plat]

        logger.debug("Platform to download: {}".format(plat))
    except KeyError:
        raise PyngrokNgrokInstallError("\"{}\" is not a supported platform".format(plat))

    try:
        download_path = _download_file(url, timeout)

        with zipfile.ZipFile(download_path, "r") as zip_ref:
            logger.debug("Extracting ngrok binary to {} ...".format(download_path))
            zip_ref.extractall(os.path.dirname(ngrok_path))

        os.chmod(ngrok_path, int("777", 8))
    except Exception as e:
        raise PyngrokNgrokInstallError("An error occurred while downloading ngrok from {}: {}".format(url, e))


def install_default_config(config_path, data=""):
    """
    Install the default `ngrok` config if one is not already present.

    :param config_path: The path to where the `ngrok` config should be installed.
    :type config_path: string
    :param data: A JSON string of things to add to the default config.
    :type data: string, optional
    """
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(config_path):
        open(config_path, "w").close()

    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
        if config is None:
            config = {}

        config.update(data)

    with open(config_path, "w") as config_file:
        yaml.dump(config, config_file)


def _download_file(url, timeout, retries=0):
    try:
        if not url.lower().startswith('http'):
            raise PyngrokSecurityError("URL must start with 'http': {}".format(url))

        logger.debug("Download ngrok from {} ...".format(url))

        local_filename = url.split("/")[-1]
        response = urlopen(url, timeout=timeout)

        status_code = response.getcode()
        logger.debug("Response status code: {}".format(status_code))

        if status_code != StatusCodes.OK:
            return None

        download_path = os.path.join(tempfile.gettempdir(), local_filename)

        with open(download_path, "wb") as f:
            shutil.copyfileobj(response, f)

        return download_path
    except socket.timeout as e:
        if retries < DEFAULT_RETRY_COUNT:
            time.sleep(0.5)

            return _download_file(url, timeout, retries + 1)
        else:
            raise e
