import random

import pyfakewebcam
import os
import numpy as np
import mediapipe as mp
import cv2
import argparse

BG_COLOR = (192, 192, 192)
SCRIPT_DIR = os.path.dirname(__file__)

mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation


# Loads the background and creates a mask using the current frame from the webcam

class Background:

    def __init__(self, args):
        self.width = args.width
        self.height = args.height
        self.background_image = cv2.resize(cv2.imread(args.background_image), (self.width, self.height))

    def frame_with_background(self, current_frame):
        mask = generate_mask(current_frame)
        condition = np.stack((mask.segmentation_mask,) * 3, axis=-1) > 0.1
        if self.background_image is None:
            self.background_image = np.zeros(current_frame.shape, dtype=np.uint8)
            self.background_image[:] = BG_COLOR
        masked_frame = np.where(condition, current_frame, self.background_image)
        return masked_frame


# Captures input from the webcam hardware and outputs to a modprobe v4l2loopback "fake" camera

class CameraOutput:

    def __init__(self, args):
        self.capture = cv2.VideoCapture('/dev/video0')
        self.width = args.width
        self.height = args.height
        self.capture.set(3, self.width)
        self.capture.set(4, self.height)
        self.capture.set(cv2.CAP_PROP_FPS, args.fps)
        try:
            self.output = pyfakewebcam.FakeWebcam(args.output, self.width, self.height)
        except:
            quit(1)

    def run(self):
        ret, frame = self.capture.read()
        if not ret:
            print("Ignoring empty frame.")
        else:
            return frame


# Optional visual effects class

class Effects:

    def __init__(self, args):
        self.wave_distortion = args.wave_distortion

    def apply_effects(self, current_frame):
        if self.wave_distortion is True:
            return


# Function to generate human outline mask over background

def generate_mask(current_frame):
    with mp_selfie_segmentation.SelfieSegmentation(
            model_selection=0) as selfie_segmentation:
        results = selfie_segmentation.process(current_frame)
        return results


def str2bool(string):
    if isinstance(string, bool):
        return string
    if string.lower() in ('true', 't'):
        return True
    elif string.lower() in ('false', 'f'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# Function to parse arguments from the command line into the script

def parse_args():
    parser = argparse.ArgumentParser(description='Create virtual webcam backgrounds in Linux.')
    parser.add_argument('-o',
                        '--output',
                        default='/dev/video2',
                        help='v4l2loopback video output path.')
    parser.add_argument('-b',
                        '--background_image',
                        default=SCRIPT_DIR+'/Backgrounds/burzum_filosofem.jpg',
                        help='Background image path.')
    parser.add_argument('-H',
                        '--height',
                        type=int,
                        default=720,
                        help='Height of the webcam input.')
    parser.add_argument('-W',
                        '--width',
                        type=int,
                        default=1280,
                        help='Width of the webcam input.')
    parser.add_argument('-f',
                        '--fps',
                        type=int,
                        default=30,
                        help='Frames per second for the webcam input.')
    parser.add_argument('--wave_distortion',
                        type=str2bool,
                        nargs='?',
                        default=True,
                        help='Toggle a wave distortion effect.')
    return parser.parse_args()


# Main script body

args = parse_args()
cam = CameraOutput(args)
background = Background(args)
effects = Effects(args)
while cam.capture.isOpened():
    frame = cam.run()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_with_background = background.frame_with_background(rgb_frame)
    effects.apply_effects(frame_with_background)
    cam.output.schedule_frame(frame_with_background)
