import struct
from typing import ByteString

class FrameControl(object):
    def __init__(self, ctrl_byte):
        self.adr = ctrl_byte & 0x80
        self.flag6 = ctrl_byte & 0x40
        self.ack = ctrl_byte & 0x20
        self.flag4 = ctrl_byte & 0x10
        self.f_opts_len = ctrl_byte & 0x0f
        self.ctrl_byte = ctrl_byte

    def __bytes__(self):
        return bytes([self.ctrl_byte])

    def __eq__(self, other):
        return bytes(self) == other

    def __ne__(self, other):
        return not self.__eq__(other)

class DownlinkFrameControl(FrameControl):
    @property
    def rfu(self):
        return self.flag6
    @property
    def f_pending(self):
        return self.flag4

class UplinkFrameControl(FrameControl):
    @property
    def adr_ack_req(self):
        return self.flag6
    @property
    def rfu(self):
        return self.flag4

class FrameHeader(object):
    def __init__(self, mac_payload, direction):
        self.dev_addr = mac_payload[:4] # little-endian
        f_ctrl = mac_payload[4]
        if direction:
            self.f_ctrl = DownlinkFrameControl(f_ctrl)
        else:
            self.f_ctrl = UplinkFrameControl(f_ctrl)
        self.f_cnt = int.from_bytes(mac_payload[5:7], byteorder='little') # little-endian
        self.f_opts = mac_payload[7:7+self.f_opts_len]

    # @property
    # def adr(self):
    #     return self.f_ctrl.adr
    # @property
    # def rfu(self):
    #     return self.f_ctrl.rfu
    # @property
    # def ack(self):
    #     return self.f_ctrl.ack
    # @property
    # def f_pending(self):
    #     return self.f_ctrl.f_pending
    @property
    def f_opts_len(self):
        return self.f_ctrl.f_opts_len
    # @property
    # def adr_ack_req(self):
    #     return self.f_ctrl.adr_ack_req

    def __len__(self):
        return 7+self.f_opts_len

class Message(object):
    @property
    def is_data_message(self):
        # TODO: set mtype
        if self.mtype in (
                UnconfirmedDataUp,
                UnconfirmedDataDown,
                ConfirmedDataUp,
                ConfirmedDataDown):
            return True
        return False

    def __bytes__(self):
        return bytes([self.mhdr]) + self.mac_payload + self.mic

    # TODO remove
    @property
    def mtype(self):
        return message_types[self.mhdr >> 5]

    @classmethod
    def from_phy(cls, phy_payload):
        return cls.factory(
            mhdr=phy_payload[0], #payload[:1]
            payload=phy_payload[1:-4],
            mic=phy_payload[-4:]
        )

    @classmethod
    def factory(cls, mhdr, payload, mic):
        mtype, _, _ = (mhdr >> 5, mhdr & 0x03, mhdr & 0x1c)
        return message_types[mtype](mhdr, payload, mic)

    def __init__(self, mhdr, payload, mic):
        self.mhdr = mhdr
        mtype, _, _ = (mhdr >> 5, mhdr & 0x03, mhdr & 0x1c)
        self.mac_payload = payload
        self.mic = mic

    @classmethod
    def from_hex(cls, _hex):
        return cls.from_phy(
            bytearray.fromhex(_hex)
        )

class JoinRequest(Message):
    def __init__(self, mhdr, join_request, mic):
        super().__init__(mhdr, join_request, mic)
        assert self.mtype is JoinRequest
        self.app_eui = join_request[:8:-1] # little-endian
        self.dev_eui = join_request[8:16:-1] # little-endian
        self.dev_nonce = join_request[16::-1] # little-endian

    @property
    def join_request(self):
        return self.mac_payload

class JoinAccept(Message):
    def __init__(self, mhdr, join_response, mic):
        super().__init__(mhdr, join_response, mic)
        assert self.mtype is JoinAccept
        self.app_nonce = join_response[:3:-1] # 3 bytes little-endian
        self.net_id = join_response[3:6:-1] # 3 bytes little-endian
        self.dev_addr = join_response[6:10:-1] # 4 bytes little-endian
        self.dl_settings = join_response[10] # 1 byte
        self.rx_delay = join_response[11] # 1 byte
        if len(join_response) == 12+16:
            self.cf_list = join_response[12:] # 16 bytes, optional
        else:
            self.cf_list = bytes()

    @property
    def join_response(self):
        return self.mac_payload

class DataMessage(Message):
    def __init__(self, mhdr, mac_payload, mic):
        super().__init__(mhdr, mac_payload, mic)
        assert self.is_data_message
        #self.__cls__ = self.mtype
        self.f_hdr = FrameHeader(mac_payload, self.direction)

        if len(self.f_hdr) != len(mac_payload):
            self.f_port = int.from_bytes(mac_payload[len(self.f_hdr):len(self.f_hdr)+1], byteorder='little')
            self.frm_payload = mac_payload[len(self.f_hdr)+1:]
        else:
            self.f_port = bytes()
            self.frm_payload = bytes()

    @property
    def dev_addr(self):
        return self.f_hdr.dev_addr
    @property
    def f_ctrl(self):
        return self.f_hdr.f_ctrl
    @property
    def f_cnt(self):
        return self.f_hdr.f_cnt
    @property
    def f_opts(self):
        return self.f_hdr.f_opts

class UnconfirmedDataUp(DataMessage):
    direction = 0
class UnconfirmedDataDown(DataMessage):
    direction = 1
class ConfirmedDataUp(DataMessage):
    direction = 0
class ConfirmedDataDown(DataMessage):
    direction = 1

message_types = {
    0: JoinRequest,
    1: JoinAccept,
    2: UnconfirmedDataUp,
    3: UnconfirmedDataDown,
    4: ConfirmedDataUp,
    5: ConfirmedDataDown
}
