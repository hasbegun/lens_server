# import asyncio
import aiofiles as aiof
import os
import gridfs
import uuid

from tornado.web import RequestHandler
from lib.innox.handlers import UploadRequestHandler
from lib.innox.std_logger import logger

class UploadHandler(UploadRequestHandler):
    async def post(self):
        for field_names, files in self.request.files.items():
            logger.info('Field names: %s', field_names)
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                logger.debug('content type %s', content_type)

                _, f_ext = os.path.splitext(filename)
                # upload image
                if not (f_ext in self.IMG_ALLOWED_LIST or content_type.startswith('image/')) \
                    or f_ext in self.DENIED_LIST :
                    logger.error('Uploading file %s is denied.', filename)
                    continue

                file_content = info['body']
                # todo: 1. save it only img and video. no other types.
                # todo: 2. support multiple.... maybe multi thread..... async
                # todo: 3. limit the size
                fname = str(uuid.uuid4())
                final_filename = fname + f_ext

                # upload files to filesystem and modngo.
                # once system is stable enough drop file system upload routine.

                # this stores the file to the mongodb gridfs.
                mongo_upload_done = self.upload_mongo(file_content, filename)

                # maybe optional
                # this stores the file to the file system.
                file_upload_done = await self.upload_file(file_content,
                                                          final_filename)

                if file_upload_done or mongo_upload_done:
                    self.finish("File %s is uploaded." % final_filename)
                else:
                    self.finish("Failed to upload %s." % final_filename)

    async def upload_file(self, file_content, filename):
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        logger.info('upload dir: %s', upload_dir)
        try:
            async with aiof.open(
                '%s/%s' % (upload_dir, filename), 'wb') as f:
                await f.write(file_content)
                await f.flush()

            logger.debug('Upload %s done.', filename)
            return True

        except IOError:
            logger.error('Failed to upload %s.', filename)
            return False

    def upload_mongo(self, file_content, filename):
        logger.debug('Server: %s, Port: %s, DB Name: %s',
            self.MONGODB_SERVER, self.MONGODB_PORT, self.MONGODB_DBNAME)

        try:
            db_client = self.DB_CLIENT[self.MONGODB_DBNAME]
            fs = gridfs.GridFS(db_client)
            res = fs.put(file_content, filename=filename)
            logger.debug('Upload %s to DB done: %s', filename, res)
            return True
        except Exception as e:
            logger.debug('Failed to upload %s in DB.', filename)
            logger.debug(e)
            return False
