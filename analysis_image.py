import torch, torchvision
import detectron2
from detectron2.utils.logger import setup_logger

class AnalysisImage:
    def __init__(self, img_file):
        self.__img_img = img_file;
        