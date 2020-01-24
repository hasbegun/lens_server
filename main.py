import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options
import string, random
import uuid
# import asyncio
import aiofiles as aiof
import logging

define("port", default=8888, help="Run on the given port", type=int)
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/upload", UploadHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # self.write('server is running....')
        self.render("www/upload_form.html")
    def post(self):
        pass

class UploadHandler(tornado.web.RequestHandler):
    # async def write_to_disk(self, fname, content):
    #     with open(fname, 'wb') as f:
    #         await f.write(content)
    #     print("File %s is uploaded." % fname)

    async def post(self):
        for field_names, files in self.request.files.items():
            print(field_names)
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                body = info['body']
                print('content type ', content_type)
                # todo: 1. save it only img and video. no other types.
                # todo: 2. support multiple.... maybe multi thread..... async
                # todo: 3. limit the size
                fname = str(uuid.uuid4())
                print('filename: ', filename)
                extenstion = os.path.splitext(filename)[1]
                final_filename = fname + extenstion

                async with aiof.open('uploads/%s' % final_filename, 'wb') as f:
                    await f.write(body)
                    await f.flush()
                self.finish("File %s is uploaded." % final_filename)


        # file1 = self.request.files['file1'][0]
        # original_fname = file1['filename']
        # extenstion = os.path.splitext(original_fname)[1]
        # # fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(20))
        # fname = str(uuid.uuid4())
        # final_filename = fname + extenstion

        # blocking version.
        # self.write_to_disk(final_filename, file1['body'])
        # output_file = open('uploads/%s' % final_filename, 'wb')
        # output_file.write(file1['body'])

        # async version.
        # async with aiof.open('final_filename', 'wb') as f:
        #     await f.write(file1['body'])
        #     await f.flush()
        # self.finish("File %s is uploaded." % final_filename)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
