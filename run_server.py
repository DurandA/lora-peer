import asyncio
from semtech.protocol import Protocol, PushData, PushAck, PullData, PullAck

class EchoServerProtocol:
    def connection_made(self, transport):
        print("connection made")
        self.transport = transport

    def datagram_received(self, data, addr):
        packet = Protocol.from_packet(data)
        print('Received %s from %s' % (packet, addr))
        if type(packet) is PushData:
            ack = PushAck(packet.protocol_verison, packet.token)
            self.transport.sendto(bytes(ack), addr)
        elif type(packet) is PullData:
            ack = PullAck(packet.protocol_verison, packet.token)
            self.transport.sendto(bytes(ack), addr)

loop = asyncio.get_event_loop()
print("Starting UDP server")
# One protocol instance will be created to serve all client requests
listen = loop.create_datagram_endpoint(
    EchoServerProtocol, local_addr=('0.0.0.0', 1680))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
