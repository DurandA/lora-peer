import asyncio
from base64 import b64decode
from binascii import hexlify
from datetime import datetime, timedelta
from os import urandom

from lorawan.message import JoinAccept, JoinRequest, MACMessage
from semtech.protocol import (Protocol, PullAck, PullData, PullResp, PushAck,
                              PushData)

class EchoServerProtocol:

    def __init__(self, remote_addr, loop):
        self.remote_addr = remote_addr
        self.remotes = {}
        self.gw_addr = None
        self.loop = loop

    def connection_made(self, transport):
        print("connection made")
        self.transport = transport

    def datagram_received(self, data, addr):
        packet = Protocol.from_packet(data)
        print('Received \x1b[0;30;46m%s\x1b[0m from %s' % (packet, addr))
        if type(packet) is PushData:
            self.gw_addr = self.gw_addr or addr
            if 'rxpk' in packet.json_obj:
                for obj in packet.json_obj['rxpk']:
                    phy_payload = b64decode(obj['data'])
                    message = MACMessage.from_phy(phy_payload)
                    print('\x1b[0;30;42m%s\x1b[0m' % message)
                    if type(message) is JoinRequest:
                        print(message.verify_mic(bytes.fromhex('442DD2300ED0E4967BBCCA25707E4C1E')))
                        app_eui = message.app_eui
                        if app_eui in self.remotes:
                            self.remotes[app_eui].q.put_nowait(data)
                            #self.remotes[app_eui].transport.sendto(data)
                            return
                        self.create_remote(app_eui, packet.gateway_id, data)

            #ack = PushAck(packet.protocol_verison, packet.token)
            #self.transport.sendto(bytes(ack), addr)

            #self.transport.sendto(data, self.remote_addr)
        elif type(packet) is PushAck:
            self.transport.sendto(data, self.gw_addr)
        elif type(packet) is PullData:
            self.gw_addr = self.gw_addr or addr
            ack = PullAck(packet.protocol_verison, packet.token)
            #self.transport.sendto(bytes(ack), addr)
            self.transport.sendto(data, self.gw_addr)
        elif type(packet) is PullAck:
            self.transport.sendto(data, self.gw_addr)
        elif type(packet) is PullResp:
            pass
            #self.transport.sendto(data, self.gw_addr)

    def create_remote(self, app_eui, gateway_id, packet):
        addr = self.remote_addr
        self.remotes[app_eui] = RemoteDatagramProtocol(self, addr, gateway_id, packet)
        coro = self.loop.create_datagram_endpoint(
            lambda: self.remotes[app_eui], remote_addr=addr)
        asyncio.ensure_future(coro)


class RemoteDatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self, proxy, addr, gateway_id, push_data):
        self.proxy = proxy
        self.addr = addr
        self.gateway_id = gateway_id
        self.push_data = push_data
        super().__init__()
        self.expire = datetime.now() + timedelta(seconds=120)
        self.q = asyncio.Queue(maxsize=10)

    async def poll_data(self, keepalive=10.):
        while True:
            # print('poll: %s' % (self.addr,))
            # if self.expire < datetime.now():
            #     del self.proxy.remotes[self.app_eui]
            #     return
            self.transport.sendto(bytes(PullData(1, urandom(2), self.gateway_id)))
            await asyncio.sleep(keepalive)

    async def sender(self, keepalive=30.):
        try:
            while True:
                data = await asyncio.wait_for(self.q.get(), keepalive)
                if data:
                    self.transport.sendto(data)
        except asyncio.TimeoutError:
            del self.proxy.remotes[self.app_eui]

    def connection_made(self, transport):
        print("remote connection made")
        self.transport = transport
        #self.transport.sendto(self.push_data) #TODO
        loop.create_task(self.sender())
        loop.create_task(self.poll_data())

    def datagram_received(self, data, _):
        packet = Protocol.from_packet(data)
        print('Received \x1b[0;30;43m%s\x1b[0m from %s' % (packet, self.addr))
        if type(packet) is PullAck:
            self.expire = datetime.now() + timedelta(seconds=120)
            self.q.put_nowait(False)
        if type(packet) is PullResp:
            obj = packet.json_obj['txpk']
            phy_payload = b64decode(obj['data'])
            message = MACMessage.from_phy(phy_payload)
            print('\x1b[0;30;41m%s\x1b[0m' % message)
            return
            self.proxy.transport.sendto(data, self.proxy.gw_addr)
        if type(packet) is PushAck:
            pass

    def connection_lost(self, exc):
        self.proxy.remotes.pop(self.attr)

loop = asyncio.get_event_loop()
print("Starting UDP server")
# One protocol instance will be created to serve all client requests
listen = loop.create_datagram_endpoint(
    lambda: EchoServerProtocol(remote_addr=('127.0.0.1', 9999), loop=loop), local_addr=('0.0.0.0', 1680))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
