import unittest
from lora.message import Message
import binascii

class TestMessage(unittest.TestCase):
    def test_parse_message(self):
        message = Message.from_hex("40F17DBE4900020001954378762B11FF0D")
        assert message.payload == bytearray.fromhex('40f17dbe4900020001954378762b11ff0d')
        assert message.mhdr == (2, 0, 0)
        assert message.mtype == message.mhdr[0] == Message.UNCONFIRMED_DATA_UP
        assert message.mac_payload == bytearray.fromhex('f17dbe490002000195437876')
        print(binascii.hexlify(message.dev_addr))
        print('->')
        print(binascii.hexlify(message.frm_payload))
        assert message.frm_payload == bytearray.fromhex('95437876')

    def test_parse_empty_payload_message(self):
        pass

    def test_parse_large_message(self):
        pass

    def test_parse_ack(self):
        pass

    def test_parse_bogus_message(self):
        pass

if __name__ == '__main__':
    unittest.main()
