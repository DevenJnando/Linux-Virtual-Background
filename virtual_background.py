import pyfakewebcam
import os
import numpy as np
import mediapipe as mp
import cv2
import argparse

BG_COLOR = (192, 192, 192)
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation


# Loads the background and creates a mask using the current frame from the webcam

class Background:

    def __init__(self, args):
        self.width = args.width
        self.height = args.height
        self.background_image = cv2.resize(cv2.imread(args.background_image), (self.width, self.height))

    def frame_with_background(self, current_frame, effects, frame_no):
        mask = generate_mask(current_frame)
        condition = np.stack((mask.segmentation_mask,) * 3, axis=-1) > 0.1
        if self.background_image is None:
            self.background_image = np.zeros(current_frame.shape, dtype=np.uint8)
            self.background_image[:] = BG_COLOR
        applicator = effects.apply_effects(current_frame, frame_no)
        masked_frame = np.where(condition, applicator.current_frame, self.background_image)
        masked_frame = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2RGB)
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
        self.sepia = args.sepia
        self.film_jitter = args.film_jitter
        self.noise = args.noise
        self.width = args.width
        self.height = args.height

    def apply_effects(self, current_frame, frame_no):
        applicator = EffectApplicator(current_frame, frame_no, self.width, self.height)
        if self.sepia is True:
            applicator.sepia_applicator()
        if self.film_jitter is True:
            applicator.film_jittering_applicator()
        if self.noise is True:
            applicator.noise_applicator()
        return applicator


class EffectApplicator:

    def __init__(self, current_frame, frame_no, width, height):
        self.current_frame = current_frame
        self.frame_no = frame_no
        self.width = width
        self.height = height

    def sepia_applicator(self):
        working_frame = self.current_frame
        working_frame = np.array(working_frame, dtype=np.uint8)
        working_frame = cv2.transform(working_frame, np.matrix([[0.272, 0.534, 0.131],
                                                                [0.349, 0.686, 0.168],
                                                                [0.393, 0.769, 0.189]]))
        working_frame[np.where(working_frame > 255)] = 255
        self.current_frame = working_frame

    def film_jittering_applicator(self):
        working_frame = self.current_frame
        if self.frame_no % 2 == 0:
            jitter_height = self.height / 160
        if self.frame_no % 2 == 1:
            jitter_height = -(self.height / 160)
        translation = np.float32([[1, 0, 0], [0, 1, jitter_height]])
        working_frame = cv2.warpAffine(working_frame, translation, (working_frame.shape[1], working_frame.shape[0]))
        self.current_frame = working_frame

    def noise_applicator(self):
        working_frame = self.current_frame
        row, col, ch = working_frame.shape
        gauss = np.random.randn(row, col, ch).astype(np.uint8)
        gauss = gauss.reshape(row, col, ch)
        noisy = working_frame + working_frame * gauss
        self.current_frame = noisy


# Function to generate human outline mask over background

def generate_mask(current_frame):
    with mp_selfie_segmentation.SelfieSegmentation(
            model_selection=0) as selfie_segmentation:
        current_frame.flags.writeable = False
        bilateral_frame = cv2.bilateralFilter(current_frame, 15, 75, 75)
        results = selfie_segmentation.process(bilateral_frame)
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
    parser.add_argument('--sepia',
                        type=str2bool,
                        nargs='?',
                        default=False,
                        help='Toggle a sepia effect.')
    parser.add_argument('--film_jitter',
                        type=str2bool,
                        nargs='?',
                        default=False,
                        help='Toggle a film jittering effect.')
    parser.add_argument('--noise',
                        type=str2bool,
                        nargs='?',
                        default=False,
                        help='Toggle a speckled noise effect.')
    return parser.parse_args()


# Camera polling function

def poll(cam, background, effects, frame_counter):
    while cam.capture.isOpened():
        frame = cam.run()
        frame_no = frame_counter + 1
        frame_counter = frame_no
        frame_with_background = background.frame_with_background(frame, effects, frame_no)
        cam.output.schedule_frame(frame_with_background)


# Main script body

def main():
    args = parse_args()
    print(SCRIPT_DIR)
    cam = CameraOutput(args)
    background = Background(args)
    effects = Effects(args)
    frame_counter = 0
    poll(cam, background, effects, frame_counter)


main()
