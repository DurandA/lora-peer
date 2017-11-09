import struct

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

    FCTRL_ADR = 0x80
    FCTRL_ADRACKREQ = 0x40
    FCTRL_ACK = 0x20
    FCTRL_FPENDING = 0x10

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
            self.dev_addr = mac_payload[:4:-1]
            f_ctrl = mac_payload[4]
            self.adr, _, _, _, f_opts_len = self.f_ctrl = (f_ctrl & 0x80, f_ctrl & 0x40, f_ctrl & 0x20, f_ctrl & 0x10, f_ctrl & 0x0f)
            self.f_cnt = mac_payload[5:7:-1]
            self.f_opts = mac_payload[7:7+f_opts_len]

            self.f_hdr = (self.dev_addr, self.f_ctrl, self.f_cnt, self.f_opts)
            fhdr_len = 7+f_opts_len
            print('fhdr_len: %i' % fhdr_len)
            if fhdr_len == len(mac_payload):
                self.f_port = mac_payload[fhdr_len:fhdr_len+1]
                self.frm_payload = mac_payload[fhdr_len+1:]
            else:
                self.f_port = bytes()
                self.frm_payload = bytes()

    @classmethod
    def from_hex(cls, _hex):
        return cls(
            bytearray.fromhex(_hex)
        )
