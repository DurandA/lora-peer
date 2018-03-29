import asyncio

from resolver import Resolver
from protocol import ForwarderProtocol

loop = asyncio.get_event_loop()


async def resolver():
    default_addr=('127.0.0.1', 9999)
    return default_addr

async def run_app(default_addr, loop):
    print("Starting UDP server")

    # One protocol instance will be created to serve all client requests
    return await loop.create_datagram_endpoint(
        lambda: ForwarderProtocol(resolver, loop=loop), local_addr=('0.0.0.0', 1680))

transport, protocol = loop.run_until_complete(run_app(('127.0.0.1', 9999), loop))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
