# CDP-Socket

* Handle [Chrome-Developer-Protocol](https://chromedevtools.github.io/devtools-protocol/) connections

### Feel free to test my code!

## Getting Started

### Dependencies

* [Python >= 3.7](https://www.python.org/downloads/)
* [Chrome-Browser](https://www.google.de/chrome/) installed

### Installing

* [Windows] Install [Chrome-Browser](https://www.google.de/chrome/)
* ```pip install cdp-socket```

#### getting started
```python
from cdp_socket.utils.utils import launch_chrome, random_port
from cdp_socket.utils.conn import get_websock_url

from cdp_socket.socket import SingleCDPSocket

import os
import asyncio


async def main():
    PORT = random_port()
    process = launch_chrome(PORT)

    websock_url = await get_websock_url(PORT, timeout=5)
    async with SingleCDPSocket(websock_url, timeout=5) as conn:
        targets = await conn.exec("Target.getTargets")
        print(targets)

    os.kill(process.pid, 15)


asyncio.run(main())
```

#### on_closed callback
```python
from cdp_socket.socket import SingleCDPSocket

def on_closed(code, reason):
    print("Closed with: ", code, reason)

async with SingleCDPSocket('ws://localhost:52395/devtools/page/9E297E3F03148EFBC52F26EB3E5A6474', timeout=5) as conn:
    conn.on_closed = on_closed
    targets = await conn.exec("Target.getTargets")
    print(targets)
```

#### add event listener
```python
from cdp_socket.socket import SingleCDPSocket
import asyncio

def on_detached(params):
    print("Detached with: ", params)
    
async with SingleCDPSocket('ws://localhost:52395/devtools/page/9E297E3F03148EFBC52F26EB3E5A6474', timeout=5) as conn:
        conn.add_listener('Inspector.detached', on_detached)
        await asyncio.sleep(1000)
```

#### iterate over event
```python
from cdp_socket.socket import SingleCDPSocket

async with SingleCDPSocket('ws://localhost:52395/devtools/page/9E297E3F03148EFBC52F26EB3E5A6474', timeout=5) as conn:
    async for i in conn.method_iterator('Inspector.detached'):
        print(i)
        break
```

#### wait for event
```python
from cdp_socket.socket import SingleCDPSocket

async with SingleCDPSocket('ws://localhost:52395/devtools/page/9E297E3F03148EFBC52F26EB3E5A6474', timeout=5) as conn:
    res = await conn.wait_for('Inspector.detached')
    print(res)
```

## Help

Please feel free to open an issue or fork!

## Todo



## Deprecated

## Authors

[Aurin Aegerter](mailto:aurinliun@gmx.ch)

## License

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

## Disclaimer

I am not responsible what you use the code for!!! Also no warranty!

## Acknowledgments

Inspiration, code snippets, etc.
- [Chrome-Developer-Protocol](https://chromedevtools.github.io/devtools-protocol/)

## contributors

- thanks to @Redrrx who gave me some starting-points
