import logging
import os
import platform
import socket
import sys
import tempfile
import time
import zipfile
from http import HTTPStatus
from urllib.request import urlopen

import yaml

from pyngrok.exception import PyngrokNgrokInstallError, PyngrokSecurityError, PyngrokError

__author__ = "Alex Laird"
__copyright__ = "Copyright 2021, Alex Laird"
__version__ = "5.0.6"

logger = logging.getLogger(__name__)

CDN_URL_PREFIX = "https://bin.equinox.io/c/4VmDzA7iaHb/"
PLATFORMS = {
    "darwin_x86_64": CDN_URL_PREFIX + "ngrok-stable-darwin-amd64.zip",
    "darwin_x86_64_arm": CDN_URL_PREFIX + "ngrok-stable-darwin-arm64.zip",
    "windows_x86_64": CDN_URL_PREFIX + "ngrok-stable-windows-amd64.zip",
    "windows_i386": CDN_URL_PREFIX + "ngrok-stable-windows-386.zip",
    "linux_x86_64_arm": CDN_URL_PREFIX + "ngrok-stable-linux-arm64.zip",
    "linux_i386_arm": CDN_URL_PREFIX + "ngrok-stable-linux-arm.zip",
    "linux_i386": CDN_URL_PREFIX + "ngrok-stable-linux-386.zip",
    "linux_x86_64": CDN_URL_PREFIX + "ngrok-stable-linux-amd64.zip",
    "freebsd_x86_64": CDN_URL_PREFIX + "ngrok-stable-freebsd-amd64.zip",
    "freebsd_i386": CDN_URL_PREFIX + "ngrok-stable-freebsd-386.zip",
    "cygwin_x86_64": CDN_URL_PREFIX + "ngrok-stable-windows-amd64.zip",
}
DEFAULT_DOWNLOAD_TIMEOUT = 6
DEFAULT_RETRY_COUNT = 0

_config_cache = None
_print_progress_enabled = True


def get_ngrok_bin():
    """
    Get the ``ngrok`` executable for the current system.

    :return: The name of the ``ngrok`` executable.
    :rtype: str
    """
    system = platform.system().lower()
    if system in ["darwin", "linux", "freebsd"]:
        return "ngrok"
    elif system in ["windows", "cygwin"]:  # pragma: no cover
        return "ngrok.exe"
    else:  # pragma: no cover
        raise PyngrokNgrokInstallError("\"{}\" is not a supported platform".format(system))


def install_ngrok(ngrok_path, **kwargs):
    """
    Download and install the latest ``ngrok`` for the current system, overwriting any existing contents
    at the given path.

    :param ngrok_path: The path to where the ``ngrok`` binary will be downloaded.
    :type ngrok_path: str
    :param kwargs: Remaining ``kwargs`` will be passed to :func:`_download_file`.
    :type kwargs: dict, optional
    """
    logger.debug(
        "Installing ngrok to {}{} ...".format(ngrok_path, ", overwriting" if os.path.exists(ngrok_path) else ""))

    ngrok_dir = os.path.dirname(ngrok_path)

    if not os.path.exists(ngrok_dir):
        os.makedirs(ngrok_dir)

    arch = "x86_64" if sys.maxsize > 2 ** 32 else "i386"
    if platform.uname()[4].startswith("arm") or \
            platform.uname()[4].startswith("aarch64"):
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
        download_path = _download_file(url, **kwargs)

        _install_ngrok_zip(ngrok_path, download_path)
    except Exception as e:
        raise PyngrokNgrokInstallError("An error occurred while downloading ngrok from {}: {}".format(url, e))


def _install_ngrok_zip(ngrok_path, zip_path):
    """
    Extract the ``ngrok`` zip file to the given path.

    :param ngrok_path: The path where ``ngrok`` will be installed.
    :type ngrok_path: str
    :param zip_path: The path to the ``ngrok`` zip file to be extracted.
    :type zip_path: str
    """
    _print_progress("Installing ngrok ... ")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        logger.debug("Extracting ngrok binary from {} to {} ...".format(zip_path, ngrok_path))
        zip_ref.extractall(os.path.dirname(ngrok_path))

    os.chmod(ngrok_path, int("777", 8))

    _clear_progress()


def get_ngrok_config(config_path, use_cache=True):
    """
    Get the ``ngrok`` config from the given path.

    :param config_path: The ``ngrok`` config path to read.
    :type config_path: str
    :param use_cache: Use the cached version of the config (if populated).
    :type use_cache: bool
    :return: The ``ngrok`` config.
    :rtype: dict
    """
    global _config_cache

    if not _config_cache or not use_cache:
        with open(config_path, "r") as config_file:
            config = yaml.safe_load(config_file)
            if config is None:
                config = {}

        _config_cache = config

    return _config_cache


def install_default_config(config_path, data=None):
    """
    Install the given data to the ``ngrok`` config. If a config is not already present for the given path, create one.
    Before saving new data to the default config, validate that they are compatible with ``pyngrok``.

    :param config_path: The path to where the ``ngrok`` config should be installed.
    :type config_path: str
    :param data: A dictionary of things to add to the default config.
    :type data: dict, optional
    """
    if data is None:
        data = {}

    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(config_path):
        open(config_path, "w").close()

    config = get_ngrok_config(config_path, use_cache=False)

    config.update(data)

    validate_config(config)

    with open(config_path, "w") as config_file:
        logger.debug("Installing default ngrok config to {} ...".format(config_path))

        yaml.dump(config, config_file)


def validate_config(data):
    """
    Validate that the given dict of config items are valid for ``ngrok`` and ``pyngrok``.

    :param data: A dictionary of things to be validated as config items.
    :type data: dict
    """
    if data.get("web_addr", None) is False:
        raise PyngrokError("\"web_addr\" cannot be False, as the ngrok API is a dependency for pyngrok")
    elif data.get("log_format") == "json":
        raise PyngrokError("\"log_format\" must be \"term\" to be compatible with pyngrok")
    elif data.get("log_level", "info") not in ["info", "debug"]:
        raise PyngrokError("\"log_level\" must be \"info\" to be compatible with pyngrok")


def _download_file(url, retries=0, **kwargs):
    """
    Download a file to a temporary path and emit a status to stdout (if possible) as the download progresses.

    :param url: The URL to download.
    :type url: str
    :param retries: The retry attempt index, if download fails.
    :type retries: int, optional
    :param kwargs: Remaining ``kwargs`` will be passed to :py:func:`urllib.request.urlopen`.
    :type kwargs: dict, optional
    :return: The path to the downloaded temporary file.
    :rtype: str
    """
    kwargs["timeout"] = kwargs.get("timeout", DEFAULT_DOWNLOAD_TIMEOUT)

    if not url.lower().startswith("http"):
        raise PyngrokSecurityError("URL must start with \"http\": {}".format(url))

    try:
        _print_progress("Downloading ngrok ...")

        logger.debug("Download ngrok from {} ...".format(url))

        local_filename = url.split("/")[-1]
        response = urlopen(url, **kwargs)

        status_code = response.getcode()

        if status_code != HTTPStatus.OK:
            logger.debug("Response status code: {}".format(status_code))

            return None

        length = response.getheader("Content-Length")
        if length:
            length = int(length)
            chunk_size = max(4096, length // 100)
        else:
            chunk_size = 64 * 1024

        download_path = os.path.join(tempfile.gettempdir(), local_filename)
        with open(download_path, "wb") as f:
            size = 0
            while True:
                buffer = response.read(chunk_size)

                if not buffer:
                    break

                f.write(buffer)
                size += len(buffer)

                if length:
                    percent_done = int((float(size) / float(length)) * 100)
                    _print_progress("Downloading ngrok: {}%".format(percent_done))

        _clear_progress()

        return download_path
    except socket.timeout as e:
        if retries < DEFAULT_RETRY_COUNT:
            logger.warning("ngrok download failed, retrying in 0.5 seconds ...")
            time.sleep(0.5)

            return _download_file(url, retries + 1, **kwargs)
        else:
            raise e


def _print_progress(line):
    if _print_progress_enabled:
        sys.stdout.write("{}\r".format(line))
        sys.stdout.flush()


def _clear_progress(spaces=100):
    if _print_progress_enabled:
        sys.stdout.write((" " * spaces) + "\r")
        sys.stdout.flush()
