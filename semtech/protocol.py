import json
from base64 import b64decode

class UpstreamProtocol(object):
    class PushData:
        identifier = b'\x00'

        def __init__(self, token, gateway_id, json_obj, protocol_verison=b'\x01'):
            self.protocol_verison = protocol_verison
            self.token = token
            self.gateway_id = gateway_id
            self._json_obj = json_obj

        @property
        def json_obj(self):
            return json.loads(self._json_obj.decode())

        @property
        def data(self):
            try:
                return b64decode(self.json_obj['rxpk'][0]['data'])
            except KeyError:
                print('ERROR')
                print(self.json_obj)

        def __str__(self):
            data = self.data
            mhdr = data[:1]
            print('mtype')
            print(mhdr[0] >> 5)
            return 'PUSH_DATA: %r' % self.json_obj

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
