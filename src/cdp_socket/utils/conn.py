import asyncio
import aiohttp


async def get_http(url: str, timeout: float or None = 10):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=timeout) as resp:
            return resp


async def get_json(host: str, timeout: float or None = 10):
    res = None
    while not res:
        try:
            async with aiohttp.ClientSession() as session:
                res = await session.get(f"http://{host}/json", timeout=timeout)
                return await res.json()
        except aiohttp.ClientError:
            pass


async def get_websock_url(port: int, host: str = "127.0.0.1", timeout: float or None = 10):
    host = f"{host}:{port}"
    try:
        _json = await asyncio.wait_for(get_json(host, timeout=timeout), timeout)
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError(f"No response from Chrome within {timeout} seconds, assuming it crashed")
    return _json[0]['webSocketDebuggerUrl']
