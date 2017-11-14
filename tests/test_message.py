import unittest
from lora.message import Message, JoinRequest, JoinAccept, UnconfirmedDataUp, UnconfirmedDataDown
import binascii
import array

#reorder = lambda x: array.array('I', buf).byteswap()

def swap(typecode, buf):
    buf = array.array(typecode, buf)
    buf.byteswap()
    return buf

def swap16(buf):
    return swap('H', buf)
def swap32(buf):
    return swap('I', buf)
def swap64(buf):
    return swap('L', buf)


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
        assert swap32(message.dev_addr) == bytearray.fromhex('49be7df1')
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
        assert swap32(message.dev_addr) == bytearray.fromhex('49be7df1')
        assert message.f_cnt == 2
        assert message.f_port == 1
        assert message.frm_payload == bytearray()

        assert type(message) is UnconfirmedDataDown

        assert message.f_ctrl.ack == True
        assert message.f_ctrl.adr == False

    def test_parse_bogus_message(self):
        pass

    def test_parse_join_request(self):
        message = Message.from_hex("00dc0000d07ed5b3701e6fedf57ceeaf00c886030af2c9")

        assert bytes(message) == bytearray.fromhex('00dc0000d07ed5b3701e6fedf57ceeaf00c886030af2c9')
        assert message.mhdr == 0x00
        assert swap64(message.app_eui) == bytearray.fromhex('70B3D57ED00000DC')
        assert swap64(message.dev_eui) == bytearray.fromhex('00AFEE7CF5ED6F1E')
        assert swap16(message.dev_nonce) == bytearray.fromhex('86C8')
        assert message.mic == bytearray.fromhex('030AF2C9')

        assert type(message) is JoinRequest

    def test_parse_join_accept(self):
        message = Message.from_hex("20813f47f508ffa2670b6e23e01f84b9e25d9c4115f02eea0b3dd3e20b3eca92da")

        assert bytes(message) == bytearray.fromhex("20813f47f508ffa2670b6e23e01f84b9e25d9c4115f02eea0b3dd3e20b3eca92da")
        assert type(message) is JoinAccept

if __name__ == '__main__':
    unittest.main()
