__copyright__ = "Copyright (c) 2018-2026 Alex Laird"
__license__ = "MIT"

import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union

from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig
from pyngrok.ngrok import NgrokApiResponse, NgrokTunnel
from pyngrok.process import NgrokProcess


async def install_ngrok(pyngrok_config: Optional[PyngrokConfig] = None) -> None:
    """
    See :func:`~pyngrok.ngrok.install_ngrok`.
    """
    await asyncio.to_thread(ngrok.install_ngrok, pyngrok_config)


async def set_auth_token(token: str,
                         pyngrok_config: Optional[PyngrokConfig] = None) -> None:
    """
    See :func:`~pyngrok.ngrok.set_auth_token`.
    """
    await asyncio.to_thread(ngrok.set_auth_token, token, pyngrok_config)


async def set_api_key(key: str,
                      pyngrok_config: Optional[PyngrokConfig] = None) -> None:
    """
    See :func:`~pyngrok.ngrok.set_api_key`.
    """
    await asyncio.to_thread(ngrok.set_api_key, key, pyngrok_config)


async def get_ngrok_process(pyngrok_config: Optional[PyngrokConfig] = None) -> NgrokProcess:
    """
    See :func:`~pyngrok.ngrok.get_ngrok_process`.
    """
    return await asyncio.to_thread(ngrok.get_ngrok_process, pyngrok_config)


async def connect(addr: Optional[str] = None,
                  proto: Optional[Union[str, int]] = None,
                  name: Optional[str] = None,
                  pyngrok_config: Optional[PyngrokConfig] = None,
                  **options: Any) -> NgrokTunnel:
    """
    See :func:`~pyngrok.ngrok.connect`.
    """
    return await asyncio.to_thread(ngrok.connect, addr, proto, name, pyngrok_config, **options)


async def connect_all(pyngrok_config: Optional[PyngrokConfig] = None) -> List[NgrokTunnel]:
    """
    See :func:`~pyngrok.ngrok.connect_all`.
    """
    return await asyncio.to_thread(ngrok.connect_all, pyngrok_config)


async def disconnect(public_url: str,
                     pyngrok_config: Optional[PyngrokConfig] = None) -> None:
    """
    See :func:`~pyngrok.ngrok.disconnect`.
    """
    await asyncio.to_thread(ngrok.disconnect, public_url, pyngrok_config)


async def get_tunnels(pyngrok_config: Optional[PyngrokConfig] = None) -> List[NgrokTunnel]:
    """
    See :func:`~pyngrok.ngrok.get_tunnels`.
    """
    return await asyncio.to_thread(ngrok.get_tunnels, pyngrok_config)


async def kill(pyngrok_config: Optional[PyngrokConfig] = None) -> None:
    """
    See :func:`~pyngrok.ngrok.kill`.
    """
    await asyncio.to_thread(ngrok.kill, pyngrok_config)


async def api(*args: Any,
              pyngrok_config: Optional[PyngrokConfig] = None) -> NgrokApiResponse:
    """
    See :func:`~pyngrok.ngrok.api`.
    """
    return await asyncio.to_thread(ngrok.api, *args, pyngrok_config=pyngrok_config)


async def get_version(pyngrok_config: Optional[PyngrokConfig] = None) -> Tuple[str, str]:
    """
    See :func:`~pyngrok.ngrok.get_version`.
    """
    return await asyncio.to_thread(ngrok.get_version, pyngrok_config)


async def update(pyngrok_config: Optional[PyngrokConfig] = None) -> str:
    """
    See :func:`~pyngrok.ngrok.update`.
    """
    return await asyncio.to_thread(ngrok.update, pyngrok_config)


async def api_request(url: str,
                      method: str = "GET",
                      data: Optional[Dict[str, Any]] = None,
                      params: Optional[Dict[str, Any]] = None,
                      timeout: float = 4,
                      auth: Optional[str] = None) -> Dict[str, Any]:
    """
    See :func:`~pyngrok.ngrok.api_request`.
    """
    return await asyncio.to_thread(ngrok.api_request, url, method, data, params, timeout, auth)
