import os
import yaml

from pymongo import MongoClient
from tornado.web import RequestHandler

from lib.pybloom import BloomFilter
from lib.innox.std_logger import logger

class BaseHandler(RequestHandler):
    def db_conn(self):
        db_config_file = os.path.join(os.path.dirname(__file__), 'conf',
                                      'db_config.yaml')
        logger.info('DB config file: %s', db_config_file)
        try:
            with open(db_config_file, 'r') as f:
                db_config = yaml.full_load(f)
                logger.debug('Loading config file: %s', db_config)
        except IOError:
            logger.error('Failed to load config file: %s', upload_config_file)
            return

        self.MONGODB_SERVER = db_config.get('mongodb').get('server', 'mongodb')
        self.MONGODB_PORT = db_config.get('mongodb').get('port', 27017)
        self.MONGODB_DBNAME = db_config.get('mongodb').get('db_name', 'images')
        self.DB_CLIENT = MongoClient(self.MONGODB_SERVER, self.MONGODB_PORT)

class UploadRequestHandler(BaseHandler):
    """
    bloom filter reference: https://github.com/jaybaird/python-bloomfilter
    """
    def initialize(self):
        # open the upload deny file ext list and create a bloom filter DENY_LIST.
        upload_config_file = os.path.join(os.path.dirname(__file__), 'conf',
                                          'upload_config.yaml')
        BLOOMFILTER_DEFAULT_CAP = 50
        BLOOMFILTER_DEFAULT_ER = 0.001

        try:
            logger.debug('Loading upload config file: %s', upload_config_file)
            with open(upload_config_file, 'r') as f:
                config_dict = yaml.full_load(f)
                logger.debug('Loading config file: %s', config_dict)
        except IOError:
            logger.error('Failed to load config file: %s', upload_config_file)
            return

        # Create a bloomfilter for deny exts.
        bloomfilter_cap = config_dict.get('upload_deny_ext').get('bloomfilter_cap', BLOOMFILTER_DEFAULT_CAP)
        bloomfilter_er = config_dict.get('upload_deny_ext').get('error_rate', BLOOMFILTER_DEFAULT_ER)
        self.DENIED_LIST = BloomFilter(capacity=bloomfilter_cap, error_rate=bloomfilter_er)
        for i in config_dict.get('upload_deny_ext').get('denied_types'):
            self.DENIED_LIST.add(i)
        logger.debug('Upload deny config loaded.')

        bloomfilter_cap = config_dict.get('image_restriction').get('bloomfilter_cap', BLOOMFILTER_DEFAULT_CAP)
        bloomfilter_er = config_dict.get('image_restriction').get('error_rate', BLOOMFILTER_DEFAULT_ER)
        self.IMG_ALLOWED_LIST = BloomFilter(capacity=bloomfilter_cap, error_rate=bloomfilter_er)
        for i in config_dict.get('image_restriction').get('allowed_types'):
            self.IMG_ALLOWED_LIST.add(i)
        logger.debug('Upload allow config loaded.')

        self.MAX_IMG_SIZE = config_dict.get('image_restriction').get('max_size', 4194304)

        self.db_conn()

class FetchHandler(BaseHandler):
    def initialize(self):
        self.db_conn()
