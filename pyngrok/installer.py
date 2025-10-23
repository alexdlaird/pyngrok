__copyright__ = "Copyright (c) 2018-2025 Alex Laird"
__license__ = "MIT"

import copy
import logging
import os
import platform
import socket
import sys
import tempfile
import threading
import time
import zipfile
from http import HTTPStatus
from typing import Any, Dict, Optional
from urllib.error import URLError
from urllib.request import urlopen

import yaml

from pyngrok.exception import PyngrokError, PyngrokNgrokInstallError, PyngrokSecurityError

logger = logging.getLogger(__name__)

CDN_URL_PREFIX = "https://bin.equinox.io/c/4VmDzA7iaHb/"
CDN_V3_URL_PREFIX = "https://bin.equinox.io/c/bNyj1mQVY4c/"
PLATFORMS = {
    "darwin_x86_64": CDN_URL_PREFIX + "ngrok-stable-darwin-amd64.zip",
    "darwin_x86_64_arm": CDN_URL_PREFIX + "ngrok-stable-darwin-arm64.zip",
    "windows_i386": CDN_URL_PREFIX + "ngrok-stable-windows-386.zip",
    "windows_x86_64": CDN_URL_PREFIX + "ngrok-stable-windows-amd64.zip",
    "linux_i386": CDN_URL_PREFIX + "ngrok-stable-linux-386.zip",
    "linux_i386_arm": CDN_URL_PREFIX + "ngrok-stable-linux-arm.zip",
    "linux_x86_64": CDN_URL_PREFIX + "ngrok-stable-linux-amd64.zip",
    "linux_x86_64_arm": CDN_URL_PREFIX + "ngrok-stable-linux-arm64.zip",
    "freebsd_i386": CDN_URL_PREFIX + "ngrok-stable-freebsd-386.zip",
    "freebsd_x86_64": CDN_URL_PREFIX + "ngrok-stable-freebsd-amd64.zip"
}
PLATFORMS_V3 = {
    "darwin_x86_64": CDN_V3_URL_PREFIX + "ngrok-v3-stable-darwin-amd64.zip",
    "darwin_x86_64_arm": CDN_V3_URL_PREFIX + "ngrok-v3-stable-darwin-arm64.zip",
    "windows_i386": CDN_V3_URL_PREFIX + "ngrok-v3-stable-windows-386.zip",
    "windows_x86_64": CDN_V3_URL_PREFIX + "ngrok-v3-stable-windows-amd64.zip",
    "windows_x86_64_arm": CDN_V3_URL_PREFIX + "ngrok-v3-stable-windows-arm64.zip",
    "linux_i386": CDN_V3_URL_PREFIX + "ngrok-v3-stable-linux-386.zip",
    "linux_i386_arm": CDN_V3_URL_PREFIX + "ngrok-v3-stable-linux-arm.zip",
    "linux_x86_64": CDN_V3_URL_PREFIX + "ngrok-v3-stable-linux-amd64.zip",
    "linux_x86_64_arm": CDN_V3_URL_PREFIX + "ngrok-v3-stable-linux-arm64.zip",
    "linux_s390x": CDN_V3_URL_PREFIX + "ngrok-v3-stable-linux-s390x.zip",
    "linux_ppc64": CDN_V3_URL_PREFIX + "ngrok-v3-stable-linux-ppc64.zip",
    "linux_ppc64le": CDN_V3_URL_PREFIX + "ngrok-v3-stable-linux-ppc64le.zip",
    "freebsd_i386": CDN_V3_URL_PREFIX + "ngrok-v3-stable-freebsd-386.zip",
    "freebsd_x86_64": CDN_V3_URL_PREFIX + "ngrok-v3-stable-freebsd-amd64.zip",
    "freebsd_i386_arm": CDN_V3_URL_PREFIX + "ngrok-v3-stable-freebsd-arm.zip"
}
UNIX_BINARIES = ["darwin", "linux", "freebsd"]
SUPPORTED_NGROK_VERSIONS = ["v2", "v3"]
DEFAULT_DOWNLOAD_TIMEOUT = 6
DEFAULT_RETRY_COUNT = 0

config_file_lock = threading.RLock()

_config_cache: Dict[str, Dict[str, Any]] = {}
_print_progress_enabled = True


def get_default_ngrok_dir() -> str:
    """
    Get the default ``ngrok`` directory for the current system.

    :return: The default ``ngrok`` directory.
    """
    system = get_system()
    user_home = os.path.expanduser("~")
    if system == "darwin":
        return os.path.join(user_home, "Library", "Application Support", "ngrok")
    elif system == "windows":
        return os.path.join(user_home, "AppData", "Local", "ngrok")
    else:
        return os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.join(user_home, ".config")), "ngrok")


def get_system() -> str:
    """
    Parse the name of the OS from the system and return a friendly name.

    :return: The friendly name of the OS.
    :raises: :class:`~pyngrok.exception.PyngrokNgrokInstallError`: When the platform is not supported.
    """
    system = platform.system().replace(" ", "").lower()

    if system.startswith("darwin"):
        return "darwin"
    elif system.startswith("windows") \
            or system.startswith("cygwin") \
            or system.startswith("ming"):
        return "windows"
    elif system.startswith("linux"):
        return "linux"
    elif system.startswith("freebsd"):
        return "freebsd"
    else:
        raise PyngrokNgrokInstallError(f"\"{system}\" is not a supported system")


def get_arch() -> str:
    """
    Get the architecture of the current system. This will be ``i386`` for 32-bit systems, ``x86_64`` for 64-bit
    systems, and have ``_arm`` appended for ARM systems. Special architectures like `s390x` and `ppc64le` will be
    returned as-is.

    :return: The name of the architecture.
    """
    machine = platform.machine().lower()

    if machine in ["s390x", "ppc64", "ppc64le"]:
        return machine

    arch = "x86_64" if machine.endswith("64") else "i386"
    if machine.startswith("arm") or \
            machine.startswith("aarch64"):
        arch += "_arm"
    return arch


def get_ngrok_bin() -> str:
    """
    Get the ``ngrok`` executable for the current system.

    :return: The name of the ``ngrok`` executable.
    :raises: :class:`~pyngrok.exception.PyngrokNgrokInstallError`: When the platform is not supported.
    """
    system = get_system()
    if system in UNIX_BINARIES:
        return "ngrok"
    else:
        return "ngrok.exe"


def get_ngrok_cdn_url(ngrok_version: Optional[str]) -> str:
    """
    Determine the ``ngrok`` CDN URL for the current OS and architecture.

    :param ngrok_version: The major version of ``ngrok`` to be installed.
    :return: The ``ngrok`` CDN URL.
    """
    plat = "{system}_{arch}".format(system=get_system(), arch=get_arch())

    logger.debug(f"Platform to download: {plat}")

    try:
        if ngrok_version == "v2":
            return PLATFORMS[plat]
        elif ngrok_version == "v3":
            return PLATFORMS_V3[plat]
        else:
            raise PyngrokError(f"\"ngrok_version\" must be a supported version: {SUPPORTED_NGROK_VERSIONS}")
    except KeyError:
        raise PyngrokNgrokInstallError(f"\"{plat}\" is not a supported platform")


def install_ngrok(ngrok_path: str,
                  ngrok_version: Optional[str] = "v3",
                  **kwargs: Any) -> None:
    """
    Download and install the latest ``ngrok`` for the current system, overwriting any existing contents
    at the given path.

    :param ngrok_path: The path to where the ``ngrok`` binary will be downloaded.
    :param ngrok_version: The major version of ``ngrok`` to be installed.
    :param kwargs: Remaining ``kwargs`` will be passed to :func:`_download_file`.
    :raises: :class:`~pyngrok.exception.PyngrokError`: When the ``ngrok_version`` is not supported.
    :raises: :class:`~pyngrok.exception.PyngrokNgrokInstallError`: When an error occurs installing ``ngrok``.
    """
    logger.debug(
        "Installing ngrok {ngrok_version} to "
        "{ngrok_path}{optional_overwrite} ...".format(ngrok_version=ngrok_version,
                                                      ngrok_path=ngrok_path,
                                                      optional_overwrite=", overwriting" if os.path.exists(
                                                          ngrok_path) else ""))

    ngrok_dir = os.path.dirname(ngrok_path)

    if not os.path.exists(ngrok_dir):
        os.makedirs(ngrok_dir)

    url = get_ngrok_cdn_url(ngrok_version)

    try:
        download_path = _download_file(url, **kwargs)

        _install_ngrok_zip(ngrok_path, download_path)
    except Exception as e:
        raise PyngrokNgrokInstallError(f"An error occurred while downloading ngrok from {url}: {e}")


def _install_ngrok_zip(ngrok_path: str,
                       zip_path: str) -> None:
    """
    Extract the ``ngrok`` zip file to the given path.

    :param ngrok_path: The path where ``ngrok`` will be installed.
    :param zip_path: The path to the ``ngrok`` zip file to be extracted.
    """
    _print_progress("Installing ngrok ... ")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        logger.debug(f"Extracting ngrok binary from {zip_path} to {ngrok_path} ...")
        zip_ref.extractall(os.path.dirname(ngrok_path))

    os.chmod(ngrok_path, int("700", 8))

    _clear_progress()


def get_ngrok_config(config_path: str,
                     use_cache: bool = True,
                     ngrok_version: Optional[str] = "v3",
                     config_version: Optional[str] = "2") -> Dict[str, Any]:
    """
    Get the ``ngrok`` config from the given path.

    :param config_path: The ``ngrok`` config path to read.
    :param use_cache: Use the cached version of the config (if populated).
    :param ngrok_version: The major version of ``ngrok`` installed.
    :param config_version: The ``ngrok`` config version.
    :return: The ``ngrok`` config.
    """
    with config_file_lock:
        if config_path not in _config_cache or not use_cache:
            with open(config_path, "r") as config_file:
                config = yaml.safe_load(config_file)
                if config is None:
                    config = get_default_config(ngrok_version, config_version)

            _config_cache[config_path] = config

    return _config_cache[config_path]


def get_default_config(ngrok_version: Optional[str],
                       config_version: Optional[str]) -> Dict[str, Any]:
    """
    Get the default config params for the given major version of ``ngrok`` and config version.

    :param ngrok_version: The major version of ``ngrok`` installed.
    :param config_version: The ``ngrok`` config version.
    :return: The default config.
    :raises: :class:`~pyngrok.exception.PyngrokError`: When the ``ngrok_version`` is not supported.
    """
    if ngrok_version == "v2":
        return {}
    elif ngrok_version == "v3":
        config = {"version": config_version}
        if str(config_version) == "2":
            config["region"] = "us"
        return config
    else:
        raise PyngrokError(f"\"ngrok_version\" must be a supported version: {SUPPORTED_NGROK_VERSIONS}")


def install_default_config(config_path: str,
                           data: Optional[Dict[str, Any]] = None,
                           ngrok_version: Optional[str] = "v3",
                           config_version: Optional[str] = "2") -> None:
    """
    Install the given data to the ``ngrok`` config. If a config is not already present for the given path, create one.
    Before saving new data to the default config, validate that they are compatible with ``pyngrok``.

    :param config_path: The path to where the ``ngrok`` config should be installed.
    :param data: A dictionary of things to add to the default config.
    :param ngrok_version: The major version of ``ngrok`` installed.
    :param config_version: The ``ngrok`` config version.
    """
    with config_file_lock:
        if data is None:
            data = {}
        else:
            data = copy.deepcopy(data)

        data.update(get_default_config(ngrok_version, config_version))

        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        if not os.path.exists(config_path):
            open(config_path, "w").close()

        config = get_ngrok_config(config_path,
                                  use_cache=False,
                                  ngrok_version=ngrok_version,
                                  config_version=config_version)

        config.update(data)

        validate_config(config)

        with open(config_path, "w") as config_file:
            logger.debug(f"Installing default ngrok config to {config_path} ...")

            yaml.dump(config, config_file)


def validate_config(data: Dict[str, Any]) -> None:
    """
    Validate that the given dict of config items are valid for ``ngrok`` and ``pyngrok``.

    :param data: A dictionary of things to be validated as config items.
    :raises: :class:`~pyngrok.exception.PyngrokError`: When a key or value fails validation.
    """
    if data.get("web_addr", None) is False:
        raise PyngrokError("\"web_addr\" cannot be False, as the ngrok API is a dependency for pyngrok")
    elif data.get("log_format") == "json":
        raise PyngrokError("\"log_format\" must be \"term\" to be compatible with pyngrok")
    elif data.get("log_level", "info") not in ["info", "debug"]:
        raise PyngrokError("\"log_level\" must be \"info\" to be compatible with pyngrok")


def _download_file(url: str,
                   retries: int = 0,
                   **kwargs: Any) -> str:
    """
    Download a file to a temporary path and emit a status to stdout (if possible) as the download progresses.

    :param url: The URL to download.
    :param retries: The retry attempt index, if download fails.
    :param kwargs: Remaining ``kwargs`` will be passed to :py:func:`urllib.request.urlopen`.
    :return: The path to the downloaded temporary file.
    :raises: :class:`~pyngrok.exception.PyngrokSecurityError`: When the ``url`` is not supported.
    :raises: :class:`~pyngrok.exception.PyngrokNgrokInstallError`: When an error occurs downloading ``ngrok``.
    """
    kwargs["timeout"] = kwargs.get("timeout", DEFAULT_DOWNLOAD_TIMEOUT)

    if not url.lower().startswith("http"):
        raise PyngrokSecurityError(f"URL must start with \"http\": {url}")

    try:
        _print_progress("Downloading ngrok ...")

        logger.debug(f"Download ngrok from {url} ...")

        local_filename = url.split("/")[-1]
        response = urlopen(url, **kwargs)

        status_code = response.getcode()

        if status_code != HTTPStatus.OK:
            logger.debug(f"Response status code: {status_code}")

            raise PyngrokNgrokInstallError(f"Download failed, status code: {status_code}")

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
                    _print_progress(f"Downloading ngrok: {percent_done}%")

        _clear_progress()

        return download_path
    except (socket.timeout, URLError) as e:
        if retries < DEFAULT_RETRY_COUNT:
            logger.warning("ngrok download failed, retrying in 0.5 seconds ...")
            time.sleep(0.5)

            return _download_file(url, retries + 1, **kwargs)
        else:
            raise e


def _print_progress(line: str) -> None:
    if _print_progress_enabled:
        sys.stdout.write(f"{line}\r")
        sys.stdout.flush()


def _clear_progress(spaces: int = 100) -> None:
    if _print_progress_enabled:
        sys.stdout.write((" " * spaces) + "\r")
        sys.stdout.flush()
