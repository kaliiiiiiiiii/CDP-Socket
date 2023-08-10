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
        if not self._fut:
            self._new_fut()
        self._fut.add_done_callback(self._new_fut)
        return await self._fut

    def __del__(self):
        try:
            # noinspection PyProtectedMember
            del self._socket._iter_callbacks[self._method][self._id]
        except KeyError:
            pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()
