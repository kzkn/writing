# -*- coding: utf-8 -*-

from struct import pack


class Frame(object):
    def __init__(self, fin=1, rsv1=0, rsv2=0, rsv3=0, opcode=1, masking_key=[],
            payload=''):
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3
        self.opcode = opcode
        self.masking_key = masking_key
        if isinstance(payload, str):
            self.payload = [ord(c) for c in payload]
        else:
            self.payload = payload
        self.payload_length = len(payload)

    @staticmethod
    def decode(data):
        if isinstance(data, str):
            data = [ord(c) for c in data]

        first_byte = data[0]
        fin = (first_byte >> 7) & 1
        rsv1 = (first_byte >> 6) & 1
        rsv2 = (first_byte >> 5) & 1
        rsv3 = (first_byte >> 4) & 1
        opcode = first_byte & 0xf

        second_byte = data[1]
        mask = (second_byte >> 7) & 1

        payload_length = second_byte & 0x7f
        if payload_length <= 125:
            payload_length = payload_length
            data = data[2:]
        elif payload_length == 126:
            payload_length = (data[2] << 8) \
                           | (data[3] << 0)
            data = data[4:]
        elif payload_length == 127:
            payload_length = (data[2] << 54) \
                           | (data[3] << 48) \
                           | (data[4] << 40) \
                           | (data[5] << 32) \
                           | (data[6] << 24) \
                           | (data[7] << 16) \
                           | (data[8] << 8) \
                           | (data[9] << 0)
            data = data[10:]

        if mask:
            masking_key = data[:4]
            data = data[4:]
        else:
            masking_key = []

        if len(data) == payload_length:
            payload = data[:]
        else:
            payload = data[:payload_length]
        return Frame(fin, rsv1, rsv2, rsv3, opcode, masking_key, payload)

    def mask(self):
        if self.masking_key:
            masked = []
            for i in range(len(self.payload)):
                masked.append(self.payload[i] ^ self.masking_key[i % 4])
            self.payload = masked

    unmask = mask

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        if self.opcode == 1:  # text frame
            return bytearray(self.payload).decode('utf-8')
        else:
            return unicode(self.payload)

    def build(self):
        msg = pack('!B', ((self.fin << 7)
                        | (self.rsv1 << 6)
                        | (self.rsv2 << 5)
                        | (self.rsv3 << 4)
                        | self.opcode))

        mask = (1 << 7) if self.masking_key else 0
        length = self.payload_length
        if length < 126:
            msg += pack('!B', (mask | length))
        elif length < (1 << 16):
            msg += pack('!B', (mask | 126)) + pack('!H', length)
        elif length < (1 << 63):
            msg += pack('!B', (mask | 127)) + pack('!Q', length)
        else:
            raise ValueError()  # too large frame

        payload = ''.join([pack('!B', i) for i in self.payload])
        if not self.masking_key:
            return msg + payload

        masking_key = ''.join([pack('!B', i) for i in self.masking_key])
        return msg + masking_key + payload


def test():
    f1 = Frame.decode([0x81, 0x05, 0x48, 0x65, 0x6c, 0x6c, 0x6f])
    assert str(f1) == 'Hello'

    f2 = Frame.decode(
            [0x81, 0x85, 0x37, 0xfa, 0x21, 0x3d, 0x7f, 0x9f, 0x4d, 0x51, 0x58])
    f2.unmask()
    assert str(f2) == 'Hello'
