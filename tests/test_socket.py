import time

from cdp_socket.utils.utils import launch_chrome, random_port
from cdp_socket.socket import CDPSocket

import os
import asyncio
import unittest
import warnings
import orjson
import sys

global sock
global pid
data_dir = os.getcwd()+"/data_dir"
loop = asyncio.get_event_loop()


async def check_exec():
    global sock
    start = time.monotonic()
    n_times = 10_000
    size = sys.getsizeof("Browser.getVersion")  # Bytes
    for _ in range(n_times):
        res = await sock.exec("Browser.getVersion")
    _time = time.monotonic()-start
    size += sys.getsizeof(orjson.dumps(res))
    return (f"\nStatic benchmark:"
            f"\npassed {round(size*n_times/1000,2):_} mB  in {round(_time,2)} s, {round((size* n_times/100) / _time, 4):_} mB/sec "
            f"\n{int(n_times/_time):_} (each {size} bytes) exec per sec.")


async def benchmark():
    global sock
    script = """[{"321":true,"2664":true,"throughout":null,"behavior":{"attack":null,
    "them":"bite this adjective on think"},"curve":null,"dull":647,"joy":225,"handsome":[2088,3634,3256,255]},
    {"321":true,"2664":true,"throughout":null,"behavior":{"attack":null,"them":"bite this adjective on think"},
    "curve":null,"dull":647,"joy":225,"handsome":[2088,3634,3256,255]},{"321":true,"2664":true,"throughout":null,
    "behavior":{"attack":null,"them":"bite this adjective on think"},"curve":null,"dull":647,"joy":225,
    "handsome":[2088,3634,3256,255]},""" + f'"{"A" * 1000}"' + "]"
    args = {"expression": script, "serializationOptions": {"serialization": "deep", "maxDepth": 20}}
    n_times = 5_000
    size = sys.getsizeof(orjson.dumps(args))/1000  # in mB
    start = time.monotonic()
    for _ in range(n_times):
        res = await sock.exec("Runtime.evaluate", args)
        assert (res['result']['deepSerializedValue']['value'][0]['value'][3][1]['value'][1][1]['value'] ==
                'bite this adjective on think')
    _time = time.monotonic() - start
    size += sys.getsizeof(orjson.dumps(res))/1000
    return (f"\nJS benchmark:"
            f"\npassed {size* n_times:_} mB in {round(_time, 2)} s, {round((size* n_times) / _time, 4):_} mB/sec "
            f"\n{int(n_times/_time):_} (each {size} mB) exec (JS) per s")


async def check_wait_for():
    global loop
    await sock.exec("Page.enable")
    # noinspection PyAsyncCall

    wait = asyncio.ensure_future(sock.wait_for("Page.domContentEventFired"))
    await sock.exec("Page.navigate", {"url": "chrome://version"})
    res = await wait
    monotonic_time = res['timestamp']


async def make_socket():
    global sock
    global pid
    PORT = random_port()

    warnings.simplefilter(action='ignore', category=ResourceWarning)
    pid = launch_chrome(data_dir, PORT).pid
    warnings.simplefilter("always")

    base_socket = await CDPSocket(PORT)
    targets = await base_socket.targets
    sock = await base_socket.get_socket(targets[0])


class Driver(unittest.TestCase):

    def test_all(self):
        global loop
        loop.run_until_complete(self._all())
        self.assertEqual(True, True)

    # noinspection PyMethodMayBeStatic
    async def _all(self):
        await make_socket()
        print(await check_exec())
        await check_wait_for()
        print(await benchmark())
        await sock.close()
        os.kill(pid, 15)


if __name__ == '__main__':
    unittest.TestCase(methodName="test_all")
