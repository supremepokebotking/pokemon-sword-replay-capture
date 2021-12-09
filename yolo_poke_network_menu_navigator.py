import colorsys
import os
from timeit import default_timer as timer
import re
#from PIL import Image, ImageFont, ImageDraw

import os
#from dark_yolo import YOLO
from opencv_yolo import YOLO

import enum
import numpy as np
import cv2
import pytesseract

from poke_state_common import *
from pokemon_regex import *
from image_text_processing import *
import time
from switch_button_press import *

import random

import datetime
datetime_object = datetime.datetime.now()
print(datetime_object)

import logging
log_filename = 'logs/circle_state_%s.log' % (datetime_object)
logging.basicConfig(filename=log_filename, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.warning('This will get logged to a file')
logging.info('This will info message get logged to a file')


party_pokemon = [NetworkNavigationAction.PARTY_ADD_FIRST_POKEMON, NetworkNavigationAction.PARTY_ADD_SECOND_POKEMON, NetworkNavigationAction.PARTY_ADD_THIRD_POKEMON, NetworkNavigationAction.PARTY_ADD_FOURTH_POKEMON, NetworkNavigationAction.PARTY_ADD_FIFTH_POKEMON, NetworkNavigationAction.PARTY_ADD_SIXTH_POKEMON]

class NetworkState():

#    def __init__(self, trainer_name='thunder'):
    def __init__(self, trainer_name='Lou Rui'):
        self.trainer_name = trainer_name
        self.navigation_actions = []
#        self.navigation_actions = np.random.choice(party_pokemon, 3, replace=False).tolist()
#        self.navigation_actions.append(NetworkNavigationAction.QUEUE_MATCH)
        self.current_navigation_action = None
        self.battle_state = None
        self.battle_selectable = None
        self.battle_sub_selectable = None
        self.is_series_done = False

    def reset(self):
        self.navigation_actions = []
        self.current_navigation_action = None
        self.battle_state = None
        self.battle_selectable = None
        self.battle_sub_selectable = None
        self.is_series_done = False


    def process_frame(self, image, labels_boxes):
        self.curr_frame = image
        self.labels_and_boxes = labels_boxes
        center_team = None
        wait = 0.27


        state = network_update_state(labels_boxes)
        self.battle_state = state
        print('battle_state:', self.battle_state)
        #Emergency override because of japanese/unknown 3 member temas?
        if self.battle_state == None and (('team_pokemon_selected' in labels_boxes) or ('team_pokemon' in labels_boxes)):
            self.battle_state = NETWORK_STATES.NETWORK_PARTY_SELECT
        if self.battle_state == None and (('available_team' in labels_boxes) or ('empty_team' in labels_boxes)):
            self.battle_state = NETWORK_STATES.NETWORK_TEAM_SELECT
        next_battle_selectable = network_update_selectables(self.battle_state, labels_boxes)
        next_battle_sub_selectable = network_update_sub_selectables(self.battle_state, next_battle_selectable, labels_boxes)
        action = None
        done = False
        print('next_battle_selectable:', next_battle_selectable)
        print('next_battle_sub_selectable', next_battle_sub_selectable)

        # Something must've went wrong during team select
        if 'match_about_to_begin' in labels_boxes:
            print('emergency match about to begin trigger')
            logging.info('emergency match about to begin trigger')
            self.is_series_done = True

        if self.current_navigation_action == None and len(self.navigation_actions):
            self.current_navigation_action = self.navigation_actions.pop(0)

        # Update if battle state isnt None
        if self.battle_state != None:
            self.battle_selectable = next_battle_selectable
            self.battle_sub_selectable = next_battle_sub_selectable

        # Handle disconnect
        if self.battle_state == NETWORK_STATES.NETWORK_PLAYER_DISCONNECT:
            self.current_navigation_action = None
            action = BUTTON_ACTION.A_BUTTON
            done = False
            return action, done, wait


        if self.current_navigation_action == None and self.battle_state != None and self.battle_state != NETWORK_STATES.NETWORK_TEAM_SELECT:
            # Assume at any other screen
            if self.battle_state != NETWORK_STATES.NETWORK_CONTINUE_BATTLING:
                self.current_navigation_action = NetworkNavigationAction.NAVIGATE_TO_TEAM_SELECTION
                # Flip a coin between continue fighting and another team
            else:
                # 33% chance to switch teams
                if random.randint(0,10) % 3 == 0:
                    self.current_navigation_action = NetworkNavigationAction.NAVIGATE_TO_TEAM_SELECTION
                else:
                    self.current_navigation_action = NetworkNavigationAction.PARTY_COUNT_POKEMON

        # Update if battle state isnt None
        if self.battle_state != None and self.current_navigation_action != None:
            action = self.current_navigation_action.action_for_state(self.battle_state, self.battle_selectable, self.battle_sub_selectable)
            print('we are hereeeeeee')
            print(action)
            done = self.check_if_nav_action_finished(self.current_navigation_action, self.battle_state, self.battle_selectable, self.battle_sub_selectable, action)

        # if no navigation and on team page, possibly select
        if self.battle_state == NETWORK_STATES.NETWORK_TEAM_SELECT and self.current_navigation_action == None:
            for label in labels_boxes:
                if label == 'available_team':
                    for rect in labels_boxes[label]:
                        if RENTAL_TEAM_MENU.get_item_for_rect(rect):
                            center_team = RENTAL_TEAM_MENU.get_item_for_rect(rect)
            print('center_team', center_team)
            if center_team != None:
                #50% chance to select team, otherwise keep Going
                if False and random.randint(0, 10) % 2 == 0:
                    self.navigation_actions.append(NetworkNavigationAction.FIND_NEXT_TEAM)
                else:
                    self.navigation_actions.append(NetworkNavigationAction.SELECT_CURRENT_TEAM)
            else:
                self.navigation_actions.append(NetworkNavigationAction.FIND_NEXT_TEAM)

        if done:
            print('nav completed:', self.current_navigation_action)
            if self.current_navigation_action == NetworkNavigationAction.NAVIGATE_TO_TEAM_SELECTION:
                self.navigation_actions.append(NetworkNavigationAction.FIND_NEXT_TEAM)
            if self.current_navigation_action == NetworkNavigationAction.FIND_NEXT_TEAM:
                self.switching_team()
            if self.current_navigation_action == NetworkNavigationAction.SELECT_CURRENT_TEAM:
                self.selecting_team()
                self.navigation_actions.append(NetworkNavigationAction.PARTY_COUNT_POKEMON)
            if self.current_navigation_action in party_pokemon:
                self.adding_pokemon_to_party()
            if self.current_navigation_action == NetworkNavigationAction.PARTY_COUNT_POKEMON:
                self.navigation_actions.extend(np.random.choice(self.party_pokemon, 3, replace=False).tolist())
                self.navigation_actions.append(NetworkNavigationAction.QUEUE_MATCH)
            if self.current_navigation_action == NetworkNavigationAction.QUEUE_MATCH:
                self.queued_for_match()
                self.is_series_done = True
            self.current_navigation_action = None
        print('Current Nave')
        print(self.current_navigation_action)

        print('Nav Actions')
        print(self.navigation_actions)

        # Inspect network message only if battle state is none
        # Should be ok to block
        # Dont want decisions to stack
        if self.battle_state is None and 'network_message' in self.labels_and_boxes:
            message = parse_network_message(self.get_subframe(ONLINE_MESSAGE.MESSAGE.get_rect()))
            if re.search(network_menu_can_see_nickname, message) or re.search(now_connected_to_the_internet, message):
                action = BUTTON_ACTION.A_BUTTON

        # Just in case disconnect happened
        if self.battle_state is None:
            ok_rect = self.get_subframe(DISCONNECT_MESSAGE.OK_BOX.get_message_rect())
            if calculate_communicating_black_ratio(ok_rect) < 0.01:
                message = parse_rect_with_pytesseract(ok_rect, False, True)
                if re.search(diconnect_ok_regex, message):
                    print('Disconnect Detected')
                    logging.info('Disconnect Detected')
                    action = BUTTON_ACTION.A_BUTTON
                    #reset state in case we are brought back to continue battling.
                    self.reset()


        if action == BUTTON_ACTION.A_BUTTON:
            print('pressed A')
#            action = None
            wait = 0.67
#            self.is_series_done = True


        return action, self.is_series_done, wait

    def check_if_nav_action_finished(self, nav_action, state, selectable, submenu, button_action):
        done = False

        if nav_action == NetworkNavigationAction.NAVIGATE_TO_TEAM_SELECTION:
            if state == NETWORK_STATES.NETWORK_TEAM_SELECT:
                done = True

        if nav_action == NetworkNavigationAction.FIND_NEXT_TEAM:
            if state == NETWORK_STATES.NETWORK_TEAM_SELECT:
                if button_action ==  BUTTON_ACTION.RIGHT_BUTTON:
                    done = True

        if nav_action == NetworkNavigationAction.SELECT_CURRENT_TEAM:
            if state == NETWORK_STATES.NETWORK_TEAM_SELECT_OPTION_MENU:
                if button_action ==  BUTTON_ACTION.A_BUTTON:
                    done = True

        if nav_action == NetworkNavigationAction.PARTY_COUNT_POKEMON:
            if state == NETWORK_STATES.NETWORK_PARTY_SELECT:
                self.count_party()
                done = True

        if nav_action == NetworkNavigationAction.NAVIGATE_TO_TEAM_SELECTION:
            if state == NETWORK_STATES.NETWORK_TEAM_SELECT:
                done = True
            if state == NETWORK_STATES.NETWORK_CONTINUE_BATTLING:
                if selectable == CONTINUE_BATTLING_DIALOG.SWITCH_BATTLE_TEAMS and button_action ==  BUTTON_ACTION.A_BUTTON:
                    done = True

        if nav_action in [NetworkNavigationAction.PARTY_ADD_FIRST_POKEMON, NetworkNavigationAction.PARTY_ADD_SECOND_POKEMON, NetworkNavigationAction.PARTY_ADD_THIRD_POKEMON, NetworkNavigationAction.PARTY_ADD_FOURTH_POKEMON, NetworkNavigationAction.PARTY_ADD_FIFTH_POKEMON, NetworkNavigationAction.PARTY_ADD_SIXTH_POKEMON]:
            if state == NETWORK_STATES.NETWORK_PARTY_SELECT_OPTION_MENU:
                if button_action ==  BUTTON_ACTION.A_BUTTON:
                    done = True

        if nav_action == NetworkNavigationAction.QUEUE_MATCH:
            if state == NETWORK_STATES.NETWORK_PARTY_DONE or state == NETWORK_STATES.NETWORK_PARTY_SELECT:
                if button_action ==  BUTTON_ACTION.A_BUTTON:
                    done = True

        return done

    def count_party(self):
        party_size = 0
        if 'team_pokemon' in self.labels_and_boxes:
            party_size += len(self.labels_and_boxes['team_pokemon'])
        if 'team_pokemon_selected' in self.labels_and_boxes:
            party_size += len(self.labels_and_boxes['team_pokemon_selected'])

        self.party_pokemon = []
        add_pokemon_offset = 4
        for i in range(party_size):
            self.party_pokemon.append(NetworkNavigationAction(i + add_pokemon_offset))

    def queued_for_match(self):
        print('Match beginning soon')

    def adding_pokemon_to_party(self):
        print('Adding pokemon to party')

    def switching_team(self):
        print('Switching Team')

    def selecting_team(self):
        print('Selecting Team')

    def get_subframe(self, rect, strip_color=False):
        x1, y1, x2, y2 = rect
        crop_img = self.curr_frame[y1:y2, x1:x2]
        if strip_color:
            lower =(0, 0, 0) # lower bound for each channel
            upper = (140, 140, 140) # upper bound for each channel

            # create the mask and use it to change the colors
            mask = cv2.inRange(crop_img, lower, upper)
            mask = 255 - mask
            crop_img[mask != 0] = [0,255,255]
        return crop_img



network_battle_states_labels = ['vs_menu_option', 'battle_stadium_menu_option', 'network_main_menu', 'match_style_menu', 'team_pick_preview', 'network_party_select', 'waiting_room', 'match_about_to_begin', 'communication_error', 'continue_battling_options_menu', 'network_party_select_options', 'team_pick_options_menu', 'network_party_done_selected']
network_submenu_selectables_labels = ['submenu_item_selected']
network_battle_selectables_labels = ['network_party_done', 'continue_battling_options_menu', 'team_pokemon_selected']

def network_update_state(labels_boxes):
    battle_state = None
    for label in labels_boxes:
        first_box = labels_boxes[label][0]
        if label in network_battle_states_labels:
            battle_state = NETWORK_STATES.state_for_label(label)

    # interesting handle situation of options menu and party both being present.
    if 'network_party_select_options' in labels_boxes and battle_state == NETWORK_STATES.NETWORK_PARTY_SELECT:
        battle_state = NETWORK_STATES.NETWORK_PARTY_SELECT_OPTION_MENU

    if 'network_party_done_selected' in labels_boxes and battle_state == NETWORK_STATES.NETWORK_PARTY_SELECT:
        battle_state = NETWORK_STATES.NETWORK_PARTY_DONE

    return battle_state

def network_update_selectables(battle_state, labels_boxes):
    battle_selectable = None
    # Used to infere switch battle teams
    continue_battling_unselected = False
    quit_battle_unselected = False
    for label in labels_boxes:
        if battle_selectable is not None:
            break
        for box in labels_boxes[label]:
            if label in network_battle_selectables_labels:
                print(label)
                print(box)
                battle_selectable = BATTLE_SELECTABLES.get_item_for_network_rect(battle_state, box)
            if label == 'submenu_item_selected' and battle_state == NETWORK_STATES.NETWORK_CONTINUE_BATTLING:
                print('continue battling')
                print(label)
                print(box)
                battle_selectable = CONTINUE_BATTLING_DIALOG.get_item_for_rect(box)
            if label == 'submenu_item' and battle_state == NETWORK_STATES.NETWORK_CONTINUE_BATTLING:
                print('continue battling')
                print(label)
                print(box)
                unselected = CONTINUE_BATTLING_DIALOG.get_item_for_rect(box)
                if unselected == CONTINUE_BATTLING_DIALOG.CONTINUE_BATTLING:
                    continue_battling_unselected = True
                if unselected == CONTINUE_BATTLING_DIALOG.QUIT_BATTLING:
                    quit_battle_unselected = True
    if battle_selectable is None and continue_battling_unselected and quit_battle_unselected:
        battle_selectable = CONTINUE_BATTLING_DIALOG.SWITCH_BATTLE_TEAMS
    return battle_selectable

def network_update_sub_selectables(battle_state, battle_selectable, labels_boxes, mini=False):
    battle_sub_selectable = None
    for label in labels_boxes:
        for box in labels_boxes[label]:
            if label in network_battle_selectables_labels:
                battle_sub_selectable = NETWORK_BATTLE_SUBMENU_SELECTABLES.get_item_for_rect(battle_selectable, box)
    return battle_sub_selectable


def process_test_navigation():
    import os

    state = NetworkState()
    i = 0

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_FFMPEG,True)
    cam.set(cv2.CAP_PROP_FPS,30)
#    cam.set(cv2.CAP_PROP_BUFFERSIZE,0)

#    _fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#    _out = cv2.VideoWriter("test_poke.mp4", _fourcc, 20.0, (1920,1080))

    i = 0
    actionCoolDown = time.time()
    wait_threshold = 0.2
    action = None
    while(True):
        if action is not None:
            for i in range(5):
                cam.grab()
        action, done = None, False
        ret,image = cam.read()
        image = cv2.resize(image, (1280, 720), interpolation = cv2.INTER_AREA)
#        if i % 5 == 0:
#            cv2.imshow('frame',frame)
#        _out.write(frame);
        if time.time() - actionCoolDown >= wait_threshold: #some  value
            labels_boxes = yolo.process_image(image, True)

            if len(labels_boxes) > 0:
                print(labels_boxes)
            else:
                sleep(0.1)
                action = 'clear sleep'
                continue

            #
            #  process both frames NOW !
            #
            action, done, wait = state.process_frame(image, labels_boxes)
            wait_threshold = wait
            actionCoolDown = time.time()
        else:
            pass
#            print('actionCoolDown', actionCoolDown)
#            print('time.time()', time.time())
#            print('time.time() - actionCoolDown', time.time() - actionCoolDown)

        # reset time to make move
        if action is not None:
            send(action.serial_rep())
            actionCoolDown = time.time()
            print('Just wait a second')

        print('Performing Action?: ', action)
        print('Done?',done)

#        if is_done or i > 100:
        if done:
            break
            """
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
        i += 1
        if i == 1000:
            break
            """
    cam.release()
#    _out.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    yolo = YOLO(**{
                "score" : 0.6,
                "gpu_num" : 0,
                }
               )
    battle_state = None
    battle_selectable = None
    battle_sub_selectable = None
    image_count = 0.0

    process_test_navigation()
    i = 1/0
