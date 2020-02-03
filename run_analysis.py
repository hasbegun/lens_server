import argparse
import glob
import multiprocessing as mp
import os
import time
import cv2
import tqdm

from detectron2.config import get_cfg
from detectron2.data.detection_utils import read_image
from detectron2.utils.logger import setup_logger

from predictor import Visualization

# constants
WINDOW_NAME = "COCO detections"

class Config:
    def __init__(self, config_file="configs/quick_schedules/mask_rcnn_R_50_FPN_inference_acc_test.yaml",
                 opts=[], input_format="file", confidence_threshold=0.5,
                 output="output"):
        """
        :param config_file: Model path. Look up the derectory of "configs"
        Default is configs/quick_schedules/mask_rcnn_R_50_FPN_inference_acc_test.yaml
        :param opts: Extra options. To run on CPU add "MODEL.DEVICE cpu"
        :param input_format: It could be "webcam" for web camera. "video" for mp4, and files for a list of files.
        :param confidence_threshold: Minimum score for instance predictions to be shown. Default is 0.5.
        :param output: The output path.
        """
        setup_logger(name="Config")
        self.logger = setup_logger
        self.__config_file = config_file
        self.__opts = opts
        self.__input_format = input_format
        self.__confidence_threshold = confidence_threshold
        self.__output = output
        self._set_config()

    @property
    def config_file(self):
        return self.__config_file
    @property.setter
    def config_file(self, config_file):
        self.__config_file = config_file
    @property
    def opts(self):
        return self.__opts
    @property.setter
    def opts(self, opts):
        if isinstance(opts, list):
            self.__opts = opts
        else:
            raise Exception("Options must be list format.")
    @property
    def input_format(self):
        return self.__input_format
    @property.setter
    def input_format(self, input_format):
        if input_format in ["webcam", "video", "files"]:
            self.__input_format = input_format
        else:
            raise Exception("Input format must be one of following: webcam, video, files.")
    @property
    def confidence_threshold(self):
        return self.__confidence_threshold
    @property.setter
    def confidence_threshold(self, confidence_threshold):
        if confidence_threshold < 0.0:
            self.logger.info("Confidence threshold value is too low. Set to 0.1. However recommend to set 0.5.")
            self.__confidence_threshold = 0.1
        elif confidence_threshold > 100.0:
            self.logger.info("Confidence threshold value is too high. Set to 100.0. However recommend to set 0.5.")
            self.__confidence_threshold = 100.0
        else:
            self.__confidence_threshold = confidence_threshold
    @property
    def output(self):
        return self.__output
    @property.setter
    def output(self, output):
        self.__output = output

    def _set_config(self):
        self._cfg = get_cfg()
        self._cfg.merge_from_file(self.__config_file)
        self._cfg.merge_from_list(self.__opts)
        self._cfg.MODEL.RETINANET.SCORE_THRESH_TEST = self.__confidence_threshold
        self._cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.__confidence_threshold
        self._cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = self.__confidence_threshold
        self._cfg.freeze()

        self._input_format = self.__input_format
        self._output = self.__output

class Analysis(Config):
    """
    Object detect
    """
    def __init__(self, config_file="configs/quick_schedules/mask_rcnn_R_50_FPN_inference_acc_test.yaml",
                 opts=[], input_format="file", confidence_threshold=0.5,
                 output="output"):
        super(Analysis, self).__init__(config_file, opts, input_format, confidence_threshold, output)
        setup_logger(name="fvcore")
        self.logger = setup_logger

    def analysis(self):
        mp.set_start_method("spawn", force=True)
        self.logger.info("Running analysis...")


def setup_cfg(args):
    # load config from file and command-line arguments
    cfg = get_cfg()
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    # Set score_threshold for builtin models
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = args.confidence_threshold
    cfg.freeze()
    return cfg


def get_parser():
    parser = argparse.ArgumentParser(description="Detectron2 demo for builtin models")
    parser.add_argument(
        "--config-file",
        default="configs/quick_schedules/mask_rcnn_R_50_FPN_inference_acc_test.yaml",
        metavar="FILE",
        help="path to config file",
    )
    parser.add_argument("--webcam", action="store_true", help="Take inputs from webcam.")
    parser.add_argument("--video-input", help="Path to video file.")
    parser.add_argument("--input", nargs="+", help="A list of space separated input images")
    parser.add_argument(
        "--output",
        help="A file or directory to save output visualizations. "
        "If not given, will show output in an OpenCV window.",
    )

    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.5,
        help="Minimum score for instance predictions to be shown",
    )
    parser.add_argument(
        "--opts",
        help="Modify config options using the command-line 'KEY VALUE' pairs",
        default=[],
        nargs=argparse.REMAINDER,
    )
    return parser


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    args = get_parser().parse_args()
    setup_logger(name="fvcore")
    logger = setup_logger()
    logger.info("Arguments: " + str(args))

    cfg = setup_cfg(args)

    demo = Visualization(cfg)

    if args.input:
        if len(args.input) == 1:
            args.input = glob.glob(os.path.expanduser(args.input[0]))
            assert args.input, "The input path(s) was not found"
        for path in tqdm.tqdm(args.input, disable=not args.output):
            # use PIL, to be consistent with evaluation
            img = read_image(path, format="BGR")
            start_time = time.time()
            predictions, visualized_output = demo.run_on_image(img)
            logger.info(
                "{}: detected {} instances in {:.2f}s".format(
                    path, len(predictions["instances"]), time.time() - start_time
                )
            )

            if args.output:
                if os.path.isdir(args.output):
                    assert os.path.isdir(args.output), args.output
                    out_filename = os.path.join(args.output, os.path.basename(path))
                else:
                    assert len(args.input) == 1, "Please specify a directory with args.output"
                    out_filename = args.output
                visualized_output.save(out_filename)
            else:
                cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
                cv2.imshow(WINDOW_NAME, visualized_output.get_image()[:, :, ::-1])
                if cv2.waitKey(0) == 27:
                    break  # esc to quit
    elif args.webcam:
        assert args.input is None, "Cannot have both --input and --webcam!"
        cam = cv2.VideoCapture(0)
        for vis in tqdm.tqdm(demo.run_on_video(cam)):
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.imshow(WINDOW_NAME, vis)
            if cv2.waitKey(1) == 27:
                break  # esc to quit
        cv2.destroyAllWindows()
    elif args.video_input:
        video = cv2.VideoCapture(args.video_input)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frames_per_second = video.get(cv2.CAP_PROP_FPS)
        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        basename = os.path.basename(args.video_input)

        if args.output:
            if os.path.isdir(args.output):
                output_fname = os.path.join(args.output, basename)
                output_fname = os.path.splitext(output_fname)[0] + ".mkv"
            else:
                output_fname = args.output
            assert not os.path.isfile(output_fname), output_fname
            output_file = cv2.VideoWriter(
                filename=output_fname,
                # some installation of opencv may not support x264 (due to its license),
                # you can try other format (e.g. MPEG)
                fourcc=cv2.VideoWriter_fourcc(*"x264"),
                fps=float(frames_per_second),
                frameSize=(width, height),
                isColor=True,
            )
        assert os.path.isfile(args.video_input)
        for vis_frame in tqdm.tqdm(demo.run_on_video(video), total=num_frames):
            if args.output:
                output_file.write(vis_frame)
            else:
                cv2.namedWindow(basename, cv2.WINDOW_NORMAL)
                cv2.imshow(basename, vis_frame)
                if cv2.waitKey(1) == 27:
                    break  # esc to quit
        video.release()
        if args.output:
            output_file.release()
        else:
            cv2.destroyAllWindows()
