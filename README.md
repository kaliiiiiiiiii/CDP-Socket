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

#### CDPSocket
```python
from cdp_socket.utils.utils import launch_chrome, random_port
from cdp_socket.socket import CDPSocket

import os
import asyncio

async def main():
    data_dir = os.getcwd()+"/data_dir"
    PORT = random_port()
    process = launch_chrome(data_dir,PORT)
    
    async with CDPSocket(PORT) as base_socket:
        targets = await base_socket.targets
        sock1 = await base_socket.get_socket(targets[0])
        targets = await sock1.exec("Target.getTargets")
        print(targets)
    os.kill(process.pid, 15)


asyncio.run(main())
```

#### Single socket
```python
from cdp_socket.utils.utils import launch_chrome, random_port
from cdp_socket.utils.conn import get_websock_url

from cdp_socket.socket import SingleCDPSocket

import os
import asyncio


async def main():
    data_dir = os.getcwd()+"/data_dir"
    PORT = random_port()
    process = launch_chrome(data_dir,PORT)

    websock_url = await get_websock_url(PORT, timeout=5)
    async with SingleCDPSocket(websock_url, timeout=5) as sock:
        targets = await sock.exec("Target.getTargets")
        print(targets)

    os.kill(process.pid, 15)


asyncio.run(main())
```

#### on_closed callback
```python
from cdp_socket.socket import SingleCDPSocket

def on_closed(code, reason):
    print("Closed with: ", code, reason)

async with SingleCDPSocket(websock_url, timeout=5) as sock:
    sock.on_closed.append(on_closed)
    # close window for dispatching this event
    targets = await sock.exec("Target.getTargets")
    print(targets)
```

#### add event listener
```python
from cdp_socket.socket import SingleCDPSocket
import asyncio

def on_detached(params):
    print("Detached with: ", params)
    
async with SingleCDPSocket(websock_url, timeout=5) as sock:
        # close window for dispatching this event
        sock.add_listener('Inspector.detached', on_detached)
        await asyncio.sleep(1000)
```

#### iterate over event
```python
from cdp_socket.socket import SingleCDPSocket

async with SingleCDPSocket(websock_url, timeout=5) as sock:
    async for i in sock.method_iterator('Inspector.detached'):
        print(i)
        break
```

#### wait for event
```python
from cdp_socket.socket import SingleCDPSocket

async with SingleCDPSocket(websock_url, timeout=5) as sock:
    res = await sock.wait_for('Inspector.detached')
    print(res)
```

#### synchronous
```python
from cdp_socket.utils.utils import launch_chrome, random_port
from cdp_socket.utils.conn import get_websock_url

from cdp_socket.socket import SingleCDPSocket

import os
import shutil
import asyncio

data_dir = os.getcwd()+"/data_dir"
PORT = random_port()
process = launch_chrome(data_dir,PORT)

loop = asyncio.get_event_loop()
websock_url = loop.run_until_complete(get_websock_url(PORT, timeout=5))

conn = loop.run_until_complete(SingleCDPSocket(websock_url, timeout=5, loop=loop))
targets = loop.run_until_complete(conn.exec("Target.getTargets"))
print(targets)

os.kill(process.pid, 15)
shutil.rmtree(data_dir)
```

## Help

Please feel free to open an issue or fork!

## Performance
On a Win10 Laptop

executing `"Browser.getVersion"`
```
Static benchmark:
passed 3_640.0 mB  in 2.74 s, 13_308.958 mB/sec 
3_656 (each 364 bytes) exec per sec.
```
for returning a big (static) object over javascript
```
JS benchmark:
passed 22_990.0 mB in 3.16 s, 7_284.5374 mB/sec 
1_584 (each 4.598 mB) exec (JS) per s
```



## Deprecated

## Authors

[Aurin Aegerter](mailto:aurinliun@gmx.ch)

## License

see [/LICENSE](/LICENSE)

## known bugs
- [ ] timeout doesn't raise in `httpx` ([bug](https://github.com/encode/httpx/discussions/2142))

## Disclaimer

I am not responsible what you use the code for!!! Also no warranty!

## Acknowledgments

Inspiration, code snippets, etc.
- [Chrome-Developer-Protocol](https://chromedevtools.github.io/devtools-protocol/)

## contributors

- thanks to [@Redrrx](https://github.com/Redrrx) who gave me some starting-points
