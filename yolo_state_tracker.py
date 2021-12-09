# -*- coding: utf-8 -*-
"""
Class definition of YOLO_v3 style detection model on image and video
"""

import colorsys
import os
from timeit import default_timer as timer

import numpy as np
from keras import backend as K
from keras.models import load_model
from keras.layers import Input
from PIL import Image, ImageFont, ImageDraw

from yolo3.model import yolo_eval, yolo_body, tiny_yolo_body
from yolo3.utils import letterbox_image
import os
from keras.utils import multi_gpu_model

import enum

#from poke_switch_rand_env import *

class YOLO(object):
    _defaults = {
        "model_path": 'model_data/yolo.h5',
        "anchors_path": 'model_data/yolo_anchors.txt',
        "classes_path": 'model_data/coco_classes.txt',
        "score" : 0.8,
        "iou" : 0.9,
        "model_image_size" : (416, 416),
        "gpu_num" : 1,
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults) # set up default values
        self.__dict__.update(kwargs) # and update with user overrides
        self.class_names = self._get_class()
        self.anchors = self._get_anchors()
        self.sess = K.get_session()
        self.boxes, self.scores, self.classes = self.generate()

    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def _get_anchors(self):
        anchors_path = os.path.expanduser(self.anchors_path)
        with open(anchors_path) as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        return np.array(anchors).reshape(-1, 2)

    def generate(self):
        model_path = os.path.expanduser(self.model_path)
        assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'

        # Load model, or construct model and load weights.
        start = timer()
        num_anchors = len(self.anchors)
        num_classes = len(self.class_names)
        is_tiny_version = num_anchors==6 # default setting
        print(model_path)
        try:
            self.yolo_model = load_model(model_path, compile=False)
        except:
            self.yolo_model = tiny_yolo_body(Input(shape=(None,None,3)), num_anchors//2, num_classes) \
                if is_tiny_version else yolo_body(Input(shape=(None,None,3)), num_anchors//3, num_classes)
            self.yolo_model.load_weights(self.model_path) # make sure model, anchors and classes match
        else:
            assert self.yolo_model.layers[-1].output_shape[-1] == \
                num_anchors/len(self.yolo_model.output) * (num_classes + 5), \
                'Mismatch between model and given anchor and class sizes'

        end = timer()
        print('{} model, anchors, and classes loaded in {:.2f}sec.'.format(model_path, end-start))

        # Generate colors for drawing bounding boxes.
        if len(self.class_names) == 1:
            self.colors = ['GreenYellow']
        else:
            hsv_tuples = [(x / len(self.class_names), 1., 1.)
                          for x in range(len(self.class_names))]
            self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
            self.colors = list(
                map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                    self.colors))
            np.random.seed(10101)  # Fixed seed for consistent colors across runs.
            np.random.shuffle(self.colors)  # Shuffle colors to decorrelate adjacent classes.
            np.random.seed(None)  # Reset seed to default.

        # Generate output tensor targets for filtered bounding boxes.
        self.input_image_shape = K.placeholder(shape=(2, ))
        if self.gpu_num>=2:
            self.yolo_model = multi_gpu_model(self.yolo_model, gpus=self.gpu_num)
        boxes, scores, classes = yolo_eval(self.yolo_model.output, self.anchors,
                len(self.class_names), self.input_image_shape,
                score_threshold=self.score, iou_threshold=self.iou)
        return boxes, scores, classes

    def detect_image(self, image, show_stats = True):
        start = timer()

        if self.model_image_size != (None, None):
            assert self.model_image_size[0]%32 == 0, 'Multiples of 32 required'
            assert self.model_image_size[1]%32 == 0, 'Multiples of 32 required'
            boxed_image = letterbox_image(image, tuple(reversed(self.model_image_size)))
        else:
            new_image_size = (image.width - (image.width % 32),
                              image.height - (image.height % 32))
            boxed_image = letterbox_image(image, new_image_size)
        image_data = np.array(boxed_image, dtype='float32')
        if show_stats:
            print(image_data.shape)
        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.

        out_boxes, out_scores, out_classes = self.sess.run(
            [self.boxes, self.scores, self.classes],
            feed_dict={
                self.yolo_model.input: image_data,
                self.input_image_shape: [image.size[1], image.size[0]],
                K.learning_phase(): 0
            })
        if show_stats:
            print('Found {} boxes for {}'.format(len(out_boxes), 'img'))
        out_prediction = []

        font_path = os.path.join(os.path.dirname(__file__),'font/FiraMono-Medium.otf')
        font = ImageFont.truetype(font=font_path,
                    size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 300

        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = self.class_names[c]
            box = out_boxes[i]
            score = out_scores[i]

            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)

            top, left, bottom, right = box
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))

            # image was expanded to model_image_size: make sure it did not pick
            # up any box outside of original image (run into this bug when
            # lowering confidence threshold to 0.01)
            if top > image.size[1] or right > image.size[0]:
                continue
            if show_stats:
                print(label, (left, top), (right, bottom))

            # output as xmin, ymin, xmax, ymax, class_index, confidence
            out_prediction.append([left, top, right, bottom, c, score])

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, bottom])

            # My kingdom for a good redistributable image drawing library.
            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=self.colors[c])
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=self.colors[c])

            draw.text(text_origin, label, fill=(0, 0, 0), font=font)
            del draw

        end = timer()
        if show_stats:
            print('Time spent: {:.3f}sec'.format(end - start))
        return out_prediction, image

    def close_session(self):
        self.sess.close()

def detect_video(yolo, video_path, output_path=""):
    import cv2
    vid = cv2.VideoCapture(video_path)
    if not vid.isOpened():
        raise IOError("Couldn't open webcam or video")
    video_FourCC    = cv2.VideoWriter_fourcc(*'mp4v') #int(vid.get(cv2.CAP_PROP_FOURCC))
    video_fps       = vid.get(cv2.CAP_PROP_FPS)
    video_size      = (int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    isOutput = True if output_path != "" else False
    if isOutput:
        print('Processing {} with frame size {} at {:.1f} FPS'.format(os.path.basename(video_path), video_size, video_fps))
        # print("!!! TYPE:", type(output_path), type(video_FourCC), type(video_fps), type(video_size))
        out = cv2.VideoWriter(output_path, video_FourCC, video_fps, video_size)
    accum_time = 0
    curr_fps = 0
    fps = "FPS: ??"
    prev_time = timer()
    did_battle_start = False
    navigation_action = NavigationAction.STANDBY_ACTIVATE_DYNAMAX
    state = BATTLE_STATES.STANDBY
    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False
    while vid.isOpened():
        return_value, frame = vid.read()
        if not return_value:
            break
        # opencv images are BGR, translate to RGB
        frame = frame[:,:,::-1]
        image = Image.fromarray(frame)
        out_pred, image = yolo.detect_image(image,show_stats = False)
        if len(out_pred) == 0:
            continue
        for output in out_pred:
            left, top, right, bottom, c, score = output
            predicted_class = self.class_names[c]
        result = np.asarray(image)
        curr_time = timer()
        exec_time = curr_time - prev_time
        prev_time = curr_time
        accum_time = accum_time + exec_time
        curr_fps = curr_fps + 1
        if accum_time > 1:
            accum_time = accum_time - 1
            fps = "FPS: " + str(curr_fps)
            curr_fps = 0
        cv2.putText(result, text=fps, org=(3, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.50, color=(255, 0, 0), thickness=2)
        #cv2.namedWindow("result", cv2.WINDOW_NORMAL)
        #cv2.imshow("result", result)
        if isOutput:
            out.write(result[:,:,::-1])
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    vid.release()
    out.release()
    # yolo.close_session()

def get_state_selectable_for_prediction(output):
    left, top, right, bottom, c, score = output
    return None

class WildState():

    def __init__(self, vid):
        self.vid = vid
        self.battle_state = None
        self.did_scan_team_info = False
        self.need_team_order_info = True
        self.did_scan_active_info = False
        # Opponent Switch in/boost move/gain status
        self.need_active_scan = True
        self.waiting_for_button_press = False


    def is_next_state_valid(self, new_state):
        pass

class BATTLE_SUBMENU_SELECTABLES(enum.Enum):
    SWAP_POKEMON = 0
    CHECK_SUMMARY = 1
    RESTORE = 2
    CANCEL = 3

class BUTTON_ACTION(enum.Enum):
    BACK_BUTTON = 0
    A_BUTTON = 1
    Y_BUTTON = 2
    R_BUTTON = 3
    L_BUTTON = 4
    LEFT_BUTTON = 5
    RIGHT_BUTTON = 6
    UP_BUTTON = 7
    DOWN_BUTTON = 8


class BATTLE_STATES(enum.Enum):
    STANDBY = 0
    FIGHT_MENU = 1
    ACTIVE_MENU = 2
    ACTIVE_POKEMON_STATS = 3
    TEAM_MENU = 4
    TEAM_MEMBER_OPTIONS_MENU = 5
    POKEMON_SUMMARY_INFO = 6
    POKEMON_SUMMARY_BASE_STATS = 7
    POKEMON_SUMMARY_ATTACKS = 8
    MUST_SWITCH = 9
    BATTLE_OVER = 10

class BATTLE_SELECTABLES(enum.Enum):
    STANDBY_FIGHT = 0
    STANDBY_POKEMON = 1  # if dynamax selected push right
    STANDBY_BAG = 2
    STANDBY_RUN = 3
    STANDBY_DYNAMAX = 4   # IF others selected, push left
    FIGHT_MENU_ATTACK_1 = 5
    FIGHT_MENU_ATTACK_2 = 6
    FIGHT_MENU_ATTACK_3 = 7
    FIGHT_MENU_ATTACK_4 = 8
    TEAM_POKEMON_SELECTED_1 = 9
    TEAM_POKEMON_SELECTED_2 = 10
    TEAM_POKEMON_SELECTED_3 = 11
    TEAM_POKEMON_SELECTED_4 = 12
    TEAM_POKEMON_SELECTED_5 = 13
    TEAM_POKEMON_SELECTED_6 = 14

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == BATTLE_SELECTABLES.STANDBY_FIGHT:
            return (1039, 409, 1269, 481)
        if self == BATTLE_SELECTABLES.STANDBY_POKEMON:
            return (1039, 486, 1269, 558)
        if self == BATTLE_SELECTABLES.STANDBY_BAG:
            return (1039, 566, 1269, 638)
        if self == BATTLE_SELECTABLES.STANDBY_RUN:
            return (1039, 641, 1269, 713)

    def get_item_for_rect(battle_state, rect):
        if battle_state == BATTLE_STATES.STANDBY:
            if calculate_overlap(BATTLE_SELECTABLES.STANDBY_FIGHT.get_rect(), rect) > 0.7:
                return BATTLE_SELECTABLES.STANDBY_FIGHT
            if calculate_overlap(BATTLE_SELECTABLES.STANDBY_POKEMON.get_rect(), rect) > 0.7:
                return BATTLE_SELECTABLES.STANDBY_POKEMON
            if calculate_overlap(BATTLE_SELECTABLES.STANDBY_BAG.get_rect(), rect) > 0.7:
                return BATTLE_SELECTABLES.STANDBY_BAG
            if calculate_overlap(BATTLE_SELECTABLES.STANDBY_RUN.get_rect(), rect) > 0.7:
                return BATTLE_SELECTABLES.STANDBY_RUN

        return None

class ACTIVE_STATS_INFORMATION(enum.Enum):
    ABILITY_1 = 0
    ABILITY_2 = 1
    FIELD_MODIFIER_1 = 2
    FIELD_MODIFIER_2 = 2
    FIELD_MODIFIER_3 = 2
    FIELD_MODIFIER_4 = 2

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == ACTIVE_STATS_INFORMATION.ABILITY_1:
            return (690, 71, 1172, 125)
        if self == ACTIVE_STATS_INFORMATION.ABILITY_2:
            return (690, 130, 1172, 168)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_1:
            return (690, 225, 1172, 279)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_2:
            return (690, 284, 1172, 338)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_3:
            return (690, 334, 1172, 398)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_4:
            return (690, 395, 1172, 449)

    def get_item_for_rect(rect):
        if calculate_overlap(ACTIVE_STATS_INFORMATION.ABILITY_1.get_rect(), rect) > 0.7:
            return ACTIVE_STATS_INFORMATION.ABILITY_1
        if calculate_overlap(ACTIVE_STATS_INFORMATION.ABILITY_2.get_rect(), rect) > 0.7:
            return ACTIVE_STATS_INFORMATION.ABILITY_2
        if calculate_overlap(ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_1.get_rect(), rect) > 0.7:
            return ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_1
        if calculate_overlap(ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_2.get_rect(), rect) > 0.7:
            return ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_2
        if calculate_overlap(ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_3.get_rect(), rect) > 0.7:
            return ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_3
        if calculate_overlap(ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_4.get_rect(), rect) > 0.7:
            return ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_4

        return None

class ACTIVE_STATS_ELEMENT(enum.Enum):
    ELEMENT_SLOT_1 = 0
    ELEMENT_SLOT_2 = 1

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1:
            return (264, 121, 406, 159)
        if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2:
            return (409, 121, 551, 159)

    def get_item_for_rect(self, rect):
        if calculate_overlap(ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1.get_rect(), rect) > 0.7:
            return ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1
        if calculate_overlap(ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2.get_rect(), rect) > 0.7:
            return ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2

        return None

# Just count the number of buffs/ debuffs per row. no need to compare against rect
# This requires another neural network lookup.
class ACTIVE_STATS_MODIFIER(enum.Enum):
    ATTACK_MODIFIER_ROW = 0
    DEFENSE_MODIFIER_ROW = 1
    SPECIAL_ATTACK_MODIFIER_ROW = 2
    SPECIAL_DEFENSE_MODIFIER_ROW = 3
    SPEED_MODIFIER_ROW = 4
    ACCURACY_MODIFIER_ROW = 5
    EVASIVENESS_MODIFIER_ROW = 6

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == ACTIVE_STATS_MODIFIER.ATTACK_MODIFIER_ROW:
            return (240, 231, 496, 288)
        if self == ACTIVE_STATS_MODIFIER.DEFENSE_MODIFIER_ROW:
            return (240, 284, 496, 341)
        if self == ACTIVE_STATS_MODIFIER.SPECIAL_ATTACK_MODIFIER_ROW:
            return (240, 322, 496, 379)
        if self == ACTIVE_STATS_MODIFIER.SPECIAL_DEFENSE_MODIFIER_ROW:
            return (240, 362, 496, 419)
        if self == ACTIVE_STATS_MODIFIER.SPEED_MODIFIER_ROW:
            return (240, 408, 496, 465)
        if self == ACTIVE_STATS_MODIFIER.ACCURACY_MODIFIER_ROW:
            return (240, 461, 496, 518)
        if self == ACTIVE_STATS_MODIFIER.EVASIVENESS_MODIFIER_ROW:
            return (240, 516, 496, 573)

    def buff_in_stat_rect(self, rect):
        if calculate_overlap(self.get_rect(), rect) > 0.7:
            return True

        return False

def calculate_overlap(rect_1, rect_2):
    XA2 = rect_1[2]
    XB2 = rect_2[2]
    XA1 = rect_1[0]
    XB1 = rect_2[0]

    YA2 = rect_1[3]
    YB2 = rect_2[3]
    YA1 = rect_1[1]
    YB1 = rect_2[1]

    SI = max(0, min(XA2, XB2) - max(XA1, XB1)) * max(0, min(YA2, YB2) - max(YA1, YB1))
    SU = SA + SB - SI
    return float(SI) / SU

class BATTLE_SUBMENU_SELECTABLES(enum.Enum):
    SWAP_POKEMON = 0
    CHECK_SUMMARY = 1
    RESTORE = 2
    CANCEL = 3

if __name__ == '__main__':
    yolo = YOLO(**{
                "score" : 0.8,
                "gpu_num" : 0,
                "model_image_size" : (416, 416),
                }
               )
