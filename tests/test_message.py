import unittest
from lora.message import Message, JoinRequest, JoinAccept, UnconfirmedDataUp, UnconfirmedDataDown
import binascii


class TestMessage(unittest.TestCase):
    def test_parse_message(self):
        message = Message.from_phy(binascii.unhexlify("40F17DBE4900020001954378762B11FF0D"))

        assert bytes(message) == binascii.unhexlify('40f17dbe4900020001954378762b11ff0d')
        assert message.mhdr == 0x40
        assert message.mac_payload == binascii.unhexlify('f17dbe490002000195437876')
        assert message.mic == binascii.unhexlify('2b11ff0d')
        assert message.f_opts == bytes()
        assert message.f_ctrl == b'\x00'
        # TODO check f_hdr
        assert message.dev_addr == (0x49be7df1).to_bytes(4, byteorder='little')
        assert message.f_cnt == 2
        assert message.f_port == 1
        assert message.frm_payload == binascii.unhexlify('95437876')

        assert type(message) is UnconfirmedDataUp

        assert message.f_ctrl.ack == False
        assert message.f_ctrl.adr == False

    def test_parse_empty_payload_message(self):
        message = Message.from_phy(binascii.unhexlify("40F17DBE49000300012A3518AF"))

    def test_parse_large_message(self):
        pass

    def test_parse_ack(self):
        message = Message.from_phy(binascii.unhexlify("60f17dbe4920020001f9d65d27"))

        assert bytes(message) == binascii.unhexlify('60f17dbe4920020001f9d65d27')
        assert message.mhdr == 0x60
        assert message.mac_payload == binascii.unhexlify('f17dbe4920020001')
        assert message.mic == binascii.unhexlify('f9d65d27')
        assert message.f_opts == bytes()
        assert message.f_ctrl == b'\x20'
        # TODO check f_hdr
        assert message.dev_addr == (0x49be7df1).to_bytes(4, byteorder='little')
        assert message.f_cnt == 2
        assert message.f_port == 1
        assert message.frm_payload == bytes()

        assert type(message) is UnconfirmedDataDown

        assert message.f_ctrl.ack == True
        assert message.f_ctrl.adr == False

    def test_parse_bogus_message(self):
        pass

    def test_parse_join_request(self):
        message = Message.from_phy(binascii.unhexlify("00dc0000d07ed5b3701e6fedf57ceeaf00c886030af2c9"))

        assert bytes(message) == binascii.unhexlify('00dc0000d07ed5b3701e6fedf57ceeaf00c886030af2c9')
        assert message.mhdr == 0x00
        assert message.app_eui == (0x70B3D57ED00000DC).to_bytes(8, byteorder='little')
        assert message.dev_eui == (0x00AFEE7CF5ED6F1E).to_bytes(8, byteorder='little')
        assert message.dev_nonce == (0x86C8).to_bytes(2, byteorder='little')
        assert message.mic == binascii.unhexlify('030AF2C9')

        assert type(message) is JoinRequest

    def test_parse_join_accept(self):
        message = Message.from_phy(binascii.unhexlify("20813f47f508ffa2670b6e23e01f84b9e25d9c4115f02eea0b3dd3e20b3eca92da"))

        assert bytes(message) == binascii.unhexlify("20813f47f508ffa2670b6e23e01f84b9e25d9c4115f02eea0b3dd3e20b3eca92da")
        assert type(message) is JoinAccept

if __name__ == '__main__':
    unittest.main()
