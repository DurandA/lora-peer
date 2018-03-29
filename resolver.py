from ipaddress import IPv4Address

import aioethereum


class Resolver(object):
    def __init__(self, client, contract, loop):
        self.client = client
        self.contract = contract
        self.loop = loop

    async def create(uri, contract, loop):
        client = await aioethereum.create_ethereum_client(
            uri, loop=loop)
        resolver = Resolver(client, contract, loop)
        resolver.coinbase = await client.eth_coinbase()
        return resolver

    async def resolve_eui(self, join_eui):
        data = join_eui | 0x81e9dfdd0000000000000000000000000000000000000000000000000000000000000000
        value = await self.client.eth_call(None, to=self.contract, data='0x{:072x}'.format(data))
        return int(value, 16)

    async def resolve_eth_address(self, eth_address):
        data = eth_address | 0x69f9c5ac0000000000000000000000000000000000000000000000000000000000000000
        value = await self.client.eth_call(None, to=self.contract, data='0x{:072x}'.format(data))
        return IPv4Address(int(value, 16))

    async def resolve(self, join_eui):
        eth_address = await self.resolve_eui(join_eui)
        return await self.resolve_eth_address(eth_address)


if __name__ == '__main__':
    import argparse, asyncio

    hex = lambda value: int(value, 16)
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--json-rpc", default='http://localhost:8545', dest='uri', help="host on ethereum node")
    parser.add_argument("eui", type=hex, help="JoinEUI")
    parser.add_argument("contract", help="contract address")

    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    async def go():
        resolver = await Resolver.create(args.uri, args.contract, loop)
        address = await resolver.resolve(args.eui) #0x4e8df0e4f3d352ec
        print(address)

    loop.run_until_complete(go())
