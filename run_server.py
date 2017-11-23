import asyncio
from semtech.protocol import Protocol, PushData, PushAck, PullData, PullAck, PullResp
from lora.message import MACMessage, JoinRequest, JoinAccept
from base64 import b64decode
from binascii import hexlify


class EchoServerProtocol:
    def __init__(self, remote_addr, loop):
        self.remote_addr = remote_addr
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
            #ack = PushAck(packet.protocol_verison, packet.token)
            #self.transport.sendto(bytes(ack), addr)
            self.transport.sendto(data, self.remote_addr)
        elif type(packet) is PushAck:
            self.transport.sendto(data, self.gw_addr)
        elif type(packet) is PullData:
            self.gw_addr = self.gw_addr or addr
            #ack = PullAck(packet.protocol_verison, packet.token)
            #self.transport.sendto(bytes(ack), addr)
            self.transport.sendto(data, self.remote_addr)
        elif type(packet) is PullAck:
            self.transport.sendto(data, self.gw_addr)
        elif type(packet) is PullResp:
            self.transport.sendto(data, self.gw_addr)

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
