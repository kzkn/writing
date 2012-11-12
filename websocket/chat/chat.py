#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler


class MainHandler(RequestHandler):
    def get(self):
        self.render("chat.html")


connections = []


class ChatHandler(WebSocketHandler):
    def open(self):
        if self not in connections:
            connections.append(self)

    def on_message(self, msg):
        for conn in connections:
            try:
                conn.write_message(msg)
            except:
                connections.remove(conn)

    def on_close(self):
        if self in connections:
            connections.remove(self)


app = Application([
    (r"/", MainHandler),
    (r"/chat", ChatHandler)
    ])

if __name__ == "__main__":
    app.listen(8080)
    IOLoop.instance().start()
