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

    MTYPE_JOIN_REQUEST = 0
    MTYPE_JOIN_ACCEPT = 1
    MTYPE_UNCONFIRMED_DATA_UP = 2
    MTYPE_UNCONFIRMED_DATA_DOWN = 3
    MTYPE_CONFIRMED_DATA_UP = 4
    MTYPE_CONFIRMED_DATA_DOWN = 5

    MTYPE_DESCRIPTIONS: [
        'Join Request',
        'Join Accept',
        'Unconfirmed Data Up',
        'Unconfirmed Data Down',
        'Confirmed Data Up',
        'Confirmed Data Down',
        'RFU',
        'Proprietary'
    ]

    MTYPE_DIRECTIONS = [
        None,
        None,
        'up',
        'down',
        'up',
        'down',
        None,
        None
    ]

    FCTRL_ADR = 0x80
    FCTRL_ADRACKREQ = 0x40
    FCTRL_ACK = 0x20
    FCTRL_FPENDING = 0x10

    mtypes = {
        MTYPE_JOIN_REQUEST: ('Join Request', None),
        MTYPE_JOIN_ACCEPT:  ('Join Accept', None),
        MTYPE_UNCONFIRMED_DATA_UP:  ('Unconfirmed Data Up', 'up'),
        MTYPE_UNCONFIRMED_DATA_DOWN:  ('Unconfirmed Data Down', 'down'),
        MTYPE_CONFIRMED_DATA_UP:  ('Confirmed Data Up', 'up'),
        MTYPE_CONFIRMED_DATA_DOWN:  ('Confirmed Data Down', 'down'),
        6: ('RFU', None),
        7: ('Proprietary', None)
    }

    @property
    def is_data_message(self):
        # TODO: set mtype
        if self.mtype in (
                MTYPE_UNCONFIRMED_DATA_UP,
                MTYPE_UNCONFIRMED_DATA_DOWN,
                MTYPE_CONFIRMED_DATA_UP,
                MTYPE_CONFIRMED_DATA_DOWN):
            return True
        return False

    def __init__(self, payload):
        self._payload = payload
        self.mhdr = payload[:1]
        self.mtype = mhdr[0] >> 5)
