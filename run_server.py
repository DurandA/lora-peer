import asyncio
from semtech.protocol import DownstreamProtocol, UpstreamProtocol

packets = {
    0: UpstreamProtocol.PushData,
    1: UpstreamProtocol.PushAck,
    2: DownstreamProtocol.PullData,
    4: DownstreamProtocol.PullAck
}

class EchoServerProtocol:
    def connection_made(self, transport):
        print("connection made")
        self.transport = transport

    def datagram_received(self, data, addr):
        packet = packets[data[3]].from_bytes(data)
        print('Received %s from %s' % (packet, addr))
        if type(packet) is UpstreamProtocol.PushData:
            ack = UpstreamProtocol.PushAck(packet.token, protocol_verison=packet.protocol_verison)
            self.transport.sendto(bytes(ack), addr)
        elif type(packet) is DownstreamProtocol.PullData:
            ack = DownstreamProtocol.PullAck(packet.token, protocol_verison=packet.protocol_verison)
            self.transport.sendto(bytes(ack), addr)

        #print('Send %r to %s' % (message, addr))
        #self.transport.sendto(data, addr)

loop = asyncio.get_event_loop()
print("Starting UDP server")
# One protocol instance will be created to serve all client requests
listen = loop.create_datagram_endpoint(
    EchoServerProtocol, local_addr=('0.0.0.0', 9999))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
