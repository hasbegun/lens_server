#!/usr/bin/env python3

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.web import Application, RequestHandler
from tornado.options import define, options
import tornado.autoreload

from upload_handler import UploadHandler
from show_handler import ShowHandler
from lib.innox.std_logger import logger

define("port", default=8080, help="Run on the given port", type=int)
define("mode", default='dev', help="Running mode.", type=str)
class App(Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/upload', UploadHandler),
            (r'/show', ShowHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'})
        ]
        debug_mode = True if options.mode == 'dev' else False
        if debug_mode:
            logger.info('Debug mode is on!!!')
        # debug=True need to be removed for production.
        tornado.web.Application.__init__(self, handlers, debug=True)

class MainHandler(RequestHandler):
    def get(self):
        self.render("www/upload_form.html")


def main():
    http_server = tornado.httpserver.HTTPServer(App())
    http_server.listen(options.port)

    #TODO: remove in prod
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
