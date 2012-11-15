# -*- coding: utf-8 -*-

import SocketServer
from base64 import b64encode
from hashlib import sha1

from frame import Frame


class WebSocketServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port

    def start(self):
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        server = SocketServer.ThreadingTCPServer((self.host, self.port),
                WebSocketHandler)
        server.serve_forever()


class WebSocketHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.handshake(self.request.recv(1024))

        while True:
            data = self.request.recv(1024)
            if not len(data):
                continue  # empty data (sent by chrome)

            frm = Frame.decode(data)
            frm.unmask()
            if frm.opcode == 0x1:  # text
                msg = 'you said: ' + str(frm)
                reply = Frame(payload=msg)
                self.request.send(reply.build())
            elif frm.opcode == 0x8:  # close
                self.close_connection()
                break
            elif frm.opcode == 0x9:  # ping
                pong = Frame(opcode=0xA, payload=str(frm))
                self.request.send(pong.build())
            elif frm.opcode == 0xA:  # pong
                continue

    def close_connection(self):
        self.request.send(Frame(opcode=0x8).build())
        self.finish()

    def handshake(self, data):
        fields = self.parse_handshake(data)
        self.send_handshake(fields)

    def parse_handshake(self, data):
        d = dict()
        lines = data.split('\r\n')
        d['Request-Line'] = lines[0]
        for line in lines[1:]:
            if len(line):
                name, value = line.split(': ', 1)
                d[name.lower()] = value
        return d

    def send_handshake(self, fields):
        key = self.accept_key(fields['sec-websocket-key'])
        data = 'HTTP/1.1 101 Switching Protocols\r\n'
        data += 'Upgrade: websocket\r\n'
        data += 'Connection: Upgrade\r\n'
        data += 'Sec-WebSocket-Accept: ' + key + '\r\n'
        data += '\r\n'
        self.request.send(data)

    def accept_key(self, key):
        GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        return b64encode(sha1(key + GUID).digest())


def start():
    s = WebSocketServer()
    s.start()
