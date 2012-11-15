# -*- coding: utf-8 -*-

import uuid
import base64
import socket
import urlparse
import os

from frame import Frame


class WebSocketClient(object):
    def __init__(self):
        self.is_connected = False
        self.sock = socket.socket()

    def open(self, uri):
        hostname, port = self.parse_uri(uri)
        self.sock.connect((hostname, port))
        self.handshake(hostname, port)
        self.is_connected = True

    def parse_uri(self, uri):
        parsed = urlparse.urlparse(uri)
        return parsed.hostname, parsed.port or 80

    def handshake(self, host, port):
        data = 'GET /chat HTTP/1.1\r\n'
        data += 'Host: ' + host + '\r\n'
        data += 'Upgrade: websocket\r\n'
        data += 'Connection: Upgrade\r\n'
        data += 'Sec-WebSocket-Key: ' + self.gen_sec_websocket_key() + '\r\n'
        data += 'Sec-WebSocket-Version: 13\r\n'
        data += '\r\n'
        self.sock.send(data)
        self.sock.recv(1024)  # recv handshake response

    def gen_sec_websocket_key(self):
        uid = uuid.uuid4()
        return base64.encodestring(uid.bytes).strip()

    def send(self, msg):
        frm = Frame(masking_key=self.gen_masking_key(), payload=msg)
        frm.mask()
        self.sock.send(frm.build())

    def gen_masking_key(self):
        return [ord(c) for c in os.urandom(4)]

    def recv(self):
        while True:
            data = self.sock.recv(1024)
            frm = Frame.decode(data)
            if frm.opcode == 0x1:  # text
                return str(frm)
            elif frm.opcode == 0x8:  # close
                self.close()
                return None
            elif frm.opcode == 0x9:  # ping
                pong = Frame(opcode=0xA, payload=str(frm))
                self.request.send(pong.build())

    def close(self):
        if self.is_connected:
            self.sock.send(Frame(opcode=0x8).build())
            self.sock.shutdown(socket.SHUT_RDWR)
            self.is_connected = False
            self.sock.close()
