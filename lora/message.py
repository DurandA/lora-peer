class Message(object):

    class MType(object):
        def __init__(uid, description, direction=None):
            self.uid = uid
            self.description = description
            self.direction = direction

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.uid == other.uid
            return self.uid == other

        def __ne__(self, other):
            return not self.__eq__(other)

    JOIN_REQUEST = Mtype(0, 'Join Request')
    JOIN_ACCEPT = Mtype(1, 'Join Accept')
    UNCONFIRMED_DATA_UP = Mtype(2, 'Unconfirmed Data Up', 'up')
    UNCONFIRMED_DATA_DOWN = Mtype(3, 'Unconfirmed Data Down', 'down')
    CONFIRMED_DATA_UP = Mtype(4, 'Confirmed Data Up', 'up')
    CONFIRMED_DATA_DOWN = Mtype(5, 'Confirmed Data Down', 'down')

    FCTRL_ADR = 0x80
    FCTRL_ADRACKREQ = 0x40
    FCTRL_ACK = 0x20
    FCTRL_FPENDING = 0x10

    @property
    def is_data_message(self):
        # TODO: set mtype
        if self.mtype in (
                UNCONFIRMED_DATA_UP,
                UNCONFIRMED_DATA_DOWN,
                CONFIRMED_DATA_UP,
                CONFIRMED_DATA_DOWN):
            return True
        return False

    def __init__(self, phy_payload):
        self._payload = phy_payload
        mhdr = payload[0]#payload[:1]
        self.mtype, _, _ = self.mhdr = (mhdr >> 5, mhdr, mhdr & 0x03, mhdr & 0x1c)
        self.mac_payload [1:-4]
        self.mic[-4:]

        if self.mtype == JOIN_REQUEST:
            self.app_eui = mac_payload[:8]
            self.dev_eui =  mac_payload[8:16]
            self.dev_nonce = mac_payload[16:]
        elif self.mtype == JOIN_ACCEPT:
            pass
        elif self.is_data_message:
            pass
