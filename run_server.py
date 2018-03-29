import asyncio
import argparse

from resolver import Resolver
from protocol import ForwarderProtocol

loop = asyncio.get_event_loop()


async def run_app(eth_node_uri, contract, loop):
    print("Starting UDP server")

    resolver = await Resolver.create(eth_node_uri, contract, loop)

    # One protocol instance will be created to serve all client requests
    return await loop.create_datagram_endpoint(
        lambda: ForwarderProtocol(resolver.resolve, loop=loop), local_addr=('0.0.0.0', 1680))

hex = lambda value: int(value, 16)
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--json-rpc", default='http://localhost:8545', dest='uri', help="host on ethereum node")
parser.add_argument("contract", help="contract address")

args = parser.parse_args()

loop = asyncio.get_event_loop()

transport, protocol = loop.run_until_complete(run_app(args.uri, args.contract, loop))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
