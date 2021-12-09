# -*- coding: utf-8 -*-
"""
Class definition of YOLO_v3 style detection model on image and video
"""
import sys
sys.path.insert(0, './pokemon_voices')

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
#from ainetwork import AiNetwork

from poke_state_common import *
from pokemon_regex import *
from image_text_processing import *
import time
import random
import threading
from poke_common import *
from switch_button_press import *
from tensorflow.keras import backend as K
import tensorflow as tf
from multiprocessing import Pool
import concurrent.futures

import audio_manager
from voice_fetcher import *

# Speed up pytesseract?
os.environ['OMP_THREAD_LIMIT'] = '1'

#battle_states_labels = ['standby', 'active_menu', 'attack_fight_menu', 'active_pokemon_info', 'team_menu', 'team_member_options_menu', 'pokemon_summary_base_stats', 'pokemon_summary_info', 'pokemon_summary_attacks', 'use_next_pokemon', 'trainer_switch_pokemon', 'wild_battle_over', 'wild_pokemon_begin', 'surprise_wild_battle_begin']
#submenu_selectables_labels = ['submenu_item', 'submenu_item_selected']
#battle_selectables_labels = ['menu_option_selected', 'attack_option_selected', 'dynamax_selected', 'team_pokemon_selected']
import datetime
datetime_object = datetime.datetime.now()
print(datetime_object)

import logging
log_filename = 'logs/wild_state_%s.log' % (datetime_object)
logging.basicConfig(filename=log_filename, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.warning('This will get logged to a file')
logging.info('This will info message get logged to a file')

non_alpha_regex = re.compile('[^a-zA-Z]')


ACTIVATE = '-activate'
DAMAGE = '-damage'
WEATHER = '-weather'
FIELD_START = '-fieldstart'
FIELD_END = '-fieldend'
SIDE_START = '-sidestart'
SIDE_END = '-sideend'
SINGLE_MOVE = '-singlemove'
RESISTED = '-resisted'
SUPER_EFFECTIVE = '-supereffective'
IMMUNE = '-immune'
START = '-start'
END = '-end'
END_ITEM = '-enditem'
ITEM = '-item'
HEAL = '-heal'
SET_HP = '-sethp'
ABILITY = '-ability'
CLEAR_ALL_BOOST = '-clearallboost'
CLEAR_BOOST = '-clearboost'
CLEAR_NEGATIVE_BOOST = '-clearnegativeboost'
STATUS  = '-status'
CURE_STATUS  = '-curestatus'
CRIT = '-crit'
SWITCH = 'switch'
SWITCHOUT = 'switchout'
DRAG = 'drag'
MOVE = 'move'
FAINT = 'faint'
REPLACE = 'replace'
ZPOWER = '-zpower'
MEGA = '-mega'
MISS = '-miss'
FAIL = '-fail'
ROOM = '-room'
BOOST = '-boost'
UNBOOST = '-unboost'
DETAILS_CHANGE = 'detailschange'
FORME_CHANGE = 'formechange'
DYNAMAX = 'Dynamax'
TURN = 'turn'
move_did_not_succeed = ['-fail','-miss','cant']
HAZARD_DAMAGE = '-hazarddamage'
MUST_SWITCH = '-must_switch'
HAZARDS = ['Stealth Rock', 'Spikes', 'Toxic Spikes', 'Sticky Web']
NON_HAZARDS = ['Aurora Veil', 'Reflect', 'Safeguard', 'Tailwind', 'Light Screen']
MATCH_OVER = '-match_over'
TRICK = '-trick'

SUPPORTED_UPDATES = [ACTIVATE, DAMAGE, WEATHER, FIELD_START, FIELD_END, SIDE_END, SINGLE_MOVE, RESISTED, SUPER_EFFECTIVE, IMMUNE, START, END, END_ITEM,
ITEM, HEAL, SET_HP, ABILITY, CLEAR_ALL_BOOST, CLEAR_BOOST, CLEAR_NEGATIVE_BOOST, STATUS, CURE_STATUS, CRIT, SWITCH, DRAG, MOVE, FAINT, REPLACE, ZPOWER,
MEGA, MISS, FAIL, BOOST, UNBOOST, DETAILS_CHANGE, FORME_CHANGE]

revealed_items = set()
revealed_attack_names = set()
revealed_pokemon_names = set()
revealed_abilities = set()

item_damage_regex = "\|\-damage\|.*\|\[from\] item\:.*"

nav_needs_message_confirmation_when_done = [NavigationAction.STANDBY_ATTACK_SLOT_1, NavigationAction.STANDBY_ATTACK_SLOT_2, NavigationAction.STANDBY_ATTACK_SLOT_3, NavigationAction.STANDBY_ATTACK_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]
team_info_nav_actions = [NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO]
attack_nav_actions  =   [NavigationAction.STANDBY_ATTACK_SLOT_1, NavigationAction.STANDBY_ATTACK_SLOT_2, NavigationAction.STANDBY_ATTACK_SLOT_3, NavigationAction.STANDBY_ATTACK_SLOT_4]
change_slots_nav_actions = [NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]
NONTEAM_NAV_ACTIONS = [NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO, NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO, NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6, NavigationAction.STANDBY_PEEK_TEAM_INFO]

def bool_to_int(value):
    return 1 if value else 0


class Action(enum.Enum):
  Attack_Slot_1 = 0
  Attack_Slot_2 = 1
  Attack_Slot_3 = 2
  Attack_Slot_4 = 3
  Attack_Dyna_Slot_1 = 4
  Attack_Dyna_Slot_2 = 5
  Attack_Dyna_Slot_3 = 6
  Attack_Dyna_Slot_4 = 7
  Change_Slot_1 = 8
  Change_Slot_2 = 9
  Change_Slot_3 = 10
  Change_Slot_4 = 11
  Change_Slot_5 = 12
  Change_Slot_6 = 13
  Attack_Struggle = 14
  Not_Decided = 15          # position hasn't been decided yet

  def get_nav_value(self):
      if self == Action.Attack_Slot_1:
          return [NavigationAction.STANDBY_ATTACK_SLOT_1]
      if self == Action.Attack_Slot_2:
          return [NavigationAction.STANDBY_ATTACK_SLOT_2]
      if self == Action.Attack_Slot_3:
          return [NavigationAction.STANDBY_ATTACK_SLOT_3]
      if self == Action.Attack_Slot_4:
          return [NavigationAction.STANDBY_ATTACK_SLOT_4]

      # Dyna choices
      if self == Action.Attack_Dyna_Slot_1:
          return [NavigationAction.STANDBY_ACTIVATE_DYNAMAX, NavigationAction.STANDBY_ATTACK_SLOT_1]
      if self == Action.Attack_Dyna_Slot_2:
          return [NavigationAction.STANDBY_ACTIVATE_DYNAMAX, NavigationAction.STANDBY_ATTACK_SLOT_2]
      if self == Action.Attack_Dyna_Slot_3:
          return [NavigationAction.STANDBY_ACTIVATE_DYNAMAX, NavigationAction.STANDBY_ATTACK_SLOT_3]
      if self == Action.Attack_Dyna_Slot_4:
          return [NavigationAction.STANDBY_ACTIVATE_DYNAMAX, NavigationAction.STANDBY_ATTACK_SLOT_4]

      if self == Action.Change_Slot_1:
          return [NavigationAction.STANDBY_CHANGE_SLOT_1]
      if self == Action.Change_Slot_2:
          return [NavigationAction.STANDBY_CHANGE_SLOT_2]
      if self == Action.Change_Slot_3:
          return [NavigationAction.STANDBY_CHANGE_SLOT_3]
      if self == Action.Change_Slot_4:
          return [NavigationAction.STANDBY_CHANGE_SLOT_4]
      if self == Action.Change_Slot_5:
          return [NavigationAction.STANDBY_CHANGE_SLOT_5]
      if self == Action.Change_Slot_6:
          return [NavigationAction.STANDBY_CHANGE_SLOT_6]

      if self == Action.Attack_Struggle:
          return [NavigationAction.STANDBY_STRUGGLE]

  def get_attack_priority_weight(self):
      if self in ATTACK_ACTIONS:
          return 0.2
      if self in SWITCH_ACTIONS:
          return 0.1
      if self == Action.Attack_Struggle:
          return 0.01
      return 0.05

  def get_twitch_commands(self):
      if self == Action.Attack_Slot_1:
          return '!attack1'
      if self == Action.Attack_Slot_2:
          return '!attack2'
      if self == Action.Attack_Slot_3:
          return '!attack3'
      if self == Action.Attack_Slot_4:
          return '!attack4'
      if self == Action.Attack_Dyna_Slot_1:
          return '!dyna1'
      if self == Action.Attack_Dyna_Slot_2:
          return '!dyna2'
      if self == Action.Attack_Dyna_Slot_3:
          return '!dyna3'
      if self == Action.Attack_Dyna_Slot_4:
          return '!dyna4'
      if self == Action.Change_Slot_1:
          return '!switch1'
      if self == Action.Change_Slot_2:
          return '!switch2'
      if self == Action.Change_Slot_3:
          return '!switch3'
      if self == Action.Change_Slot_4:
          return '!switch4'
      if self == Action.Change_Slot_5:
          return '!switch5'
      if self == Action.Change_Slot_6:
          return '!switch6'
      if self == Action.Attack_Struggle:
          return '!struggle'

  def get_action_for_twitch_commands(command):
      if command == '!attack1':
          return Action.Attack_Slot_1
      if command == '!attack2':
          return Action.Attack_Slot_2
      if command == '!attack3':
          return Action.Attack_Slot_3
      if command == '!attack4':
          return Action.Attack_Slot_4
      if command == '!dyna1':
          return Action.Attack_Dyna_Slot_1
      if command == '!dyna2':
          return Action.Attack_Dyna_Slot_2
      if command == '!dyna3':
          return Action.Attack_Dyna_Slot_3
      if command == '!dyna4':
          return Action.Attack_Dyna_Slot_4
      if command == '!switch1':
          return Action.Change_Slot_1
      if command == '!switch2':
          return Action.Change_Slot_2
      if command == '!switch3':
          return Action.Change_Slot_3
      if command == '!switch4':
          return Action.Change_Slot_4
      if command == '!switch5':
          return Action.Change_Slot_5
      if command == '!switch6':
          return Action.Change_Slot_6
      if command == '!struggle':
          return Action.Attack_Struggle


ATTACK_ACTIONS = [Action.Attack_Slot_1, Action.Attack_Slot_2, Action.Attack_Slot_3, Action.Attack_Slot_4, Action.Attack_Dyna_Slot_1, Action.Attack_Dyna_Slot_2, Action.Attack_Dyna_Slot_3, Action.Attack_Dyna_Slot_4]
SWITCH_ACTIONS = [Action.Change_Slot_1, Action.Change_Slot_2, Action.Change_Slot_3, Action.Change_Slot_4, Action.Change_Slot_5, Action.Change_Slot_6]
REGULAR_ATTACK_ACTIONS = [Action.Attack_Slot_1, Action.Attack_Slot_2, Action.Attack_Slot_3, Action.Attack_Slot_4]
CHOICED_ITEMS = ['Choice Band', 'Choice Scarf', 'Choice Specs']
FORCE_MATCH_OVER_LABELS = ['continue_battling_options_menu', 'network_main_menu']
#Triples       Doubles     Singles
# 3  2  1         2  1         1
#-1 -2 -3        -1 -2        -1

series_attacks_torment_faint_actions = [
#Skip first to make life easier
    Action.Attack_Slot_3,
    #Environment should lookup new active stats details
    Action.Attack_Slot_2,
    Action.Attack_Slot_4,
    Action.Attack_Slot_3,
    Action.Attack_Slot_3, #Should fail from torment, request new action
    Action.Change_Slot_6,
    Action.Attack_Slot_2,
]

series_attacks_torment_faint_request_actions = [
    Action.Attack_Slot_2,

]

framed_fresh_battle_win_actions = [
    Action.Attack_Slot_4,
    Action.Attack_Slot_1,
    Action.Attack_Slot_1,

]

framed_switch_peak_team_peak_attack_attack_actions = [
    Action.Change_Slot_6,
    Action.Attack_Slot_3,
]

class SELECTABLE_TARGET(enum.Enum):
    DO_NOT_SPECIFY=0  # Used for most options, singles/random/normal/self,multi... and shifts
    SELF=1
    FOE_SLOT_1=2
    FOE_SLOT_2=3
    FOE_SLOT_3=4  # Only in triples
    ALLY_SLOT_1=5
    ALLY_SLOT_2=6
    ALLY_SLOT_3=7 # Only in triples


class TARGET(enum.Enum):
    #These all use target DO_NOT_SPECIFY
    SELF = 'self'
    ALL_ADJACENT_FOES = 'allAdjacentFoes'
    ALLY_SIDE = 'allySide'
    ALLY_TEAM = 'allyTeam'
    FOE_SIDE = 'foeSide'
    ALL = 'all'
    ALL_ADJACENT = 'allAdjacent'
    RANDOM_NORMAL = 'randomNormal'   # outrage

#require a pick
    NORMAL = 'normal'
    ANY = 'any'
    ADJACENT_FOE = 'adjacentFoe'
    ADJACENT_ALLY = 'adjacentAlly'
    ADJACENT_ALLY_OR_SELF = 'adjacentAllyOrSelf'
    SCRIPTED = 'scripted'

class Status(enum.Enum):
    NOTHING = ''
    BURN = 'brn'
    SLEEP = 'slp'
    FROZEN = 'frz'
    PARALYSIS = 'par'
    POISON = 'psn'
    TOXIC = 'tox'
    FAINTED = 'fnt'

class NETWORK_STYLE(enum.Enum):
    TWITCH_BOT = 'twitcho'
    RANDO_BOT = 'rando'
    HONORABLE_SALAD = 'honorable'





def get_state_selectable_for_prediction(output):
    left, top, right, bottom, c, score = output
    return None

class SEQUENCE_STATE(enum.Enum):
    NOT_STARTED = 0
    STANDBY = 1
    BATTLING = 2
    AWAITING_SWITCH = 3
    BATTLE_END = 4

    def get_name(self):
        if self == SEQUENCE_STATE.NOT_STARTED:
            return 'Not Started'
        if self == SEQUENCE_STATE.STANDBY:
            return 'Standby'
        if self == SEQUENCE_STATE.BATTLING:
            return 'Battling'
        if self == SEQUENCE_STATE.AWAITING_SWITCH:
            return 'AWAITING_SWITCH'

class COMMAND_ACTIONS(enum.Enum):
    CONSTRUCT_TEAM = 0
    CHECK_TEAM_ORDER = 1
    UPDATE_ACTIVE_POKEMON = 2
    GET_ACTION_FOR_POKEMON_A = 3
    GET_ACTION_FOR_POKEMON_B = 4


class ActiveStats():
    def __init__(self):
        self.seeded = False
        self.confused = False
        self.taunted = False
        self.encored = False
        self.substitute = False
        self.attracted = False
        self.seeded = False
        self.dynamax_activated = False
        self.dynamax_turns = 0
        self.must_recharge = False
        self.accuracy_modifier = 0
        self.attack_modifier = 0
        self.spatk_modifier = 0
        self.defense_modifier = 0
        self.spdef_modifier = 0
        self.speed_modifier = 0
        self.evasion_modifier = 0

    def boost_stat(self, stat, amt, is_boost=True):
        modified = int(amt)
        if is_boost == False:
            modified = int(amt) * -1
        if stat == 'evasion':
            self.evasion_modifier += modified
        if stat == 'accuracy':
            self.accuracy_modifier += modified
        if stat == 'atk':
            self.attack_modifier += modified
        if stat == 'spa':
            self.spatk_modifier += modified
        if stat == 'def':
            self.defense_modifier += modified
        if stat == 'spd':
            self.spdef_modifier += modified
        if stat == 'spe':
            self.speed_modifier += modified

    def clear_all_boosts(self):
        self.accuracy_modifier = 0
        self.attack_modifier = 0
        self.spatk_modifier = 0
        self.defense_modifier = 0
        self.spdef_modifier = 0
        self.speed_modifier = 0
        self.evasion_modifier = 0

    def clear_neg_boosts(self):
        self.accuracy_modifier = max(0, self.accuracy_modifier)
        self.attack_modifier = max(0, self.attack_modifier)
        self.spatk_modifier = max(0, self.spatk_modifier)
        self.defense_modifier = max(0, self.defense_modifier)
        self.spdef_modifier = max(0, self.spdef_modifier)
        self.speed_modifier = max(0, self.speed_modifier)
        self.evasion_modifier = max(0, self.evasion_modifier)

    def get_encode(self):
        raw_encode = [
            bool_to_int(self.seeded),
            bool_to_int(self.confused),
            bool_to_int(self.taunted),
            bool_to_int(self.encored),
            bool_to_int(self.substitute),
            bool_to_int(self.attracted),
            bool_to_int(self.seeded),
            bool_to_int(self.must_recharge),
            bool_to_int(self.dynamax_activated),
            self.dynamax_turns / 3,
            self.accuracy_modifier / 6,
            self.attack_modifier / 6,
            self.spatk_modifier / 6,
            self.defense_modifier / 6,
            self.spdef_modifier / 6,
            self.speed_modifier / 6,
            self.evasion_modifier / 6,
        ]
        return raw_encode

    def apply_modifiers(self, modifiers):
        self.accuracy_modifier = modifiers[ACTIVE_STATS_MODIFIER.ACCURACY_MODIFIER_ROW]
        self.attack_modifier = modifiers[ACTIVE_STATS_MODIFIER.ATTACK_MODIFIER_ROW]
        self.spatk_modifier = modifiers[ACTIVE_STATS_MODIFIER.SPECIAL_ATTACK_MODIFIER_ROW]
        self.defense_modifier = modifiers[ACTIVE_STATS_MODIFIER.DEFENSE_MODIFIER_ROW]
        self.spdef_modifier = modifiers[ACTIVE_STATS_MODIFIER.SPECIAL_DEFENSE_MODIFIER_ROW]
        self.speed_modifier = modifiers[ACTIVE_STATS_MODIFIER.SPEED_MODIFIER_ROW]
        self.evasion_modifier = modifiers[ACTIVE_STATS_MODIFIER.EVASIVENESS_MODIFIER_ROW]

class ActionRequest():
    def __init__(self):
        self.active_pokemon_actions = {'a':Action.Not_Decided,'b':Action.Not_Decided}
        self.active_pokemon_targets = {'a':SELECTABLE_TARGET.DO_NOT_SPECIFY,'b':SELECTABLE_TARGET.DO_NOT_SPECIFY}
        #Important enough for one hot encoding?
        self.action_for_position = SELECTABLE_TARGET.ALLY_SLOT_1


class WildState():

    def __init__(self, trainer_name='thunder', network_style=NETWORK_STYLE.RANDO_BOT):
#    def __init__(self, trainer_name='Lou Rui', network_style=NETWORK_STYLE.RANDO_BOT):
        self.trainer_name = trainer_name
        self.sequence = SEQUENCE_STATE.NOT_STARTED
        self.pool = Pool(os.cpu_count())
        self.futures = []
        # add support for pokemon names that might not be english whenever entering
        self.registered_pokemon_names = []
        self.uturn_like_move_used = False
        self.is_series_done = False
        self.is_network_match = False
        self.network_style = network_style
        if self.network_style == NETWORK_STYLE.HONORABLE_SALAD:
            self.ainetwork = AiNetwork()
        if self.network_style == NETWORK_STYLE.RANDO_BOT:
            self.ainetwork = None
        if self.network_style == NETWORK_STYLE.TWITCH_BOT:
            self.ainetwork = AiNetwork()
#        self.twitchnetwork = TwitchNetwork()

        self.did_scan_team_info = False
        self.need_team_order_info = True
        self.did_scan_active_info = False
        # Opponent Switch in/boost move/gain status
        self.need_active_scan = True
        self.waiting_for_button_press = False
#        self.navigation_actions = [NavigationAction.STANDBY_CHANGE_SLOT_6]
#        self.navigation_actions = [NavigationAction.STANDBY_COUNT_ACTIVE_POKEMON, NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO]
        self.navigation_actions = []
#        self.navigation_actions = []
#        self.navigation_actions = [NavigationAction.STANDBY_COUNT_ACTIVE_POKEMON]
        self.clear_nav_action()
        self.curr_frame = None
        self.labels_and_boxes = None
        self.active_pokemon_count = 0
        self.needs_update_positioning_next_turn = True
        self.team_size = 0
        self.packaged_attacks = []
        self.stats_print_count = 0

        self.last_accepted_message = ''
        self.last_player_ability = None
        self.last_enemy_ability  = None
        self.player_pokemon = {}
        self.current_team_pokemon = None

        self.p1_used_dynamax = False
        self.p2_used_dynamax = False

        # Context tracking
        self.current_focus_player_1 = False
        self.current_focus_pokemon = None

        self.waiting_for_message_to_confirm_action = False

        self.player_active_pokemon_set = {}
        self.enemy_active_pokemon_set = {}

        self.player_last_health_sequence = {'a':None, 'b':None}
        self.enemy_last_health_sequence = {'a':None, 'b':None}
        self.player_current_health_sequence = {'a':None, 'b':None}
        self.enemy_current_health_sequence = {'a':None, 'b':None}
        self.player_start_health_sequence = {'a':None, 'b':None}
        self.enemy_start_health_sequence = {'a':None, 'b':None}

        self.number_of_actions_needed = 0
        self.turns = 0
        self.p1_dynamax_turns = 0
        self.p2_dynamax_turns = 0

        self.commands = []
        self.current_command = None
        self.p1_reward = 0
        self.p2_reward = 0
        self.team_position_index = 0
        self.p1_choice_attack_action = None
        self.p1_last_attempted_action = None
        self.switch_was_from = None
        self.did_construct_team_info = False
        self.needs_team_order_update = False

        #Used to keep track of failed navigation_actions
        self.waiting_for_navigation_action = None
        self.needs_new_player_action = False



        self.gen = GEN.EIGHT
        self.gametype = GameType.SINGLES
        self.tier = Tier.UBERS

        self.weather_condition = 'none'
        self.weather_turns = 0
        self.terrain_condition = 'none'
        self.terrain_turns = 0
        self.current_room = 'none'
        self.room_turns = 0
        self.p1_safeguard = False
        self.p2_safeguard = False
        self.p1_lightscreen = False
        self.p2_lightscreen = False
        self.p1_reflect = False
        self.p2_reflect = False
        self.p1_tailwind = False
        self.p2_tailwind = False
        self.p1_aurora_veil = False
        self.p2_aurora_veil = False

        self.p1_used_zmove = False
        self.p2_used_zmove = False
        self.p1_used_mega = False
        self.p2_used_mega = False
        self.p1_transcript = ''
        self.p2_transcript = ''
        # Used to let us know p1/p2 needs a new action.
        # When exploring tags, it will be p1_a/p1_b...
        self.p1_has_rocks = False
        self.p2_has_rocks = False
        self.p1_has_web = False
        self.p2_has_web = False
        self.p1_spikes = 0
        self.p2_spikes = 0
        self.p1_toxic_spikes = 0
        self.p2_toxic_spikes = 0




        #not sent to neural network
        self.p1_seen_details = {}
        self.p2_seen_details = {}
        self.p1_active_pokemon_stats = {'a':ActiveStats(),'b':ActiveStats()}
        self.p2_active_pokemon_stats = {'a':ActiveStats(),'b':ActiveStats()}
        #Yawn and perish are reset at the beginning of each turn.
        #game will update them each turn
        self.p1_yawned = {'a':False, 'b':False}
        self.p2_yawned = {'a':False, 'b':False}
        self.p1_perished = {'a':0, 'b':0}
        self.p2_perished = {'a':0, 'b':0}
        self.p1_missed_failed = {'a':False, 'b':False}
        self.p2_missed_failed = {'a':False, 'b':False}
        self.p1_smack_down = {'a':False, 'b':False}
        self.p2_smack_down = {'a':False, 'b':False}
        #Level 1 logic, convert each turn. from ints to enums. == 0 Neutral < 1 Resisted > 1 Super
        #Level 2 logic, decrease if player hurts ally regardless  -  ignore for now until doubles data is collected.
        self.p1_effective = {'a':0, 'b':0}
        self.p2_effective = {'a':0, 'b':0}
        self.p1_destined = {'a':False, 'b':False}
        self.p2_destined = {'a':False, 'b':False}
        self.p1_move_succeeded = {'a':False, 'b':False}
        self.p2_move_succeeded = {'a':False, 'b':False}
        self.p1_trapped = {'a':False, 'b':False}
        self.p2_trapped = {'a':False, 'b':False}
        self.p1_protect_counter = {'a':0, 'b':0}
        self.p2_protect_counter = {'a':0, 'b':0}

        self.transcripto = []
        self.should_self_print = True
        self.need_action_for_position = {'a':False, 'b':False}

        # Used to know which pokemon is currently selected. not directly sent to neural network
        self.p1_selected = {'a':None, 'b':None}
        self.p2_selected = {'a':None, 'b':None}
        # used to keep which requests we need to ask for.
        self.p1_open_request = {'a':False, 'b':False}
        self.p2_open_request = {'a':False, 'b':False}
        # switching moves
        self.p1_must_switch = {'a':False, 'b':False}
        self.p2_must_switch = {'a':False, 'b':False}

        #Pending moves - embedding that has selected action
        self.p1_pending_actions = {'a':Action.Not_Decided, 'b':Action.Not_Decided}
        self.p1_pending_targets = {'a':SELECTABLE_TARGET.DO_NOT_SPECIFY, 'b':SELECTABLE_TARGET.DO_NOT_SPECIFY}

        self.p2_pending_actions = {'a':Action.Not_Decided, 'b':Action.Not_Decided}
        self.p2_pending_targets = {'a':SELECTABLE_TARGET.DO_NOT_SPECIFY, 'b':SELECTABLE_TARGET.DO_NOT_SPECIFY}
        # Keeps tracks of attacks used last turn
        self.p1_seen_attacks = {'a':'no attack', 'b':'no attack'}
        self.p2_seen_attacks = {'a':'no attack', 'b':'no attack'}

        #Not sent to neural network. used for forced switches so we dont request more actions
        self.p1_is_waiting = False
        self.p2_is_waiting = False

        self.request_outputs = []

        self.battle_state = None
        self.battle_selectable = None
        self.battle_sub_selectable = None
        self.last_battle_state = None
        self.last_battle_selectable = None
        self.last_battle_sub_selectable = None

        self.added_team_members = []
        # each pokemon has a list of selectables
        self.added_attack_names = {}

        self.current_team_pokemon = None
        self.added_base_stats = []
        self.added_basic_info = []
        self.match_allows_dynamatch = False
        self.last_inp_type = None
        self.last_params = None
        self.disabled_actions = set()
        self.player_pokemon_did_faint = False

        self.p1_teamsize = 0
        self.p2_teamsize = 0
        # If A button press doesnt go through reset nav action
        self.misfire_count = 0
        self.aaas = 0

        #sometimes team positioning is off, add uncertain indexes and make them pickable until next peek
        self.uncertain_positions = set()
        # Only want to set the current team name once per position
        self.added_team_members_selectables = set()
        self.last_two_english_messages = deque(['', ''], maxlen=4)
        self.last_two_japanese_messages = deque(['', ''], maxlen=4)

    def reset_state_transcript(self):
        self.p1_transcript = ''
        self.p2_transcript = ''

    def append_to_transcript(self, message):
        message = message.strip()
        if message == '':
            return
        player_regex = '_p1_'  # for player replace with nothing, for agent replace with opposing
        agent_regex = '_p2_'  # for player replace with opposing, for agent replace with nothing
        self.p1_transcript = '%s\n%s' % (self.p1_transcript, message)
        self.p1_transcript = self.p1_transcript.replace('_p1_', '')
        self.p1_transcript = self.p1_transcript.replace('_p2_', 'Opposing ')

    def refresh_needs_modifier_update(self):
        self.need_active_scan = True

    def process_frame(self, image, labels_boxes, override_sequence=None):
        self.stats_print_count = 0
        self.curr_frame = image
        self.labels_and_boxes = labels_boxes
        state = update_state(labels_boxes)
        self.battle_state = state
        wait = 0.2


        # IF we miss the you lose message, force stop.
        for label in labels_boxes:
            if label in FORCE_MATCH_OVER_LABELS:
                return None, True, wait

        #FORCED STATE ASSIGNMENTS BEGIN
        #Emergency override because of japanese/unknown 3 member temas?
        if self.battle_state == None and ('team_pokemon_selected' in labels_boxes):
            self.battle_state = BATTLE_STATES.TEAM_MENU
        if self.battle_state == None and ('menu_option_selected' in labels_boxes):
            self.battle_state = BATTLE_STATES.STANDBY
        if self.battle_state == None and ('active_stat_element' in labels_boxes):
            self.battle_state = BATTLE_STATES.ACTIVE_POKEMON_STATS
        if self.battle_state == None and ('attack_option_selected' in labels_boxes):
            self.battle_state = BATTLE_STATES.FIGHT_MENU
        if self.battle_state == None and ('active_menu_pokemon' in labels_boxes and len(labels_boxes['active_menu_pokemon']) > 1):
            self.battle_state = BATTLE_STATES.ACTIVE_MENU
        #FORCED STATE ASSIGNMENTS END
        print('battle_state:', self.battle_state)
        next_battle_selectable = update_selectables(self.battle_state, labels_boxes, self.is_network_match)
        mini_menu = self.sequence == SEQUENCE_STATE.AWAITING_SWITCH
        next_battle_sub_selectable = update_sub_selectables(self.battle_state, next_battle_selectable, labels_boxes, mini_menu)

        if next_battle_selectable == None and 'dynamax_selected' in self.labels_and_boxes:
            next_battle_selectable = BATTLE_SELECTABLES.STANDBY_DYNAMAX

        # Update if battle state isnt None
        if self.battle_state is not None:
            self.battle_selectable = next_battle_selectable
            self.battle_sub_selectable = next_battle_sub_selectable
        print('next_battle_selectable:', next_battle_selectable)
#        print('next_battle_sub_selectable:', next_battle_sub_selectable)

        # Check if switch was rejected by shadow tag
        if self.battle_state == BATTLE_STATES.TEAM_MENU_SWITCH_INFO or 'switch_error_message' in labels_boxes:
            print('switch_error_message detected')
            logging.info('switch_error_message detected')
            self.update_options_request_new_action()
            action = BUTTON_ACTION.A_BUTTON
            self.clear_nav_action()
            wait = 0.67
            return action, self.is_series_done, wait

        # Early Discconect - Press A to dismiss
        if self.battle_state == BATTLE_STATES.PLAYER_DISCONNECT:
            action = BUTTON_ACTION.A_BUTTON
            self.is_series_done = True
            return action, self.is_series_done, wait

        # Wild battle over,experience menu - Press A to dismiss
        if self.battle_state == BATTLE_STATES.EXPERIENCE_SCREEN or self.battle_state == BATTLE_STATES.MESSAGE_NEEDS_ACTION:
            action = BUTTON_ACTION.A_BUTTON
            self.is_series_done = False
            return action, self.is_series_done, wait

        # Update current team member whenever on team page
        if 'team_pokemon_selected' in labels_boxes:
            element_rect = labels_boxes['team_pokemon_selected'][0]
            print('mystery boxes:', len(labels_boxes['team_pokemon_selected']))
            #TODO fix team menu detection
            element = BATTLE_SELECTABLES.get_item_for_rect(self.battle_state, element_rect)
            if element is not None and element not in self.added_team_members_selectables:
                self.added_team_members_selectables.add(element)
                #Maybe consider double construction of name?
                name_rect = element.get_name_rect()
                name = process_image_for_text_on_team_menu(self.get_subframe(name_rect), True)
                print('parsed team member name is:%s position: %d' % (name, element.get_team_position()))
#                if re.search(self.construct_seen_pokemon_regex(), name):
#                    name = re.search(self.construct_seen_pokemon_regex(), name).group(0)
                if len(name) > 0:
                    if name != self.current_team_pokemon:
                        print('updated team member name is:%s position: %d' % (name, element.get_team_position()))
                        logging.info('updated team member name is:%s position: %d' % (name, element.get_team_position()))
                    self.current_team_pokemon = name


        # Dont wanna process communication waiting frames
        if 'message' in labels_boxes and not 'communication_waiting' in labels_boxes:
            rect = self.labels_and_boxes['message'][0]
            message = MESSAGE_ABILITY_REVEALED.get_item_for_rect(rect)
            if message is not None:
                if calculate_communicating_black_ratio(self.get_subframe(message.get_communicating_rect())) > 0.05:
                    print('commincating detected pass')
                    if self.waiting_for_message_to_confirm_action:
                        print('Communication triggering battle sequence')
                        logging.info('Communication triggering battle sequence')
                        self.battle_phase_begin()
                    self.waiting_for_message_to_confirm_action = False
                else:
                    frame = self.get_subframe(message.get_rect())
                    future = self.pool.apply_async(self.extract_english_japanese_text, [frame], callback=self.check_message_in_background)
                    self.futures.append(future)
            else:
                print('Not sure why message is none')
        if 'ability' in labels_boxes:
            for rect in self.labels_and_boxes['ability']:
                ability = MESSAGE_ABILITY_REVEALED.get_item_for_rect(rect)
                if ability == None:
                    continue

                new_ability = parse_rect_with_pytesseract(self.get_subframe(ability.get_rect()), True)
                if self.is_ability_valid(new_ability):
                    self.draw_message_on_frame(new_ability)
                    print('new_ability:', new_ability)
                    if ability == MESSAGE_ABILITY_REVEALED.PLAYER_ABILITY and self.last_player_ability != new_ability:
                        self.last_player_ability = new_ability
                        self.process_ability(new_ability, True)
                    elif ability == MESSAGE_ABILITY_REVEALED.ENEMY_ABILITY and self.last_enemy_ability != new_ability:
                        self.last_enemy_ability = new_ability
                        self.process_ability(new_ability, False)

        if self.sequence != SEQUENCE_STATE.STANDBY and self.battle_state == BATTLE_STATES.STANDBY:
            positions = ['a', 'b']
            for position in positions:
                # increase duynamax counter
                if self.p1_active_pokemon_stats[position].dynamax_activated:
                    self.p1_active_pokemon_stats[position].dynamax_turns += 1

                if self.p2_active_pokemon_stats[position].dynamax_activated:
                    self.p2_active_pokemon_stats[position].dynamax_turns += 1

                # At 4, assume dynamax is over, go to 0
                if self.p1_active_pokemon_stats[position].dynamax_turns > 3:
                    self.p1_active_pokemon_stats[position].dynamax_activated = False
                    self.p1_active_pokemon_stats[position].dynamax_turns = 0

                if self.p2_active_pokemon_stats[position].dynamax_turns > 3:
                    self.p2_active_pokemon_stats[position].dynamax_activated = False
                    self.p2_active_pokemon_stats[position].dynamax_turns = 0

            # Did we construct team info successfully - adding now might remove struggle?
            if not self.did_construct_team_info:
                if NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO not in self.navigation_actions:
                    print('Adding team info nav action')
                    self.navigation_actions.append(NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO)

            # Do we need to check active stats?
            if self.need_active_scan:
                if COMMAND_ACTIONS.UPDATE_ACTIVE_POKEMON not in self.commands:
                    self.commands.append(COMMAND_ACTIONS.UPDATE_ACTIVE_POKEMON)

            self.sequence = SEQUENCE_STATE.STANDBY
            obs = self.get_observation(True)
            print('observation: ', obs)
            combined = obs['combined']
            transcript = obs['transcript']
            valid_moves = obs['valid_onehot_player_1']
            valid_targets = obs['valid_onehot_p1_targets']
            print('combined',combined)
            print('transcript',transcript)
            print('valid_moves',repr(valid_moves))
            print('valid_targets',repr(valid_targets))
            if self.network_style == NETWORK_STYLE.HONORABLE_SALAD:
                network_action = self.ainetwork.step(combined, valid_moves, valid_targets, transcript)[0]
                print('raw network action', network_action)

            # Reset player/enemy health delta
            self.reset_for_turn()
            print('Beginning new turn')
            print('Updating Health')
            self.update_active_popkemon_health()
            # Add action for each active pokemon for player
            self.number_of_actions_needed = 0#len()
            self.commands.append(COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A)
            if len(self.navigation_actions) > 0:
                self.current_navigation_action = self.navigation_actions.pop(0)
                print('Setting new nav action:',self.current_navigation_action)

        # Dont think this is necessary
        """
        if self.battle_state != self.last_battle_state or self.battle_sub_selectable != self.last_battle_selectable or self.battle_sub_selectable != self.last_battle_sub_selectable:
            self.last_battle_state = self.battle_state
            self.last_battle_selectable = self.battle_sub_selectable
            self.last_battle_sub_selectable = self.battle_sub_selectable
#            self.mark_for_state(state)
            self.update_active_popkemon_health()
        """

        # Assume uturn used or an unregistered gfaint occured
        if self.sequence not in [SEQUENCE_STATE.STANDBY, SEQUENCE_STATE.AWAITING_SWITCH] and self.battle_state == BATTLE_STATES.TEAM_MENU:
            print('Unexpected team screen, attempting switch')
            logging.info('Unexpected team screen, attempting switch')
            self.clear_dirty_nav_actions()
            self.unexpected_switch_screen()
            self.sequence = SEQUENCE_STATE.AWAITING_SWITCH
            if NavigationAction.STANDBY_PEEK_TEAM_INFO not in self.navigation_actions:
                self.navigation_actions.insert(0, NavigationAction.STANDBY_PEEK_TEAM_INFO)
            if COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A not in self.commands:
                self.commands.append(COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A)


        action = None
        done = False
        # Update if battle state isnt None
        if self.battle_state is not None and self.current_navigation_action is not None:
            action = self.current_navigation_action.action_for_state(self.battle_state, self.battle_selectable, self.battle_sub_selectable)
            print(action)
            done, wait = self.check_if_nav_action_finished(self.current_navigation_action, self.battle_state, self.battle_selectable, self.battle_sub_selectable, action)

        #
        # THIS IS FOR WILD BATTLES ONLY
        # Just default to continue fighting when a pokemon faint
        if self.battle_state == BATTLE_STATES.MUST_SWITCH:
            action = BUTTON_ACTION.A_BUTTON
            self.sequence = SEQUENCE_STATE.AWAITING_SWITCH
            print('Continuing Battle After Faint')
            logging.info('Continuing Battle After Faint')
            self.unexpected_switch_screen()
            if NavigationAction.STANDBY_PEEK_TEAM_INFO not in self.navigation_actions:
                self.navigation_actions.insert(0, NavigationAction.STANDBY_PEEK_TEAM_INFO)
            if COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A not in self.commands:
                self.commands.append(COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A)

        if self.needs_new_player_action:
            self.needs_new_player_action = False
            if COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A not in self.commands:
                self.commands.append(COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A)

        # Skip turn 1
        if self.needs_team_order_update:
            self.needs_team_order_update = False
            if self.did_construct_team_info:
                # Peek team order
                # Dont need to check turn 1 either since team is being established
                if COMMAND_ACTIONS.CHECK_TEAM_ORDER not in self.commands and self.current_navigation_action != NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO and NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO not in self.navigation_actions:
                    self.commands.append(COMMAND_ACTIONS.CHECK_TEAM_ORDER)

        # THIS IS FOR NETWORK BATTLES ONLY
        # Just default to continue fighting when a pokemon faint
        if self.player_pokemon_did_faint:
            print('Adding actions after faint')
            logging.info('Adding actions after faint')
            self.player_pokemon_did_faint = False
            self.sequence = SEQUENCE_STATE.AWAITING_SWITCH
            if NavigationAction.STANDBY_PEEK_TEAM_INFO not in self.navigation_actions:
                self.navigation_actions.insert(0, NavigationAction.STANDBY_PEEK_TEAM_INFO)
            if COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A not in self.commands:
                self.commands.append(COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A)

        # Just default to continue fighting when a pokemon faint
        if self.uturn_like_move_used == True:
            self.uturn_like_move_used = False
            print('Preparing for uturn switch')
            logging.info('Preparing for uturn switch')
            action = None
            self.sequence = SEQUENCE_STATE.AWAITING_SWITCH
            if NavigationAction.STANDBY_PEEK_TEAM_INFO not in self.navigation_actions:
                self.navigation_actions.insert(0, NavigationAction.STANDBY_PEEK_TEAM_INFO)
            if COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A not in self.commands:
                self.commands.append(COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A)



        if self.sequence == SEQUENCE_STATE.STANDBY or self.sequence == SEQUENCE_STATE.AWAITING_SWITCH or (self.sequence == SEQUENCE_STATE.STANDBY and self.battle_state == BATTLE_STATES.TEAM_MENU):
            # If waiting for congirmation, skip popping anything.
            if self.waiting_for_message_to_confirm_action:
                pass
            elif self.current_navigation_action == None and len(self.navigation_actions) > 0:
                self.current_navigation_action = self.navigation_actions.pop(0)
                logging.info('Navigation Changed to:%s' % (self.current_navigation_action,))
            elif self.current_navigation_action == None:
                #Run a command if it exists
                if len(self.commands) > 0:
                    command = self.commands.pop(0)
                    popping = 'popping command: %s' % command
                    print(popping)
#                    self.draw_message_on_frame(popping)

                    if command == COMMAND_ACTIONS.GET_ACTION_FOR_POKEMON_A:
                        self.decide_action()
                    if command == COMMAND_ACTIONS.UPDATE_ACTIVE_POKEMON:
                        self.navigation_actions.append(NavigationAction.STANDBY_COUNT_ACTIVE_POKEMON)
                    if command == COMMAND_ACTIONS.CHECK_TEAM_ORDER:
                        self.navigation_actions.append(NavigationAction.STANDBY_PEEK_TEAM_INFO)

#        if self.enemy_last_health_sequence['a'] is not None and self.player_last_health_sequence['a'] is not None and self.enemy_current_health_sequence['a'] > 0 and self.player_current_health_sequence['a'] > 0 and (self.sequence == SEQUENCE_STATE.STANDBY or self.sequence == SEQUENCE_STATE.BATTLING):
        if self.enemy_last_health_sequence['a'] is not None:
            enemy_health_change = (self.enemy_last_health_sequence['a'] - self.enemy_current_health_sequence['a']) / float(self.enemy_current_health_sequence['a']+0.0001)
            enemy_message = 'enemy health change this turn: %.2f' % enemy_health_change

            self.draw_message_on_frame(enemy_message)
#            print(enemy_message)

        if self.player_last_health_sequence['a'] is not None:
            player_health_change = (self.player_last_health_sequence['a'] - self.player_current_health_sequence['a']) / float(self.player_current_health_sequence['a']+0.0001)

            player_message = 'player health change this turn: %.2f' % player_health_change

            self.draw_message_on_frame(player_message)
#            print(player_message)

        self.draw_message_on_frame('Sequence is: ' + str(self.sequence.get_name()))

#        print('Sequence is: ' + str(self.sequence.get_name()))

        context_message = 'player_has_context: %s, pkmn context: %s' % (self.current_focus_player_1, self.current_focus_pokemon)

        self.draw_message_on_frame(context_message)

        action_is_done = 'Action: %s, nav is_done: %s' % (action, done)

        self.draw_message_on_frame(action_is_done)

#        is_series_done = not self.waiting_for_message_to_confirm_action and self.sequence == SEQUENCE_STATE.STANDBY and self.current_navigation_action == None and len(self.navigation_actions) == 0

        series_message = 'Series is done: %s' % (self.is_series_done)
        self.draw_message_on_frame(series_message)

        remaining_nav_message = 'Remaining nav items %s' % (self.navigation_actions)
        self.draw_message_on_frame(remaining_nav_message)
#        print(remaining_nav_message)
        remaining_command_message = 'Remaining command items %s' % (self.commands)
        self.draw_message_on_frame(remaining_command_message)
        remaining_nav_count_message = 'Remaining nav items count %d' % len(self.navigation_actions)
        self.draw_message_on_frame(remaining_nav_count_message)
        current_nav_count_message = 'Current nav %s, battle_state: %s' % (self.current_navigation_action, self.battle_state)
        self.draw_message_on_frame(current_nav_count_message)

        if done:
            print('nav completed:', self.current_navigation_action)
            logging.info('nav completed to:%s' % (self.current_navigation_action,))
            if self.current_navigation_action in nav_needs_message_confirmation_when_done:
                self.waiting_for_message_to_confirm_action = True
            if self.current_navigation_action == NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO:
                for i in range(self.team_size):
                    print('Adding Team info checks to nav items')
                    # Want these done in order, otherwise will go from 6 to 1st
                    self.navigation_actions.insert(i, team_info_nav_actions[i])
                print('self.navigation_actions', self.navigation_actions)

            if self.current_navigation_action == NavigationAction.STANDBY_COUNT_ACTIVE_POKEMON:
                self.reset_active_fighters_list()
                for i in range(self.active_pokemon_count):
                    print('Adding active check to nav items')
                    self.navigation_actions.insert(0, NavigationAction.STANDBY_CHECK_NEXT_ACTIVE)

            if self.current_navigation_action == NavigationAction.STANDBY_ACTIVATE_DYNAMAX:
                self.p1_used_dynamax = True
                self.p1_dynamax_turns = 1

            if self.current_navigation_action in [NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO]:
                print('team nav finished:',self.current_navigation_action)
                print('Info on constructed player team')
                print(self.player_pokemon)
                print('current team focus', self.current_team_pokemon)

            # clear, update if need be
            self.clear_nav_action()
            # Clear navigation if needed
            if not self.waiting_for_message_to_confirm_action:
                if len(self.navigation_actions) > 0:
                    self.current_navigation_action = self.navigation_actions.pop(0)
                    print('Setting new nav action:',self.current_navigation_action)
                    logging.info('Navigation Changed to:%s' % (self.current_navigation_action,))
        if 'message' in labels_boxes:
            wait = 0.06

        # Cut down on the processing spent on waiting messages
        if 'communication_waiting' in labels_boxes:
            wait = 0.1

        if 'message' not in labels_boxes:
#        """
            print('Ice Age!!!!!')
            print('Player Pokemon')
            print(self.player_pokemon)
            print('Enemy Active')
            print(self.enemy_active_pokemon_set)

            print('Player Active')
            print(self.player_active_pokemon_set)

            print('Player Seen')
            print(self.p1_seen_details)

            print('Enemy seen')
            print(self.p2_seen_details)
#        "" "
            print('Sequence')
            print(self.sequence)

            print('Current Nave')
            print(self.current_navigation_action)

            print('Nav Actions')
            print(self.navigation_actions)

            print('Commands')
            print(self.commands)
            print('wait', wait)
    #        """

        # Just in case disconnect happened
        if self.battle_state is None:
            ok_rect = self.get_subframe(DISCONNECT_MESSAGE.OK_BOX.get_message_rect())
            #TODO Maybe add a more narrow range so that pitch black doesn't trigger
            if calculate_communicating_black_ratio(ok_rect) < 0.01:
                message = parse_rect_with_pytesseract(ok_rect, False, True)
                #recieved: OSError: [Errno 24] Too many open files
                # I think logic triggered too many pytesseract calls
                # during waiting for match to begin
                wait = 0.4
                if re.search(diconnect_ok_regex, message):
                    print('Disconnect Detected')
                    logging.info('Disconnect Detected')
                    action = BUTTON_ACTION.A_BUTTON
                    self.is_series_done = True

        if action == BUTTON_ACTION.A_BUTTON:
            wait = 0.67
            logging.info('Button A Pressed')

            logging.info('Commands:%s' % (self.commands))
            logging.info('waiting_for_message_to_confirm_action:%s' % (self.waiting_for_message_to_confirm_action))
            logging.info('Sequence:%s' % (self.sequence))
            logging.info('Current Nave:%s' % (self.current_navigation_action))
            logging.info('Nav Actions:%s' % (self.navigation_actions))
            logging.info('battle_state:%s' % (self.battle_state))
            logging.info('next_battle_selectable:%s' % (self.battle_selectable))
            logging.info('next_battle_sub_selectable:%s' % (self.battle_sub_selectable))

        # Specifically for error messages
        if self.waiting_for_message_to_confirm_action:
            wait = 0.1
            #Only count when battle state is none
            #Long dynamax animation actually screwed this up
            if self.battle_state is not None:
                self.misfire_count += 1
        else:
            self.misfire_count = 0

        # Long wait in case disabled move text pops up from processing
        if self.misfire_count > 200:
            self.waiting_for_message_to_confirm_action = False
            if len(self.navigation_actions) == 0 and len(self.commands) == 0 and self.current_navigation_action is None:
                print('Possibly Button misfiring resetting last nav action.: %s' % (self.p1_last_attempted_action.get_nav_value()))
                logging.info('Possibly Button misfiring resetting last nav action.: %s' % (self.p1_last_attempted_action.get_nav_value()))
                self.misfire_count = 0
                self.navigation_actions.extend(self.p1_last_attempted_action.get_nav_value())
#                b = 1/0
        return action, self.is_series_done, wait

    def battle_phase_begin(self):
        print('Beginning Battle Phase')
        logging.info('Beginning Battle Phase')
        self.disabled_actions = set()

        self.sequence = SEQUENCE_STATE.BATTLING
        self.clear_nav_action()
        self.navigation_actions = []
        self.commands = []

    def clear_nav_action(self):
        self.current_navigation_action = None
        logging.info('Navigation Cleared ')

    def decide_action(self):
        valid_moves = self.get_valid_moves_for_player()
        print('got the moves', valid_moves, '\n')

        obs = self.get_observation(True)
        print('observation: ', obs)
        combined = obs['combined']
        transcript = obs['transcript']
        valid_moves_one_hot = obs['valid_onehot_player_1']
        valid_targets = obs['valid_onehot_p1_targets']
        print('combined',combined)
        print('transcript',transcript)
        print('valid_moves',repr(valid_moves_one_hot))
        print('valid_targets',repr(valid_targets))
        if self.network_style == NETWORK_STYLE.HONORABLE_SALAD:
            network_action = self.ainetwork.step(combined, valid_moves_one_hot, valid_targets, transcript)[0]
            attack_action = Action(network_action)
        else:
            attack_action = self.get_next_action(valid_moves)
        if self.aaas > 0:
            self.aaas = 0
            attack_action = Action.Attack_Slot_3
        #Used to mark failures choice band, shadow tag
        self.p1_last_attempted_action = attack_action
        nav_actions = attack_action.get_nav_value()
        self.navigation_actions.extend(nav_actions)
        self.log_decision(combined, transcript, valid_moves_one_hot)


    def log_decision(self, combined, transcript, valid_moves):
        logging.info('combined: %s' %(combined))
        logging.info('transcript: %s' %(transcript))
        logging.info('valid_moves: %s' %(valid_moves))

    def log_teams_encoded_construction(self, p1_pokemon, p2_pokemon):
        logging.info('Player_1 Encoded Pokemon')
        for pkmn in p1_pokemon:
            logging.info(pkmn.__dict__)
            for atk in pkmn.attacks:
                logging.info(atk.__dict__)
        logging.info('Player_2 Encoded Pokemon')
        for pkmn in p2_pokemon:
            logging.info(pkmn.__dict__)
            for atk in pkmn.attacks:
                logging.info(atk.__dict__)

    def log_active_pokemon_info(self, active_stats, is_player_1):
        logging.info('Active pokemon added for trainer:%s' % (is_player_1,))
        logging.info(active_stats)

    #Partial because called after each page 3 complete
    def log_constructed_team_info(self):
        logging.info('Player Team Pokemon Constructed')
        for pkmn in self.player_pokemon:
            pkmn = self.player_pokemon[pkmn]
            logging.info(pkmn)


    @staticmethod
    def extract_english_japanese_text(frame):
        print('inside of extracto magneto')
        jap_new_message = parse_rect_with_pytesseract(frame, True)
        print('pre new_message:', jap_new_message)
        if re.search(communicating_regex, jap_new_message):
            print('Communication short circuit not checking english')
            english_new_message = jap_new_message
        else:
            english_new_message = parse_rect_with_pytesseract(frame)
        print('english pre new_message:', english_new_message)
        return jap_new_message, english_new_message

    def check_message_in_background(self, future):
        jap_new_message, english_new_message = future
        # ignore communication
        # Dont process strings under 6 legth
        message_processed = False
        too_short = len(jap_new_message) < 6 or len(english_new_message) < 6
        is_communication_message = re.search(communicating_regex, jap_new_message) or re.search(communicating_regex, english_new_message)
        if too_short or is_communication_message:
            # Should only occur in network match. is as good as a go. mid game japanese text wont trigger force battle mode.
            # Searching out communication is good enough.
            if is_communication_message:
                if self.waiting_for_message_to_confirm_action == True:
                    print('Communication triggering battle sequence')
                    logging.info('Communication triggering battle sequence')
                    self.battle_phase_begin()
                self.waiting_for_message_to_confirm_action = False
        elif  isEditDistanceWithinTwo(self.last_accepted_message, jap_new_message) or isEditDistanceWithinTwo(self.last_accepted_message, english_new_message):
            pass
        elif  isEditDistanceWithinTwo(self.last_two_english_messages[0], english_new_message, 5) or isEditDistanceWithinTwo(self.last_two_english_messages[1], english_new_message, 5):
            pass
        elif  isEditDistanceWithinTwo(self.last_two_japanese_messages[0], jap_new_message, 5) or isEditDistanceWithinTwo(self.last_two_japanese_messages[1], jap_new_message, 5):
            pass
        else:
            if  self.last_accepted_message != jap_new_message:
                message_processed = self.process_message(jap_new_message)
                new_message = jap_new_message

            #Try english
            if message_processed == False and self.last_accepted_message != english_new_message:
                message_processed = self.process_message(english_new_message)
                new_message = english_new_message


            if  message_processed:
                self.draw_message_on_frame(new_message)
                print('completed new_message:', new_message)
                self.last_accepted_message = new_message
                self.last_two_english_messages.appendleft(english_new_message)
                self.last_two_japanese_messages.appendleft(jap_new_message)

    #                self.process_message(new_message)
                #Split health delta on each succesful message
#                    self.apply_damage_or_heal_reward()
#                    self.reset_health_delta()
                # The way we know our action was accepted
                if self.waiting_for_message_to_confirm_action:
                    self.waiting_for_message_to_confirm_action = False
                    print('waiting_for_message_to_confirm_action: %s' % (new_message))
                    logging.info('waiting_for_message_to_confirm_action: %s' % (new_message))
                    if self.action_succeeded(new_message):
                        print('good action_succeeded: %s' % (new_message))
                        logging.info('good action_succeeded: %s' % (new_message))
                        # Maybe a faint occurs and a switch is now possible
                        self.battle_phase_begin()
                        # Regular attacks only
                        if self.p1_last_attempted_action in REGULAR_ATTACK_ACTIONS:
                            self.p1_choice_attack_action = self.p1_last_attempted_action
                    else:
                        print('did not action_succeeded: %s' % (new_message))
                        print('failure_action: %s' % (self.current_navigation_action))
                        logging.info('did not action_succeeded: %s' % (new_message))
                        logging.info('failure_action: %s' % (self.current_navigation_action))
                        self.update_options_request_new_action()
                        self.clear_nav_action()
                        # Clear new message to allow multiple hhits of choice scarf
                        self.last_accepted_message = ''
                        self.last_two_english_messages.remove(english_new_message)
                        self.last_two_japanese_messages.remove(jap_new_message)

    def deprecated_check_message_in_background(self, frame):
        jap_new_message = parse_rect_with_pytesseract(frame, True)
        print('pre new_message:', jap_new_message)
        english_new_message = parse_rect_with_pytesseract(frame)
        print('english pre new_message:', english_new_message)
        message_processed = False

        message_lock = threading.RLock()
        print("trying to acquire message lock")

        with message_lock:
            print('entered lock')
            if  self.last_accepted_message == jap_new_message or self.last_accepted_message == english_new_message:
                pass
            else:
                if  self.last_accepted_message != jap_new_message:
                    message_processed = self.process_message(jap_new_message)
                    new_message = jap_new_message

                #Try english
                if message_processed == False and self.last_accepted_message != english_new_message:
                    message_processed = self.process_message(english_new_message)
                    new_message = english_new_message


                if  message_processed:
                    self.draw_message_on_frame(new_message)
                    print('new_message:', new_message)
                    self.last_accepted_message = new_message
        #                self.process_message(new_message)
                    #Split health delta on each succesful message
#                    self.apply_damage_or_heal_reward()
#                    self.reset_health_delta()
                    # The way we know our action was accepted
                    if self.waiting_for_message_to_confirm_action:
                        self.waiting_for_message_to_confirm_action = False
                        print('waiting_for_message_to_confirm_action:', new_message)
                        if self.action_succeeded(new_message):
                            print('good action_succeeded:', new_message)
                            # Maybe a faint occurs and a switch is now possible
                            self.battle_phase_begin()
                            # Regular attacks only
                            if self.p1_last_attempted_action in REGULAR_ATTACK_ACTIONS:
                                self.p1_choice_attack_action = self.p1_last_attempted_action
                        else:
                            print('did not action_succeeded:', new_message)
                            print('failure_action', self.current_navigation_action)
                            self.update_options_request_new_action()
                            self.clear_nav_action()
                            # Clear new message to allow multiple hhits of choice scarf
                            self.last_accepted_message = ''
        print('exit lock')

    # Anti Pressure tech
    def update_seen_pp_for_player(self, ):
        pass

    # Sometimes we fall a turn behind
    def clear_dirty_nav_actions(self):
        #Reset stale
        self.clear_nav_action()
        for nav_action in self.navigation_actions:
            if (nav_action in ATTACK_ACTIONS) or (nav_action in SWITCH_ACTIONS):
                self.navigation_actions.remove(nav_action)
                print('Stale action removed', nav_action)

    def get_next_action(self, valid_moves=None):
        if valid_moves is not None:
            # Not using targets
#            idx = random.randint(0,100) % len(valid_moves)
            weights = [action.get_attack_priority_weight() for action, _ in valid_moves]
            weights = np.asarray(weights)/sum(weights)
            idx = np.random.choice(len(valid_moves), p=weights)

            return valid_moves[idx][0]
#        return NavigationAction.STANDBY_ATTACK_SLOT_1
        if len(framed_fresh_battle_win_actions) > 0:
            return framed_fresh_battle_win_actions.pop(0).get_nav_value()
        if len(series_attacks_torment_faint_actions) > 0:
            return series_attacks_torment_faint_actions.pop(0).get_nav_value()

    def get_next_action_for_failure(self):
        if len(series_attacks_torment_faint_request_actions) > 0:
            return series_attacks_torment_faint_request_actions.pop(0).get_nav_value()

    def complete_damage_sequence():
        pass

    def begin_turn(self):
        self.moves_disabled = {}
        self.turns += 1

    def reset_health_delta(self):
        self.player_last_health_sequence = {'a':None, 'b':None}
        self.enemy_last_health_sequence = {'a':None, 'b':None}
        self.player_current_health_sequence = {'a':None, 'b':None}
        self.enemy_current_health_sequence = {'a':None, 'b':None}

    def reset_for_turn(self):
        self.reset_state_transcript()
        self.turns += 1
        logging.info('turn: %d' %(self.turns))
        logging.info('self.p1_selected[a]: %s' % (self.p1_selected['a'],))
        logging.info('self.p2_selected[a]: %s' % (self.p2_selected['a'],))
        self.player_last_health_sequence = {'a':None, 'b':None}
        self.enemy_last_health_sequence = {'a':None, 'b':None}
        self.player_current_health_sequence = {'a':None, 'b':None}
        self.enemy_current_health_sequence = {'a':None, 'b':None}
        self.player_start_health_sequence = {'a':None, 'b':None}
        self.enemy_start_health_sequence = {'a':None, 'b':None}
        self.disabled_actions = set()
        self.uturn_like_move_used = False
        self.player_pokemon_did_faint = False
        self.p1_must_switch = {'a':False, 'b':False}
        self.clear_dirty_nav_actions()
        self.need_active_scan = False
        self.waiting_for_message_to_confirm_action = False
        self.last_two_english_messages = deque(['', ''], maxlen=4)
        self.last_two_japanese_messages = deque(['', ''], maxlen=4)


    def get_observation(self, includeTranscript=False):

        normal_encodes = []
        reverse_encodes = []

        field_cat, field_raw = self.encode_field_state()
        p1_pokemon, p2_pokemon = self.get_preprocessed_pokemon()

        p1_cat, p1_raw = self.encode_pokemon_state(p1_pokemon)
        p2_cat, p2_raw = self.encode_pokemon_state(p2_pokemon)
        normal_encodes.extend(field_cat)
        normal_encodes.extend(p1_cat)
        normal_encodes.extend(p2_cat)

        # flatten categories
        normal_encodes = flatten(normal_encodes)

        categories_length = len(normal_encodes)
        normal_encodes.extend(field_raw)
        normal_encodes.extend(p1_raw)
        normal_encodes.extend(p2_raw)

        obs_length = len(normal_encodes)

        p1_actions_targets = self.get_valid_moves_for_player(position='a')

        p1_actions = self.split_actions_from_targets(p1_actions_targets)

        p1_targets = self.get_filled_targets_for_actions(p1_actions_targets)
        if not includeTranscript:
            return normal_encodes
        results = {
            'transcript': self.p1_transcript,
            'reverse_transcript': self.p2_transcript,
            'field': self.encode_field_state(),
            'player': self.encode_pokemon_state(p1_pokemon),
            'agent':self.encode_pokemon_state(p2_pokemon),
            'combined': normal_encodes,
            'cat_length':categories_length,
            'full_obs_len':obs_length,
            'raw_length':(obs_length-categories_length),
            'valid_moves_player_1': self.get_valid_moves_for_player(),
            'valid_onehot_player_1': self.valid_onehot_moves(p1_actions),
            'valid_onehot_p1_targets': self.valid_onehot_targets(p1_targets),
        }
        return results

    def encode_field_state(self):
        category_encode = [
            all_generations_labels.transform([self.gen.value]),     # category
            all_gametypes_labels.transform([self.gametype.value]),     # category
            all_tiers_labels.transform([self.tier.value]),     # category
            all_weather_labels.transform([self.weather_condition]),     # category
            all_terrains_labels.transform([self.terrain_condition]),     # category
            all_rooms_labels.transform([self.current_room]),     # category
        ]
        field_raw_encodes = [
            self.weather_turns,
            self.terrain_turns,
            self.room_turns,
            bool_to_int(self.need_action_for_position['a']),
            bool_to_int(self.need_action_for_position['b']),
            self.p1_used_dynamax,
            self.p2_used_dynamax,
        ]

        p1_category_encodes = [
            all_actions_labels.transform([self.p1_pending_actions['a'].value]),     # category
            all_actions_labels.transform([self.p1_pending_actions['b'].value]),     # category
            all_selectable_targets_labels.transform([self.p1_pending_targets['a'].value]),     # category
            all_selectable_targets_labels.transform([self.p1_pending_targets['b'].value]),     # category
        ]

        p1_raw_encodes = [
            self.p1_teamsize,
            bool_to_int(self.p1_safeguard),
            bool_to_int(self.p1_lightscreen),
            bool_to_int(self.p1_reflect),
            bool_to_int(self.p1_tailwind),
            bool_to_int(self.p1_aurora_veil),
            bool_to_int(self.p1_used_zmove),
            bool_to_int(self.p1_used_mega),
            bool_to_int(self.p1_has_rocks),
            bool_to_int(self.p1_has_web),
            self.p1_spikes,
            self.p1_toxic_spikes,
            bool_to_int(self.p1_yawned['a']),
            bool_to_int(self.p1_yawned['b']),
            self.p1_perished['a'],
            self.p1_perished['b'],
            bool_to_int(self.p1_missed_failed['a']),
            bool_to_int(self.p1_missed_failed['b']),
            bool_to_int(self.p1_smack_down['a']),
            bool_to_int(self.p1_smack_down['b']),
            self.p1_effective['a'],
            self.p1_effective['b'],
            bool_to_int(self.p1_destined['a']),
            bool_to_int(self.p1_destined['b']),
            bool_to_int(self.p1_move_succeeded['a']),
            bool_to_int(self.p1_move_succeeded['b']),
            bool_to_int(self.p1_trapped['a']),
            bool_to_int(self.p1_trapped['b']),
            self.p1_protect_counter['a'],
            self.p1_protect_counter['b'],
        ]

        p1_raw_encodes.extend(self.p1_active_pokemon_stats['a'].get_encode())
        p1_raw_encodes.extend(self.p1_active_pokemon_stats['b'].get_encode())

        p2_category_encodes = [
            all_actions_labels.transform([self.p2_pending_actions['a'].value]),     # category
            all_actions_labels.transform([self.p2_pending_actions['b'].value]),     # category
            all_selectable_targets_labels.transform([self.p2_pending_targets['a'].value]),     # category
            all_selectable_targets_labels.transform([self.p2_pending_targets['b'].value]),     # category
        ]


        p2_raw_encodes = [
            self.p2_teamsize,
            bool_to_int(self.p2_safeguard),
            bool_to_int(self.p2_lightscreen),
            bool_to_int(self.p2_reflect),
            bool_to_int(self.p2_tailwind),
            bool_to_int(self.p2_aurora_veil),
            bool_to_int(self.p2_used_zmove),
            bool_to_int(self.p2_used_mega),
            bool_to_int(self.p2_has_rocks),
            bool_to_int(self.p2_has_web),
            self.p2_spikes,
            self.p2_toxic_spikes,
            bool_to_int(self.p2_yawned['a']),
            bool_to_int(self.p2_yawned['b']),
            self.p2_perished['a'],
            self.p2_perished['b'],
            bool_to_int(self.p2_missed_failed['a']),
            bool_to_int(self.p2_missed_failed['b']),
            bool_to_int(self.p2_smack_down['a']),
            bool_to_int(self.p2_smack_down['b']),
            self.p2_effective['a'],
            self.p2_effective['b'],
            bool_to_int(self.p2_destined['a']),
            bool_to_int(self.p2_destined['b']),
            bool_to_int(self.p2_move_succeeded['a']),
            bool_to_int(self.p2_move_succeeded['b']),
            bool_to_int(self.p2_trapped['a']),
            bool_to_int(self.p2_trapped['b']),
            self.p2_protect_counter['a'],
            self.p2_protect_counter['b'],
        ]

        p2_raw_encodes.extend(self.p2_active_pokemon_stats['a'].get_encode())
        p2_raw_encodes.extend(self.p2_active_pokemon_stats['b'].get_encode())


        # Fix with attacks instead
        # TO be added after field category encodes and before p1/p2 category
        seen_attacks_category_encodes = [
            all_pokemon_attacks_labels.transform([id_for_attack_name(self.p1_seen_attacks['a'])]),     # category
            all_pokemon_attacks_labels.transform([id_for_attack_name(self.p1_seen_attacks['b'])]),     # category
        ]



        full_category_encodes = []
        full_raw_encodes = []

        full_category_encodes.extend(category_encode)
        full_category_encodes.extend(p1_category_encodes)
        full_category_encodes.extend(seen_attacks_category_encodes)

        full_raw_encodes.extend(field_raw_encodes)
        full_raw_encodes.extend(p1_raw_encodes)
        full_raw_encodes.extend(p2_raw_encodes)

        return full_category_encodes, full_raw_encodes



    # Update pokemon's name with form name, update attack pp by usage
    # Fill empty attacks With
    def encode_pokemon_state(self, pokemon):
        # if we have empty spots for missing pokemon, just set 0s
        category_encodes = []
        raw_encodes = []
        # add current pokemon first to denote that it is selected.
        for pkmn in pokemon:
            cat, raw = self.encode_single_pokemon_state(pkmn)
            category_encodes.extend(cat)
            raw_encodes.extend(raw)
        return category_encodes, raw_encodes

    def split_actions_from_targets(self, actions_targets):
      actions = []
      for act, tars in actions_targets:
        actions.append(act)

      return actions

    def valid_onehot_moves(self, avail_moves):
        moves = np.zeros(15)
        for move in avail_moves:
            moves[move.value] = 1
#        moves[np.nonzero(moves==0)] = -500
#        moves[np.nonzero(moves==0)] = -500
#		moves[np.nonzero(moves==0)] = -math.inf
#		moves[np.nonzero(moves==0)] = -4000000
        moves[np.nonzero(moves==1)] = 1
        return moves

    def valid_onehot_targets(self, avail_targets):
        targets = np.zeros((15, 8))
        for idx in range(targets.shape[0]):
          for target in avail_targets[idx]:
              targets[idx][target.value] = 1
#        targets[np.nonzero(targets==0)] = -math.inf
#        targets[np.nonzero(targets==0)] = -4000000
        targets[np.nonzero(targets==1)] = 1
        return targets.reshape(-1)

    def get_filled_targets_for_actions(self, actions_targets):
      targets = []
      for idx, action in enumerate(Action):
        targets.append([])
        for act, tars in actions_targets:
            if action == act:
                targets[idx].extend(tars)
                break
      return targets



    def get_preprocessed_pokemon(self):

        # wild matches is 1
        p2_teamsize = 1
        if self.is_network_match:
            #network is 3
            p2_teamsize = 3
        self.p2_teamsize = p2_teamsize
        self.p1_teamsize = len(self.player_pokemon)

        # Sort pokemon by position index
        temp_team_list = []
        for pkmn in self.player_pokemon:
            temp_team_list.append((pkmn, self.player_pokemon[pkmn]))

        # To sort the list in place...
        temp_team_list.sort(key=lambda pkmn: pkmn[1]['position'], reverse=False)

        real_team_list = []
        for name_pkmn_pair in temp_team_list:
            team_name = name_pkmn_pair[0]
            pkmn = name_pkmn_pair[1]
            element_1 = pkmn['element_1']
            element_2 = pkmn['element_2']

            real_team_list.append((team_name, sim_pokemon_from_json(pkmn, element_1, element_2)))


        p1_poke = get_seen_rep_of_pokemon(real_team_list, self.p1_seen_details, self.p1_teamsize, a_slot=self.p1_selected['a'], b_slot=self.p1_selected['b'])
        p2_poke = get_seen_rep_of_opponent_pokemon(self.p2_seen_details, p2_teamsize, a_slot=self.p2_selected['a'], b_slot=self.p2_selected['b'])
        print('printingh p1_poke_info')
        for pkmn in p1_poke:
            print(pkmn.__dict__)
            for atk in pkmn.attacks:
                print(atk.__dict__)
            print()
        print('printingh p22_poke_info')
        for pkmn in p2_poke:
            print(pkmn.__dict__)
            for atk in pkmn.attacks:
                print(atk.__dict__)
            print()

        self.log_teams_encoded_construction(p1_poke, p2_poke)

        return p1_poke, p2_poke

    # IF pokemon is not  revealed, pass None.
    # Only opponents/p2s can be none.
    def encode_single_pokemon_state(self, pokemon, show_full_details=False):
        # empty pokemon slot
        # max IV/EV stat
        max_ev_iv_value = 800

        element_2nd_type = ELEMENT_TYPE.TYPELESS.value
        if pokemon.element_2nd_type is not None:
            element_2nd_type = pokemon.element_2nd_type.value
        category_encode = [
            all_pokemon_names_labels.transform([pokemon.name]),     # category
            # TDOD, update status correctly
#            all_status_labels.transform([pokemon.status.value]),   # category
            all_status_labels.transform([Status.NOTHING.value]),   # category
            all_element_types_labels.transform([pokemon.element_1st_type.value]),     # category
            all_element_types_labels.transform([element_2nd_type]),   # category
            all_abilities_labels.transform([id_for_ability_name(pokemon.ability)]),
            all_items_labels.transform([id_for_item_name(pokemon.item)]),
            all_genders_labels.transform([pokemon.gender.value]),
        ]
        raw_encode = []
        if show_full_details:
            raw_encode.append(pokemon.max_health / max_ev_iv_value)
            raw_encode.append(pokemon.atk / max_ev_iv_value)
            raw_encode.append(pokemon.spatk / max_ev_iv_value)
            raw_encode.append(pokemon.defense / max_ev_iv_value)
            raw_encode.append(pokemon.spdef / max_ev_iv_value)
            raw_encode.append(pokemon.speed / max_ev_iv_value)

        health_ratio = 1
        if pokemon.name == 'empty_pokemon':
            health_ratio = 0
        elif pokemon.max_health > 0:
            health_ratio = pokemon.curr_health/float(pokemon.max_health)

        max_weight = 2204.4
        raw_encode.extend([
            pokemon.level / 100.00,
            health_ratio,
            pokemon.weight/max_weight,
        ])

        attack_category_encode = []
        attack_raw_encode = []
        for attack in pokemon.attacks:
            attack_category_encode.append(all_pokemon_attacks_labels.transform([attack.id]))
            attack_category_encode.append(all_element_types_labels.transform([attack.element_type.value]))
            attack_category_encode.append(all_categories_labels.transform([attack.category.value]))

            attack_raw_encode.append(attack.power / 160.00)
            accuracy = 1 if attack.accuracy == True else attack.accuracy
            attack_raw_encode.append(accuracy)
            attack_raw_encode.append(attack.priority / 6.00)
            attack_raw_encode.append(attack.used_pp/float(attack.pp))
            attack_raw_encode.append(bool_to_int(attack.disabled))
        category_encode.extend(attack_category_encode)
        raw_encode.extend(attack_raw_encode)

        return category_encode, raw_encode

    # You hate to see it
    def handle_cant_select_attack(self, attack_name):
        # set move as disabled this turn.
        self.moves_disabled[attack_name] = True
        pass

    def get_position_for_next_player_pokemon(self):
        return 'a'

    def get_position_for_next_enemy_pokemon(self):
        return 'a'

    def action_succeeded(self, message):
        # If move or switch cannot be performed determine
        if re.search(get_move_cannot_be_used(self.construct_seen_pokemon_regex()), message):
            print('Invalid mesage', message)

            return False
        print('valido mesage', message)
        return True

    def update_options_request_new_action(self):
        print('Nav action failed: ', self.current_navigation_action)
        print('disabling action : ', self.p1_last_attempted_action)
        logging.info('Nav action failed: %s' % (self.current_navigation_action))
        logging.info('disabling action : %s' % (self.p1_last_attempted_action))
        self.disabled_actions.add(self.p1_last_attempted_action)
        print('self.disabled_actions list : ', self.disabled_actions)
        logging.info('self.disabled_actions list : %s' % (self.disabled_actions))
        self.waiting_for_message_to_confirm_action = False

        if self.current_navigation_action in attack_nav_actions:
            print('Need new Action, move failed')

        if self.current_navigation_action in change_slots_nav_actions:
            print('Need new Action, switch failed')
        self.needs_new_player_action = True

        valid_moves = self.get_valid_moves_for_player()
        print('next set of legal moves', valid_moves, '\n')
        logging.info('next set of legal moves: %s' % (valid_moves))

    def construct_seen_pokemon_regex(self):
        if len(self.registered_pokemon_names) == 0:
            return pokemon_names_regex

        extension = '|'
        for pkmn_name in self.registered_pokemon_names:
            if pkmn_name == self.registered_pokemon_names[-1]:
                extension += ('%s' % pkmn_name)
            else:
                extension += ('%s|' % pkmn_name)
        extension += ')'
        # replace with construction once working
        return (pokemon_names_regex[:-1] + extension)

    def lookup_pokemon_name(self):
        pass

    def get_switch_in_utterance(self, pkmn_name):
        audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
        audio_dialog_name = (MediaType.DIALOG, 'switch_in_5_a')
        audio_dialog_name_2 = (MediaType.ATTACK, 'switch_in_5_b')
        utterances = [audio_dialog_name, audio_pkmn_name, audio_dialog_name_2]
        # 20% chance to do other stuff
        if random.randint(0, 10) % 5 == 0:
            switch_num = random.randint(1, 5)
            switch_num = 'switch_in_%d' % (switch_num)
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'switch_in_5_a')
            utterances = [audio_dialog_name, audio_pkmn_name]
        return utterances


    def process_message(self, message):
        message_is_valid = False

        params = []
        utterances = []
        inp_type = None

        # Example Utterances
        #audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
        #audio_dialog_name = (MediaType.DIALOG, 'switched_items')
        #audio_attack_name = (MediaType.ATTACK, 'pikachu')

        if re.search(end_battle_over_regex, message):
            message_is_valid = True
            inp_type = MATCH_OVER


        # If move or switch cannot be performed determine
        # Even failure messages are valid
        if re.search(get_move_cannot_be_used(self.construct_seen_pokemon_regex()), message):

            return True

        if re.search(trick_regex, message):
            message_is_valid = True
            inp_type = TRICK
            pkmn_name = re.search(self.construct_seen_pokemon_regex(), message).group(0)
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'switched_items')
            utterances.append(audio_pkmn_name)
            utterances.append(audio_dialog_name)

        # Player switching out
        if re.search(get_returned_to_player_regex(self.construct_seen_pokemon_regex()), message):
            position = self.get_position_for_next_player_pokemon()
            self.current_focus_player_1 = True

            self.switch_was_from = self.p1_selected['a']
            self.current_focus_pokemon = re.search(self.construct_seen_pokemon_regex(), message).group(0)
            message_is_valid = True
            inp_type = SWITCHOUT
            pkmn_name = self.current_focus_pokemon
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'come_back')
            utterances.append(audio_pkmn_name)
            utterances.append(audio_dialog_name)
        #Player Uturn/Volt Switch must be checked first.
        # Similar wording to roar i believe for opponent.
        if re.search(get_uturn_volt_switch_regex(self.trainer_name), message):
            position = self.get_position_for_next_player_pokemon()
            self.current_focus_player_1 = True
            self.current_focus_pokemon = re.search(self.construct_seen_pokemon_regex(), message).group(0)
            print('uturn like move used ')
            message_is_valid = True
            inp_type = MUST_SWITCH

        # Enemy switching out
        if re.search(get_returned_to_enemy_regex(self.construct_seen_pokemon_regex()), message):
            position = self.get_position_for_next_enemy_pokemon()
            self.current_focus_player_1 = False
            self.current_focus_pokemon = re.search(self.construct_seen_pokemon_regex(), message).group(0)
            message_is_valid = True
            inp_type = SWITCHOUT
            pkmn_name = self.current_focus_pokemon
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'withdrew')
            utterances.append(audio_dialog_name)
            utterances.append(audio_pkmn_name)

        # Player switching
        if re.search(get_player_single_pokemon_sentout(), message) or re.search(get_player_pokemon_dragged_out(), message):
            position = self.get_position_for_next_player_pokemon()
            self.current_focus_player_1 = True
            self.p1_selected[position] = self.current_focus_pokemon = re.search(get_player_single_pokemon_complete(message), message).group(1).strip().split(' ')[0]
            print('trying to send out pokemon', self.p1_selected[position])
            message_is_valid = True
            inp_type = SWITCH
            pkmn_name = self.p1_selected[position]
            utterances = self.get_switch_in_utterance(pkmn_name)

        # Player switching  --- DRAGGGED
        if re.search(get_player_pokemon_dragged_out(), message):
            position = self.get_position_for_next_player_pokemon()
            self.current_focus_player_1 = True
            self.p1_selected[position] = self.current_focus_pokemon = re.search(get_player_pokemon_dragged_out(), message).group(1).strip()
            print('trying to send out pokemon', self.p1_selected[position])
            message_is_valid = True
            inp_type = SWITCH
            pkmn_name = self.p1_selected[position]
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'dragged_out')
            utterances.extend([audio_pkmn_name, audio_dialog_name])

        # Enemy switching  - WILD ENCOUNTER Name must exist
        if re.search(get_wilder_encounters_appeared(self.construct_seen_pokemon_regex()), message):
            position = self.get_position_for_next_enemy_pokemon()
            self.current_focus_player_1 = False
            self.p2_selected[position] = self.current_focus_pokemon = re.search(pokemon_names_regex, message).group(0).strip()
            message_is_valid = True
            inp_type = SWITCH
            pkmn_name = self.p2_selected[position]
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'encounter_2')
            utterances.extend([audio_pkmn_name, audio_dialog_name])

        # Enemy switching
        if re.search(get_enemy_single_pokemon_sentout(self.construct_seen_pokemon_regex()), message):
            position = self.get_position_for_next_enemy_pokemon()
            self.current_focus_player_1 = False
            self.p2_selected[position] = self.current_focus_pokemon = re.search(get_enemy_single_pokemon_sentout(self.construct_seen_pokemon_regex()), message).group(1).strip().split(' ')[0]
            message_is_valid = True
            inp_type = SWITCH
            pkmn_name = self.p2_selected[position]
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'opponent_switch_in_1')
            utterances.extend([audio_dialog_name, audio_pkmn_name])

        # Enemy switching   - DRAGGED
        if re.search(get_enemy_pokemon_dragged_out(), message):
            position = self.get_position_for_next_enemy_pokemon()
            self.current_focus_player_1 = False
            self.p2_selected[position] = self.current_focus_pokemon = re.search(get_enemy_single_pokemon_sentout(), message).group(1).strip()
            message_is_valid = True
            inp_type = SWITCH
            pkmn_name = self.p2_selected[position]
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'dragged_out')
            utterances.extend([audio_pkmn_name, audio_dialog_name])

        # Player Double switching
        # perform 1st pokemon update here, second can happen at bottom
        if re.search(get_player_doubles_pokemon_sentout(self.construct_seen_pokemon_regex()), message):
            self.current_focus_player_1 = True
            self.p1_selected['a'] = self.current_focus_pokemon = re.search(get_player_doubles_pokemon_sentout(self.construct_seen_pokemon_regex()), message).group(1)
            message_is_valid = True
            inp_type = SWITCH
            self.process_update(inp_type, params)
            self.p1_selected['a'] = self.current_focus_pokemon = re.search(get_player_doubles_pokemon_sentout(self.construct_seen_pokemon_regex()), message).group(2)
            pkmn_name = self.p1_selected['a']
            #TODO update to use both names
            utterances = self.get_switch_in_utterance(pkmn_name)

        # Enemy Double switching
        # perform 1st pokemon update here, second can happen at bottom
        if re.search(get_enemy_doubles_pokemon_sentout(self.construct_seen_pokemon_regex()), message):
            self.current_focus_player_1 = False
            self.p2_selected['a'] = self.current_focus_pokemon = re.search(get_enemy_doubles_pokemon_sentout(self.construct_seen_pokemon_regex()), message).group(1)
            message_is_valid = True
            inp_type = SWITCH
            self.process_update(inp_type, params)
            self.p2_selected['b'] = self.current_focus_pokemon = re.search(get_enemy_doubles_pokemon_sentout(self.construct_seen_pokemon_regex()), message).group(2)
            pkmn_name = self.p2_selected['a']
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'opponent_switch_in_1')
            utterances.extend([audio_dialog_name, audio_pkmn_name])

        # Player has moved
        if re.search(get_player_used_move_one_regex(self.construct_seen_pokemon_regex()), message):
            self.current_focus_player_1 = True
            self.current_focus_pokemon = re.search(self.construct_seen_pokemon_regex(), message).group(1)
            print('self.current_focus_pokemon', self.current_focus_pokemon)
            message_is_valid = True
            inp_type = MOVE
            atk_name = re.search(pokemon_attacks_regex, message).group(0)
            params.append(atk_name)
            pkmn_name = re.search(self.construct_seen_pokemon_regex(), message).group(0)
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'used')
            audio_attack_name = (MediaType.ATTACK, atk_name)
            special_attack_utterance  = is_special_attack(atk_name)
            if special_attack_utterance is not None:
                utterances.extend(special_attack_utterance)
            else:
                utterances.extend([audio_pkmn_name, audio_dialog_name, audio_attack_name])

        # Enemy has move
        elif re.search(get_enemy_used_move_one_regex(self.construct_seen_pokemon_regex()), message):
            self.current_focus_player_1 = False
            self.current_focus_pokemon = re.search(self.construct_seen_pokemon_regex(), message).group(0)
            print('2222self.current_focus_pokemon', self.current_focus_pokemon)
            message_is_valid = True
            inp_type = MOVE
            atk_name = re.search(pokemon_attacks_regex, message).group(0)
            params.append(atk_name)
            pkmn_name = re.search(self.construct_seen_pokemon_regex(), message).group(0)
            audio_pkmn_name = (MediaType.POKEMON, pkmn_name)
            audio_dialog_name = (MediaType.DIALOG, 'used')
            audio_attack_name = (MediaType.ATTACK, atk_name)
            special_attack_utterance  = is_special_attack(atk_name)
            if special_attack_utterance is not None:
                utterances.extend(special_attack_utterance)
            else:
                utterances.extend([audio_pkmn_name, audio_dialog_name, audio_attack_name])



        # Boost or unboost has occurred
        if re.search(enemy_stats_rose_regex, message) or re.search(enemy_stats_rose_sharply_regex, message) or re.search(enemy_stats_rose_drastically_regex, message) or re.search(enemy_stats_fell_regex, message) or re.search(enemy_stats_fell_harshly_regex, message) or re.search(enemy_stats_fell_severely_regex, message) or \
            re.search(player_stats_rose_regex, message) or re.search(player_stats_rose_sharply_regex, message) or re.search(player_stats_rose_drastically_regex, message) or re.search(player_stats_fell_regex, message) or re.search(player_stats_fell_harshly_regex, message) or re.search(player_stats_fell_severely_regex, message):
            message_is_valid = True
            inp_type = BOOST

        # Small reward/punishment
        if re.search(get_player_stat_changes_removed_regex(self.construct_seen_pokemon_regex()), message) or re.search(get_enemy_stat_changes_removed_regex(self.construct_seen_pokemon_regex()), message):
            message_is_valid = True
            inp_type = BOOST
            audio_dialog_name = (MediaType.DIALOG, 'stats_changes_removed')
            utterances.append(audio_dialog_name)

        # All stat changes eliminated
        if re.search(all_stats_eliminated_regex, message):
            message_is_valid = True
            inp_type = UNBOOST
#            params =  [is_player_1, pkmn]
            audio_dialog_name = (MediaType.DIALOG, 'stats_were_not_lowered')
            utterances.append(audio_dialog_name)

        if re.search(critical_regex, message):
            message_is_valid = True
            inp_type = CRIT
            audio_dialog_name = (MediaType.DIALOG, 'a_critical_hit')
            utterances.append(audio_dialog_name)

        if re.search(grassy_terrain, message):
            message_is_valid = True
            inp_type = FIELD_START
            params = ['Grassy Terrain']
            terrain_start_options = ['grassy_terrain_start_1', 'grassy_terrain_start_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(terrain_start_options))
            utterances.append(audio_dialog_name)

        if re.search(misty_terrain, message):
            message_is_valid = True
            inp_type = FIELD_START
            params = ['Misty Terrain']
            terrain_start_options = ['misty_terrain_start_1', 'misty_terrain_start_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(terrain_start_options))
            utterances.append(audio_dialog_name)

        if re.search(electric_terrain, message):
            message_is_valid = True
            inp_type = FIELD_START
            params = ['Electric Terrain']
            terrain_start_options = ['electric_terrain_start_1', 'electric_terrain_start_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(terrain_start_options))
            utterances.append(audio_dialog_name)

        if re.search(psychic_terrain, message):
            message_is_valid = True
            inp_type = FIELD_START
            params = ['Psychic Terrain']
            terrain_start_options = ['psychic_terrain_start_1', 'psychic_terrain_start_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(terrain_start_options))
            utterances.append(audio_dialog_name)

        # terrain end
        if re.search(terrain_end, message):
            message_is_valid = True
            inp_type = FIELD_END
            params = [message]
            if re.search(grassy_terrain_end, message):
                terrain_end_options = ['grassy_terrain_end_1', 'grassy_terrain_end_2']
                audio_dialog_name = (MediaType.DIALOG, np.random.choice(terrain_start_options))
                utterances.append(audio_dialog_name)

            if re.search(psychic_terrain_end, message):
                terrain_end_options = ['psychic_terrain_start_1', 'psychic_terrain_start_2']
                audio_dialog_name = (MediaType.DIALOG, np.random.choice(terrain_start_options))
                utterances.append(audio_dialog_name)

            if re.search(electric_terrain_end, message):
                terrain_end_options = ['electric_terrain_end_1', 'electric_terrain_end_2']
                audio_dialog_name = (MediaType.DIALOG, np.random.choice(terrain_start_options))
                utterances.append(audio_dialog_name)

            if re.search(misty_terrain_end, message):
                terrain_end_options = ['misty_terrain_end_1', 'misty_terrain_end_2']
                audio_dialog_name = (MediaType.DIALOG, np.random.choice(terrain_start_options))
                utterances.append(audio_dialog_name)

        # Weaher Begin
        if re.search(rain_start, message):
            message_is_valid = True
            inp_type = WEATHER
            params = ['RainDance']
            weather_start_options = ['heavy_rain_start', 'rain_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(weather_start_options))
            utterances.append(audio_dialog_name)

        if re.search(sun_start, message):
            message_is_valid = True
            inp_type = WEATHER
            params = ['SunnyDay']
            weather_start_options = ['harsh_sunlight_start', 'sunlight_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(weather_start_options))
            utterances.append(audio_dialog_name)

        if re.search(sandstorm_start, message):
            message_is_valid = True
            inp_type = WEATHER
            params = ['Sandstorm']
            weather_start_options = ['sandstorm_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(weather_start_options))
            utterances.append(audio_dialog_name)

        if re.search(hail_start, message):
            message_is_valid = True
            inp_type = WEATHER
            params = ['Hail']
            weather_start_options = ['hailing_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(weather_start_options))
            utterances.append(audio_dialog_name)

        # Weather end
        if re.search(weather_end, message):
            message_is_valid = True
            inp_type = WEATHER
            params = [message]
            if re.search(rain_start_end, message):
                weather_end_options = ['heavy_rain_end', 'rain_end']
                audio_dialog_name = (MediaType.DIALOG, np.random.choice(weather_start_options))
                utterances.append(audio_dialog_name)

            if re.search(sun_start_end, message):
                weather_end_options = ['sunlight_end', 'harsh_sunlight_end']
                audio_dialog_name = (MediaType.DIALOG, np.random.choice(weather_start_options))
                utterances.append(audio_dialog_name)

            if re.search(sandstorm_start_end, message):
                weather_end_options = ['sandstorm_end']
                audio_dialog_name = (MediaType.DIALOG, np.random.choice(weather_start_options))
                utterances.append(audio_dialog_name)

            if re.search(hail_start_end, message):
                weather_end_options = ['hail_end']
                audio_dialog_name = (MediaType.DIALOG, np.random.choice(weather_start_options))
                utterances.append(audio_dialog_name)

        # Rooms start
        if re.search(get_trick_room_start(self.construct_seen_pokemon_regex()), message):
            message_is_valid = True
            inp_type = ROOM
            params = ['Trick Room']
            audio_dialog_name = (MediaType.DIALOG, 'trick_room_start')
            utterances.append(audio_dialog_name)

        if re.search(wonder_room_start, message):
            message_is_valid = True
            inp_type = ROOM
            params = ['Wonder Room']
            audio_dialog_name = (MediaType.DIALOG, 'wonder_room_start')
            utterances.append(audio_dialog_name)

        if re.search(magic_room_start, message):
            message_is_valid = True
            inp_type = ROOM
            params = ['Magic Room']
            audio_dialog_name = (MediaType.DIALOG, 'magic_room_start')
            utterances.append(audio_dialog_name)

        # Rooms end
        if re.search(magic_room_end, message):
            message_is_valid = True
            inp_type = ROOM
            params = [message]
            audio_dialog_name = (MediaType.DIALOG, 'magic_room_end')
            utterances.append(audio_dialog_name)

        if re.search(trick_room_end, message):
            message_is_valid = True
            inp_type = ROOM
            params = [message]
            audio_dialog_name = (MediaType.DIALOG, 'trick_room_end')
            utterances.append(audio_dialog_name)

        if re.search(wonder_room_end, message):
            message_is_valid = True
            inp_type = ROOM
            params = [message]
            audio_dialog_name = (MediaType.DIALOG, 'wonder_room_end')
            utterances.append(audio_dialog_name)

        # Sticky web Hazard
        if re.search(sticky_web_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Sticky Web']
            hazards_start_options = ['sticky_web_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_start_options))
            utterances.append(audio_dialog_name)

        # Sticky web Hazard
        if re.search(sticky_web_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Sticky Web']
            hazards_start_options = ['sticky_web_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_start_options))
            utterances.append(audio_dialog_name)

        # Sticky web Hazard
        if re.search(sticky_web_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Sticky Web']
            hazards_end_options = ['sticky_web_end_1', 'sticky_web_end_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_end_options))
            utterances.append(audio_dialog_name)

        # Sticky web Hazard
        if re.search(sticky_web_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Sticky Web']
            hazards_end_options = ['sticky_web_end_1', 'sticky_web_end_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_end_options))
            utterances.append(audio_dialog_name)

        # Spikes Hazard
        if re.search(spikes_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Spikes']
            hazards_start_options = ['spikes_start_1', 'spikes_start_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_start_options))
            utterances.append(audio_dialog_name)

        # Spikes Hazard
        if re.search(spikes_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Spikes']
            hazards_start_options = ['spikes_start_1', 'spikes_start_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_start_options))
            utterances.append(audio_dialog_name)

        # Spikes Hazard
        if re.search(spikes_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Spikes']
            hazards_end_options = ['spikes_end']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_end_options))
            utterances.append(audio_dialog_name)

        # Spikes Hazard
        if re.search(spikes_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Spikes']
            hazards_end_options = ['spikes_end']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_end_options))
            utterances.append(audio_dialog_name)

        # Toxic Spikes Hazard
        if re.search(toxic_spikes_player_side_start, message):
            message_is_valid = True
            inp_type = FIELD_START
            is_player = True
            params = [is_player, 'Toxic Spikes']
            hazards_start_options = ['toxic_spikes_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_start_options))
            utterances.append(audio_dialog_name)

        # Toxic Spikes Hazard
        if re.search(toxic_spikes_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Toxic Spikes']
            hazards_start_options = ['toxic_spikes_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_start_options))
            utterances.append(audio_dialog_name)

        # Toxic Spikes Hazard
        if re.search(toxic_spikes_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Toxic Spikes']
            hazards_end_options = ['toxic_spikes_end_1', 'toxic_spikes_end_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_end_options))
            utterances.append(audio_dialog_name)

        # Toxic Spikes Hazard
        if re.search(toxic_spikes_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Toxic Spikes']
            hazards_end_options = ['toxic_spikes_end_1', 'toxic_spikes_end_2']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_end_options))
            utterances.append(audio_dialog_name)


        # Stealth Rocks Hazard
        if re.search(stealth_rocks_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Stealth Rock']
            hazards_start_options = ['stealth_rocks_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_start_options))
            utterances.append(audio_dialog_name)

        # Stealth Rocks Hazard
        if re.search(stealth_rocks_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Stealth Rock']
            hazards_start_options = ['stealth_rocks_start']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_start_options))
            utterances.append(audio_dialog_name)

        # Stealth Rocks Hazard
        if re.search(stealth_rocks_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Stealth Rock']
            hazards_end_options = ['stealth_rocks_end']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_end_options))
            utterances.append(audio_dialog_name)

        # Stealth Rocks Hazard
        if re.search(stealth_rocks_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Stealth Rock']
            hazards_end_options = ['stealth_rocks_end']
            audio_dialog_name = (MediaType.DIALOG, np.random.choice(hazards_end_options))
            utterances.append(audio_dialog_name)



        # Reflect NonHazard
        if re.search(reflect_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Reflect']
            audio_dialog_name = (MediaType.DIALOG, 'reflect_start')
            utterances.append(audio_dialog_name)

        # Reflect NonHazard
        if re.search(reflect_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Reflect']
            audio_dialog_name = (MediaType.DIALOG, 'reflect_start')
            utterances.append(audio_dialog_name)

        # Reflect NonHazard
        if re.search(reflect_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Reflect']
            audio_dialog_name = (MediaType.DIALOG, 'reflect_end')
            utterances.append(audio_dialog_name)

        # Reflect NonHazard
        if re.search(reflect_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Reflect']
            audio_dialog_name = (MediaType.DIALOG, 'reflect_end')
            utterances.append(audio_dialog_name)



        # Light screen NonHazard
        if re.search(light_screen_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Light Screen']
            audio_dialog_name = (MediaType.DIALOG, 'light_screen_start')
            utterances.append(audio_dialog_name)

        # Light screen NonHazard
        if re.search(light_screen_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Light Screen']
            audio_dialog_name = (MediaType.DIALOG, 'light_screen_start')
            utterances.append(audio_dialog_name)

        # Light screen NonHazard
        if re.search(light_screen_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Light Screen']
            audio_dialog_name = (MediaType.DIALOG, 'light_screen_end')
            utterances.append(audio_dialog_name)

        # Light screen NonHazard
        if re.search(light_screen_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Light Screen']
            audio_dialog_name = (MediaType.DIALOG, 'light_screen_end')
            utterances.append(audio_dialog_name)



        # auraviel NonHazard
        if re.search(aurora_veil_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Aurora Veil']
            audio_dialog_name = (MediaType.DIALOG, 'aurora_veil_start')
            utterances.append(audio_dialog_name)

        # auraviel NonHazard
        if re.search(aurora_veil_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Aurora Veil']
            audio_dialog_name = (MediaType.DIALOG, 'aurora_veil_start')
            utterances.append(audio_dialog_name)

        # auraviel NonHazard
        if re.search(aurora_veil_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Aurora Veil']
            audio_dialog_name = (MediaType.DIALOG, 'aurora_veil_end')
            utterances.append(audio_dialog_name)

        # auraviel NonHazard
        if re.search(aurora_veil_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Aurora Veil']
            audio_dialog_name = (MediaType.DIALOG, 'aurora_veil_end')
            utterances.append(audio_dialog_name)



        # Safeguard NonHazard
        if re.search(safeguard_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Safeguard']
            audio_dialog_name = (MediaType.DIALOG, 'safeguard_start')
            utterances.append(audio_dialog_name)

        # Safeguard NonHazard
        if re.search(safeguard_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Safeguard']
            audio_dialog_name = (MediaType.DIALOG, 'safeguard_start')
            utterances.append(audio_dialog_name)

        # Safeguard NonHazard
        if re.search(safeguard_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Safeguard']
            audio_dialog_name = (MediaType.DIALOG, 'safeguard_end')
            utterances.append(audio_dialog_name)

        # Safeguard NonHazard
        if re.search(safeguard_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Safeguard']
            audio_dialog_name = (MediaType.DIALOG, 'safeguard_end')
            utterances.append(audio_dialog_name)



        # Prevents stats reduction   - mist NonHazard
        if re.search(mist_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Mist']
            audio_dialog_name = (MediaType.DIALOG, 'mist_start_start')
            utterances.append(audio_dialog_name)

        # Prevents stats reduction   - mist NonHazard
        if re.search(mist_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Mist']
            audio_dialog_name = (MediaType.DIALOG, 'mist_start_start')
            utterances.append(audio_dialog_name)

        # Prevents stats reduction   - mist NonHazard
        if re.search(mist_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Mist']
            audio_dialog_name = (MediaType.DIALOG, 'mist_start_end')
            utterances.append(audio_dialog_name)

        # Prevents stats reduction   - mist NonHazard
        if re.search(mist_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Mist']
            audio_dialog_name = (MediaType.DIALOG, 'mist_start_end')
            utterances.append(audio_dialog_name)



        # Tail wind NonHazard
        if re.search(tailwind_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Tailwind']
            audio_dialog_name = (MediaType.DIALOG, 'tailwind_player_start')
            utterances.append(audio_dialog_name)

        # Tail wind NonHazard
        if re.search(tailwind_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Tailwind']
            audio_dialog_name = (MediaType.DIALOG, 'tailwind_enemy_start')
            utterances.append(audio_dialog_name)

        # Tail wind NonHazard
        if re.search(tailwind_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Tailwind']
            audio_dialog_name = (MediaType.DIALOG, 'tailwind_player_end')
            utterances.append(audio_dialog_name)

        # Tail wind NonHazard
        if re.search(tailwind_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Tailwind']
            audio_dialog_name = (MediaType.DIALOG, 'tailwind_enemy_end')
            utterances.append(audio_dialog_name)



        # Not in gen 8, prevents criticals NonHazard
        if re.search(lucky_chant_player_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = True
            params = [is_player, 'Lucky Chant']
            audio_dialog_name = (MediaType.DIALOG, 'lucky_chant_player_start')
            utterances.append(audio_dialog_name)

        # Not in gen 8, prevents criticals NonHazard
        if re.search(lucky_chant_enemy_side_start, message):
            message_is_valid = True
            inp_type = SIDE_START
            is_player = False
            params = [is_player, 'Lucky Chant']
            audio_dialog_name = (MediaType.DIALOG, 'lucky_chant_enemy_start')
            utterances.append(audio_dialog_name)

        # Not in gen 8, prevents criticals NonHazard
        if re.search(lucky_chant_player_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = True
            params = [is_player, 'Lucky Chant']
            audio_dialog_name = (MediaType.DIALOG, 'lucky_chant_player_end')
            utterances.append(audio_dialog_name)

        # Not in gen 8, prevents criticals NonHazard
        if re.search(lucky_chant_enemy_side_end, message):
            message_is_valid = True
            inp_type = SIDE_END
            is_player = False
            params = [is_player, 'Lucky Chant']
            audio_dialog_name = (MediaType.DIALOG, 'lucky_chant_enemy_end')
            utterances.append(audio_dialog_name)



        # Water Sport start
        if re.search(water_start_regex, message):
            message_is_valid = True
            inp_type = FIELD_START
            params = ['Water Sport']
            audio_dialog_name = (MediaType.DIALOG, 'water_sport_start')
            utterances.append(audio_dialog_name)

        # Water Sport end
        if re.search(water_end_regex, message):
            message_is_valid = True
            inp_type = FIELD_END
            params = ['Water Sport']
            audio_dialog_name = (MediaType.DIALOG, 'water_sport_end')
            utterances.append(audio_dialog_name)

        # Mud Sport start
        if re.search(mdusport_start_regex, message):
            message_is_valid = True
            inp_type = FIELD_START
            params = ['Mud Sport']
            audio_dialog_name = (MediaType.DIALOG, 'mud_sport_start')
            utterances.append(audio_dialog_name)

        # Mud Sport end
        if re.search(mdusport_end_regex, message):
            message_is_valid = True
            inp_type = FIELD_END
            params = ['Mud Sport']
            audio_dialog_name = (MediaType.DIALOG, 'mud_sport_end')
            utterances.append(audio_dialog_name)

        # Gravity start
        if re.search(gravity_start_regex, message):
            message_is_valid = True
            inp_type = FIELD_START
            params = ['Gravity']
            audio_dialog_name = (MediaType.DIALOG, 'gravity_start')
            utterances.append(audio_dialog_name)

        # Gravity end
        if re.search(gravity_end_regex, message):
            message_is_valid = True
            inp_type = FIELD_END
            params = ['Gravity']
            audio_dialog_name = (MediaType.DIALOG, 'gravity_end')
            utterances.append(audio_dialog_name)

        # Neutralizing Gas start
        if re.search(neutralizing_gas_start, message):
            message_is_valid = True
            inp_type = FIELD_START
            is_player = False
            params = ['Neutralizing Gas']
            audio_dialog_name = (MediaType.DIALOG, 'neutralizing_gas_start')
            utterances.append(audio_dialog_name)

        # Neutralizing Gas end
        if re.search(neutralizing_gas_end, message):
            message_is_valid = True
            inp_type = FIELD_END
            params = ['Neutralizing Gas']
            audio_dialog_name = (MediaType.DIALOG, 'neutralizing_gas_end')
            utterances.append(audio_dialog_name)

        # No Retreat Player start
        if re.search(get_player_no_retreat_start(self.construct_seen_pokemon_regex()), message):
            message_is_valid = True
            inp_type = SINGLE_MOVE
            is_player = True
            params = ['No Retreat']
            audio_dialog_name = (MediaType.DIALOG, 'no_retreat')
            utterances.append(audio_dialog_name)

        # No Retreat Enemy start
        if re.search(get_enemy_no_retreat_start(self.construct_seen_pokemon_regex()), message):
            message_is_valid = True
            inp_type = SINGLE_MOVE
            is_player = False
            params = ['No Retreat']
            audio_dialog_name = (MediaType.DIALOG, 'no_retreat')
            utterances.append(audio_dialog_name)

        # Faint Player start
        if re.search(get_fainted_player_regex(self.construct_seen_pokemon_regex()), message):
            message_is_valid = True
            self.current_focus_player_1 = True
            self.current_focus_pokemon = re.search(self.construct_seen_pokemon_regex(), message).group()
            inp_type = FAINT
            is_player = True
            audio_pkmn_name = (MediaType.POKEMON, self.current_focus_pokemon)
            audio_dialog_name = (MediaType.DIALOG, 'fainted')
            audio_dialog_name_2 = (MediaType.DIALOG, 'oh_no')
            utterances.extend([audio_pkmn_name, audio_dialog_name, audio_dialog_name_2])

        # Faint Enemy start
        if re.search(get_fainted_enemy_regex(self.construct_seen_pokemon_regex()), message):
            message_is_valid = True
            self.current_focus_player_1 = False
            self.current_focus_pokemon = re.search(self.construct_seen_pokemon_regex(), message).group()
            pkmn = re.search(self.construct_seen_pokemon_regex(), message).group()
            inp_type = FAINT
            is_player = False
            audio_pkmn_name = (MediaType.POKEMON, pkmn)
            audio_dialog_name = (MediaType.DIALOG, 'fainted_oh_yea')
            utterances.extends([audio_pkmn_name, audio_dialog_name])


        # perhaps removing exclamation might trigger multiple
        if message_is_valid:# and not (self.last_inp_type == inp_type or self.last_params == params):
            self.last_inp_type = inp_type
            self.last_params = params
            self.process_update(inp_type, params)
            logging.info('new_message: %s' % (message,))

            if len(utterances) > 0:
                self.handle_utterances(utterances)


        return message_is_valid

    def handle_utterances(self, utterances):
        audio_manager.play_audio_local(utterances)

    def process_ability(self, ability, is_player):
        # Ability is broken.
        #choices, lookup true name based on entered nmes #1
        # find proper colorings for extraction - weaker more error prone.
        #Example _p2_ドリユウスフ entered
        # new_ability: ドリユウズ“s Mold Breaker
        return

        pkmn_name = re.search(self.construct_seen_pokemon_regex(), ability).group(0)
        ability = re.search(pokemon_ability_regex, ability).group(0)
        inp_type = ABILITY
        self.process_update(inp_type, [is_player, pkmn_name, ability])

    def is_message_valid(self, message):
        return True

    def is_ability_valid(self, ability):
        return re.search(pokemon_ability_regex, ability)

    def is_next_state_valid(self, new_state):
        pass

    def construct_team_pokemon(self):
        pass


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

    def get_subframe_from_frame(self, rect, source_frame):
        x1, y1, x2, y2 = rect
        crop_img = source_frame[y1:y2, x1:x2]
        return crop_img

    def draw_message_on_frame(self, message):
        return
        y_position = 50 * (self.stats_print_count + 1)
        cv2.putText(self.curr_frame, str(message), (100, y_position), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        self.stats_print_count += 1


    def check_if_nav_action_finished(self, nav_action, state, selectable, submenu, button_action):
        # used to notifiy if we need to wait longer than .2 for next action
        wait = 0.23
        done = False
        #Default A presses to longer
        if button_action ==  BUTTON_ACTION.A_BUTTON:
            wait = 0.37

        if nav_action == NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO:
            if state == BATTLE_STATES.TEAM_MENU:
                self.count_team_pokemon()
                done = True

        if nav_action == NavigationAction.STANDBY_PEEK_TEAM_INFO:
            if state == BATTLE_STATES.TEAM_MENU:
                self.peek_team_pokemon()
                done = True

        if nav_action in [NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO]:
            # Add a wait for opening the menu
            if state in [BATTLE_STATES.TEAM_MENU, BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU]:
#                if button_action ==  BUTTON_ACTION.A_BUTTON or submenu is not None:
                if button_action ==  BUTTON_ACTION.A_BUTTON:
                    wait = 0.67

            pkmn_name = self.current_team_pokemon
            frame = self.curr_frame
            labels_and_boxes = self.labels_and_boxes
            #Pokemon team info page 1
            if state == BATTLE_STATES.POKEMON_SUMMARY_INFO:
                self.analyze_team_pokemon()
                if pkmn_name not in self.player_pokemon:
                    self.player_pokemon[pkmn_name] = {}
                    self.player_pokemon[pkmn_name] = {'position':-1, 'element_1':None, 'element_2':None, 'item':'', 'name':''}

                name_rect = None
                item_rect = None
                element_1_rect = None
                element_2_rect = None

                name_rect = SUMMARY_INFO_SCREEN.NAME.get_name_rect()
                name_rect = self.get_subframe_from_frame(name_rect, frame)

                item_rect = SUMMARY_INFO_SCREEN.ITEM.get_name_rect()
                item_rect = self.get_subframe_from_frame(item_rect, frame)


                if 'active_stat_element' in labels_and_boxes:
                    # selected y1 will have highest height.
                    for rect in labels_and_boxes['active_stat_element']:
                        element_info = ACTIVE_STATS_ELEMENT.get_item_for_rect(rect, BATTLE_STATES.POKEMON_SUMMARY_INFO)
                        if element_info == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1:
                            element_1_rect = element_info.get_name_rect(BATTLE_STATES.POKEMON_SUMMARY_INFO)
                            element_1_rect = self.get_subframe_from_frame(element_1_rect, frame)

                        if element_info == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2:
                            element_2_rect = element_info.get_name_rect(BATTLE_STATES.POKEMON_SUMMARY_INFO)
                            element_2_rect = self.get_subframe_from_frame(element_2_rect, frame)
                            print('found element 2 for %s' % (pkmn_name))
                            logging.info('found element 2 for %s' % (pkmn_name))
                print('starting page 1 extract')
                logging.info('starting page 1 extract')
#                print('element_2_rect')
#                print(element_2_rect)
                future = self.pool.apply_async(self.extract_pokemon_info_page_1, [pkmn_name, name_rect, item_rect, element_1_rect, element_2_rect], callback=self.construct_pokemon_info_page_1)
                self.futures.append(future)
                wait = 0.56
            elif state == BATTLE_STATES.POKEMON_SUMMARY_BASE_STATS:
                print('Starting thread construct_pokemon_info_page_2 with %s' % pkmn_name)

                hp_rect = BASE_STATS_SCREEN.HP.get_rect()
                hp_rect = self.get_subframe_from_frame(hp_rect, frame)

                sp_atk_rect = BASE_STATS_SCREEN.SP_ATK.get_rect()
                sp_atk_rect = self.get_subframe_from_frame(sp_atk_rect, frame)

                atk_rect = BASE_STATS_SCREEN.ATTACK.get_rect()
                atk_rect = self.get_subframe_from_frame(atk_rect, frame)

                sp_def_rect = BASE_STATS_SCREEN.SP_DEF.get_rect()
                sp_def_rect = self.get_subframe_from_frame(sp_def_rect, frame)

                def_rect = BASE_STATS_SCREEN.DEFENSE.get_rect()
                def_rect = self.get_subframe_from_frame(def_rect, frame)

                speed_rect = BASE_STATS_SCREEN.SPEED.get_rect()
                speed_rect = self.get_subframe_from_frame(speed_rect, frame)

                ability_rect = BASE_STATS_SCREEN.ABILITY.get_rect()
                ability_rect = self.get_subframe_from_frame(ability_rect, frame)
                print('gotcha   Starting thread construct_pokemon_info_page_2 with %s' % pkmn_name)

                future = self.pool.apply_async(self.extract_pokemon_info_page_2, [pkmn_name, hp_rect, sp_atk_rect, atk_rect, sp_def_rect, def_rect, speed_rect, ability_rect], callback=self.construct_pokemon_info_page_2)
                self.futures.append(future)
                wait = 0.4

            elif state == BATTLE_STATES.POKEMON_SUMMARY_ATTACKS:
                print('Starting thread construct_pokemon_info_page_3 with %s' % pkmn_name)
                attack_slot_1_rect = None
                attack_slot_2_rect = None
                attack_slot_3_rect = None
                attack_slot_4_rect = None

                for label in self.labels_and_boxes:
                    if label in ['team_pokemon_attack']:
                        for rect in self.labels_and_boxes[label]:
                            attack_slot = ATTACKS_SCREEN.get_item_for_rect(rect)
                            if attack_slot in [ATTACKS_SCREEN.ATTACK_SLOT_1, ATTACKS_SCREEN.ATTACK_SLOT_2, ATTACKS_SCREEN.ATTACK_SLOT_3, ATTACKS_SCREEN.ATTACK_SLOT_4]:
                                name_rect = attack_slot.get_name_rect()
                                pp_rect = attack_slot.get_pp_count_rect()

                                name_rect = self.get_subframe_from_frame(name_rect, frame)
                                pp_rect = self.get_subframe_from_frame(pp_rect, frame)

                                if attack_slot == ATTACKS_SCREEN.ATTACK_SLOT_1:
                                    attack_slot_1_rect = (name_rect, pp_rect)
                                if attack_slot == ATTACKS_SCREEN.ATTACK_SLOT_2:
                                    attack_slot_2_rect = (name_rect, pp_rect)
                                if attack_slot == ATTACKS_SCREEN.ATTACK_SLOT_3:
                                    attack_slot_3_rect = (name_rect, pp_rect)
                                if attack_slot == ATTACKS_SCREEN.ATTACK_SLOT_4:
                                    attack_slot_4_rect = (name_rect, pp_rect)

                future = self.pool.apply_async(self.extract_pokemon_info_page_3, [pkmn_name, attack_slot_1_rect, attack_slot_2_rect, attack_slot_3_rect, attack_slot_4_rect], callback=self.construct_pokemon_info_page_3)
                self.futures.append(future)
                done = True
                wait = 0.43

        if nav_action == NavigationAction.STANDBY_COUNT_ACTIVE_POKEMON:
            if state == BATTLE_STATES.ACTIVE_MENU:
                self.count_active_pokemon()
                done = True

        if nav_action == NavigationAction.STANDBY_CHECK_NEXT_ACTIVE:

            #Pokemon team info page 1
            if state == BATTLE_STATES.ACTIVE_POKEMON_STATS:
                frame = self.curr_frame
                labels_and_boxes = self.labels_and_boxes
                print('Starting thread self.analyze_active_pokemon')

                buffs = []
                debuffs = []
                mod_list = [ACTIVE_STATS_MODIFIER.ATTACK_MODIFIER_ROW, ACTIVE_STATS_MODIFIER.DEFENSE_MODIFIER_ROW, ACTIVE_STATS_MODIFIER.SPECIAL_ATTACK_MODIFIER_ROW,
                     ACTIVE_STATS_MODIFIER.SPECIAL_DEFENSE_MODIFIER_ROW, ACTIVE_STATS_MODIFIER.SPEED_MODIFIER_ROW, ACTIVE_STATS_MODIFIER.ACCURACY_MODIFIER_ROW,
                     ACTIVE_STATS_MODIFIER.EVASIVENESS_MODIFIER_ROW]

                if 'active_stat_buff' in labels_and_boxes:
                    buffs = labels_and_boxes['active_stat_buff']
                if 'active_stat_debuff' in labels_and_boxes:
                    debuffs = labels_and_boxes['active_stat_debuff']

                modifiers = {ACTIVE_STATS_MODIFIER.ATTACK_MODIFIER_ROW:0, ACTIVE_STATS_MODIFIER.DEFENSE_MODIFIER_ROW:0, ACTIVE_STATS_MODIFIER.SPECIAL_ATTACK_MODIFIER_ROW:0,
                             ACTIVE_STATS_MODIFIER.SPECIAL_DEFENSE_MODIFIER_ROW:0, ACTIVE_STATS_MODIFIER.SPEED_MODIFIER_ROW:0, ACTIVE_STATS_MODIFIER.ACCURACY_MODIFIER_ROW:0,
                             ACTIVE_STATS_MODIFIER.EVASIVENESS_MODIFIER_ROW:0 }

                for mod in mod_list:
                    buffs_count = 0
                    for rect in buffs:
                        if mod.buff_in_stat_rect(rect):
                            buffs_count += 1
                    for rect in debuffs:
                        if mod.buff_in_stat_rect(rect):
                            buffs_count -= 1
                    modifiers[mod] = buffs_count

                gender = None
                if 'active_stat_gender_male' in labels_and_boxes:
                    gender = 'Male'
                if 'active_stat_gender_female' in labels_and_boxes:
                    gender = 'Female'


                name_rect = ACTIVE_INFO_NAME_STATUS.NAME.get_name_rect()
                name_rect = self.get_subframe_from_frame(name_rect, frame)

                trainer = None
                trainer_rect = ACTIVE_INFO_NAME_STATUS.TRAINER.get_name_rect()
                trainer_rect = self.get_subframe_from_frame(trainer_rect, frame)

                level = None
                level_rect = ACTIVE_INFO_NAME_STATUS.LEVEL.get_name_rect()
                level_rect = self.get_subframe_from_frame(level_rect, frame)


                status_rect = None
                # Potentially add labels for each status
                if 'active_stats_status' in labels_and_boxes:
                    status_rect = ACTIVE_INFO_NAME_STATUS.STATUS.get_name_rect()
                    status_rect = self.get_subframe_from_frame(status_rect, frame)

                item_name_rect = None
                ability_name_rect = None
                element_1_rect = None
                element_2_rect = None

                field_modifiers_rects = []
                for label in labels_and_boxes:
                    if label == 'active_stat_element':
                        #TODO replace with -psm7 for for a one shot
                        # selected y1 will have highest height.
                        """
                        min_y1 = labels_and_boxes[label][0][1]
                        for rect in labels_and_boxes[label]:
                            min_y1 = min(min_y1, rect[1])
                        """
                        for rect in labels_and_boxes[label]:
                            invert = True
                            element_info = ACTIVE_STATS_ELEMENT.get_item_for_rect(rect, BATTLE_STATES.ACTIVE_POKEMON_STATS)
                            if element_info == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1:
                                element_name_rect = element_info.get_name_rect(BATTLE_STATES.ACTIVE_POKEMON_STATS)
                                element_1_rect = self.get_subframe_from_frame(element_name_rect, frame)

                            if element_info == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2:
                                element_name_rect = element_info.get_name_rect(BATTLE_STATES.ACTIVE_POKEMON_STATS)
                                element_2_rect = self.get_subframe_from_frame(element_name_rect, frame)

                    if label == 'active_stat_information':
                        for rect in labels_and_boxes[label]:
                            stat_info = ACTIVE_STATS_INFORMATION.get_item_for_rect(rect)
                            if stat_info == ACTIVE_STATS_INFORMATION.ITEM:
                                item_name_rect = stat_info.get_name_rect()
                                item_name_rect = self.get_subframe_from_frame(item_name_rect, frame)

                            elif stat_info == ACTIVE_STATS_INFORMATION.ABILITY:
                                ability_name_rect = stat_info.get_name_rect()
                                ability_name_rect = self.get_subframe_from_frame(ability_name_rect, frame)

                            elif stat_info is not None:
                                field_name_rect = stat_info.get_name_rect()
                                field_turn_count_rect = stat_info.get_turn_count_rect()
                                field_name_rect = self.get_subframe_from_frame(field_name_rect, frame)
                                field_turn_count_rect = self.get_subframe_from_frame(field_turn_count_rect, frame)

                                field_modifiers_rects.append((field_name_rect, field_turn_count_rect))

                future = self.pool.apply_async(self.extract_active_pokemon, [modifiers, gender, name_rect, trainer_rect, level_rect, status_rect, element_1_rect, element_2_rect, item_name_rect, ability_name_rect, field_modifiers_rects], callback=self.analyze_active_pokemon)
                self.futures.append(future)
                done = True
                wait = 0.43

        if nav_action == NavigationAction.STANDBY_UPDATE_PP_USAGE:
            if state == BATTLE_STATES.FIGHT_MENU:
#                self.update_pp_usage()
                done = True

        if nav_action == NavigationAction.STANDBY_DYNAMAX_RECORD_MAX_MOVES:
            if state == BATTLE_STATES.FIGHT_MENU:
                self.update_max_moes()
                done = True

        if nav_action == NavigationAction.STANDBY_STRUGGLE:
            if selectable == BATTLE_STATES.FIGHT_MENU and button_action == BUTTON_ACTION.A_BUTTON:
                self.struggle_used()
                done = True

        if nav_action == NavigationAction.STANDBY_ACTIVATE_DYNAMAX:
            if selectable == BATTLE_SELECTABLES.STANDBY_DYNAMAX and button_action == BUTTON_ACTION.A_BUTTON:
                self.activate_dynamax()
                done = True

        if nav_action == NavigationAction.STANDBY_ATTACK_SLOT_1:
            if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1 and button_action == BUTTON_ACTION.A_BUTTON:
#                self.select_attack_1()
                done = True

        if nav_action == NavigationAction.STANDBY_ATTACK_SLOT_2:
            if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2 and button_action == BUTTON_ACTION.A_BUTTON:
#                self.select_attack_2()
                done = True

        if nav_action == NavigationAction.STANDBY_ATTACK_SLOT_3:
            if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3 and button_action == BUTTON_ACTION.A_BUTTON:
#                self.select_attack_3()
                done = True

        if nav_action == NavigationAction.STANDBY_ATTACK_SLOT_4:
            if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4 and button_action == BUTTON_ACTION.A_BUTTON:
#                self.select_attack_4()
                done = True

        if nav_action in [NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]:
            # Add a wait for opening the menu
            if state in [BATTLE_STATES.TEAM_MENU, BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU]:
                if button_action ==  BUTTON_ACTION.A_BUTTON or submenu is not None:
                    wait = 0.67

            if button_action ==  BUTTON_ACTION.A_BUTTON and submenu == BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON:
                self.swapping_pokemon()
                done = True

        return done, wait


    def process_update(self, inp_type, params):
        if 'heal' in inp_type or 'switch' in inp_type or 'move' in inp_type or '-mega' in inp_type:
            pass
        else:
            pass
#                print(inp_type, params)
        print('process_update with:', inp_type, 'and params', params)
        logging.info('process_update with:%s and params:%s' % (inp_type, params))

        # Stale state, for battle state
        # With parralell programming messages can come late.
        # Make sure message box is showing and not on standby state
        if inp_type in [MOVE, SWITCH]:
            if self.sequence not in [SEQUENCE_STATE.BATTLING, SEQUENCE_STATE.AWAITING_SWITCH] and 'message' in self.labels_and_boxes and self.battle_state not in [BATTLE_STATES.STANDBY, BATTLE_STATES.FIGHT_MENU, BATTLE_STATES.ACTIVE_MENU, BATTLE_STATES.ACTIVE_POKEMON_STATS, BATTLE_STATES.TEAM_MENU, BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU, BATTLE_STATES.POKEMON_SUMMARY_INFO]:
                print('Forcing battling sequence')
                logging.info('Forcing battling sequence')
                self.sequence = SEQUENCE_STATE.BATTLING


        message  = ''
        #Used to observe failure for that game while ignoring other games
        self.transcripto.append((inp_type, params))
        if inp_type == MATCH_OVER:
            print('Match Ended Correctly')
            logging.info('Match Ended Correctly')
            self.is_series_done = True
#            continue
        # damage comes in pairs. ignore the second one.
        if inp_type == START and len(params) > 1 and params[1] == DYNAMAX:
            is_player, pkmn, position = self.get_player_pkmn_position()
#inp_type -start
#params ['p2a: Flareon', 'Dynamax']
            pass
        # trick resets choice scarfs
        if inp_type == TRICK:
            self.p1_choice_attack_action = None
        if inp_type == BOOST or inp_type == UNBOOST:
            self.refresh_needs_modifier_update()

        if inp_type == FORME_CHANGE or inp_type == DETAILS_CHANGE:
            self.process_form_update(params)
        if inp_type == START and re.search(perish_song_regex, params[-1]):
            self.update_perish_song(params)
        if inp_type == START and re.search(smack_down_regex, params[-1]):
#'|-start|p1a: Gliscor|Smack Down'
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_smack_down[position] = True
                message = '_p1_%s is smacked_down' % (pkmn,)
            else:
                self.p2_smack_down[position] = True
                message = '_p2_%s is smacked_down' % (pkmn,)
        if inp_type == START and len(params) > 1 and re.search(yawned_used_regex, params[1]) :
#|-start|p2a: Emboar|move: Yawn|[of] p1a: Uxie
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_yawned[position] = True
                message = '_p1_%s is yawned' % (pkmn,)
            else:
                self.p2_yawned[position] = True
                message = '_p2_%s is yawned' % (pkmn,)
        if inp_type == END and len(params) > 1 and re.search(yawned_used_regex, params[1]) :
            # Yawn succeeded. doc target player
#|-end|p2a: Emboar|move: Yawn|[silent]
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_reward -= 5
                message = '_p1_%s is asleep by yawn' % (pkmn,)
            else:
                self.p2_reward -= 5
                message = '_p2_%s is asleep by yawn' % (pkmn,)

    #Level 1 logic, convert each turn. from ints to enums. == 0 Neutral < 1 Resisted > 1 Super
    #Level 2 logic, decrease if player hurts ally regardless  -  ignore for now until doubles data is collected.
#        self.p1_effective = {'a':0, 'b':0, 'c':0}
#        self.p2_effective = {'a':0, 'b':0, 'c':0}
        if inp_type == RESISTED:
            #opposite
#inp_type -resisted
#params ['p1a: Scrafty']
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_effective[position] += 1
                self.p1_reward += 1
                self.p2_reward -= 1
                message = '_p1_%s resisted' % (pkmn,)
            else:
                self.p2_effective[position] += 1
                self.p2_reward += 1
                self.p1_reward -= 1
                message = '_p2_%s resisted' % (pkmn,)
        if inp_type == SUPER_EFFECTIVE:
            # resist -1, super +1, immune -2
            # hurt ally logic should be in damage -2
#|-supereffective|p2a: Tangrowth
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_effective[position] += -1
                self.p1_reward -= 1
                self.p2_reward += 1
            else:
                self.p2_effective[position] += -1
                self.p2_reward -= 1
                self.p1_reward += 1
            message = 'attack was super effective'
        if inp_type == IMMUNE:
            # resist -1, super +1, immune -2
            # hurt ally logic should be in damage -2
#|-immune|p2a: Landorus
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_effective[position] += 2
                self.p1_reward += 2
                self.p2_reward -= 2
                message = 'doesnt affect _p1_%s' % (pkmn,)
            else:
                self.p2_effective[position] += 2
                self.p2_reward += 2
                self.p1_reward -= 2
                message = 'doesnt affect _p2_%s' % (pkmn,)
        if inp_type == START and len(params) > 0 and params[1] == 'confusion':
#|-start|p1a: Dragonite|confusion|[fatigue]
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_active_pokemon_stats[position].confused = True
                self.p1_reward -= 2
                message = '_p1_%s is confused' % (pkmn,)
            else:
                self.p2_active_pokemon_stats[position].confused = True
                self.p2_reward -= 2
                message = '_p2_%s is confused' % (pkmn,)
        if inp_type == END and len(params) > 0 and params[1] == 'confusion':
#|-end|p1a: Dragonite|confusion|
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_active_pokemon_stats[position].confused = False
                self.p1_reward += 2
                message = '_p1_%s confusion ended' % (pkmn,)
            else:
                self.p2_active_pokemon_stats[position].confused = False
                self.p2_reward += 2
                message = '_p2_%s confusion ended' % (pkmn,)
        if inp_type == END_ITEM and len(params) > 2 and re.search(item_removed_by_knock_off_regex, params[2]):
#|-enditem|p1a: Darmanitan|Life Orb|[from] move: Knock Off|[of] p2a: Meloetta
#inp_type -enditem
#params ['p2a: Regice', 'Weakness Policy', '[from] move: Knock Off', '[of] p1a: Furret']
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_reward -= 2
                self.p2_reward += 2
                message = '_p1_%s item knocked off' % (pkmn,)
            else:
                self.p2_reward -= 2
                self.p1_reward += 2
                message = '_p2_%s item knocked off' % (pkmn,)
            no_item = 'noitem'
            self.update_item(pkmn, no_item, is_player)
        elif inp_type == END_ITEM:
#|-enditem|p1a: Magcargo|White Herb
#inp_type -enditem
#params ['p2a: Stakataka', 'Air Balloon']

            is_player, pkmn, position = self.get_player_pkmn_position()
            no_item = 'noitem'
            message = '_p1_%s used item' % (pkmn,)
            if not is_player:
                message = '_p2_%s used item' % (pkmn,)
            self.update_item(pkmn, no_item, is_player)
        if inp_type == ITEM:
#|-item|p2a: Solgaleo|Choice Band|[from] move: Switcheroo
            is_player, pkmn, position = self.get_player_pkmn_position()
            new_item = params[1]
            message = '_p1_%s has item %s' % (pkmn,new_item)
            if not is_player:
                message = '_p2_%s has item %s' % (pkmn,new_item)
            self.update_item(pkmn, new_item, is_player)
        if inp_type == ITEM and re.search(item_frisked_regex, params[2]):
#|-item|p1a: Swalot|Black Sludge|[from] ability: Frisk|[of] p2a: Exeggutor|[identify]
#|-item|p1a: Sableye|Sablenite|[from] ability: Frisk|[of] p2a: Exeggutor|[identify]
#|-item|p1a: Weavile|Assault Vest|[from] ability: Pickpocket|[of] p2a: Lurantis
            item = params[1]
            item_player_pokemon = params[0]
            it_play, it_pkmn, _  = self.get_player_pkmn_position(item_player_pokemon)

            ability_player_pokemon = params[3]
            ab_play, ab_pkmn, _  = self.get_player_pkmn_position(ability_player_pokemon)

            seen_ability = params[2].replace('[from] ability: ','')
            message = '_p1_%s identified %s %s' % (ab_pkmn,it_pkmn,item)
            if not it_play:
                message = '_p2_%s identified %s %s' % (ab_pkmn,it_pkmn,item)

            self.update_item(it_pkmn, item, it_play)
            self.update_seen_ability(ab_play, ab_pkmn, seen_ability)
        if inp_type in move_did_not_succeed or (inp_type == '-damage' and re.search('\[from\] confusion', params[-1])):
#|-fail|p1a: Zapdos
#|cant|p1a: Lanturn|flinch
#|-miss|p1a: Victreebel|p2a: Malamar
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_move_succeeded[position] = False
                self.p1_reward -= 2
            message = 'Move failed'

        if inp_type == ACTIVATE and re.search(sticky_web_activated_regex, params[-1]):
#|-activate|p2a: Venomoth|move: Sticky Web
#|-unboost|p2a: Venomoth|spe|1
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_reward -= 5
                self.p2_reward += 5
                message = '_p1_%s slowed down' % (pkmn,)
            else:
                self.p1_reward += 5
                self.p2_reward -= 5
                message = '_p2_%s slowed down' % (pkmn,)
# Damage dealt by opponent hazards/items/abilities
        if inp_type == HAZARD_DAMAGE and (re.search(spike_damage_regex, params[-1]) or re.search( stealthrock_damage_regex, params[-1]) or re.search(opponent_ability_damage_regex, params[-1]) or re.search(item_damage_from_opponent_regex, params[-1])) :
#  ['p2a: Lanturn', '151/339'],
#  ['p1a: Glalie', '23/100'],
#  ['p2a: Sableye', '162/216', '[from] Spikes'],
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_reward -= 5
                self.p2_reward += 5
                message = '_p1_%s hurt by spikes' % (pkmn,)
            else:
                self.p1_reward += 5
                self.p2_reward -= 5
                message = '_p2_%s hurt by spikes' % (pkmn,)
# Damage dealt by own item like life orb
#inp_type -damage
#params ['p2a: Scolipede', '207/230', '[from] item: Life Orb']
        elif inp_type == DAMAGE and re.search(item_damage_regex, params[-1])  :
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_reward -= 2
                message = '_p1_%s hurt by item' % (pkmn,)
            else:
                self.p1_reward += 2
                message = '_p2_%s hurt by item' % (pkmn,)
# Generic damage
        elif inp_type == DAMAGE:
            is_player, pkmn, position = self.get_player_pkmn_position()
#  ['p1a: Kartana', '75/100'],
#  ['p2a: Sawk', '0 fnt'],
            if is_player:
                self.p1_reward -= 3
                message = '_p1_%s hurt by attack' % (pkmn,)
            else:
                self.p1_reward += 3
                message = '_p2_%s hurt by attack' % (pkmn,)
        if inp_type == WEATHER and re.search(weather_start, params[0])  :
#inp_type -weather
#params ['DesolateLand', '[upkeep]']
            new_weather = params[0]
            if self.weather_condition == new_weather:
                self.weather_turns += 1
            else:
                self.weather_turns = 1
            self.weather_condition = new_weather
            message = 'weather is %s' % (new_weather,)
        elif inp_type == WEATHER and re.search(weather_end, params[0]):
            #|-weather|RainDance|[upkeep]
            self.weather_turns = 0
            self.weather_condition = 'none'
            message = 'weather ended'
        if inp_type == FIELD_START and re.search(terrain_start, params[0])  :
#terrain upkeep
            new_terrain = params[0]
            if 'Grassy Terrain' in new_terrain:
                self.terrain_condition = 'Grassy Terrain'
            if 'Misty Terrain' in new_terrain:
                self.terrain_condition = 'Misty Terrain'
            if 'Electric Terrain' in new_terrain:
                self.terrain_condition = 'Electric Terrain'
            if 'Psychic Terrain' in new_terrain:
                self.terrain_condition = 'Psychic Terrain'
            message = 'terrain is %s' % (new_terrain,)
        if inp_type == FIELD_END and re.search(terrain_end, params[0]):
            #|-fieldstart|move: Grassy Terrain|
            self.terrain_condition = 'none'
            message = 'terrain ended'
        if inp_type == ROOM and re.search(room_regex, params[0])  :
#trick room/magic room
#inp_type -fieldstart
#params ['move: Trick Room', '[of] p1a: Reuniclus']
            new_room = params[0]
            if 'Trick Room' in new_room:
                self.current_room = 'Trick Room'
            if 'Magic Room' in new_room:
                self.current_room = 'Magic Room'
            if 'Wonder Room' in new_room:
                self.current_room = 'Wonder Room'
            message = 'Room is %s' % (new_room,)
        if inp_type == ROOM and re.search(room_regex, params[0]):
#|-fieldstart|move: Grassy Terrain|
#inp_type -fieldend
#params ['move: Trick Room']
            self.current_room = 'none'
            message = 'room ended'
        if inp_type == SIDE_END and params[0] in HAZARDS  :
#sideend hazards
#inp_type -sideend
#params ['p2: coolcatuser', 'Stealth Rock', '[from] move: Defog', '[of] p1a: Skarmory']
            #p1/p2

            player = params[0].split(': ')[0]
            hazard = params[1]

            if self.player_id in player:
                self.p1_reward += 10
                message = '_p1_player lost %s' % (hazard,)
            else:
                self.p2_reward += 10
                message = '_p2_player lost %s' % (hazard,)
            if hazard == 'Sticky Web':
                if self.player_id in player:
                    self.p1_has_web = False
                else:
                    self.p2_has_web = False
            if hazard == 'Stealth Rock':
                if self.player_id in player:
                    self.p1_has_rocks = False
                else:
                    self.p2_has_rocks = False
            if hazard == 'Spikes':
                if self.player_id in player:
                    self.p1_spikes = 0
                else:
                    self.p2_spikes = 0
            # Toxic spikes formatted differently
            if 'Toxic Spikes' in hazard:
                if self.player_id in player:
                    self.p1_toxic_spikes = 0
                else:
                    self.p2_toxic_spikes = 0
        if inp_type == SIDE_END and params[0] in NON_HAZARDS  :
#sideend non hazards
#inp_type -sideend
#params ['p2: coolcatuser', 'move: Aurora Veil']
            #p1/p2
            player = params[0].split(': ')[0]
            non_hazard = params[1]

            if self.player_id in player:
                self.p1_reward += -3
                message = '_p1_player lost %s' % (non_hazard,)
            else:
                self.p2_reward += -3
                message = '_p2_player lost %s' % (non_hazard,)
            if 'Safeguard' in non_hazard:
                if self.player_id in player:
                    self.p1_safeguard = False
                else:
                    self.p2_safeguard = False
            if 'Light Screen' in non_hazard:
                if self.player_id in player:
                    self.p1_lightscreen = False
                else:
                    self.p2_lightscreen = False
            if 'Reflect' in non_hazard:
                if self.player_id in player:
                    self.p1_reflect = False
                else:
                    self.p2_reflect = False
            if 'Tailwind' in non_hazard:
                if self.player_id in player:
                    self.p1_tailwind = False
                else:
                    self.p2_tailwind = False
            if 'Aurora Veil' in non_hazard:
                if self.player_id in player:
                    self.p1_aurora_veil = False
                else:
                    self.p2_aurora_veil = False

        if inp_type == SIDE_START and (params[0] in NON_HAZARDS or params[0] in HAZARDS) :
#sidestart  hazards and blizards
#inp_type -sidestart
#params ['p2: coolcatuser', 'move: Stealth Rock']
#inp_type move
#params ['p1a: Wigglytuff', 'Reflect', 'p1a: Wigglytuff']
            player = params[0].split(': ')[0]
            move = params[1]
            #p1/p2
            # make negative if hazard
            hzard_shield_reward = 10

            if 'Safeguard' in move:
                if self.player_id in player:
                    self.p1_safeguard = True
                else:
                    self.p2_safeguard = True
            if 'Light Screen' in move:
                if self.player_id in player:
                    self.p1_lightscreen = True
                else:
                    self.p2_lightscreen = True
            if 'Reflect' in move:
                if self.player_id in player:
                    self.p1_reflect = True
                else:
                    self.p2_reflect = True
            if 'Tailwind' in move:
                if self.player_id in player:
                    self.p1_tailwind = True
                else:
                    self.p2_tailwind = True
            if 'Aurora Veil' in move:
                if self.player_id in player:
                    self.p1_aurora_veil = True
                else:
                    self.p2_aurora_veil = True
            if 'Sticky Web' in move:
                hzard_shield_reward = -10
                if self.player_id in player:
                    self.p1_has_web = True
                else:
                    self.p2_has_web = True
            if 'Stealth Rock' in move:
                hzard_shield_reward = -10
                if self.player_id in player:
                    self.p1_has_rocks = True
                else:
                    self.p2_has_rocks = True
            if 'Spikes' in move and 'Toxic Spikes' not in move:
                hzard_shield_reward = -10
                if self.player_id in player:
                    self.p1_spikes += 1
                else:
                    self.p2_spikes += 1
            # Toxic spikes formatted differently
            if 'Toxic Spikes' in move:
                hzard_shield_reward = -10
                if self.player_id in player:
                    self.p1_toxic_spikes += 1
                else:
                    self.p2_toxic_spikes += 1
            if self.player_id in player:
                self.p1_reward += hzard_shield_reward
                message = '_p1_player has %s' % (move,)
            else:
                self.p2_reward += hzard_shield_reward
                message = '_p2_player has %s' % (move,)


        if inp_type == SINGLE_MOVE and params[0] == destiny_bond_regex:
#|-singlemove|p1a: Sharpedo|Destiny Bond
#inp_type -singlemove
#params ['p1a: Delibird', 'Destiny Bond']
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_destined[position] = True
                self.p1_reward += 2
                message = '_p1_%s trying to take down with it' % (pkmn,)
            else:
                self.p2_destined[position] = True
                self.p2_reward += 2
                message = '_p2_%s trying to take down with it' % ( pkmn,)
        if inp_type == HEAL:
#|-heal|p2a: Venusaur|31/100|[from] drain|[of] p1a: Flygon
#inp_type -heal
#params ['p1a: Delibird', '95/100', '[from] item: Leftovers']
#inp_type -heal
#params ['p1a: Scrafty', '72/100', '[from] drain', '[of] p2a: Carracosta']
            is_player, pkmn = params
            if is_player:
                self.p1_reward += 2
                message = '_p1_%s healed a little' % (pkmn,)
            else:
                self.p2_reward += 2
                message = '_p2_%s healed a little' % (pkmn,)
        # Currently painsplit?
        if inp_type == SET_HP :
#|-sethp|p2a: Mismagius|77/100|[from] move: Pain Split
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_reward += 2
                message = '_p1_%s shared the pain' % (pkmn,)
            else:
                self.p2_reward += 2
                message = '_p2_%s shared the pain' % (pkmn,)
# General Reveal of ability
        if inp_type == ABILITY:
#|-ability|p2a: Gardevoir|Water Absorb|[from] ability: Trace|[of] p1a: Jellicent
#  ['p1a: Qwilfish', 'Intimidate', 'boost'],
#  ['p2a: Scolipede', 'Speed Boost', 'boost'],
#  ['p1a: Scrafty', 'Moxie', 'boost'],
            is_player, pkmn, position = self.get_player_pkmn_position()
            ability = params[1]
            self.update_seen_ability(is_player, pkmn, ability)
            if is_player:
                message = '_p1_%s has ability %s' % (pkmn, ability)
            else:
                message = '_p2_%s has ability %s' % (pkmn, ability)
# Does trace need special logic? maybe not. TODO
        """
        if inp_type == ABILITY and len(params) > 2 and re.search(trace_regex, params[2]) :
#|-ability|p2a: Gardevoir|Water Absorb|[from] ability: Trace|[of] p1a: Jellicent
            is_player, pkmn, position = self.get_player_pkmn_position()
            ability = params[1]
            target_player, target_pkmn, _ = self.get_player_pkmn_position(params[-1])
            self.update_seen_ability(is_player, pkmn, ability)
            self.update_seen_ability(target_player, target_pkmn, ability)
            if is_player:
                message = '_p1_%s traced %s' % (pkmn, ability)
            else:
                message = '_p2_%s traced %s' % (pkmn, ability)
            """
        if inp_type == CLEAR_ALL_BOOST :
#|-clearallboost
            self.p1_active_pokemon_stats['a'].clear_all_boosts()
            self.p1_active_pokemon_stats['b'].clear_all_boosts()
            self.p1_active_pokemon_stats['c'].clear_all_boosts()
            self.p2_active_pokemon_stats['a'].clear_all_boosts()
            self.p2_active_pokemon_stats['b'].clear_all_boosts()
            self.p2_active_pokemon_stats['c'].clear_all_boosts()
            message = 'All stats cleared'
        if inp_type == CLEAR_NEGATIVE_BOOST :
# '-clearnegativeboost': [['p1a: Carracosta', '[silent]'],
#  ['p1a: Minior', '[silent]'],
#  ['p1a: Gorebyss', '[silent]']],
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_active_pokemon_stats[position].clear_neg_boosts()
                message = '_p1_%s negative stats cleared' % (pkmn, )
            else:
                self.p2_active_pokemon_stats[position].clear_neg_boosts()
                message = '_p2_%s negative stats cleared' % (pkmn, )
        if inp_type == CLEAR_BOOST:
#|-clearboost|p2a: Zeraora
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                message = '_p1_%s boosts cleared' % (pkmn, )
                self.p1_active_pokemon_stats[position].clear_all_boosts()
            else:
                self.p2_active_pokemon_stats[position].clear_all_boosts()
                message = '_p2_%s boosts cleared' % (pkmn, )
# Punish all statuses equally. even if self inflicted like poison heal with toxic orb.
        if inp_type == STATUS:
#|-status|p1a: Carracosta|psn
#  ['p2a: Pikachu', 'tox'],
            is_player, pkmn, position = self.get_player_pkmn_position()
#                status = output.split('|')[-3]
            status = 'statused'
#                status = params[1]
            if is_player:
                self.p1_reward -= 5
                message = '_p1_%s is %s' % (pkmn, status)
            else:
                self.p2_reward -= 5
                message = '_p2_%s is %s' % (pkmn, status)
        if inp_type == CURE_STATUS:
#|-curestatus|p2a: Spiritomb|slp|[msg]
            is_player, pkmn, position = self.get_player_pkmn_position()
            status = params[1]
            if is_player:
                self.p1_reward += 5
                message = '_p1_%s is cured of %s' % (pkmn, status)
            else:
                self.p2_reward += 5
                message = '_p2_%s is cured of %s' % (pkmn, status)
        # lazy regex, make sure Frisk doesnt exist
# Weather triggered from ability.
        if inp_type == START and re.search(start_substitute_regex, params[1]):
#|-start|p2a: Cresselia|Substitute
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_active_pokemon_stats[position].substitute = True
                message = '_p1_%s used substitute' % (pkmn, )
            else:
                self.p2_active_pokemon_stats[position].substitute = True
                message = '_p2_%s used substitute' % (pkmn, )
        if inp_type == START and re.search(end_substitute_regex, params[1]):
#|-end|p2a: Serperior|Substitute
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_active_pokemon_stats[position].substitute = False
                message = '_p1_%s substitute broken' % (pkmn, )
            else:
                self.p2_active_pokemon_stats[position].substitute = False
                message = '_p2_%s substitute broken' % (pkmn, )
        if inp_type == CRIT:
#|-crit|p2a: Ambipom
#  ['p2a: Ninetales'],
#  ['p2a: Marshadow'],
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_reward -= 5
            else:
                self.p2_reward -= 5
            message = 'Critical hit!'
        if inp_type == SWITCH or inp_type == DRAG:
#|switch|p2a: Zygarde|Zygarde, L78|75/100|[from]move: U-turn
#  ['p2a: Tentacruel', 'Tentacruel, L82, F', '265/265'],
#  ['p2a: Ditto', 'Ditto, L89', '230/230'],
#  ['p2a: Tentacruel', 'Tentacruel, L82, F', '265/265'],
#  ['p2a: Pheromosa', 'Pheromosa, L78', '48/239'],
            print('trying to switch')
            is_player, pkmn, position = self.get_player_pkmn_position()
            self.handle_switch(is_player, pkmn, position)
            if is_player:
                message = '_p1_%s entered' % (pkmn, )
            else:
                message = '_p2_%s entered' % (pkmn, )
        if inp_type == SWITCHOUT:
#|switch|p2a: Zygarde|Zygarde, L78|75/100|[from]move: U-turn
#  ['p2a: Tentacruel', 'Tentacruel, L82, F', '265/265'],
#  ['p2a: Ditto', 'Ditto, L89', '230/230'],
#  ['p2a: Tentacruel', 'Tentacruel, L82, F', '265/265'],
#  ['p2a: Pheromosa', 'Pheromosa, L78', '48/239'],
            print('switching out')
            is_player, pkmn, position = self.get_player_pkmn_position()
            self.handle_switch_out(is_player, pkmn, position)
        if inp_type == MOVE:
#|move|p2a: Garchomp|Outrage|p1a: Ninetales|[from]lockedmove
#  ['p1a: Kartana', 'Leaf Blade', 'p2a: Furfrou'],
#  ['p1a: Kartana', 'Leaf Blade', 'p2a: Alakazam'],
#  ['p2a: Ferrothorn', 'Protect', 'p2a: Ferrothorn'],
            is_player, pkmn, position = self.get_player_pkmn_position()
            atk_name = params[0]
            self.update_seen_moves(is_player, pkmn, atk_name)
            if is_player:
                message = '_p1_%s used %s' % (pkmn, atk_name)
                self.p1_seen_attacks[position] = atk_name
            else:
                message = '_p2_%s used %s' % (pkmn, atk_name)
                self.p2_seen_attacks[position] = atk_name

        if inp_type == FAINT:
#|faint|p1a: Hawlucha
#  ['p2a: Articuno'],

            is_player, pkmn, position = self.get_player_pkmn_position()
            self.handle_switch_out(is_player, pkmn, position)
            self.handle_faint(is_player, pkmn)
            if is_player:
                self.p1_reward -= 35
                self.p2_reward += 35
#                    self.p1_selected[position] = None
#                    self.p1_must_switch[positions[idx]] = switch
#                    self.p1_open_request[positions[idx]] = True
                message = '_p1_%s fainted' % (pkmn, )
            else:
                self.p2_reward -= 35
                self.p1_reward += 35
#                    self.p2_selected[position] = None
#                    self.p2_must_switch[positions[idx]] = switch
#                    self.p2_open_request[positions[idx]] = True
                message = '_p2_%s fainted' % (pkmn, )
        # u turn stuff
        if inp_type == MUST_SWITCH:
#|faint|p1a: Hawlucha
#  ['p2a: Articuno'],
            is_player, pkmn, position = self.get_player_pkmn_position()
            self.switch_from_uturn_volt_switch_initiated()
            message = '_p1_%s pokemon returned' % (pkmn, )
        if inp_type == END and re.search(zoroark_end_illusion_regex, params[1]):
#|-end|p2a: Zoroark|Illusion
# '-end': [['p1a: Gorebyss', 'Substitute']],

            #reward goes to oppposite player
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p2_reward += 15
                message = '_p1_%s illusion ended' % (pkmn, )
            else:
                self.p1_reward += 15
                message = '_p2_%s illusion ended' % (pkmn, )
            self.update_seen_pokemon(is_player, pkmn)
        if inp_type == REPLACE:
#|replace|p2a: Zoroark|Zoroark, L80, F
# 'replace': ['p1a: Gorebyss', 'Substitute'],
            is_player, pkmn, position = self.get_player_pkmn_position()
            self.update_seen_pokemon(is_player, pkmn)
        if inp_type == ZPOWER:
#|-zpower|p1a: Charizard
            is_player, pkmn, position = self.get_player_pkmn_position()
            if is_player:
                self.p1_used_zmove = True
                message = '_p1_%s used zmove' % (pkmn, )
            else:
                self.p2_used_zmove = True
                message = '_p2_%s used zmove' % (pkmn, )
        if inp_type == MEGA:
#|-mega|p1a: Alakazam|Alakazam|Alakazite
            is_player, pkmn, position = self.get_player_pkmn_position()
            new_item = params[-1]
            if is_player:
                self.p1_used_mega = True
                message = '_p1_%s used mega' % (pkmn, )
            else:
                self.p2_used_mega = True
                message = '_p2_%s used mega' % (pkmn, )
            self.update_item(pkmn, new_item, is_player)
        self.append_to_transcript(message)
        print(message)
        self.draw_message_on_frame('Processed message: ' + message)

    def get_player_pkmn_position(self):
        if self.current_focus_player_1:
            pkmn_position = 'a'
            if self.p1_selected['b'] == self.current_focus_pokemon:
                pkmn_position = 'b'
        else:
            pkmn_position = 'a'
            if self.p2_selected['b'] == self.current_focus_pokemon:
                pkmn_position = 'b'

        return (self.current_focus_player_1), self.current_focus_pokemon, pkmn_position

    def update_player_pokemon_health(self, pkmn_name, health_ratio):
        self.update_seen_pokemon(True, pkmn_name)
        seen_details = self.p1_seen_details
        seen_details[pkmn_name]['health'] = health_ratio
        seen_details[pkmn_name]['last_health'] = health_ratio
        if seen_details[pkmn_name]['health'] == 0:
            seen_details[pkmn_name]['status'] = Status.FAINTED


    # Call upon switchin/every turn when getting active moves
    def fetch_seen_pokemon(self, is_player, pkmn_name):
        self.update_seen_pokemon(is_player, pkmn_name)
        seen_details = self.p1_seen_details
        if not is_player:
            seen_details = self.p2_seen_details
        return seen_details[pkmn_name]

    def update_seen_pokemon_with_active(self, active_stats, is_player_1):
        selected = self.p1_selected['a']
        if not is_player_1:
            selected = self.p2_selected['a']

        # Maybe missed messages for send out. abandon if None
        if selected == None:
            print('Selected Poke is Noone, cant update_seen_pokemon_with_active')
            return

        print('update_seen_pokemon_with_active called with', active_stats['name'])
        print('update_seen_pokemon_with_active called with true current pokemon as', selected)
        print('update_seen_pokemon_with_active called as player_1', selected)
        seen_details = self.fetch_seen_pokemon(is_player_1, selected)

        # dont update name, could be incorrect
        if active_stats['ability'] is not None:
            seen_details['ability'] = active_stats['ability']
        if active_stats['item'] is not None:
            seen_details['item'] = active_stats['item']
        if active_stats['element_1'] is not None:
            seen_details['element_1'] = active_stats['element_1']
        if active_stats['element_2'] is not None:
            seen_details['element_2'] = active_stats['element_2']
        if active_stats['gender'] is not None:
            seen_details['gender'] = active_stats['gender']
        if active_stats['status'] is not None:
            seen_details['status'] = active_stats['status']

        # Apply field modifiers

        self.active_stats = active_stats
        if is_player_1:
            self.player_active_pokemon_set[selected] = active_stats
        else:
            self.enemy_active_pokemon_set[selected] = active_stats

        print('applied active seed pokemon')
        print(seen_details)

    # Call upon switchin/every turn when getting active moves
    def update_seen_pokemon(self, is_player, pkmn_name, gender='', level=80):
        if pkmn_name is None:
            return
        revealed_pokemon_names.add(pkmn_name)
        print('update_seen_pokemon called with', pkmn_name)
        print('update_seen_pokemon revealed_pokemon_names', revealed_pokemon_names)
        seen_attacks = self.p1_seen_details
        if not is_player:
            seen_attacks = self.p2_seen_details
        if pkmn_name not in seen_attacks:
            seen_attacks[pkmn_name] = {}
            seen_attacks[pkmn_name]['attacks'] = {}
            seen_attacks[pkmn_name]['form'] = pkmn_name
            seen_attacks[pkmn_name]['item'] = 'hidden_item'
            seen_attacks[pkmn_name]['gender'] = ''
            seen_attacks[pkmn_name]['health'] = 1
            seen_attacks[pkmn_name]['last_health'] = 1
            seen_attacks[pkmn_name]['status'] = Status.NOTHING
            seen_attacks[pkmn_name]['level'] = 80
            seen_attacks[pkmn_name]['element_1'] = None
            seen_attacks[pkmn_name]['element_2'] = None
            seen_attacks[pkmn_name]['ability'] = 'hidden_ability'
        print('seen pokemon: ', seen_attacks)

    def update_seen_ability(self, is_player, pkmn_name, ability):
        seen_details = self.fetch_seen_pokemon(is_player, pkmn_name)
        seen_details['ability'] = ability


    def update_seen_moves(self, is_player, pkmn_name, atk_name, override_pp=None):
        seen_details = self.fetch_seen_pokemon(is_player, pkmn_name)
        pkmn_attacks = {}
        atk_count = 0
        pkmn_attacks = seen_details['attacks']

        if atk_name in pkmn_attacks:
            atk_count = pkmn_attacks[atk_name]

        atk_count += 1
        if override_pp is not None:
            pkmn_attacks[atk_name] = override_pp
        else:
            pkmn_attacks[atk_name] = atk_count
        print('self.p1_seen_details:', self.p1_seen_details)
        print('self.p2_seen_details:', self.p2_seen_details)
        seen_details['attacks'] = pkmn_attacks
        revealed_attack_names.add(atk_name)



    def reset_active_fighters_list(self):
        self.player_active_pokemon_set = {}
        self.enemy_active_pokemon_set = {}

    def update_team_order(self):
        starting_position = BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1.value
        for index in range(self.team_size):
            # team_member first one is bolded/selected
            team_position = BATTLE_SELECTABLES(starting_position + index)
            invert = team_member == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1
            name_rect = team_member.get_name_rect()
            name = process_image_for_text(self.get_subframe(name_rect), invert)
            self.player_pokemon[team_name]['position'] = index

    def mark_for_state(self, state):

        if state == BATTLE_STATES.TEAM_MENU:
            self.count_team_pokemon()
            messages_to_draw = []
            for label in self.labels_and_boxes:
                if label in ['team_pokemon', 'team_pokemon_selected']:
                    invert = label == 'team_pokemon_selected'
                    for rect in self.labels_and_boxes[label]:
                        team_member = BATTLE_SELECTABLES.get_item_for_rect(state, rect)
                        name_rect = team_member.get_name_rect()
                        health_rect = team_member.get_life_rect()
                        name = process_image_for_text(self.get_subframe(name_rect), invert)
                        health_as_string = process_image_for_text(self.get_subframe(health_rect), invert)
                        health_ratio = 0
                        try:
                            max_health, curr_health =  health_as_string.split('/')
                            health_ratio = int(curr_health) / float(max_health)
                        except:
                            pass
                        message = '%s: health: %.2f' % (name, health_ratio)
                        messages_to_draw.append(message)
#            for message in messages_to_draw:
#                self.draw_message_on_frame(message)



        #Pokemon team info page 1
        if state == BATTLE_STATES.POKEMON_SUMMARY_INFO:
            self.analyze_team_pokemon()
            self.construct_pokemon_info_page_1()
#            page_1_info_message = 'name: %s, item: %s' % (self.page_1_info['name'], self.page_1_info['item'])
#            self.draw_message_on_frame(page_1_info_message)

        elif state == BATTLE_STATES.POKEMON_SUMMARY_BASE_STATS:
            self.construct_pokemon_info_page_2()
#            page_2_info_message = 'hp: %s, sp_atk: %s, atk: %s, sp_def: %s, defense: %s, speed: %s, ability: %s, ' % (self.page_2_info['hp'], self.page_2_info['sp_atk'], self.page_2_info['atk'], self.page_2_info['sp_def'], self.page_2_info['defense'], self.page_2_info['speed'], self.page_2_info['ability'], )
#            self.draw_message_on_frame(page_2_info_message)

        elif state == BATTLE_STATES.POKEMON_SUMMARY_ATTACKS:
            self.construct_pokemon_info_page_3()
#            attacks_message = 'attacks: %s' % str(self.page_3_info['attacks'])
#            self.draw_message_on_frame(attacks_message)

        if state == BATTLE_STATES.ACTIVE_MENU:
            self.count_active_pokemon()
            active_message = 'active pokemon: %d' % (self.active_pokemon_count)
            self.draw_message_on_frame(active_message)

        if state == BATTLE_STATES.ACTIVE_POKEMON_STATS:
            self.analyze_active_pokemon()
            """
            message = 'modifiers: %s' % str(self.active_stats['modifiers'])
            self.draw_message_on_frame(message)
            message = 'ability: %s' % str(self.active_stats['ability'])
            self.draw_message_on_frame(message)
            message = 'item: %s' % str(self.active_stats['item'])
            self.draw_message_on_frame(message)
            message = 'field_modifiers: %s' % str(self.active_stats['field_modifiers'])
            self.draw_message_on_frame(message)
            message = 'element_1: %s' % str(self.active_stats['element_1'])
            self.draw_message_on_frame(message)
            message = 'element_2: %s' % str(self.active_stats['element_2'])
            self.draw_message_on_frame(message)
            message = 'gender: %s' % str(self.active_stats['gender'])
            self.draw_message_on_frame(message)
            message = 'status: %s' % str(self.active_stats['status'])
            self.draw_message_on_frame(message)
            message = 'name: %s' % str(self.active_stats['name'])
            self.draw_message_on_frame(message)
            message = 'trainer: %s' % str(self.active_stats['trainer'])
            self.draw_message_on_frame(message)
            message = 'level: %s' % str(self.active_stats['level'])
            self.draw_message_on_frame(message)
            print(str(self.active_stats['modifiers']))
            """
        if state == BATTLE_STATES.FIGHT_MENU:
            self.update_pp_usage()
            self.draw_message_on_frame (str(self.packaged_attacks))

        if state == BATTLE_STATES.STANDBY:
            self.update_active_popkemon_health()

    def update_active_popkemon_health(self):
        print('updating active pokemon health')
        player_health = self.player_last_health_sequence['a']
        enemy_health  = self.enemy_last_health_sequence['a']
#        player_active_name = ''
#        enemy_active_name  = ''
        if 'active' in self.labels_and_boxes:
            for rect in self.labels_and_boxes['active']:
                active_item = BATTLE_ACTIVE_POKEMON_BOX.get_item_for_rect(rect)
                if active_item == BATTLE_ACTIVE_POKEMON_BOX.PLAYER_ACTIVE_BOX_A:
                    health_rect = self.get_subframe(active_item.get_health_rect())
                    """
                    player_health = calculate_health_ratio(health_rect)
                    name_rect = self.get_subframe(active_item.get_name_gender_rect())
                    player_active_name = parse_active_name_with_pytesseract(name_rect)
                    if re.search(self.construct_seen_pokemon_regex(), player_active_name):
                        pkmn_name = re.search(self.construct_seen_pokemon_regex(), player_active_name).group(0)
                        self.p1_selected['a'] = pkmn_name
                    """

                elif active_item == BATTLE_ACTIVE_POKEMON_BOX.ENEMY_ACTIVE_BOX_A:
                    health_rect = self.get_subframe(active_item.get_health_rect())
                    enemy_health = calculate_health_ratio(health_rect)
                    """
                    name_rect = self.get_subframe(active_item.get_name_gender_rect())
                    enemy_active_name = parse_active_name_with_pytesseract(name_rect)
                    if re.search(self.construct_seen_pokemon_regex(), enemy_active_name):
                        pkmn_name = re.search(self.construct_seen_pokemon_regex(), enemy_active_name).group(0)
                        self.p2_selected['a'] = pkmn_name
                    """

        message = 'player_health: %s, enemy_health: %s' % (str(player_health), str(enemy_health))
        print(message)
        name_message = 'player: %s, enemy: %s' % (self.p1_selected['a'], self.p2_selected['a'])
        self.draw_message_on_frame(message)
        self.draw_message_on_frame(name_message)
        print(name_message)

        if self.player_last_health_sequence['a'] == None:
            self.player_last_health_sequence['a'] = player_health
        self.player_current_health_sequence['a'] = player_health
        if self.enemy_last_health_sequence['a'] == None:
            self.enemy_last_health_sequence['a'] = enemy_health
        self.enemy_current_health_sequence['a'] = enemy_health

        if self.player_start_health_sequence['a'] == None:
            self.player_start_health_sequence['a'] = player_health
        if self.enemy_start_health_sequence['a'] == None:
            self.enemy_start_health_sequence['a'] = enemy_health

        if self.p1_selected['a'] is None:
            logging.info('Unknown player pokemon has health: %s' % str(player_health))
        else:
            # Later on, use to update health
            self.update_curr_health(self.fetch_seen_pokemon(True, self.p1_selected['a']), player_health)
        if self.p2_selected['a'] is None:
            logging.info('Unknown enemy pokemon has health: %s' % str(enemy_health))
        else:
            # Later on, use to update health
            self.update_curr_health(self.fetch_seen_pokemon(False, self.p2_selected['a']), enemy_health)



    def update_curr_health(self, seen_details, health):

        if health is None:
            health = 1

        # if pokemon doesnt exist yet, assume we never made it to active page.
        if seen_details['status'] == Status.FAINTED:
            return
        seen_details['health'] = health
        seen_details['last_health'] = health

        message = 'update_health: %s: curr: %s ' % (seen_details['form'], str(health))
        print(message)
        logging.info(message)


    def apply_damage_or_heal_reward(self):
        for position in ['a', 'b']:
            if self.player_last_health_sequence[position] is not None:
                is_player_1 = True
                pkmn = self.p1_selected[position]
                player_health_change = (self.player_last_health_sequence[position] - self.player_current_health_sequence[position]) / float(self.player_current_health_sequence[position]+0.0001)

                # No change
                if self.enemy_last_health_sequence[position] == self.enemy_current_health_sequence[position]:
                    continue
                elif player_health_change > 0:
                    #Damage taken
                    self.process_update(DAMAGE, [is_player_1, pkmn])
                else:
                    #Heal happened
                    self.process_update(HEAL, [is_player_1, pkmn])

                player_message = 'player health change this turn: %.2f' % player_health_change
                self.update_curr_health(pkmn, self.enemy_current_health_sequence[position], player_health_change, is_player_1)

                self.draw_message_on_frame(player_message)
                print(player_message)

            if self.enemy_last_health_sequence[position] is not None:
                is_player_1 = False
                pkmn = self.p2_selected[position]
                enemy_health_change = (self.enemy_last_health_sequence[position] - self.enemy_current_health_sequence[position]) / float(self.enemy_current_health_sequence[position]+0.0000001)

                # No change
                if self.enemy_last_health_sequence[position] == self.enemy_current_health_sequence[position]:
                    continue
                elif enemy_health_change > 0:
                    #Damage taken
                    self.process_update(DAMAGE, [is_player_1, pkmn])
                else:
                    #Heal happened
                    self.process_update(HEAL, [is_player_1, pkmn])

                enemy_message = 'enemy health change this turn: %.2f' % enemy_health_change
                self.update_curr_health(pkmn, self.enemy_current_health_sequence[position], enemy_health_change, is_player_1)
                self.draw_message_on_frame(enemy_message)
                print(enemy_message)


    def damage(self, pkmn, is_player_1):
        reward_modifier = 3
        if is_player_1:
            self.p1_reward -= reward_modifier
            message = '_p1_%s hurt by attack' % (pkmn,)
        else:
            self.p1_reward += reward_modifier
            message = '_p2_%s hurt by attack' % (pkmn,)

    def heal(self, pkmn, is_player_1):
        reward_modifier = 5
        if is_player_1:
            self.p1_reward += 2
            message = '_p1_%s healed a little' % (pkmn,)
        else:
            self.p2_reward += 2
            message = '_p2_%s healed a little' % (pkmn,)

    def handle_switch(self, is_player, pkmn_name, position, is_transform_or_baton=False):
        if pkmn_name not in self.registered_pokemon_names:
            self.registered_pokemon_names.append(pkmn_name)
        print('registered names',self.registered_pokemon_names)
        # Clear last successful action
        if is_player:
            self.p1_choice_attack_action = None
            if self.p1_active_pokemon_stats[position].dynamax_activated:
                self.p1_dynamax_count = 0
            self.p1_active_pokemon_stats[position] = ActiveStats()
            self.needs_team_order_update = True
        else:
            if self.p2_active_pokemon_stats[position].dynamax_activated:
                self.p2_dynamax_count = 0
            self.p2_active_pokemon_stats[position] = ActiveStats()
        self.update_seen_pokemon(is_player, pkmn_name)

        # assume None at beginning
        if self.switch_was_from is not None:
            prev_pkmn = self.switch_was_from
            prev_team_name = self.convert_registered_name_to_team_name(prev_pkmn)

            team_name = self.convert_registered_name_to_team_name(pkmn_name)

            if prev_team_name is None or team_name is None:
                print('Failed to swap positions')
                print('team_name', team_name)
                print('prev_team_name', prev_team_name)
            else:
                position_holder = self.player_pokemon[prev_team_name]['position']
                self.player_pokemon[prev_team_name]['position'] = self.player_pokemon[team_name]['position']
                self.player_pokemon[team_name]['position'] = position_holder
                print('Updated pokemon positions')



    #TODO during switchout instead. so much easier
    def handle_switch_out(self, is_player, pkmn_name, position, is_transform_or_baton=False):
#        position = self.get_position_for_pokemon(is_player, pkmn_name)
        if is_player:
            self.p1_active_pokemon_stats[position] = ActiveStats()
        else:
            self.p2_active_pokemon_stats[position] = ActiveStats()

    def get_position_for_pokemon(self, is_player, pkmn_name):
        if is_player_1:
            position = 'a'
            if self.p1_selected['b'] == name:
                position = 'b'
        else:
            position = 'a'
            if self.p2_selected['b'] == name:
                position = 'b'
        return position

    # set status to FNT, health to 0
    def handle_faint(self, is_player, pkmn_name):

        seen_details = self.p1_seen_details
        if not is_player:
            seen_details = self.p2_seen_details

        if is_player:
            self.forced_to_switch_before_turn()
            self.player_pokemon_did_faint = True
            position = 'a'
            self.p1_trapped[position] = False
            self.p1_must_switch[position] = True
            # Will be taken to team page before standby
            self.clear_dirty_nav_actions()


        # if pokemon doesnt exist yet, assume we never made it to active page.
        if pkmn_name not in seen_details:
            return
        seen_details[pkmn_name]['health'] = 0
        seen_details[pkmn_name]['status'] = Status.FAINTED

    #Delete inf uture
    def deprecated_update_curr_health(self, pkmn_name, health_current, health_delta, is_player):

        seen_details = self.p1_seen_details
        if not is_player:
            seen_details = self.p2_seen_details

        # if pokemon doesnt exist yet, assume we never made it to active page.
        if pkmn_name not in seen_details or seen_details[pkmn_name]['status'] == Status.FAINTED:
            return
        seen_details[pkmn_name]['health'] = health_current
        delta_change = seen_details[pkmn_name]['health'] - seen_details[pkmn_name]['last_health']
        seen_details[pkmn_name]['last_health'] = health_current

        # adjust score based on change in health. If negative, enemy gets reward and player loses.
        # if positive, player gains, enemy nothing.

        health_reward = delta_change * 20
        # lost life
        if delta_change < 0:
            if is_player:
                self.p1_reward -= health_reward
                self.p2_reward += health_reward
            else:
                self.p1_reward += health_reward
                self.p2_reward -= health_reward
        else:
            # gaining health worth less than taking health
            health_reward *= 0.75
            if is_player:
                self.p1_reward += health_reward
            else:
                self.p2_reward += health_reward

        message = 'update_health: %s: curr: %.2f delta:%.2f' % (pkmn_name, health_current, health_delta)
        print(message)

    @staticmethod
    def extract_pokemon_info_page_1(pkmn_name, name_rect, item_rect, element_1_rect, element_2_rect):
        sample_max_moves = [('Max Overgrowth', 10), ('Max Airstream', 10), ('Max Darkness', 10), ('Max Flare', 10)]
        print('inside extractgor starting page 1 extract')
        logging.info('inside extractgor starting page 1 extract')

        item = 'None'
        name = ''
        element_1 = None
        element_2 = None

        if name_rect is not None:
            name = parse_rect_with_pytesseract(name_rect)

        if item_rect is not None:
            item = parse_rect_with_pytesseract(item_rect)

        invert = True
        if element_1_rect is not None:
            element_1 = process_image_for_element_text(element_1_rect, invert)

        if element_2_rect is not None:
            element_2 = process_image_for_element_text(element_2_rect, invert)

        print('leaving extractgor starting page 1 extract')
        logging.info('leaving extractgor starting page 1 extract')
        return pkmn_name, name, item, element_1, element_2

    def construct_pokemon_info_page_1(self, future):
        print('before future constructing page one info plus plus')
        pkmn_name, name, item, element_1, element_2 = future
        sample_max_moves = [('Max Overgrowth', 10), ('Max Airstream', 10), ('Max Darkness', 10), ('Max Flare', 10)]
        print('constructing page one info plus plus')
        if pkmn_name in self.added_basic_info:
            print('no need to add page one info again for:',pkmn_name)
            return

        # verify name future?
#        name = parse_rect_with_pytesseract(self.get_subframe_from_frame(name_rect, frame))

        # verify name future?
#        item = parse_rect_with_pytesseract(self.get_subframe_from_frame(item_rect, frame))

        preprocesed_findings = 'findings_1 name: %s, item: %s, element_1:%s, element_2:%s' % (name, item, element_1, element_2)
        print(preprocesed_findings)
        logging.info(preprocesed_findings)

        logging.info('parsed element 1 summary: %s' % (element_1))
        if element_1 is not None:
            if re.search(pokemon_element_regex, element_1):
                element_1 = re.search(pokemon_element_regex, element_1).group(0).capitalize()
            else:
                element_1 = None


        logging.info('parsed element 2 summary: %s' % (element_2))
        if element_2 is not None:
            if re.search(pokemon_element_regex, element_2):
                element_2 = re.search(pokemon_element_regex, element_2).group(0).capitalize()
            else:
                element_2 = None

        self.player_pokemon[pkmn_name]['position'] = self.team_position_index
        self.player_pokemon[pkmn_name]['name'] = name
        self.player_pokemon[pkmn_name]['item'] = item
        self.player_pokemon[pkmn_name]['max_moves'] = sample_max_moves
        self.player_pokemon[pkmn_name]['element_1'] = element_1
        self.player_pokemon[pkmn_name]['element_2'] = element_2

        self.team_position_index += 1

        self.added_basic_info.append(pkmn_name)
        print('finished constructing page one info  for:',pkmn_name)
        print(self.player_pokemon[pkmn_name]['name'])
        print(self.player_pokemon[pkmn_name]['item'])


    @staticmethod
    def extract_pokemon_info_page_2(pkmn_name, hp_rect, sp_atk_rect, atk_rect, sp_def_rect, def_rect, speed_rect, ability_rect):
        try:

            print('inside extractor starting page 2 extract')
            logging.info('inside extractor starting page 2 extract')
            print('hp_rect')
            print(hp_rect)

            hp = parse_rect_with_pytesseract(hp_rect)

            hp = get_last_number_or_neg(hp)

            sp_atk = parse_rect_with_pytesseract(sp_atk_rect)
            sp_atk = get_last_number_or_neg(sp_atk)

            atk = parse_rect_with_pytesseract(atk_rect)
            atk = get_last_number_or_neg(atk)

            sp_def = parse_rect_with_pytesseract(sp_def_rect)
            sp_def = get_last_number_or_neg(sp_def)

            defense = parse_rect_with_pytesseract(def_rect)
            defense = get_last_number_or_neg(defense)

            speed = parse_rect_with_pytesseract(speed_rect)
            speed = get_last_number_or_neg(speed)

            ability_parsed = parse_rect_with_pytesseract(ability_rect)

            print('leaving extractor starting page 2 extract')
            logging.info('leaving extractor starting page 2 extract')

        except Exception as e:
            raise e


        return pkmn_name, hp, sp_atk, atk, sp_def, defense, speed, ability_parsed

    def construct_pokemon_info_page_2(self, future):
        print('constructing page two info')
        pkmn_name, hp, sp_atk, atk, sp_def, defense, speed, ability_parsed = future

        if pkmn_name in self.added_base_stats:
            print('no need to add base stats again for: ',pkmn_name)
            return

        preprocesed_findings = 'findings_2 hp: %d, sp_atk: %d, atk: %d, sp_def: %d, defense: %d, speed: %d, ability_parsed: %s' % (hp, sp_atk, atk, sp_def, defense, speed, ability_parsed)
        print(preprocesed_findings)

        if re.search(pokemon_ability_regex, ability_parsed):
            ability = ability_parsed
        else:
            print('ability not found', ability_parsed)

        self.player_pokemon[pkmn_name]['hp'] = hp
        self.player_pokemon[pkmn_name]['sp_atk'] = sp_atk
        self.player_pokemon[pkmn_name]['atk'] = atk
        self.player_pokemon[pkmn_name]['sp_def'] = sp_def
        self.player_pokemon[pkmn_name]['defense'] = defense
        self.player_pokemon[pkmn_name]['speed'] = speed
        self.player_pokemon[pkmn_name]['ability'] = ability

        self.added_base_stats.append(pkmn_name)
        print('finished constructing page two info  for:',pkmn_name)
        print(self.player_pokemon[pkmn_name]['atk'])
        print(self.player_pokemon[pkmn_name]['defense'])

    @staticmethod
    def extract_pokemon_info_page_3(pkmn_name, attack_slot_1_rect, attack_slot_2_rect, attack_slot_3_rect, attack_slot_4_rect):
        try:

            print('inside extractor starting page 3 extract')
            logging.info('inside extractor starting page 3 extract')
            attacks = []
            for atk_data in [attack_slot_1_rect, attack_slot_2_rect, attack_slot_3_rect, attack_slot_4_rect]:
                print('atk_data')
                print(type(atk_data))
#                print(atk_data)
                if atk_data is None:
                    continue
                name_rect = atk_data[0]
                pp_rect = atk_data[1]

                name = parse_rect_with_pytesseract(name_rect)
                pp = parse_rect_with_pytesseract(pp_rect)
                if re.search(pokemon_attacks_regex, name):
                    name = re.search(pokemon_attacks_regex, name).group(0)
                    max_pp =  20
                    if re.search(last_number_regex, pp):
                        max_pp = int(re.search(last_number_regex, pp).group())
                    attacks.append((name, max_pp))

            print('leaving extractor starting page 3 extract')
            logging.info('leaving extractor starting page 3 extract')

        except Exception as e:
            raise e

        return pkmn_name, attacks

    def construct_pokemon_info_page_3(self, future):
        print('constructing page three info')
        pkmn_name, attacks = future
        print('constructing page three info again for:',pkmn_name)

        preprocesed_findings = 'findings_3 name: %s, attacks: %s' % (pkmn_name, str(attacks))
        print(preprocesed_findings)
        logging.info(preprocesed_findings)

        self.player_pokemon[pkmn_name]['attacks'] = attacks
        print('finished constructing page three info  for:',pkmn_name)
        print(self.player_pokemon[pkmn_name]['attacks'])
        print(self.player_pokemon)
        self.log_constructed_team_info()

    def count_active_pokemon(self):
        print('counting active pokemon')
        self.active_pokemon_count = 2
        print('There are %d active pokemon' % (2))
        return
        # model is breaking shit
        active_counto = 0
        for label in self.labels_and_boxes:
            if label in ['active_menu_pokemon']:
                active_counto += len(self.labels_and_boxes[label])
        self.active_pokemon_count = active_counto
        print('There are %d active pokemon' % (active_counto))

    @staticmethod
    def extract_active_pokemon(modifiers, gender, name_rect, trainer_rect, level_rect, status_rect, element_1_rect, element_2_rect, item_name_rect, ability_name_rect, field_modifiers_rects):
        print('inside extractor active pokemon extract')
        logging.info('inside extractor active pokemon extract')
        try:

            pkmn_name = process_image_for_text(name_rect, False)
            print('parsed_name', pkmn_name)

            trainer = process_image_for_text(trainer_rect, True)
            print('parsed_trainer', trainer)

            level = get_active_name(level_rect)
            print('level was', level)
            level = get_first_number_or_neg(level)
            print('level as int', level)

            status = None
            # Potentially add labels for each status
            if status_rect is not None:
                status = process_image_for_text(status_rect, False)
            print('status__', status)

            ability = 'unknown'
            item = 'unknown'
            element_1 = None
            element_2 = None

            invert = True
            if element_1_rect is not None:
                logging.info('Before element 1')
                element_1 = process_image_for_element_text(element_1_rect, invert)
                print(element_1)
                logging.info('parsed element 1 active: %s' % (element_1))
                if re.search(pokemon_element_regex, element_1):
                    element_1 = re.search(pokemon_element_regex, element_1).group(0).capitalize()
                else:
                    element_1 = None
            print('active_element_1:', element_1)

            if element_2_rect is not None:
                logging.info('Before element 2')
                element_2 = process_image_for_element_text(element_2_rect, invert)
                print(element_2)
                logging.info('parsed element 2 active: %s' % (element_2))
                if re.search(pokemon_element_regex, element_2):
                    element_2 = re.search(pokemon_element_regex, element_2).group(0).capitalize()
                else:
                    element_2 = None
            print('active_element_2:', element_2)

            if item_name_rect is not None:
                parsed_item = process_image_for_text(item_name_rect, False, False, True)
                if re.search(pokemon_items_regex, parsed_item):
                    item = re.search(pokemon_items_regex, parsed_item).group(0)
            print('parsed_item:', item)

            if ability_name_rect is not None:
                parsed_ability = process_image_for_text(ability_name_rect, False, False, True)
                if re.search(pokemon_ability_regex, parsed_ability):
                    ability = re.search(pokemon_ability_regex, parsed_ability).group(0)
            print('parsed_ability:', ability)

            field_modifiers = []
            # selected y1 will have highest height.
            if len(field_modifiers_rects) > 0:
#                print('pre len field_modifiers_rects:', len(field_modifiers_rects))
#                print('pre field_modifiers_rects:', field_modifiers_rects)
                for rect in field_modifiers_rects:
                    field_name_rect = rect[0]
#                    print('field_name_rect', field_name_rect)
                    field_turn_count_rect = rect[1]
#                    print('field_turn_count_rect', field_turn_count_rect)
                    field_name = process_image_for_text(field_name_rect, False, False, True)
                    field_turn_count = process_image_for_text(field_turn_count_rect, False, False, True)
                    field_modifiers.append({'name':field_name, 'count':field_turn_count})
                    print('field_name:', field_name)
                    print('field_turn_count:', field_turn_count)


            print('leaving extractor active pokemon extract')
            logging.info('leaving extractor active pokemon extract')

            return modifiers, ability, item, element_1, element_2, gender, status, pkmn_name, level, trainer, field_modifiers
        except:
            raise e

    def analyze_active_pokemon(self, future):

        modifiers, ability, item, element_1, element_2, gender, status, pkmn_name, level, trainer, field_modifiers = future

        print('entering analyzing active pokemon')




        if re.search(self.construct_seen_pokemon_regex(), pkmn_name):
            pkmn_name = re.search(self.construct_seen_pokemon_regex(), pkmn_name).group(0)
        else:
            print('invalid active parsed name', pkmn_name)
            pkmn_name = None


        if trainer is not None:
            trainer = trainer.lower().strip()
        active_stats = {}
        active_stats['modifiers'] = modifiers
        active_stats['ability'] = ability
        active_stats['item'] = item
        active_stats['element_1'] = element_1
        active_stats['element_2'] = element_2
        active_stats['gender'] = gender
        active_stats['status'] = status
        active_stats['name'] = pkmn_name
        active_stats['level'] = level
        active_stats['trainer'] = trainer
        active_stats['field_modifiers'] = field_modifiers

        self.active_stats = active_stats
        is_player_1 =  trainer == self.trainer_name.lower().strip()
        selected = self.p1_selected['a']
        if not is_player_1:
            selected = self.p2_selected['a']
        if selected is None:
            #Use given name instead
            selected = pkmn_name

        if is_player_1:
            self.player_active_pokemon_set[selected] = active_stats
        else:
            self.enemy_active_pokemon_set[selected] = active_stats

        print('active player pokemon')
        print(self.player_active_pokemon_set)
        print('active enemy pokemon')
        print(self.enemy_active_pokemon_set)
        self.update_seen_pokemon_with_active(active_stats, is_player_1)
        self.apply_modifiers_to_active_info(active_stats['modifiers'], is_player_1, 'a')

        self.log_active_pokemon_info(active_stats, is_player_1)

    def apply_modifiers_to_active_info(self, modifiers, is_player_1, position):
        selected = self.p1_selected['a']
        if not is_player_1:
            selected = self.p2_selected['a']


        if is_player_1:
            self.p1_active_pokemon_stats[position].apply_modifiers(modifiers)
        else:
            self.p2_active_pokemon_stats[position].apply_modifiers(modifiers)


    def convert_pokemon_name_to_english(self, name):
        return name

    def is_valid_pokemon_name(self, name):
        # Perform conversion between languages as well
        name = self.convert_pokemon_name_to_english(name)

        return re.search(self.construct_seen_pokemon_regex(), name)

    def monitor_health_move_begin(self):
        pass

    def monitor_health_move_end(self):
        pass

    def convert_to_active_stats_info(self):
        pass


    # update team position and health
    def peek_team_pokemon(self):
        print('peaking team pokemon')
        logging.info('peaking team pokemon')
        position_and_health = {}
        # Add all positions, remove positions of noticed pokemon
        self.uncertain_positions = set()
        if self.team_size > 1:
            # Skip position 0 since you can never switch to self.
            for i in range(1, self.team_size):
                self.uncertain_positions.add(i)

        #clear out positions to -1
        for pkmn in self.player_pokemon:
            self.player_pokemon[pkmn]['position'] = -1

        team_counto = 0
        for label in self.labels_and_boxes:
            if label in ['team_pokemon', 'team_pokemon_selected']:
                for rect in self.labels_and_boxes[label]:
                    team_element = BATTLE_SELECTABLES.get_item_for_rect(self.battle_state, rect)
                    invert = label == 'team_pokemon_selected'
                    if team_element is not None:
                        team_name_rect = team_element.get_name_rect()
                        team_name_parsed = process_image_for_text(self.get_subframe(team_name_rect), team_element.is_first_element(), True)
                        team_name = self.convert_registered_name_to_team_name(team_name_parsed)
                        if team_name is not None and team_name in self.player_pokemon:
                            position = team_element.get_team_position()
                            # No longer uncertain
                            if position in self.uncertain_positions:
                                self.uncertain_positions.remove(position)
                            position_and_health[team_name] = {}
                            self.player_pokemon[team_name]['position'] = position
                            position_and_health[team_name]['position'] = position
                            health_ratio = None
                            health_rect = team_element.get_life_rect()
                            health_as_string = process_image_for_text(self.get_subframe(health_rect), invert)
                            try:
                                max_health = get_last_number_or_neg(health_as_string)
                                curr_health = get_first_number_or_neg(health_as_string)
                                health_ratio = int(curr_health) / float(max_health)
                                print('team_name max_health: %.2f' % (max_health))
                                print('team_name curr_health: %.2f' % (curr_health))
                                print('team_name health_ratio: %.2f' % (health_ratio))
                                logging.info('team_name max_health: %.2f' % (max_health))
                                logging.info('team_name curr_health: %.2f' % (curr_health))
                                logging.info('team_name health_ratio: %.2f' % (health_ratio))
                                if max_health == -1 or curr_health == -1:
                                    health_ratio = 1.0
                                position_and_health[team_name]['health'] = health_ratio
                            except:
                                raise e
                            if health_ratio is not None:
                                self.update_player_pokemon_health(team_name, health_ratio)
                        else:
                            print('junk team name', team_name_parsed)

        print('Pokemon positioning and healther: %s' % (position_and_health))
        logging.info('Pokemon positioning and healther: %s' % (position_and_health))
        print('Uncertain positions: %s' % (self.uncertain_positions))
        logging.info('Uncertain positions: %s' % (self.uncertain_positions))

    def count_team_pokemon(self):
        print('counting team pokemon')
        logging.info('counting team pokemon')
        team_counto = 0
        for label in self.labels_and_boxes:
            if label in ['team_pokemon', 'team_pokemon_selected']:
                team_counto += len(self.labels_and_boxes[label])
                continue
                #DEPRECATED
                """
                for rect in self.labels_and_boxes[label]:
                    team_element = BATTLE_SELECTABLES.get_item_for_rect(self.battle_state, rect)
                    if team_element in self.added_team_members:
                        continue
                    if team_element is not None:
                        team_name_rect = team_element.get_name_rect()
                        team_name = process_image_for_text(self.get_subframe(team_name_rect), team_element.is_first_element(), True)
                        if re.search(self.construct_seen_pokemon_regex(), team_name):
                            print('accepted pparsed team name: %s, is_first_element:%s, position: %d' % (team_name, team_element.is_first_element(), team_element.get_team_position()))
                            logging.info('accepted pparsed team name: %s, is_first_element:%s, position: %d' % (team_name, team_element.is_first_element(), team_element.get_team_position()))
                            self.added_team_members.append(team_element)
                            position = team_element.get_team_position()
                            self.player_pokemon[team_name] = {'position': position}
                        else:
                            print('rejected pparsed team name: %s, is_first_element:%s, position: %d' % (team_name, team_element.is_first_element(), team_element.get_team_position()))
                            logging.info('rejected pparsed team name: %s, is_first_element:%s, position: %d' % (team_name, team_element.is_first_element(), team_element.get_team_position()))
                            print('junk team name', team_name)
                """
        self.team_size = team_counto
        print('There are %d team pokemon' % (team_counto))
        logging.info('There are %d team pokemon' % (team_counto))
        self.did_construct_team_info = True

    def analyze_team_pokemon(self):
        print('analyzing team pokemon')


    def swapping_pokemon(self):
        print('Swapping a pokemon')
        self.needs_update_positioning_next_turn = True

    def finish_pokemon_scan(self):
        print('finished scanning a team pokemon')

    def activate_dynamax(self):
        print('Activating Dynamax')

    def struggle_used(self):
        print('using struggle_used')

    def select_attack_1(self):
        pkmn_name = self.p1_selected['a']
        frame = self.curr_frame
        labels_and_boxes = self.labels_and_boxes
        print('Starting thread self.update_pp_usage from select_attack_1')
        t = threading.Thread(target=self.update_pp_usage, args=(pkmn_name, frame, labels_and_boxes))
        t.start()
        print('Using Attack 1')

    def select_attack_2(self):
        pkmn_name = self.p1_selected['a']
        frame = self.curr_frame
        labels_and_boxes = self.labels_and_boxes
        print('Starting thread self.update_pp_usage from select_attack_2')
        t = threading.Thread(target=self.update_pp_usage, args=(pkmn_name, frame, labels_and_boxes))
        t.start()
        print('Using Attack 2')

    def select_attack_3(self):
        pkmn_name = self.p1_selected['a']
        frame = self.curr_frame
        labels_and_boxes = self.labels_and_boxes
        print('Starting thread self.update_pp_usage from select_attack_3')
        t = threading.Thread(target=self.update_pp_usage, args=(pkmn_name, frame, labels_and_boxes))
        t.start()
        print('Using Attack 3')

    def select_attack_4(self):
        pkmn_name = self.p1_selected['a']
        frame = self.curr_frame
        labels_and_boxes = self.labels_and_boxes
        print('Starting thread self.update_pp_usage from select_attack_4')
        t = threading.Thread(target=self.update_pp_usage, args=(pkmn_name, frame, labels_and_boxes))
        t.start()
        print('Using Attack 4')

    # used to directly update seen attacks not attack pp.
    # use some sort of subtraction i guess
    def update_pp_usage(self, pkmn_name, frame, labels_and_boxes):
        print('Updating PP Usage')
        number_of_attackos = 0
        attacks = {}
        # these are the packaged attacks sent to neural network.
        for label in labels_and_boxes:
            if label in ['attack_option', 'attack_option_selected']:
                number_of_attackos += 1
                for rect in labels_and_boxes[label]:
                    attack_slot = BATTLE_SELECTABLES.get_item_for_rect(self.battle_state, rect)
                    if attack_slot in [BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1, BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2, BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3, BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4]:
                        name_rect = attack_slot.get_name_rect()
                        pp_rect = attack_slot.get_pp_count_rect()

                        name = parse_rect_with_pytesseract(self.get_subframe_from_frame(name_rect, frame))
                        name = name.split('\n')[0]
                        pp = parse_rect_with_pytesseract(self.get_subframe_from_frame(pp_rect, frame))
                        attacks[name] = pp
                        if re.search(pokemon_attacks_regex, name):
                            atk_name = re.search(pokemon_attacks_regex, name).group(0)
                            max_pp = get_last_number_or_neg(pp)
                            curr_pp = get_last_number_or_neg(pp)
                            # No need guessingif cant see
                            # assume move is disabled if cant read number but can read name
                            if curr_pp == -1 or max_pp == -1:
                                self.update_seen_moves(True, pkmn_name, atk_name, 100)
                                continue

                            print('updating_atk_pp name:',atk_name)
                            print('updating_atk_pp pkmn:',pkmn_name)
                            print('updating_atk_pp max_pp:',max_pp )
                            print('updating_atk_pp curr_pp:', curr_pp)
                            print('updating_atk_pp num:',max_pp - curr_pp)
                            print('updating_atk_pp pp:',pp)

                            self.update_seen_moves(True, pkmn_name, atk_name, max_pp - curr_pp )
        self.packaged_attacks = attacks

    # used to directly update seen attacks not attack pp.
    # use some sort of subtraction i guess
    def update_max_moes(self, pkmn_name, frame, labels_and_boxes):
        print('Updating max moves, todo')
        return
        number_of_attackos = 0
        attacks = {}
        # these are the packaged attacks sent to neural network.
        for label in labels_and_boxes:
            if label in ['attack_option', 'attack_option_selected']:
                number_of_attackos += 1
                for rect in labels_and_boxes[label]:
                    attack_slot = BATTLE_SELECTABLES.get_item_for_rect(self.battle_state, rect)
                    if attack_slot in [BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1, BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2, BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3, BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4]:
                        name_rect = attack_slot.get_name_rect()
                        pp_rect = attack_slot.get_pp_count_rect()

                        name = parse_rect_with_pytesseract(self.get_subframe_from_frame(name_rect, frame))
                        name = name.split('\n')[0]
                        pp = parse_rect_with_pytesseract(self.get_subframe_from_frame(pp_rect, frame))
                        attacks[name] = pp
                        if re.search(pokemon_attacks_regex, name):
                            atk_name = re.search(pokemon_attacks_regex, name).group(0)
                            max_pp = get_last_number_or_neg(pp)
                            curr_pp = get_last_number_or_neg(pp)
                            # No need guessingif cant see
                            # assume move is disabled if cant read number but can read name
                            if curr_pp == -1 or max_pp == -1:
                                self.update_seen_moves(True, pkmn_name, atk_name, 100)
                                continue

                            print('updating_atk_pp name:',atk_name)
                            print('updating_atk_pp pkmn:',pkmn_name)
                            print('updating_atk_pp max_pp:',max_pp )
                            print('updating_atk_pp curr_pp:', curr_pp)
                            print('updating_atk_pp num:',max_pp - curr_pp)
                            print('updating_atk_pp pp:',pp)

                            self.update_seen_moves(True, pkmn_name, atk_name, max_pp - curr_pp )
        self.packaged_attacks = attacks

    def set_maxmoves(max_moves):
        for pkmn in self.player_pokemon:
            print(self.player_pokemon[pkmn])
            if self.player_pokemon[pkmn]['position'] == 0:
                self.player_pokemon[pkmn]['max_moves'] = max_moves

    # FAINT, uturn like moves, emergency exit
    def forced_to_switch_before_turn(self):
        self.disabled_actions = set()
        # Can just try clearing everything
        self.navigation_actions = []
        self.clear_nav_action()
        self.commands = []

        return
        # Remove nav actions unrelated to team's page
        for nav_action in self.navigation_actions:
            if nav_action in NONTEAM_NAV_ACTIONS:
                self.navigation_actions.remove(nav_action)

        if self.current_navigation_action in NONTEAM_NAV_ACTIONS:
            self.clear_nav_action()

        #IF commands become a problem in the future, clear them too.


    def switch_from_uturn_volt_switch_initiated(self):
        self.forced_to_switch_before_turn()
        position = 'a'
        self.p1_trapped[position] = False
        self.p1_must_switch[position] = True
        self.uturn_like_move_used = True

    def unexpected_switch_screen(self):
        self.forced_to_switch_before_turn()
        position = 'a'
        self.p1_trapped[position] = False
        self.p1_must_switch[position] = True

    def sample_scarf(self):
        self.p1_selected['a'] = 'Excadrill'
        self.player_pokemon = {'Excadril': {'position': 0, 'name': 'Excadrill', 'item': 'Choice Scarf', 'attacks': {'Rock Slide': 10, 'Iron Head': 15, 'Earthquake': 10, 'X-Scissor': 20}, 'hp': 186, 'sp_atk': 49, 'atk': 205, 'sp_def': 85, 'defense': 80, 'speed': 140, 'ability': 'Sand Rush'}, 'Tyranitar': {'position': 1, 'name': 'Tyranitar', 'item': 'Air Balloon', 'attacks': {'Protect': 10, 'Fire Punch': 20, 'Rock Slide': 10, 'Crunch': 15}, 'hp': 176, 'sp_atk': 103, 'atk': 186, 'sp_def': 120, 'defense': 130, 'speed': 124, 'ability': 'Sand Stream'}, 'Rotom': {'position': 2, 'name': 'Rotom', 'item': 'None', 'attacks': {'Trick': 10, 'Overheat': 20, 'Discharge': 20, 'Volt Switch': 20}, 'hp': 126, 'sp_atk': 157, 'atk': 64, 'sp_def': 127, 'defense': 127, 'speed': 151, 'ability': 'Levitate'}}

        self.p1_seen_details = {'Excadrill': {'attacks': {'Max Steelspike': 1, 'Max Flutterby': 1, 'Max Rockfall': 1, 'Iron Head': 1, 'Rock Slide': 2}, 'form': 'Excadrill', 'item': 'hidden_item', 'gender': '', 'health': 1, 'last_health': 1, 'status': Status.NOTHING, 'level': 80, 'ability': 'hidden_ability'}}
        self.p2_seen_details = {'Dracovish': {'attacks': {'Rock Slide': 3}, 'form': 'Dracovish', 'item': 'hidden_item', 'gender': '', 'health': 0, 'last_health': 1, 'status': Status.FAINTED, 'level': 80, 'ability': 'hidden_ability'}, 'Rotom': {'attacks': {'Will-O-Wisp': 1}, 'form': 'Rotom', 'item': 'hidden_item', 'gender': '', 'health': 1, 'last_health': 1, 'status': Status.NOTHING, 'level': 80, 'ability': 'hidden_ability'}}

        print('resetting choice action to None')
        self.p1_choice_attack_action = None

        valid_moves = self.get_valid_moves_for_player()
        print('scarf valid moves', valid_moves)

        print('Setting choice action to slot 1')
        self.p1_choice_attack_action = Action.Attack_Slot_1

        valid_moves = self.get_valid_moves_for_player()
        print('scarf valid moves', valid_moves)

    def sample_disabled_action(self):
        self.p1_selected['a'] = 'Excadrill'
        self.player_pokemon = {'Excadril': {'position': 0, 'name': 'Excadrill', 'item': 'Choice Scarf', 'attacks': {'Rock Slide': 10, 'Iron Head': 15, 'Earthquake': 10, 'X-Scissor': 20}, 'hp': 186, 'sp_atk': 49, 'atk': 205, 'sp_def': 85, 'defense': 80, 'speed': 140, 'ability': 'Sand Rush'}, 'Tyranitar': {'position': 1, 'name': 'Tyranitar', 'item': 'Air Balloon', 'attacks': {'Protect': 10, 'Fire Punch': 20, 'Rock Slide': 10, 'Crunch': 15}, 'hp': 176, 'sp_atk': 103, 'atk': 186, 'sp_def': 120, 'defense': 130, 'speed': 124, 'ability': 'Sand Stream'}, 'Rotom': {'position': 2, 'name': 'Rotom', 'item': 'None', 'attacks': {'Trick': 10, 'Overheat': 20, 'Discharge': 20, 'Volt Switch': 20}, 'hp': 126, 'sp_atk': 157, 'atk': 64, 'sp_def': 127, 'defense': 127, 'speed': 151, 'ability': 'Levitate'}}

        self.p1_seen_details = {'Excadrill': {'attacks': {'Max Steelspike': 1, 'Max Flutterby': 1, 'Max Rockfall': 1, 'Iron Head': 1, 'Rock Slide': 2}, 'form': 'Excadrill', 'item': 'hidden_item', 'gender': '', 'health': 1, 'last_health': 1, 'status': Status.NOTHING, 'level': 80, 'ability': 'hidden_ability'}}
        self.p2_seen_details = {'Dracovish': {'attacks': {'Rock Slide': 3}, 'form': 'Dracovish', 'item': 'hidden_item', 'gender': '', 'health': 0, 'last_health': 1, 'status': Status.FAINTED, 'level': 80, 'ability': 'hidden_ability'}, 'Rotom': {'attacks': {'Will-O-Wisp': 1}, 'form': 'Rotom', 'item': 'hidden_item', 'gender': '', 'health': 1, 'last_health': 1, 'status': Status.NOTHING, 'level': 80, 'ability': 'hidden_ability'}}

        print('resetting choice action to None')
        self.p1_choice_attack_action = None

        valid_moves = self.get_valid_moves_for_player()
        print('disabled valid moves', valid_moves)

        print('disabling action to slot 1')
        self.disabled_actions.add(Action.Attack_Slot_1)

        valid_moves = self.get_valid_moves_for_player()
        print('disabled valid moves', valid_moves)
        print('self.disabled_actions', self.disabled_actions)

    def get_valid_moves_for_player(self, position='a'):
        DYNA_OFFSET = 4
        CHANGE_SLOT_OFFSET = 8


        pokemon = self.player_pokemon
        selected_slots = self.p1_selected
        trapped_player = self.p1_trapped
        must_switch  = self.p1_must_switch

        #Patch for mid match testing. assign selected to position 0 pokemon in team
        if selected_slots[position] is None:
            for team_pkmn in self.player_pokemon:
                if self.player_pokemon[team_pkmn]['position'] == 0:
                    selected_slots[position] = team_pkmn
                    break

        curr_pokemon = selected_slots[position]


        valid_moves  = []
        # Team needs to be constructed first
        if curr_pokemon is None:
            return []
        # Need new footage to test pp
#        curr_attacks = [{'max_pp':5, 'used_pp':1}, {'max_pp':5, 'used_pp':1}, {'max_pp':5, 'used_pp':1}, {'max_pp':5, 'used_pp':1}]
        curr_attacks = self.get_combined_attack_for_pokemon(curr_pokemon, True)
        curr_seen_details = self.fetch_seen_pokemon(True, curr_pokemon)

        print('combined attacks', curr_attacks)

        if not ( must_switch[position] or curr_pokemon is None or curr_seen_details['status'] == Status.FAINTED):
            for idx, atk in enumerate(curr_attacks):
                # IF dynamaxed, all are available - use turns count
                if self.p1_active_pokemon_stats[position].dynamax_turns > 0:
                    print('checking choice skipped')
                    valid_moves.append((Action(idx), self.selectable_targets_for_target(TARGET.SELF, position)))
                elif atk is not None and atk['max_pp'] >= atk['used_pp']:
                    print('checking choice')
                    is_choiced = self.is_player_pokemon_choiced(curr_pokemon)
                    print('is_choiced', is_choiced)
                    # This should be expanded for taunt, disable, encore, etc
                    #Encore will require logic of name of attack
                    if is_choiced and (self.p1_choice_attack_action is not None):
                        print('%s is choiced' % curr_pokemon)
                        print('choiced action is', self.p1_choice_attack_action)
                        if Action(idx) == self.p1_choice_attack_action:
                            valid_moves.append((Action(idx), self.selectable_targets_for_target(TARGET.SELF, position)))
                    else:
                        valid_moves.append((Action(idx), self.selectable_targets_for_target(TARGET.SELF, position)))
                else:
                    print('invalid attack?')
                    print('atk is not None?', atk is not None)
                    print('atk[\'max_pp\'] >= atk[\'used_pp\']?', atk['max_pp'] >= atk['used_pp'])

#                if False and self.is_network_match and not self.p1_used_dynamax:
#                    valid_moves.append((Action(idx+DYNA_OFFSET), self.selectable_targets_for_target(TARGET.SELF, position)))

            # Struggle is the same as attack slot one.
            if len(valid_moves) == 0: # can only struggle
                valid_moves.append((Action.Attack_Struggle, self.selectable_targets_for_target(TARGET.SELF, position)))

            #Dynamax is only available when struggle isnt
            for idx, atk in enumerate(curr_attacks):
                if self.is_network_match and not self.p1_used_dynamax:
                    valid_moves.append((Action(idx+DYNA_OFFSET), self.selectable_targets_for_target(TARGET.SELF, position)))
        else:
            print('No attacks available, check must switch etc, may be reason for no moves issue')
            print('must_switch[position]', must_switch[position])
            print('curr_pokemon is None', curr_pokemon is None)
            print('curr_seen_details[\'status\']', curr_seen_details['status'])


        unavailable_switches = set()
        if selected_slots['a'] is not None:
            selected_team_name = self.convert_registered_name_to_team_name(selected_slots['a'])
            unavailable_switches.add(selected_team_name)
#            print('unavailable_switches_a', unavailable_switches)
        if selected_slots['b'] is not None:
            unavailable_switches.add(selected_slots['b'])
#            print('unavailable_switches_b', unavailable_switches)

        # trapped pokemon have no switch options
        if not trapped_player[position]:
            for idx, pkmn in enumerate(pokemon):
                if pkmn in unavailable_switches:
                    print('cant switch to pokemon apart of unavailable', pkmn)
                    continue
                pos_idx = self.player_pokemon[pkmn]['position']
                if pos_idx == -1:
                    print('Cannot determine position for %s' % (pkmn))
                    logging.info('Cannot determine position for %s' % (pkmn))
                    continue

                seen_details_pkmn_name_equiv = None
                for seen_pkmn in self.p1_seen_details:
                    temp_teamname = self.convert_registered_name_to_team_name(seen_pkmn)
                    if temp_teamname is not None and temp_teamname == pkmn:
                        seen_details_pkmn_name_equiv = seen_pkmn
                        break
                # Assume ok if not seen. 100% health
                if seen_details_pkmn_name_equiv is None:
                    print('adding as a potential switch, not in seen data', pkmn)
                    valid_moves.append((Action(CHANGE_SLOT_OFFSET+pos_idx), self.selectable_targets_for_target(TARGET.SELF, position)))
                    continue
                pkmn_seen_details = self.p1_seen_details[seen_details_pkmn_name_equiv]
                print('considering: ', pkmn_seen_details)

                # ignore active pokemons
                print('considering2: ', pkmn_seen_details)
                if pkmn_seen_details['status'] != Status.FAINTED and pkmn is not curr_pokemon:
                    print('adding as a potential switch, not fainted or current', pkmn)
                    valid_moves.append((Action(CHANGE_SLOT_OFFSET+pos_idx), self.selectable_targets_for_target(TARGET.SELF, position)))
                else:
                    print('did not add this pokemon', pkmn)
                    print('fainted?', pkmn_seen_details['status'])
                    print('curr_pokemon is', curr_pokemon)


            for pos_idx in self.uncertain_positions:
                print('potential uncertain switch added: %d' % (pos_idx))
                logging.info('potential uncertain switch added: %d' % (pos_idx))
                valid_moves.append((Action(CHANGE_SLOT_OFFSET+pos_idx), self.selectable_targets_for_target(TARGET.SELF, position)))

        else:
            print('Cant switch, pokemon trapped')
#        """
        if len(valid_moves) == 0:
            print('valid_moves %s', valid_moves)
            print('must switch %s', must_switch[position])
            print('curr_pokemon is none %s', curr_pokemon is None)
            print('No Valid Moves!!!!')
            print('team dump: %s' % (self.player_pokemon))
            print('seen dump: %s' % (self.p1_seen_details))
            print('Forcing allowing all switches')
            for pos_idx in range(1, self.team_size):
                print('forced potential switch added: %d' % (pos_idx))
                logging.info('forced potential switch added: %d' % (pos_idx))
                valid_moves.append((Action(CHANGE_SLOT_OFFSET+pos_idx), self.selectable_targets_for_target(TARGET.SELF, position)))
#            if curr_pokemon is not None:
#                print('no health', int(curr_pokemon.curr_health) <= 0)
#        """

        print('pre valid_moves', valid_moves, '\n')
        print('pre self.disabled_actions', self.disabled_actions, '\n')
        for action_pair in valid_moves:
            action = action_pair[0]
            if action in self.disabled_actions:
                print('self.disabled_actions', self.disabled_actions)
                valid_moves.remove(action_pair)
                print('Pair removed', action_pair)

            #TODO Fix by updating switch_error model. THIS Is a lazy fix. Lets Go Eevee allows slot 1 switches
            if action == Action.Change_Slot_1:
                print('removing change slot 1', self.disabled_actions)
                valid_moves.remove(action_pair)
                print('change slot 1 Pair removed', action_pair)
        print('valid_moves', valid_moves, '\n')

        #Emergency for when a pokemon switched in but text didnt catch up. allow all attacks
        if len(valid_moves) == 0:
            print('Options override adding all attacks as valid. Perhaps text didn\'t catch up')
            logging.info('Options override adding all attacks as valid. Perhaps text didn\'t catch up')
            #Dynamax is only available when struggle isnt
            for idx, atk in enumerate(curr_attacks):
                valid_moves.append((Action(idx), self.selectable_targets_for_target(TARGET.SELF, position)))
                if self.is_network_match and not self.p1_used_dynamax:
                    valid_moves.append((Action(idx+DYNA_OFFSET), self.selectable_targets_for_target(TARGET.SELF, position)))

            print('valid_moves after emergency', valid_moves, '\n')


        return valid_moves

    def convert_registered_name_to_team_name(self, registered_name):
        for name in self.player_pokemon:
            if isEditDistanceWithinTwo(registered_name, name):
                return name

    def is_player_pokemon_choiced(self, pkmn_name):
        team_name = self.convert_registered_name_to_team_name(pkmn_name)

        seen_details = self.fetch_seen_pokemon(True, pkmn_name)

        if team_name is None:
            print('registered name too different from team name', pkmn_name)
            # couldnt pull anything up
            return seen_details['item'] in CHOICED_ITEMS
        pokemon = self.player_pokemon[team_name]
        print(self.player_pokemon)
        print('team_name', team_name)
        print('seen_details[item]', seen_details['item'])
        print('pokemon[item]', pokemon['item'])
        return (seen_details['item'] in CHOICED_ITEMS) or (pokemon['item'] in CHOICED_ITEMS)

    def get_combined_attack_for_pokemon(self, pkmn_name, is_player):
        seen_details = self.p1_seen_details
        if not is_player:
            seen_details = self.p2_seen_details

        team_name = self.convert_registered_name_to_team_name(pkmn_name)


        if team_name is None or pkmn_name is None:
            print('registered name too different from team name', pkmn_name)
            # couldnt pull anything up
            return [{'max_pp':5, 'used_pp':1}, {'max_pp':5, 'used_pp':1}, {'max_pp':5, 'used_pp':1}, {'max_pp':5, 'used_pp':1}]
        seen_attacks = self.fetch_seen_pokemon(True, pkmn_name)['attacks']
        attacks_to_send = []
        print('seen_attacks', seen_attacks)
        print('team_name', team_name)
        print('pkmn_name', pkmn_name)
        print('self.player_pokemon[team_name]', self.player_pokemon[team_name])
        # registration failed. assume all 4 moves
        if 'attacks' not in self.player_pokemon[team_name]:
            return [{'max_pp':5, 'used_pp':1}, {'max_pp':5, 'used_pp':1}, {'max_pp':5, 'used_pp':1}, {'max_pp':5, 'used_pp':1}]
        print('self.player_pokemon[team_name][attacks]', self.player_pokemon[team_name]['attacks'])
        for attack_pp in  self.player_pokemon[team_name]['attacks']:
            attack = attack_pp[0]
            attack_info = {}
            attack_info['max_pp'] = attack_pp[1]
            attack_info['used_pp'] = 0

            if attack in seen_attacks:
                attack_info['used_pp'] = seen_attacks[attack]
            attacks_to_send.append(attack_info)

        print('combined: ', attacks_to_send)
        return attacks_to_send


    def selectable_targets_for_target(self, target, position='a'):
        if target in [TARGET.SELF, TARGET.ALL_ADJACENT_FOES, TARGET.ALLY_SIDE,
                    TARGET.ALLY_TEAM, TARGET.ALL, TARGET.ALL_ADJACENT, TARGET.RANDOM_NORMAL]:
            return [SELECTABLE_TARGET.DO_NOT_SPECIFY]


battle_states_labels = ['standby', 'active_menu', 'attack_fight_menu', 'active_pokemon_info', 'team_menu', 'team_member_options_menu', 'pokemon_summary_base_stats', 'pokemon_summary_info', 'pokemon_summary_attacks', 'use_next_pokemon', 'trainer_switch_pokemon', 'wild_battle_over', 'wild_pokemon_begin', 'surprise_wild_battle_begin', 'experience_gained_menu', 'level_up_box', 'message_need_action', 'team_menu_info_switch']
submenu_selectables_labels = ['submenu_item_selected']
battle_selectables_labels = ['menu_option_selected', 'attack_option_selected', 'dynamax_selected', 'team_pokemon_selected']

def update_state(labels_boxes):
    battle_state = None
    for label in labels_boxes:
        first_box = labels_boxes[label][0]
        if label in battle_states_labels:
            battle_state = BATTLE_STATES.state_for_label(label)
    return battle_state

def update_selectables(battle_state, labels_boxes, network_match=False):
    battle_selectable = None
    for label in labels_boxes:
        for box in labels_boxes[label]:
            if label in battle_selectables_labels:
                print(label)
                print(box)
                battle_selectable = BATTLE_SELECTABLES.get_item_for_rect(battle_state, box, network_match)
    return battle_selectable

def update_sub_selectables(battle_state, battle_selectable, labels_boxes, mini=False):
    battle_sub_selectable = None
    for label in labels_boxes:
        for box in labels_boxes[label]:
            if label in submenu_selectables_labels:
                battle_sub_selectable = BATTLE_SUBMENU_SELECTABLES.get_item_for_rect(battle_state, battle_selectable, box, mini)
                if battle_sub_selectable is not None:
                    return battle_sub_selectable
    return battle_sub_selectable

def print_game_state(navigation_action, state, selectable, submenu):
    print('nav: %s, bat_state: %s, bat_select: %s, submenu_sel: %s' %(navigation_action, state, selectable, submenu))

def flush_cam(cam):
    start = time.time()
    while time.time() - start < 1:
        cam.grab()

def record_test_videos():
    videos = ['attack_switch_battle_1.mov', 'attack_switch_battle_2.mov', 'attack_switch_battle_3.mov', 'check_active_check_team_then_attack_1.mov', 'quick_battle_2.mov']
    for video_name in videos:
        state = WildState()
        cam = cv2.VideoCapture("test_videos/%s" % (video_name))
#        cam.set(cv2.CAP_FFMPEG,True)
#        cam.set(cv2.CAP_PROP_FPS,60)
        #cam.set(cv2.CAP_PROP_BUFFERSIZE,5)

        _fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#        _fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        _out = cv2.VideoWriter("%s.mp4" % (video_name[:-4]), _fourcc, 20.0, (1280, 720))

        i = 0
        while(True):
            ret,frame = cam.read()
            height, width, channels = frame.shape
        #    print(height, width, channels)
            frame = cv2.resize(frame, (1280, 720), interpolation = cv2.INTER_AREA)
            labels_boxes = yolo.process_image(frame)
            print(labels_boxes)

            action, is_done = state.process_frame(frame, labels_boxes)
            print('Performing Action?: ', action)
            print('Done?',done)
            _out.write(frame);
            if is_done:
                break
#            i += 1

        cam.release()
        _out.release()
        cv2.destroyAllWindows()

def process_framed_test_videos():
    import os

    sorted_images = sorted(os.listdir('framed_shadow_tag_volt_switch_choice_specs_battle_2'))
    battle_override_frames = ['frame045.jpg', 'frame108.jpg', 'frame183.jpg', 'frame241.jpg']
    state = WildState()
    i = 0
    for image_name in sorted_images:
        i += 1
        image = cv2.imread("framed_shadow_tag_volt_switch_choice_specs_battle_2/%s" % (image_name))

        override = None
#        if image_name in battle_override_frames:
#            override = SEQUENCE_STATE.BATTLING

        labels_boxes = yolo.process_image(image)

        if len(labels_boxes) > 0:
            print(labels_boxes)

        action, is_done = state.process_frame(image, labels_boxes, override)
        print('Performing Action?: ', action)
        print('Done?',done)


        save_file = "framed_detection_shadow_tag_volt_switch_choice_specs_battle/%s" % (image_name)
#        save_file = "frames_detection_series_attacks_torment_faint/%s" % (image_name)
        cv2.imwrite(save_file, image)

#        if is_done or i > 100:
        if is_done:
            break

def process_live_video_feed():
    import os

    state = WildState()
    state.is_network_match = False

    i = 0

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_FFMPEG,True)
    cam.set(cv2.CAP_PROP_FPS,30)
#    cam.set(cv2.CAP_PROP_BUFFERSIZE,0)

#    _fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#    _out = cv2.VideoWriter("test_poke.mp4", _fourcc, 20.0, (1920,1080))

    i = 0
    actionCoolDown = time.time()
    while(True):
        action, done = None, False
        ret,image = cam.read()
        image = cv2.resize(image, (1280, 720), interpolation = cv2.INTER_AREA)
#        if i % 5 == 0:
#            cv2.imshow('frame',frame)
#        _out.write(frame);
        labels_boxes = yolo.process_image(image, True)

        if len(labels_boxes) > 0:
            print(labels_boxes)

        if time.time() - actionCoolDown >= 0.3: #some  value
            #
            #  process both frames NOW !
            #
            action, done = state.process_frame(image, labels_boxes)
        else:
            print('actionCoolDown', actionCoolDown)
            print('time.time()', time.time())
            print('time.time() - actionCoolDown', time.time() - actionCoolDown)

        # reset time to make move
        if action is not None:
            actionCoolDown = time.time()
            print('Just wait a second')

        print('Performing Action?: ', action)
        print('Done?',done)
#        cv2.imshow('image2  www',image)
#        if cv2.waitKey(1) & 0xFF == ord('q'):
#            break

#        time.sleep(1)
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


def process_live_video_feed2345():
    import os
    graph_options = tf.GraphOptions(place_pruned_graph =False)
    config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=True, graph_options=graph_options)
    config = tf.ConfigProto()
    # Avoid warning message errors
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    BUTTON_PRESS_DELAY = 0.2

    # Allowing GPU memory growth
    config.gpu_options.allow_growth = True
    K.clear_session()

    button_press_pool = Pool(1)

    use_gpu = False
    if not use_gpu:
        config = tf.ConfigProto()

    with tf.Session(config=config):

        state = WildState()
    #    state.sample_scarf()
    #    state.sample_disabled_action()
    #    return
    #    state.is_network_match = True
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
                labels_boxes = yolo.process_image(image)

                if len(labels_boxes) > 0:
                    print(labels_boxes)
                #
                #  process both frames NOW !
                #
                action, done, wait = state.process_frame(image, labels_boxes)
                actionCoolDown = time.time()
                if action is not None:
                    wait_threshold = wait
                else:
                    wait_threshold = wait
            else:
                pass

            # reset time to make move
            if action is not None:
                print('Just wait a second')
                send(action.serial_rep())
#                button_press_pool.apply_async(send, [action.serial_rep()])
                actionCoolDown = time.time()
                i += 1
#                flush_thread = threading.Thread(target=flush_cam, args=(cam,))
#                flush_thread.start()
    #            save_file = 'frame_%d_%s.jpg' % (i, action.serial_rep())
    #            cv2.imwrite(save_file, image)


            print('Performing Action?: ', action)
            print('Done?',done)
    #        cv2.imshow('image2  www',image)
    #        if cv2.waitKey(1) & 0xFF == ord('q'):
    #            break

    #        time.sleep(1)
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
                "score" : 0.8,
                "gpu_num" : 0,
                }
               )



    process_live_video_feed2345()
    i = 1/0

    battle_state = None
    battle_selectable = None
    battle_sub_selectable = None
    image_count = 0.0

    images = ['check_active_1.jpg', 'check_active_2.jpg', 'check_active_3.jpg', 'check_active_4.jpg', 'check_active_5.jpg', 'check_active_6.jpg', 'check_active_7.jpg', 'check_active_8.jpg']
#    images = ['check_moves_1.jpg', 'check_moves_2.jpg', 'check_moves_3.jpg', 'check_moves_4.jpg', 'check_moves_5.jpg']
#    images = ['check_pokemon_stats_1.jpg', 'check_pokemon_stats_2.jpg', 'check_pokemon_stats_3.jpg', 'check_pokemon_stats_4.jpg', 'check_pokemon_stats_5.jpg', 'check_pokemon_stats_6.jpg', 'check_pokemon_stats_7.jpg', 'check_pokemon_stats_8.jpg', 'check_pokemon_stats_9.jpg']
#    images = ['online_test_image.jpg']
#    images = ['active_info_1.jpg']
#    images = ['check_pokemon_stats_1.jpg', 'message_ability_1.jpg', 'message_ability_2.jpg']

    navigation_action = NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO
    battle_states = BATTLE_STATES.STANDBY
    battle_selectables = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu_selectables = BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON
    done = False

    skip_next_frame = False

    """
    cap = cv2.VideoCapture(0)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
#        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, (1280, 720), interpolation = cv2.INTER_AREA)

        if not skip_next_frame or True:

            labels_boxes = yolo.process_image(frame)
            next_battle_state = update_state(labels_boxes)
            next_battle_selectable = update_selectables(battle_state, labels_boxes)
            next_battle_sub_selectable = update_sub_selectables(battle_state, battle_selectable, labels_boxes)

            # Update if battle state isnt None
            if next_battle_state is not None:
                battle_state = next_battle_state
                battle_selectable = next_battle_selectable
                battle_sub_selectable = next_battle_sub_selectable

    #        print(labels_boxes)
            print('battle_state: %s, battle_selectable: %s, battle_sub_selectable: %s' %(battle_state, battle_selectable, battle_sub_selectable))

            action = navigation_action.action_for_state(battle_state, battle_selectable, battle_sub_selectable)
            print(action)

            if action is not None:
                skip_next_frame = True
#        else:
#            skip_next_frame = False


        # Display the resulting frame
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
#    """

#    record_test_videos()
#    i = 1/0

#    process_live_video_feed()
#    i = 1/0

    images = ['jtest1.jpg', 'jtest2.jpg', 'jtest3.jpg', 'jtest4.jpg', 'jtest5.jpg', 'jtest6.jpg', 'jtest7.jpg', 'jtest8.jpg', 'jtest9.jpg', 'jtest10.jpg', 'test_needs_1.jpg', 'frame240.jpg', 'frame241.jpg', 'frame242.jpg']
    images = []
    for i in range(1, 21):
        images.append('test_image_%d.jpg' % (i))
    state = WildState()
    for image_name in images:
        image = cv2.imread("curr_test_images/%s" % (image_name))
        labels_boxes = yolo.process_image(image, True)

        print(labels_boxes)
        print('battle_state: %s, battle_selectable: %s, battle_sub_selectable: %s' %(battle_state, battle_selectable, battle_sub_selectable))

#        state.process_frame(image, labels_boxes)

        action = None#navigation_action.action_for_state(battle_state, battle_selectable, battle_sub_selectable)
        print(action)
        done = False#check_if_nav_action_finished(navigation_action, battle_state, battle_selectable, battle_sub_selectable, action)
        print_game_state(navigation_action, battle_state, battle_selectable, battle_sub_selectable)

        save_file = "wild_object_detection_%d.jpg" % (image_count)
        image_count += 1
        cv2.imwrite(save_file, image)

    b=1/0
    for image_name in images:
        image = cv2.imread("test_images/%s" % (image_name))
        labels_boxes = yolo.process_image(image)

        print(labels_boxes)
        print('battle_state: %s, battle_selectable: %s, battle_sub_selectable: %s' %(battle_state, battle_selectable, battle_sub_selectable))

        action = None#navigation_action.action_for_state(battle_state, battle_selectable, battle_sub_selectable)
        print(action)
        done = False#check_if_nav_action_finished(navigation_action, battle_state, battle_selectable, battle_sub_selectable, action)
        print_game_state(navigation_action, battle_state, battle_selectable, battle_sub_selectable)
        print('Is nav action done: %s' % (str(done)))

        nav_str = '%s - done?: %s' % (navigation_action, done)
        exp_action_str = 'expected_action: %s' % (action)
        cv2.putText(image, str(battle_state), (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        cv2.putText(image, str(battle_selectable), (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        cv2.putText(image, str(battle_sub_selectable), (200, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        cv2.putText(image, str(nav_str), (200, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(image, str(exp_action_str), (200, 600), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        save_file = "object_detection_%d.jpg" % (image_count)
        image_count += 1
        cv2.imwrite(save_file, image)
