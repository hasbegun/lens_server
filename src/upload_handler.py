# import asyncio
import aiofiles as aiof
import filetype
import os
import uuid

from tornado.web import RequestHandler
from lib.innox.handlers import UploadRequestHandler

from lib.innox.std_logger import logger
from lib.pybloom import BloomFilter

class UploadHandler(UploadRequestHandler):
    # async def write_to_disk(self, fname, content):
    #     with open(fname, 'wb') as f:
    #         await f.write(content)
    #     print("File %s is uploaded." % fname)

    async def post(self):
        for field_names, files in self.request.files.items():
            logger.info('Field names: %s', field_names)
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                _, f_ext = os.path.splitext(filename)
                if f_ext in self.DENY_LIST:
                    logger.error('Uploading file %s is denied.', filename)
                    continue

                file_content = info['body']
                logger.debug('content type %s ', content_type)
                # todo: 1. save it only img and video. no other types.
                # todo: 2. support multiple.... maybe multi thread..... async
                # todo: 3. limit the size
                fname = str(uuid.uuid4())
                final_filename = fname + f_ext
                upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
                logger.info('upload dir: %s', upload_dir)

                async with aiof.open(
                    '%s/%s' % (upload_dir, final_filename), 'wb') as f:
                    await f.write(file_content)
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
