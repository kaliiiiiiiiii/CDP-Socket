from cdp_socket.utils.utils import launch_chrome, random_port
from cdp_socket.socket import CDPSocket
import os
import asyncio

global sock1


async def on_resumed(params):
    global sock1
    await sock1.exec("Fetch.continueRequest", {"requestId": params['requestId']})
    print(params["request"]["url"])


async def main():
    global sock1
    PORT = random_port()
    process = launch_chrome(PORT)

    async with CDPSocket(PORT) as base_socket:
        targets = await base_socket.targets
        target = targets[0]
        sock1 = await base_socket.get_socket(target)
        await sock1.exec("Network.clearBrowserCookies")
        await sock1.exec("Fetch.enable")
        sock1.add_listener("Fetch.requestPaused", on_resumed)
        await sock1.exec("Page.navigate", {"url": "https://nowsecure.nl#relax"})
        await asyncio.sleep(5)

    os.kill(process.pid, 15)


asyncio.run(main())
