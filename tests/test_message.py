import unittest
from lora.message import Message, UnconfirmedDataUp, UnconfirmedDataDown
import binascii
import array

#reorder = lambda x: array.array('I', buf).byteswap()

def reorder(buf):
    buf = array.array('I', buf)
    buf.byteswap()
    return buf

class TestMessage(unittest.TestCase):
    def test_parse_message(self):
        message = Message.from_hex("40F17DBE4900020001954378762B11FF0D")

        assert bytes(message) == bytearray.fromhex('40f17dbe4900020001954378762b11ff0d')
        assert message.mhdr == 0x40
        assert message.mac_payload == bytearray.fromhex('f17dbe490002000195437876')
        assert message.mic == bytearray.fromhex('2b11ff0d')
        assert message.f_opts == bytearray()
        assert message.f_ctrl == b'\x00'
        # TODO check f_hdr
        assert reorder(message.dev_addr) == bytearray.fromhex('49be7df1')
        assert message.f_cnt == 2
        assert message.f_port == 1
        assert message.frm_payload == bytearray.fromhex('95437876')

        assert type(message) is UnconfirmedDataUp

        assert message.f_ctrl.ack == False
        assert message.f_ctrl.adr == False

    def test_parse_empty_payload_message(self):
        message = Message.from_hex("40F17DBE49000300012A3518AF")

    def test_parse_large_message(self):
        pass

    def test_parse_ack(self):
        message = Message.from_hex("60f17dbe4920020001f9d65d27")

        assert bytes(message) == bytearray.fromhex('60f17dbe4920020001f9d65d27')
        assert message.mhdr == 0x60
        assert message.mac_payload == bytearray.fromhex('f17dbe4920020001')
        assert message.mic == bytearray.fromhex('f9d65d27')
        assert message.f_opts == bytearray()
        assert message.f_ctrl == b'\x20'
        # TODO check f_hdr
        assert reorder(message.dev_addr) == bytearray.fromhex('49be7df1')
        print(message.f_cnt)
        assert message.f_cnt == 2
        assert message.f_port == 1
        assert message.frm_payload == bytearray()

        assert type(message) is UnconfirmedDataDown

        assert message.f_ctrl.ack == True
        assert message.f_ctrl.adr == False

    def test_parse_bogus_message(self):
        pass

if __name__ == '__main__':
    unittest.main()
