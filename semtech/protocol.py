import json
from base64 import b64decode


class TokenFormatException(Exception):
    pass


class Protocol(object):
    def __init__(self, protocol_verison, token, payload=None):
        self.protocol_verison = protocol_verison
        if not isinstance(token, bytes) and len(token)!=2:
            raise TokenFormatException
        self.token = token
        self.payload = payload or bytes()

    @classmethod
    def factory(cls, protocol_verison, token, identifier, payload):
        return packet_types[identifier](protocol_verison, token, payload=payload)

    @classmethod
    def from_packet(cls, packet):
        return cls.factory(
            protocol_verison=packet[0],
            token=packet[1:3],
            identifier=packet[3],
            payload=packet[4:]
        )

    def __bytes__(self):
        return bytes([self.protocol_verison]) + self.token + bytes([self.identifier]) + self.payload

    def __str__(self):
        return '%s(v%i)' % (type(self).__name__, self.protocol_verison)

    @classmethod
    def from_packet(cls, packet):
        return cls.factory(
            protocol_verison=packet[0],
            token=packet[1:3],
            identifier=packet[3],
            payload=packet[4:]
        )

class UpstreamProtocol(Protocol):
    pass

class DownstreamProtocol(Protocol):
    pass

class PushData(UpstreamProtocol):
    identifier = 0x00

    def __init__(self, protocol_verison, token, payload):
        super().__init__(protocol_verison, token, payload)
        self.gateway_id = payload[0:8]
        self._json_obj = payload[8:]

    @property
    def json_obj(self):
        return json.loads(self._json_obj.decode())

    @json_obj.setter
    def json_obj(self, json_obj):
        self._json_obj = json.dumps(json_obj).encode()

    def __str__(self):
        return '%s %r' % (super().__str__(), self.json_obj)

class PushAck(UpstreamProtocol):
    identifier = 0x01

class PullData(DownstreamProtocol):
    identifier = 0x02

    def __init__(self, protocol_verison, token, payload):
        super().__init__(protocol_verison, token, payload)
        self.gateway_id = payload

class PullAck(DownstreamProtocol):
    identifier = 0x04

class PullResp(DownstreamProtocol):
    identifier = 0x03

    def __init__(self, protocol_verison, token, payload):
        super().__init__(protocol_verison, token, payload)
        self._json_obj = payload

    @property
    def json_obj(self):
        return json.loads(self._json_obj.decode())

    def __str__(self):
        return '%s %r' % (super().__str__(), self.json_obj)

packet_types = {
    0x00: PushData,
    0x01: PushAck,
    0x02: PullData,
    0x04: PullAck,
    0x03: PullResp
}
