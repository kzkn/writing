#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler


class MainHandler(RequestHandler):
    def get(self):
        self.render("echo.html")


class EchoHandler(WebSocketHandler):
    def on_message(self, message):
        self.write_message(u"You said: " + message)


app = Application([
    (r"/", MainHandler),
    (r"/echo", EchoHandler)
    ])

if __name__ == "__main__":
    app.listen(8080)
    IOLoop.instance().start()
