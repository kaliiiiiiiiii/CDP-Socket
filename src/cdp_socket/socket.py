import asyncio
import orjson
from collections import defaultdict
import websockets
import inspect
import typing

from cdp_socket.exceptions import CDPError
from cdp_socket.utils.conn import get_websock_url, get_json


class SingleCDPSocket:
    def __init__(self, websock_url: str, timeout: float = 10, loop: asyncio.AbstractEventLoop = None,
                 max_size: int = 2 ** 20):
        self._task = None
        if not loop:
            loop = asyncio.get_running_loop()
        self._ws: websockets.WebSocketClientProtocol = None
        self._url = websock_url
        self._timeout = timeout
        self._req_count = 0
        self._max_size = max_size
        self._responses = defaultdict(lambda: asyncio.Future())
        self._events = defaultdict(lambda: [])
        self._iter_callbacks = defaultdict(lambda: {})
        self._loop = loop
        self.on_closed = []
        self._id = websock_url.split("/")[-1]

    def __await__(self):
        return self.start_session(timeout=self._timeout).__await__()

    async def __aenter__(self):
        await self.start_session(timeout=self._timeout)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()

    async def start_session(self, timeout: float = 10):
        try:
            self._ws: websockets.WebSocketClientProtocol = await websockets.connect(uri=self._url,
                                                                                    open_timeout=timeout,
                                                                                    max_size=self._max_size)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Couldn't connect to websocket within {timeout} seconds")
        self._task = self._loop.create_task(self._rec_coro())
        self._task.add_done_callback(self._exc_handler)
        return self

    # noinspection PyMethodMayBeStatic
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
        await self._ws.send(orjson.dumps(_dict))
        self._req_count += 1
        return _id

    # noinspection PyTypeChecker
    async def exec(self, method: str, params: dict = None, timeout: float = 2):
        _id = await self.send(method=method, params=params)
        # noinspection PyStatementEffect
        self._responses[_id]
        try:
            res = await asyncio.wait_for(self._responses[_id], timeout=timeout)
            del self._responses[_id]
            return res
        except Exception as e:
            if _id in self._responses:
                del self._responses[_id]
            raise e

    def add_listener(self, method: str, callback: callable):
        self._events[method].append(callback)

    def remove_listener(self, method: str, callback: callable):
        self._events[method].remove(callback)

    def method_iterator(self, method: str):
        from cdp_socket.scripts.abstract import CDPEventIter
        return CDPEventIter(method=method, socket=self)

    async def wait_for(self, method: str, timeout=None):
        _iter = self.method_iterator(method)
        try:
            res = await asyncio.wait_for(_iter.__anext__(), timeout)
        except asyncio.TimeoutError as e:
            _id = _iter.id
            if _id in self._iter_callbacks:
                del self._iter_callbacks[_id]
            raise e
        return res

    async def _rec_coro(self):
        # noinspection PyUnresolvedReferences
        try:
            async for data in self._ws:
                data = orjson.loads(data)
                err = data.get('error')
                _id = data.get("id")
                if not (err is None):
                    exc = CDPError(error=err)
                    self._responses[_id].set_exception(exc)
                else:
                    if not (_id is None):
                        try:
                            self._responses[_id].set_result(data["result"])
                        except asyncio.InvalidStateError:
                            del self._responses[_id]
                    else:
                        method = data.get("method")
                        params = data.get("params")
                        callbacks: callable = self._events[method]
                        for callback in callbacks:
                            await self._handle_callback(callback, params)
                        for _id, callback in list(self._iter_callbacks[method].items()):
                            await self._handle_callback(callback, params)
                            del self._iter_callbacks[method][_id]
        except websockets.exceptions.ConnectionClosedError as e:
            if self.on_closed:
                for callback in self.on_closed:
                    await self._handle_callback(callback, code=e.code, reason=e.reason)
        await asyncio.sleep(0)

    async def _handle_callback(self, callback: callable, *args, **kwargs):
        if callback:
            res = callback(*args, **kwargs)
            if inspect.isawaitable(res):
                res = self._loop.create_task(res)
            return res

    async def close(self, code: int = 1000, reason: str = ''):
        if self._ws.open:
            task = self._loop.create_task(self._ws.close(code=code, reason=reason))
            try:
                await task
            except AttributeError as e:
                if e.args[0] == "'NoneType' object has no attribute 'encode'":
                    # closed
                    pass
                else:
                    raise e

    @property
    def closed(self):
        return self._ws.closed

    @property
    def ws_url(self):
        return self._url

    @property
    def id(self):
        return self._id

    def __eq__(self, other):
        if isinstance(other, SingleCDPSocket):
            return self._ws.id == other._ws.id
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class CDPSocket:
    def __init__(self, port: int, host: str = "127.0.0.1", timeout: int = 30, loop=None, max_size: int = 2 ** 20):
        if not loop:
            loop = asyncio.get_event_loop()
        self._port = port
        self._max_size = max_size
        self._host_ = host
        self._host = f"{host}:{port}"
        self._timeout = timeout
        self._loop = loop
        # noinspection PyTypeChecker
        self._sockets: typing.Dict[str, SingleCDPSocket] = defaultdict(lambda: None)

    async def __aenter__(self):
        return await self.start_session()

    def __await__(self):
        return self.start_session().__await__()

    async def start_session(self, timeout: float = None):
        if not timeout:
            timeout = self._timeout
        return await asyncio.wait_for(self._connect(), timeout=timeout)

    async def _connect(self):
        ws_url = await get_websock_url(self._port, self._host_, timeout=self._timeout)
        conn = await SingleCDPSocket(ws_url, max_size=self._max_size)
        await conn.close()
        return self

    async def __aexit__(self, *args, **kwargs):
        for socket in list(self.sockets.values()):
            await socket.__aexit__(*args, **kwargs)

    async def close(self, code: int = 1000, reason: str = None):
        for socket in list(self.sockets.values()):
            await socket.close(code, reason)

    @property
    async def targets(self):
        return await get_json(self.host, timeout=2)

    async def get_socket(self, target: dict = None, sock_id: str = None,
                         ensure_new: bool = False, timeout: float or None = 10):
        if not (target or sock_id) or (target and sock_id):
            return ValueError("expected either target or sock_id")
        if target:
            sock_id = target["id"]
        sock_url = f'ws://{self.host}/devtools/page/{sock_id}'

        existing = self.sockets[sock_id]
        if existing and (not ensure_new):
            socket = existing
        else:
            socket = await SingleCDPSocket(sock_url, timeout=timeout, loop=self._loop, max_size=self._max_size)
            self._sockets[sock_id] = socket

            # noinspection PyUnusedLocal
            def remove_sock(code, reason):
                _id = socket.id
                if _id in self._sockets:
                    del self._sockets[_id]

            socket.on_closed.append(remove_sock)
        return socket

    @property
    def host(self):
        return self._host

    @property
    def sockets(self) -> typing.Dict[str, SingleCDPSocket]:
        return self._sockets
