import asyncio
import json
from collections import defaultdict
import websockets
import inspect
from cdp_socket.exceptions import CDPError


class SingleCDPSocket:
    def __init__(self, websock_url: str, timeout: float = 10, loop: asyncio.AbstractEventLoop = None):
        self._task = None
        if not loop:
            loop = asyncio.get_running_loop()
        self._ws: websockets.WebSocketClientProtocol = None
        self._url = websock_url
        self._timeout = timeout
        self._req_count = 0
        self._responses = defaultdict(lambda: asyncio.Future())
        self._events = defaultdict(lambda: [])
        self._iter_callbacks = defaultdict(lambda: {})
        self._loop = loop
        self.on_closed = None

    def __await__(self):
        return self.start_session(timeout=self._timeout).__await__()

    async def __aenter__(self):
        await self.start_session(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def start_session(self, timeout: float = 10):
        try:
            self._ws: websockets.WebSocketClientProtocol = await websockets.connect(uri=self._url,
                                                                                    open_timeout=timeout)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Couldn't connect to websocket within {timeout} seconds")
        self._task = self._loop.create_task(self._rec_coro())
        self._task.add_done_callback(self._exc_handler)
        return self

    def _exc_handler(self, task):
        # noinspection PyProtectedMember
        exc = task._exception
        if exc:
            raise exc

    async def send(self, method: str, params: dict = None):
        _id = [self._req_count][0]
        _dict = {'id': _id, 'method': method}
        if params:
            _dict['params'] = params
        await self._ws.send(json.dumps(_dict))
        self._req_count += 1
        return _id

    async def exec(self, method: str, params: dict = None, timeout: float = 1):
        _id = await self.send(method=method, params=params)
        # noinspection PyTypeChecker
        res = await asyncio.wait_for(self._responses[_id], timeout=timeout)
        return res

    def add_listener(self, method: str, callback: callable):
        self._events[method].append(callback)

    def remove_listener(self, method: str, callback: callable):
        self._events[method].remove(callback)

    def method_iterator(self, method: str):
        from cdp_socket.scripts.abstract import CDPEventIter
        return CDPEventIter(method=method, socket=self)

    async def wait_for(self, method: str):
        _iter = self.method_iterator(method)
        res = await _iter.__anext__()
        _iter.__del__()
        return res

    async def _rec_coro(self):
        # noinspection PyUnresolvedReferences
        try:
            async for data in self._ws:
                data = json.loads(data)
                err = data.get('error')
                if err:
                    exc = CDPError(error=err)
                    self._responses[data["id"]].set_exception(exc)
                else:
                    _id = data.get("id")
                    if _id:
                        self._responses[data["id"]].set_result(data["result"])
                    else:
                        method = data.get("method")
                        params = data.get("params")
                        callbacks: callable = self._events[method]
                        iter_callbacks = list(self._iter_callbacks[method].values())
                        callbacks.extend(iter_callbacks)
                        for callback in callbacks:
                            if callback:
                                if inspect.iscoroutinefunction(callback):
                                    # noinspection PyCallingNonCallable
                                    await callback(params)
                                else:
                                    # noinspection PyCallingNonCallable
                                    callback(params)

        except websockets.exceptions.ConnectionClosedError as e:
            if self.on_closed:
                self.on_closed(code=e.code, reason=e.reason)

    async def close(self, code: int = 1000, reason: str = ''):
        await self._ws.close(code=code, reason=reason)

    @property
    def closed(self):
        return self._ws.closed

    @property
    def ws_url(self):
        return self._url
