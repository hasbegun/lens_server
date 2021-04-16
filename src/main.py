#!/usr/bin/env python3

import os
import random
import string

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.web import Application, RequestHandler
from tornado.options import define, options
import tornado.autoreload

from upload_handler import UploadHandler
from lib.innox.std_logger import logger

define("port", default=8080, help="Run on the given port", type=int)
class App(Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/upload', UploadHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'})
        ]
        tornado.web.Application.__init__(self, handlers)

class MainHandler(RequestHandler):
    def get(self):
        # self.write('server is running....')
        self.render("www/upload_form.html")
    def post(self):
        pass


def main():
    http_server = tornado.httpserver.HTTPServer(App())
    http_server.listen(options.port)

    #TODO: remove in prod
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
