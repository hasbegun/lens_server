import os
import yaml

from tornado.web import RequestHandler
from lib.pybloom import BloomFilter
from lib.innox.std_logger import logger

class UploadRequestHandler(RequestHandler):
    def initialize(self):
        # open the upload deny file ext list and create a bloom filter DENY_LIST.
        upload_deny_file = 'upload_deny_list.yaml'
        bf_config_file = 'bf_config.yaml'
        BF_DEFAULT_CAP = 50
        BF_DEFAULT_ER = 0.001
        try:
            with open(os.path.join(os.path.dirname(__file__), 'config',
                      upload_deny_file), 'r') as f:
                deny_list_dict = yaml.full_load(f)
                logger.debug('Loading upload deny file ext: %s', deny_list_dict)

            with open(os.path.join(os.path.dirname(__file__), 'config',
                      bf_config_file), 'r' ) as f:
                bf_config_dict = yaml.full_load(f)
                logger.debug('Loading bloom filter config : %s', bf_config_dict)

            deny_list_cap = bf_config_dict.get('capacity', BF_DEFAULT_CAP)
            error_rate = bf_config_dict.get('error_rate', BF_DEFAULT_ER)

            self.DENY_LIST = BloomFilter(capacity=deny_list_cap, error_rate=error_rate)
            for i in deny_list_dict.get('deny_ext'):
                self.DENY_LIST.add(i)
        except IOError:
            logger.error('Loading failed: %s', upload_deny_file)