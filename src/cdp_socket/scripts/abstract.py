from cdp_socket.socket import SingleCDPSocket
import uuid
import asyncio


class CDPEventIter(object):
    def __init__(self, method, socket: SingleCDPSocket):
        self._method = method
        self._socket = socket
        self._id = uuid.uuid4().hex
        self._fut = None

    def __aiter__(self):
        return self

    def _new_fut(self, result=None):
        self._fut = asyncio.Future()
        # noinspection PyProtectedMember
        self._socket._iter_callbacks[self._method][self._id] = self._fut.set_result

    async def __anext__(self) -> asyncio.Future:
        self._new_fut()
        return await self._fut

    @property
    def id(self):
        return self._id
