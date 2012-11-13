#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler


class MainHandler(RequestHandler):
    def get(self):
        self.render("drawtool.html")


connections = []


class DrawtoolHandler(WebSocketHandler):
    def open(self):
        if self not in connections:
            connections.append(self)

    def on_message(self, msg):
        for conn in connections:
            if self == conn:
                continue

            try:
                conn.write_message(msg)
            except:
                connections.remove(conn)

    def on_close(self):
        if self in connections:
            connections.remove(self)


app = Application([
    (r"/", MainHandler),
    (r"/drawtool", DrawtoolHandler)
    ])

if __name__ == "__main__":
    app.listen(8080)
    IOLoop.instance().start()
