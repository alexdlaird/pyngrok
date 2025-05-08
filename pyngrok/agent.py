#!/usr/bin/env python

__copyright__ = "Copyright (c) 2018-2025 Alex Laird"
__license__ = "MIT"

import logging
from typing import Any, Dict, List, Optional

from pyngrok import conf
from pyngrok.conf import PyngrokConfig
from pyngrok.ngrok import get_ngrok_process, api_request

logger = logging.getLogger(__name__)


class NgrokAgent:
    """
    An object containing information about an ``ngrok` agent.
    """

    def __init__(self,
                 data: Dict[str, Any]) -> None:
        #: The original tunnel data.
        self.data: Dict[str, Any] = data

        #: The status of the agent.
        self.status: str = data.get("status")
        #: The version of the agent.
        self.agent_version: str = data.get("agent_version")
        #: The session details for the agent.
        self.session: Dict[str, Any] = data.get("session")
        #: The URI of the agent.
        self.uri: str = data.get("uri")

    def __repr__(self) -> str:
        return f"<NgrokAgent: \"{self.uri}\">"

    def __str__(self) -> str:  # pragma: no cover
        return f"NgrokAgent: \"{self.uri}\""


class CapturedRequest:
    """
    An object containing a Captured Request from a ``ngrok` tunnel.
    """

    def __init__(self,
                 data: Dict[str, Any]) -> None:
        #: The original tunnel data.
        self.data: Dict[str, Any] = data

        #: The URI of the captured request.
        self.id: str = data.get("id")
        self.uri: str = data.get("uri")
        self.tunnel_name: str = data.get("tunnel_name")
        self.remote_addr: str = data.get("remote_addr")
        self.start: str = data.get("start")
        self.duration: str = data.get("duration")
        self.request: Dict[str, Any] = data.get("request")
        self.response: Dict[str, Any] = data.get("response")

    def __repr__(self) -> str:
        return f"<CapturedRequest: \"{self.id}\">"

    def __str__(self) -> str:  # pragma: no cover
        return f"CapturedRequest: \"{self.id}\""


def get_agent_status(pyngrok_config: Optional[PyngrokConfig] = None, ) -> NgrokAgent:
    """
    Get the ``ngrok`` agent status.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :return: The requests made to the tunnels.
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    api_url = get_ngrok_process(pyngrok_config).api_url

    return NgrokAgent(api_request(f"{api_url}/api/status", "GET",
                                  timeout=pyngrok_config.request_timeout))


def get_requests(params: Optional[Dict[str, Any]] = None,
                 pyngrok_config: Optional[PyngrokConfig] = None, ) -> List[CapturedRequest]:
    """
    Get a list of requests made to the tunnel.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param params: The URL parameters.
    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :return: The requests made to the tunnels.
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    api_url = get_ngrok_process(pyngrok_config).api_url

    requests = []
    for request in api_request(f"{api_url}/api/requests/http", "GET",
                               params=params,
                               timeout=pyngrok_config.request_timeout)["requests"]:
        requests.append(CapturedRequest(request))
    return requests


def get_request(request_id: str,
                pyngrok_config: Optional[PyngrokConfig] = None, ) -> CapturedRequest:
    """
    Get the given request made to the tunnel.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param request_id: The ID of the request to fetch.
    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    :return: The request made to the tunnel.
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    api_url = get_ngrok_process(pyngrok_config).api_url

    return CapturedRequest(api_request(f"{api_url}/api/requests/http/{request_id}", "GET",
                                       timeout=pyngrok_config.request_timeout))


def replay_request(request_id: str,
                   tunnel_name: Optional[str] = None,
                   pyngrok_config: Optional[PyngrokConfig] = None, ) -> None:
    """
    Replay a given request through the tunnel.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param request_id: The request ID.
    :param tunnel_name: The name of the tunnel to replay the request against, or ``None`` to replay against the
        original tunnel.
    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    api_url = get_ngrok_process(pyngrok_config).api_url

    api_request(f"{api_url}/api/requests/http", "POST",
                data={"id": request_id, "tunnel_name": tunnel_name},
                timeout=pyngrok_config.request_timeout)


def delete_requests(pyngrok_config: Optional[PyngrokConfig] = None) -> None:
    """
    Delete request history on the tunnel.

    If ``ngrok`` is not installed at :class:`~pyngrok.conf.PyngrokConfig`'s ``ngrok_path``, calling this method
    will first download and install ``ngrok``.

    If ``ngrok`` is not running, calling this method will first start a process with
    :class:`~pyngrok.conf.PyngrokConfig`.

    :param pyngrok_config: A ``pyngrok`` configuration to use when interacting with the ``ngrok`` binary,
        overriding :func:`~pyngrok.conf.get_default()`.
    """
    if pyngrok_config is None:
        pyngrok_config = conf.get_default()

    api_url = get_ngrok_process(pyngrok_config).api_url

    api_request(f"{api_url}/api/requests/http", "DELETE",
                timeout=pyngrok_config.request_timeout)
