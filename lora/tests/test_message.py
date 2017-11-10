import unittest
from lora.message import Message
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
        assert message.phy_paylod == bytearray.fromhex('40f17dbe4900020001954378762b11ff0d')
        assert message.mhdr == (2, 0, 0)
        assert message.mac_payload == bytearray.fromhex('f17dbe490002000195437876')
        assert message.mic == bytearray.fromhex('2b11ff0d')
        assert message.f_opts == bytearray()
        assert message.f_ctrl == (0, 0, 0, 0, 0)
        # TODO check f_hdr
        assert reorder(message.dev_addr) == bytearray.fromhex('49BE7DF1')
        assert message.f_cnt == 2
        assert message.f_port == 1
        assert message.frm_payload == bytearray.fromhex('95437876')

        assert message.mtype == message.mhdr[0] == Message.UNCONFIRMED_DATA_UP

        assert message.ack == False
        assert message.adr == False

    def test_parse_empty_payload_message(self):
        message = Message.from_hex("40F17DBE49000300012A3518AF")

    def test_parse_large_message(self):
        pass

    def test_parse_ack(self):
        pass

    def test_parse_bogus_message(self):
        pass

if __name__ == '__main__':
    unittest.main()
