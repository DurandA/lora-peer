import struct
from typing import ByteString

class FrameControl(object):
    def __init__(self, f_ctrl):
        self.adr = f_ctrl & 0x80
        self.flag6 = f_ctrl & 0x40
        self.ack = f_ctrl & 0x20
        self.flag4 = f_ctrl & 0x10
        self.f_opts_len = f_ctrl & 0x0f
        self.data = f_ctrl

    def __bytes__(self):
        return bytes([self.data])

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

class Message(object):

    class MessageType(object):
        def __init__(self, uid, description, direction=None):
            self.uid = uid
            self.description = description
            self.direction = direction

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.uid == other.uid
            return self.uid == other

        def __ne__(self, other):
            return not self.__eq__(other)

    JOIN_REQUEST = MessageType(0, 'Join Request')
    JOIN_ACCEPT = MessageType(1, 'Join Accept')
    UNCONFIRMED_DATA_UP = MessageType(2, 'Unconfirmed Data Up', 0) # dir = 0 = uplink
    UNCONFIRMED_DATA_DOWN = MessageType(3, 'Unconfirmed Data Down', 1) # dir = 1 = downlink
    CONFIRMED_DATA_UP = MessageType(4, 'Confirmed Data Up', 0)
    CONFIRMED_DATA_DOWN = MessageType(5, 'Confirmed Data Down', 1)

    @property
    def is_data_message(self):
        # TODO: set mtype
        if self.mtype in (
                Message.UNCONFIRMED_DATA_UP,
                Message.UNCONFIRMED_DATA_DOWN,
                Message.CONFIRMED_DATA_UP,
                Message.CONFIRMED_DATA_DOWN):
            return True
        return False

    @property
    def direction(self):
        if self.mtype in (
                Message.UNCONFIRMED_DATA_UP,
                Message.CONFIRMED_DATA_UP):
            return 0
        elif self.mtype in (
                Message.UNCONFIRMED_DATA_DOWN,
                Message.CONFIRMED_DATA_DOWN):
            return 1

    @property
    def phy_paylod(self):
        return self.payload

    @property
    def adr(self):
        return self.f_ctrl.adr
    @property
    def rfu(self):
        return self.f_ctrl.rfu
    @property
    def ack(self):
        return self.f_ctrl.ack
    @property
    def f_pending(self):
        return self.f_ctrl.f_pending
    @property
    def f_opts_len(self):
        return self.f_ctrl.f_opts_len
    @property
    def adr_ack_req(self):
        return self.f_ctrl.adr_ack_req

    def __init__(self, payload):
        self.payload = payload # phy payload
        mhdr = payload[0] #payload[:1]
        self.mtype, _, _ = self.mhdr = (mhdr >> 5, mhdr & 0x03, mhdr & 0x1c)
        self.mac_payload = mac_payload = payload[1:-4]
        self.mic = payload[-4:]

        if self.mtype == Message.JOIN_REQUEST:
            self.app_eui = mac_payload[:8:-1]
            self.dev_eui = mac_payload[8:16:-1]
            self.dev_nonce = mac_payload[16::-1]
        elif self.mtype == Message.JOIN_ACCEPT:
            self.app_nonce = mac_payload[:3:-1] # 3 bytes
            self.net_id = mac_payload[3:6:-1] # 3 bytes
            self.dev_addr = mac_payload[6:10:-1] # 4 bytes
            self.dl_settings = mac_payload[10] # 1 byte
            self.rx_delay = mac_payload[11] # 1 byte
            if len(mac_payload) == 12+16:
                self.cf_list = mac_payload[12:] # 16 bytes, optional
            else:
                self.cf_list = bytes()
        elif self.is_data_message:
            self.dev_addr = mac_payload[:4] # little-endian
            f_ctrl = mac_payload[4]
            if self.direction:
                self.f_ctrl = DownlinkFrameControl(f_ctrl)
            else:
                self.f_ctrl = UplinkFrameControl(f_ctrl)
            #self.adr, _, self.ack, _, f_opts_len = self.f_ctrl = (f_ctrl & 0x80, f_ctrl & 0x40, f_ctrl & 0x20, f_ctrl & 0x10, f_ctrl & 0x0f)
            self.f_cnt = int.from_bytes(mac_payload[5:7], byteorder='little') # little-endian
            self.f_opts = mac_payload[7:7+self.f_opts_len]

            self.f_hdr = (self.dev_addr, self.f_ctrl, self.f_cnt, self.f_opts)
            fhdr_len = 7+self.f_opts_len
            print('fhdr_len: %i' % fhdr_len)
            if fhdr_len != len(mac_payload):
                self.f_port = int.from_bytes(mac_payload[fhdr_len:fhdr_len+1], byteorder='little')
                self.frm_payload = mac_payload[fhdr_len+1:]
            else:
                self.f_port = bytes()
                self.frm_payload = bytes()

    @classmethod
    def from_hex(cls, _hex):
        return cls(
            bytearray.fromhex(_hex)
        )
