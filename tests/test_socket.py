from cdp_socket.utils.utils import launch_chrome, random_port
from cdp_socket.socket import CDPSocket

import os
import asyncio
import unittest
import warnings

global sock
global pid
loop = asyncio.get_event_loop()


async def test_exec():
    global sock
    res = await sock.exec("Browser.getVersion")
    return res['product'] + "\n"


async def test_wait_for():
    global loop
    await sock.exec("Page.enable")
    loop.create_task(sock.exec("Page.navigate", {"url": "https://nowsecure.nl#relax"}))
    res = await sock.wait_for("Page.domContentEventFired")
    return res['timestamp']


async def make_socket():
    global sock
    global pid
    PORT = random_port()

    warnings.simplefilter(action='ignore', category=ResourceWarning)
    pid = launch_chrome(PORT).pid
    warnings.simplefilter("always")

    base_socket = await CDPSocket(PORT)
    targets = await base_socket.targets
    sock = await base_socket.get_socket(targets[0])


class Driver(unittest.TestCase):

    def test_all(self):
        global loop
        loop.run_until_complete(self._test_all())
        self.assertEqual(True, True)

    async def _test_all(self):
        await make_socket()
        res = await asyncio.gather(
            test_exec(),
            test_wait_for()
        )
        print(*res)
        await sock.close()
        os.kill(pid, 15)


if __name__ == '__main__':
    unittest.TestCase(methodName="test_all")
