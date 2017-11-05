import asyncio

class UpstreamProtocol(object):
    class PushData:
        identifier = b'\x00'

        def __init__(self, token, gateway_id, json_obj, protocol_verison=b'\x01'):
            self.protocol_verison = protocol_verison
            self.token = token
            self.gateway_id = gateway_id
            self.json_obj = json_obj

        def __str__(self):
            return 'PUSH_DATA: %r' % self.json_obj.decode()

        @classmethod
        def from_bytes(cls, data):
            return cls(
                protocol_verison = data[0:1],
                token = data[1:3],
                gateway_id = data[4:12],
                json_obj = data[12:]
            )

    class PushAck:
        identifier = b'\x01'

        def __init__(self, token, protocol_verison=b'\x01'):
            self.protocol_verison = protocol_verison
            self.token = token

        def __bytes__(self):
            return (self.protocol_verison +
                    self.token +
                    self.identifier)

class DownstreamProtocol(object):
    class PullData:
        identifier = b'\x02'

        def __init__(self, token, gateway_id, protocol_verison=b'\x01'):
            self.protocol_verison = protocol_verison
            self.token = token
            self.gateway_id = gateway_id

        @classmethod
        def from_bytes(cls, data):
            return cls(
                protocol_verison = data[0:1],
                token = data[1:3],
                gateway_id = data[4:12]
            )

        def __str__(self):
            return 'PULL_DATA'

    class PullAck:
        identifier = b'\x04'

        def __init__(self, token, protocol_verison=b'\x01'):
            self.protocol_verison = protocol_verison
            self.token = token

        def __bytes__(self):
            return (self.protocol_verison +
                    self.token +
                    self.identifier)

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
