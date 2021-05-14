import os
import yaml

from tornado.web import RequestHandler
from lib.pybloom import BloomFilter
from lib.innox.std_logger import logger

class UploadRequestHandler(RequestHandler):
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
            logger.debug(upload_config_file)
            with open(upload_config_file, 'r') as f:
                logger.debug('bbbb')
                config_dict = yaml.full_load(f)
                # config_dict = yaml.load(f, Loader=yaml.FullLoader)
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
        logger.debug('Upload deny loaded.')

        bloomfilter_cap = config_dict.get('image_restriction').get('bloomfilter_cap', BLOOMFILTER_DEFAULT_CAP)
        bloomfilter_er = config_dict.get('image_restriction').get('error_rate', BLOOMFILTER_DEFAULT_ER)
        self.IMG_ALLOWED_LIST = BloomFilter(capacity=bloomfilter_cap, error_rate=bloomfilter_er)
        for i in config_dict.get('image_restriction').get('allowed_types'):
            self.IMG_ALLOWED_LIST.add(i)
        logger.debug('Upload allowed loaded.')

        self.MAX_IMG_SIZE = config_dict.get('image_restriction').get('max_size', 4194304)
        self.MONGODB_SERVER = config_dict.get('mongodb').get('server', 'mongodb')
        self.MONGODB_PORT = config_dict.get('mongodb').get('port', 27017)
        self.MONGODB_DBNAME = config_dict.get('mongodb').get('db_name', 'upload')
        logger.debug('DB setting loaded.')

