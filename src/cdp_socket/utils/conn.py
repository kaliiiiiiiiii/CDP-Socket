import httpx
import json
import asyncio


async def get_http(url: str, timeout:float=10):
    async with httpx.AsyncClient() as client:
        result = await client.get(url=url, timeout=timeout)
    return result


async def get_json(host: str, timeout:float=10):
    res = None
    while not res:
        try:
            res = await get_http(f"http://{host}/json", timeout=timeout)
        except httpx.ConnectError:
            pass
    return json.loads(res.text)[0]


async def get_websock_url(port: int, host: str = "localhost", timeout: float = 10):
    host = f"{host}:{port}"
    try:
        _json = await get_json(host, timeout=timeout)
    except httpx.TimeoutException:
        raise asyncio.TimeoutError(f"No response from Chrome within {timeout} seconds, assuming it crashed")
    return _json['webSocketDebuggerUrl']
