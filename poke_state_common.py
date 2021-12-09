import numpy as np
#from PIL import Image, ImageFont, ImageDraw

import os
#from opencv_yolo import YOLO

import enum

class NavigationAction(enum.Enum):
  STANDBY_CONSTRUCT_TEAM_INFO = 0   # Adds items to list for each pokemon that exists
  STANDBY_ADD_FIRST_POKEMON_INFO = 1  #Adds
  STANDBY_ADD_SECOND_POKEMON_INFO = 2
  STANDBY_ADD_THIRD_POKEMON_INFO = 3
  STANDBY_ADD_FOURTH_POKEMON_INFO = 4
  STANDBY_ADD_FIFTH_POKEMON_INFO = 5
  STANDBY_ADD_SIXTH_POKEMON_INFO = 6
  STANDBY_COUNT_ACTIVE_POKEMON = 7 # After counting active pokemon, add a STANDBY_CHECK_NEXT_ACTIVE for each to list
  STANDBY_CHECK_NEXT_ACTIVE = 8
  STANDBY_UPDATE_PP_USAGE = 9   # Not used? Can be updated when picking attack
  STANDBY_ACTIVATE_DYNAMAX = 10
  STANDBY_ATTACK_SLOT_1 = 11
  STANDBY_ATTACK_SLOT_2 = 12
  STANDBY_ATTACK_SLOT_3 = 13
  STANDBY_ATTACK_SLOT_4 = 14
  STANDBY_CHANGE_SLOT_1 = 15
  STANDBY_CHANGE_SLOT_2 = 16
  STANDBY_CHANGE_SLOT_3 = 17
  STANDBY_CHANGE_SLOT_4 = 18
  STANDBY_CHANGE_SLOT_5 = 19
  STANDBY_CHANGE_SLOT_6 = 20
  STANDBY_PEEK_TEAM_INFO = 21    # Used to update health
  STANDBY_STRUGGLE = 22    # Used to update health
  STANDBY_DYNAMAX_RECORD_MAX_MOVES = 23

  def get_supported_battle_states(self):
      if self == NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.TEAM_MENU, BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU]
      if self in [NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO]:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.TEAM_MENU, BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU, BATTLE_STATES.POKEMON_SUMMARY_INFO, BATTLE_STATES.POKEMON_SUMMARY_BASE_STATS, BATTLE_STATES.POKEMON_SUMMARY_ATTACKS]
      if self == NavigationAction.STANDBY_COUNT_ACTIVE_POKEMON:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.ACTIVE_MENU]
      if self == NavigationAction.STANDBY_CHECK_NEXT_ACTIVE:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.ACTIVE_MENU, BATTLE_STATES.ACTIVE_POKEMON_STATS]
      if self == NavigationAction.STANDBY_UPDATE_PP_USAGE:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.FIGHT_MENU]
      if self == NavigationAction.STANDBY_ACTIVATE_DYNAMAX:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.FIGHT_MENU]
      if self == NavigationAction.STANDBY_DYNAMAX_RECORD_MAX_MOVES:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.FIGHT_MENU]
      if self in [NavigationAction.STANDBY_ATTACK_SLOT_1, NavigationAction.STANDBY_ATTACK_SLOT_2, NavigationAction.STANDBY_ATTACK_SLOT_3, NavigationAction.STANDBY_ATTACK_SLOT_4]:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.FIGHT_MENU]
      if self in [NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.TEAM_MENU, BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU, BATTLE_STATES.TEAM_MENU_SWITCH_INFO]
      if self == NavigationAction.STANDBY_PEEK_TEAM_INFO:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.TEAM_MENU]
      if self == NavigationAction.STANDBY_STRUGGLE:
          return [BATTLE_STATES.STANDBY]

  def action_for_state(self, state, selectable, submenu=None):
      if state not in self.get_supported_battle_states():
          return BUTTON_ACTION.BACK_BUTTON

      # For shadow tag failure just dismiss and reject
      if self in [NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]:
          if state == BATTLE_STATES.TEAM_MENU_SWITCH_INFO:
              return BUTTON_ACTION.A_BUTTON

      if self in [NavigationAction.STANDBY_PEEK_TEAM_INFO, NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO, NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO, NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]:
          if selectable == BATTLE_SELECTABLES.STANDBY_FIGHT:
              return BUTTON_ACTION.DOWN_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_POKEMON:
              return BUTTON_ACTION.A_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_BAG:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_RUN:
              return BUTTON_ACTION.UP_BUTTON

      if selectable and self in [NavigationAction.STANDBY_ACTIVATE_DYNAMAX]:
          if selectable == BATTLE_SELECTABLES.STANDBY_FIGHT:
              return BUTTON_ACTION.A_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_POKEMON:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_BAG:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_RUN:
              return BUTTON_ACTION.UP_BUTTON

      if selectable and self in [NavigationAction.STANDBY_ATTACK_SLOT_1, NavigationAction.STANDBY_ATTACK_SLOT_2, NavigationAction.STANDBY_ATTACK_SLOT_3, NavigationAction.STANDBY_ATTACK_SLOT_4]:
          if selectable == BATTLE_SELECTABLES.STANDBY_FIGHT:
              return BUTTON_ACTION.A_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_POKEMON:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_BAG:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_RUN:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_DYNAMAX:
              return BUTTON_ACTION.RIGHT_BUTTON

          target_val = self.value - 11
          selected_val = selectable.value - 5
          if selected_val ==  target_val:
              return BUTTON_ACTION.A_BUTTON
          if selected_val >  target_val:
              return BUTTON_ACTION.UP_BUTTON
          if selected_val <  target_val:
              return BUTTON_ACTION.DOWN_BUTTON

      if self in [NavigationAction.STANDBY_UPDATE_PP_USAGE, NavigationAction.STANDBY_STRUGGLE, NavigationAction.STANDBY_DYNAMAX_RECORD_MAX_MOVES]:
          if selectable == BATTLE_SELECTABLES.STANDBY_FIGHT:
              return BUTTON_ACTION.A_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_POKEMON:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_BAG:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_RUN:
              return BUTTON_ACTION.UP_BUTTON

      #Pokemon team info page 1
      if state in [BATTLE_STATES.POKEMON_SUMMARY_INFO, BATTLE_STATES.POKEMON_SUMMARY_BASE_STATS]:
          return BUTTON_ACTION.RIGHT_BUTTON
      elif state == BATTLE_STATES.POKEMON_SUMMARY_ATTACKS:
          return BUTTON_ACTION.BACK_BUTTON

      if self in [NavigationAction.STANDBY_COUNT_ACTIVE_POKEMON]:
          if state == BATTLE_STATES.STANDBY:
              return BUTTON_ACTION.Y_BUTTON

      if self in [NavigationAction.STANDBY_CHECK_NEXT_ACTIVE]:
          if state == BATTLE_STATES.STANDBY:
              return BUTTON_ACTION.Y_BUTTON

          if state == BATTLE_STATES.ACTIVE_MENU:
              return BUTTON_ACTION.A_BUTTON

      if state == BATTLE_STATES.ACTIVE_POKEMON_STATS:
          return BUTTON_ACTION.R_BUTTON

      # make sure no submenu selected
      if submenu is not None:
          if self in [NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO]:
              if submenu == BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON:
                  return BUTTON_ACTION.DOWN_BUTTON
              if submenu == BATTLE_SUBMENU_SELECTABLES.CHECK_SUMMARY:
                  return BUTTON_ACTION.A_BUTTON
          if self in [NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]:
              if submenu == BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON:
                  return BUTTON_ACTION.A_BUTTON
#      if self in [NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO]:
      else:
          if selectable and self in [NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO]:
              # FOr pokemon info selection
              target_selected = self.value - 1
              selected_val = selectable.value - 9
#              print('selected_val, %d target_val: %d' % (selected_val, target_selected))
              if selected_val ==  target_selected:
                  return BUTTON_ACTION.A_BUTTON
              if selected_val < target_selected:
                  return BUTTON_ACTION.DOWN_BUTTON
              else:
                  return BUTTON_ACTION.UP_BUTTON
          if selectable and self in [NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]:
              # FOr pokemon info selection
              target_selected = self.value - 15
              selected_val = selectable.value - 9
#              print('selected_val, %d target_val: %d' % (selected_val, target_selected))
              if selected_val ==  target_selected:
                  return BUTTON_ACTION.A_BUTTON
              if selected_val < target_selected:
                  return BUTTON_ACTION.DOWN_BUTTON
              else:
                  return BUTTON_ACTION.UP_BUTTON

      if selectable and self in [NavigationAction.STANDBY_ATTACK_SLOT_1, NavigationAction.STANDBY_ATTACK_SLOT_2, NavigationAction.STANDBY_ATTACK_SLOT_3, NavigationAction.STANDBY_ATTACK_SLOT_4]:
          target_selected = self.value - 11
          selected_val = selectable.value - 5
          if selected_val ==  target_selected:
              return BUTTON_ACTION.A_BUTTON
          if selected_val < target_selected:
              return BUTTON_ACTION.DOWN_BUTTON
          else:
              return BUTTON_ACTION.UP_BUTTON

      if self == NavigationAction.STANDBY_ACTIVATE_DYNAMAX:
          if selectable in [BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1, BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2, BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3, BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4]:
              return BUTTON_ACTION.LEFT_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_DYNAMAX:
              return BUTTON_ACTION.A_BUTTON


      print('Not sure what to do, do nothing')
      return None

      print('emergency back')
      return BUTTON_ACTION.BACK_BUTTON
#registered names ['ゴチルゼル', 'ロトム', 'ドラパルト']
#サザフンドラ

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
    BATTLE_BEGIN = 11
    SWITCH_ERROR_MESSAGE = 12
    TEAM_MENU_SWITCH_INFO = 13
    PLAYER_DISCONNECT = 14
    EXPERIENCE_SCREEN = 15
    MESSAGE_NEEDS_ACTION = 16

    @staticmethod
    def state_for_label(label):
        state = None
        if label == 'standby':
            return BATTLE_STATES.STANDBY
        if label == 'attack_fight_menu':
            return BATTLE_STATES.FIGHT_MENU
        if label == 'active_menu':
            return BATTLE_STATES.ACTIVE_MENU
        if label == 'active_pokemon_info':
            return BATTLE_STATES.ACTIVE_POKEMON_STATS
        if label == 'team_menu':
            return BATTLE_STATES.TEAM_MENU
        if label == 'team_member_options_menu':
            return BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU
        if label == 'pokemon_summary_info':
            return BATTLE_STATES.POKEMON_SUMMARY_INFO
        if label == 'pokemon_summary_base_stats':
            return BATTLE_STATES.POKEMON_SUMMARY_BASE_STATS
        if label == 'pokemon_summary_attacks':
            return BATTLE_STATES.POKEMON_SUMMARY_ATTACKS
        if label in ['use_next_pokemon', 'trainer_switch_pokemon']:
            return BATTLE_STATES.MUST_SWITCH
        if label == 'wild_battle_over':
            return BATTLE_STATES.BATTLE_OVER
        if label in ['wild_pokemon_begin', 'surprise_wild_battle_begin']:
            return BATTLE_STATES.BATTLE_BEGIN
        if label == 'switch_error_message':
            return BATTLE_STATES.SWITCH_ERROR_MESSAGE
        if label == 'team_menu_info_switch':
            return BATTLE_STATES.TEAM_MENU_SWITCH_INFO
        if label in ['experience_gained_menu', 'level_up_box']:
            return BATTLE_STATES.EXPERIENCE_SCREEN
        if label == 'message_need_action':
            return BATTLE_STATES.MESSAGE_NEEDS_ACTION


        return state

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


    def get_name_rect(self):
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1:
            return (920, 440, 1118, 492)
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2:
            return (920, 510, 1118, 562)
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3:
            return (920, 580, 1118, 632)
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4:
            return (920, 650, 1118, 702)

        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1:
            return (138, 70, 317, 110)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2:
            return (138, 169, 317, 205)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3:
            return (138, 262, 317, 301)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4:
            return (138, 364, 317, 398)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5:
            return (138, 460, 317, 488)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6:
            return (138, 556, 317, 590)

        return None

    def get_life_rect(self):
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1:
            return (140, 120, 255, 152)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2:
            return (140, 216, 255, 248)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3:
            return (140, 310, 255, 344)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4:
            return (140, 407, 255, 442)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5:
            return (140, 502, 255, 533)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6:
            return (140, 598, 255, 628)

        return None

    def get_team_position(self):
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1:
            return 0
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2:
            return 1
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3:
            return 2
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4:
            return 3
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5:
            return 4
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6:
            return 5

        return -1

    # Used only for determining to invert colors on first
    # scanning names and HP
    def is_first_element(self):
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1:
            return True

        return False

    def get_pp_count_rect(self):
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1:
            return (1155, 441, 1252, 492)
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2:
            return (1155, 510, 1252, 560)
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3:
            return (1155, 580, 1252, 629)
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4:
            return (1155, 650, 1252, 699)
        return None

    def get_rect(self, network_match=False):
        if network_match:
            # Style, x1,y1, x2,y2
            if self == BATTLE_SELECTABLES.STANDBY_FIGHT:
                return (1039, 486, 1269, 558)
            if self == BATTLE_SELECTABLES.STANDBY_POKEMON:
                return (1039, 566, 1269, 638)
            if self == BATTLE_SELECTABLES.STANDBY_RUN:
                return (1039, 641, 1269, 713)
            if self == BATTLE_SELECTABLES.STANDBY_BAG:
                return (-1, -1, -1, -1)
        else:
            # Style, x1,y1, x2,y2
            if self == BATTLE_SELECTABLES.STANDBY_FIGHT:
                return (1039, 409, 1269, 481)
            if self == BATTLE_SELECTABLES.STANDBY_POKEMON:
                return (1039, 486, 1269, 558)
            if self == BATTLE_SELECTABLES.STANDBY_BAG:
                return (1039, 566, 1269, 638)
            if self == BATTLE_SELECTABLES.STANDBY_RUN:
                return (1039, 641, 1269, 713)

        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1:
            return (866, 437, 1272, 498)
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2:
            return (866, 502, 1272, 563)
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3:
            return (866, 574, 1272, 635)
        if self == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4:
            return (866, 644, 1272, 705)

        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1:
            return (57, 63, 449, 159)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2:
            return (57, 162, 449, 258)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3:
            return (57, 255, 449, 351)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4:
            return (57, 351, 449, 447)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5:
            return (57, 451, 449, 547)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6:
            return (57, 551, 449, 647)
        return None

    @staticmethod
    def get_item_for_rect(battle_state, rect, network_match=False):
        if battle_state == BATTLE_STATES.STANDBY:
            if calculate_overlap(rect, BATTLE_SELECTABLES.STANDBY_FIGHT.get_rect(network_match)) > 0.6:
                return BATTLE_SELECTABLES.STANDBY_FIGHT
            if calculate_overlap(rect, BATTLE_SELECTABLES.STANDBY_POKEMON.get_rect(network_match)) > 0.6:
                return BATTLE_SELECTABLES.STANDBY_POKEMON
            if calculate_overlap(rect, BATTLE_SELECTABLES.STANDBY_BAG.get_rect(network_match)) > 0.6:
                return BATTLE_SELECTABLES.STANDBY_BAG
            if calculate_overlap(rect, BATTLE_SELECTABLES.STANDBY_RUN.get_rect(network_match)) > 0.6:
                return BATTLE_SELECTABLES.STANDBY_RUN

        if battle_state == BATTLE_STATES.FIGHT_MENU :
            if calculate_overlap(BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1.get_rect(), rect) > 0.7:
                return BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1
            if calculate_overlap(BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2.get_rect(), rect) > 0.7:
                return BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2
            if calculate_overlap(BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3.get_rect(), rect) > 0.7:
                return BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3
            if calculate_overlap(BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4.get_rect(), rect) > 0.7:
                return BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4

        if battle_state in [BATTLE_STATES.TEAM_MENU, BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU] :
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1.get_rect()) > 0.6:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2.get_rect()) > 0.6:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3.get_rect()) > 0.6:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4.get_rect()) > 0.6:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5.get_rect()) > 0.6:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6.get_rect()) > 0.6:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6

        return None

    @staticmethod
    def get_item_for_network_rect(battle_state, rect):
        if battle_state in [NETWORK_STATES.NETWORK_PARTY_SELECT, NETWORK_STATES.NETWORK_PARTY_SELECT_OPTION_MENU] :
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1.get_network_rect()) > 0.5:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2.get_network_rect()) > 0.5:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3.get_network_rect()) > 0.5:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4.get_network_rect()) > 0.5:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5.get_network_rect()) > 0.5:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5
            if calculate_overlap(rect, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6.get_network_rect()) > 0.5:
                return BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6

        return None

    def get_network_rect(self):
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1:
            return (521, 33, 749, 112)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2:
            return (521, 126, 749, 211)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3:
            return (521, 226, 749, 305)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4:
            return (521, 325, 749, 404)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5:
            return (521, 417, 749, 496)
        if self == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6:
            return (521, 515, 749, 594)

        return None



class ACTIVE_STATS_INFORMATION(enum.Enum):
    ABILITY = 0
    ITEM = 1
    FIELD_MODIFIER_1 = 2
    FIELD_MODIFIER_2 = 3
    FIELD_MODIFIER_3 = 4
    FIELD_MODIFIER_4 = 5

    def get_name_rect(self):
        if self == ACTIVE_STATS_INFORMATION.ABILITY:
            return (864, 77, 1149, 119)
        if self == ACTIVE_STATS_INFORMATION.ITEM:
            return (864, 135, 1149, 178)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_1:
            return (706, 231, 1015, 272)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_2:
            return (706, 288, 1015, 329)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_3:
            return (706, 347, 1015, 388)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_4:
            return (706, 416, 1015, 445)
        return None

    def get_turn_count_rect(self):
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_1:
            return (1048, 232, 1149, 272)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_2:
            return (1048, 291, 1149, 331)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_3:
            return (1048, 347, 1149, 387)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_4:
            return (1048, 405, 1149, 445)
        return None

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == ACTIVE_STATS_INFORMATION.ABILITY:
            return (690, 71, 1172, 125)
        if self == ACTIVE_STATS_INFORMATION.ITEM:
            return (690, 130, 1172, 168)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_1:
            return (690, 225, 1172, 279)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_2:
            return (690, 284, 1172, 338)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_3:
            return (690, 334, 1172, 398)
        if self == ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_4:
            return (690, 395, 1172, 449)
        return None

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(rect, ACTIVE_STATS_INFORMATION.ABILITY.get_rect()) > 0.7:
            return ACTIVE_STATS_INFORMATION.ABILITY
        if calculate_overlap(rect, ACTIVE_STATS_INFORMATION.ITEM.get_rect()) > 0.7:
            return ACTIVE_STATS_INFORMATION.ITEM
        if calculate_overlap(rect, ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_1.get_rect()) > 0.7:
            return ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_1
        if calculate_overlap(rect, ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_2.get_rect()) > 0.7:
            return ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_2
        if calculate_overlap(rect, ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_3.get_rect()) > 0.7:
            return ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_3
        if calculate_overlap(rect, ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_4.get_rect()) > 0.7:
            return ACTIVE_STATS_INFORMATION.FIELD_MODIFIER_4

        return None

class ACTIVE_STATS_ELEMENT(enum.Enum):
    ELEMENT_SLOT_1 = 0
    ELEMENT_SLOT_2 = 1

    def get_name_rect(self, battle_state):
        if battle_state == BATTLE_STATES.ACTIVE_POKEMON_STATS:
            # Style, x1,y1, x2,y2
            if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1:
                return (307, 127, 400, 154)
            if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2:
                return (447, 127, 543, 154)
        if battle_state == BATTLE_STATES.POKEMON_SUMMARY_INFO:
            # Style, x1,y1, x2,y2
            if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1:
                return (340, 140, 432, 165)
            if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2:
                return (485, 140, 575, 164)

    def get_rect(self, battle_state):
        if battle_state == BATTLE_STATES.ACTIVE_POKEMON_STATS:
            # Style, x1,y1, x2,y2
            if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1:
                return (264, 121, 406, 159)
            if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2:
                return (409, 121, 551, 159)
        if battle_state == BATTLE_STATES.POKEMON_SUMMARY_INFO:
            # Style, x1,y1, x2,y2
            if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1:
                return (299, 136, 433, 168)
            if self == ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2:
                return (446, 138, 579, 167)

    @staticmethod
    def get_item_for_rect(rect, battle_state):
        if calculate_overlap(rect, ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1.get_rect(battle_state)) > 0.7:
            return ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_1
        if calculate_overlap(rect, ACTIVE_STATS_ELEMENT.ELEMENT_SLOT_2.get_rect(battle_state)) > 0.7:
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
        if calculate_overlap(rect, self.get_rect()) > 0.7:
            return True

        return False

class BATTLE_USE_NEXT_POKEMON_BOX(enum.Enum):
    USE_NEXT_POKEMON = 0
    RUN = 1

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == BATTLE_USE_NEXT_POKEMON_BOX.USE_NEXT_POKEMON:
            return (797, 464, 1045, 509)
        if self == BATTLE_USE_NEXT_POKEMON_BOX.RUN:
            return (797, 509, 1045, 554)

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(BATTLE_USE_NEXT_POKEMON_BOX.USE_NEXT_POKEMON.get_rect(), rect) > 0.7:
            return BATTLE_USE_NEXT_POKEMON_BOX.USE_NEXT_POKEMON
        if calculate_overlap(BATTLE_USE_NEXT_POKEMON_BOX.RUN.get_rect(), rect) > 0.7:
            return BATTLE_USE_NEXT_POKEMON_BOX.RUN

        return None

class BATTLE_TRAINER_SWITCH_POKEMON_BOX(enum.Enum):
    SWITCH_POKEMON = 0
    KEEP_CURRENT_POKEMON = 1

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == BATTLE_TRAINER_SWITCH_POKEMON_BOX.SWITCH_POKEMON:
            return (756, 459, 1049, 509)
        if self == BATTLE_TRAINER_SWITCH_POKEMON_BOX.KEEP_CURRENT_POKEMON:
            return (756, 507, 1049, 553)

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(BATTLE_TRAINER_SWITCH_POKEMON_BOX.SWITCH_POKEMON.get_rect(), rect) > 0.7:
            return BATTLE_TRAINER_SWITCH_POKEMON_BOX.SWITCH_POKEMON
        if calculate_overlap(BATTLE_TRAINER_SWITCH_POKEMON_BOX.KEEP_CURRENT_POKEMON.get_rect(), rect) > 0.7:
            return BATTLE_TRAINER_SWITCH_POKEMON_BOX.KEEP_CURRENT_POKEMON

        return None




def calculate_overlap(rect_1, rect_2):
    XA2 = rect_1[2]
    XB2 = rect_2[2]
    XA1 = rect_1[0]
    XB1 = rect_2[0]

    YA2 = rect_1[3]
    YB2 = rect_2[3]
    YA1 = rect_1[1]
    YB1 = rect_2[1]
    # overlap between A and B
    SA = (rect_1[2] - rect_1[0]) * (rect_1[3] - rect_1[1])
    SB = (rect_2[2] - rect_2[0]) * (rect_2[3] - rect_2[1])

    SI = max(0, 1+ min(XA2, XB2) - max(XA1, XB1)) * max(0, 1 + min(YA2, YB2) - max(YA1, YB1))
    SU = SA + SB - SI
    if float(SA) == 0.0:
        return 0
    return SI/float(SA)

class BATTLE_SUBMENU_SELECTABLES(enum.Enum):
    SWAP_POKEMON = 0
    CHECK_SUMMARY = 1
    RESTORE = 2
    CANCEL = 3

    def get_base_position(self, battle_selectable, mini=False):
        if not mini:
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1:
                return (449, 123, 655, 171)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2:
                return (449, 221, 655, 264)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3:
                return (449, 321, 655, 359)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4:
                return (449, 413, 655, 454)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5:
                return (449, 322, 655, 357)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6:
                return (449, 411, 655, 456)
        else:
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1:
                return (449, 123, 655, 171)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2:
                return (449, 221, 655, 264)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3:
                return (449, 321, 655, 359)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4:
                return (449, 409, 655, 456)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5:
                return (449, 507, 655, 554)
            if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6:
                return (449, 452, 655, 497)

        return (-1,-1,-1,-1)

    def get_rect(self, battle_selectable, mini=False):
        x1, y1, x2, y2 = self.get_base_position(battle_selectable, mini)
        if self == BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON:
            return (x1, y1, x2, y2)
        if self == BATTLE_SUBMENU_SELECTABLES.CHECK_SUMMARY:
            return (x1, y1+40, x2, y2+40)
        if self == BATTLE_SUBMENU_SELECTABLES.RESTORE:
            return (x1, y1+80, x2, y2+80)
        if self == BATTLE_SUBMENU_SELECTABLES.CANCEL:
            return (x1, y1+120, x2, y2+120)

    @staticmethod
    def get_item_for_rect(battle_state, battle_selectable, rect, mini=False):
        if battle_state in [BATTLE_STATES.TEAM_MENU, BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU]:
            if calculate_overlap(rect, BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON.get_rect(battle_selectable, mini)) > 0.7:
                return BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON
            if calculate_overlap(rect, BATTLE_SUBMENU_SELECTABLES.CHECK_SUMMARY.get_rect(battle_selectable, mini)) > 0.7:
                return BATTLE_SUBMENU_SELECTABLES.CHECK_SUMMARY
            if calculate_overlap(rect, BATTLE_SUBMENU_SELECTABLES.RESTORE.get_rect(battle_selectable, mini)) > 0.7:
                return BATTLE_SUBMENU_SELECTABLES.RESTORE
            if calculate_overlap(rect, BATTLE_SUBMENU_SELECTABLES.CANCEL.get_rect(battle_selectable, mini)) > 0.7:
                return BATTLE_SUBMENU_SELECTABLES.CANCEL

        return None

class NETWORK_BATTLE_SUBMENU_SELECTABLES(enum.Enum):
    ENTER = 0
    CHECK_SUMMARY = 1
    BACK = 2

    def get_base_position(self, battle_selectable):
        if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1:
            return (830, 84, 1037, 129)
        if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2:
            return (830, 181, 1037, 225)
        if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3:
            return (830, 275, 1037, 322)
        if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4:
            return (830, 373, 1037, 415)
        if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5:
            return (830, 466, 1037, 513)
        if battle_selectable == BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6:
            return (830, 411, 1037, 452)

        return (-1,-1,-1,-1)

    def get_rect(self, battle_selectable):
        x1, y1, x2, y2 = self.get_base_position(battle_selectable)
        if self == NETWORK_BATTLE_SUBMENU_SELECTABLES.ENTER:
            return (x1, y1, x2, y2)
        if self == NETWORK_BATTLE_SUBMENU_SELECTABLES.CHECK_SUMMARY:
            return (x1, y1+40, x2, y2+40)
        if self == NETWORK_BATTLE_SUBMENU_SELECTABLES.BACK:
            return (x1, y1+80, x2, y2+80)

    @staticmethod
    def get_item_for_rect(battle_selectable, rect):
        if calculate_overlap(NETWORK_BATTLE_SUBMENU_SELECTABLES.ENTER.get_rect(battle_selectable), rect) > 0.7:
            return NETWORK_BATTLE_SUBMENU_SELECTABLES.ENTER
        if calculate_overlap(NETWORK_BATTLE_SUBMENU_SELECTABLES.CHECK_SUMMARY.get_rect(battle_selectable), rect) > 0.7:
            return NETWORK_BATTLE_SUBMENU_SELECTABLES.CHECK_SUMMARY
        if calculate_overlap(NETWORK_BATTLE_SUBMENU_SELECTABLES.BACK.get_rect(battle_selectable), rect) > 0.7:
            return NETWORK_BATTLE_SUBMENU_SELECTABLES.BACK

        return None

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

    def serial_rep(self):
        if self == BUTTON_ACTION.A_BUTTON:
            return 'Button A'
        if self == BUTTON_ACTION.Y_BUTTON:
            return 'Button Y'
        if self == BUTTON_ACTION.R_BUTTON:
            return 'Button R'
        if self == BUTTON_ACTION.L_BUTTON:
            return 'Button L'
        if self == BUTTON_ACTION.BACK_BUTTON:
            return 'Button B'
        if self == BUTTON_ACTION.LEFT_BUTTON:
            return 'LX MIN'
        if self == BUTTON_ACTION.RIGHT_BUTTON:
            return 'LX MAX'
        if self == BUTTON_ACTION.DOWN_BUTTON:
            return 'LY MAX'
        if self == BUTTON_ACTION.UP_BUTTON:
            return 'LY MIN'

class BATTLE_ACTIVE_POKEMON_BOX(enum.Enum):
    PLAYER_ACTIVE_BOX_A = 0
    PLAYER_ACTIVE_BOX_B = 1
    ENEMY_ACTIVE_BOX_A = 2
    ENEMY_ACTIVE_BOX_B = 3

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == BATTLE_ACTIVE_POKEMON_BOX.PLAYER_ACTIVE_BOX_A:
            return (1, 622, 295, 695)
        if self == BATTLE_ACTIVE_POKEMON_BOX.ENEMY_ACTIVE_BOX_A:
            return (973, 23, 1280, 85)
        return None

    # Will need fine tuning
    def get_health_rect(self):
        # Style, x1,y1, x2,y2
        if self == BATTLE_ACTIVE_POKEMON_BOX.PLAYER_ACTIVE_BOX_A:
            return (15, 657, 282, 664)
        if self == BATTLE_ACTIVE_POKEMON_BOX.ENEMY_ACTIVE_BOX_A:
            return (979, 63, 1245, 73)
        return None

    # Will need fine tuning
    def get_health_ratio_rect(self):
        # Style, x1,y1, x2,y2
        if self == BATTLE_ACTIVE_POKEMON_BOX.PLAYER_ACTIVE_BOX_A:
            return (86, 667, 185, 694)
        return None

    # Will need fine tuning
    def get_name_gender_rect(self):
        # Style, x1,y1, x2,y2
        if self == BATTLE_ACTIVE_POKEMON_BOX.PLAYER_ACTIVE_BOX_A:
            return (15, 618, 207, 654)
        if self == BATTLE_ACTIVE_POKEMON_BOX.ENEMY_ACTIVE_BOX_A:
            return (978, 29, 1124, 61)
        return None

    # Will need fine tuning
    def get_level_rect(self):
        # Style, x1,y1, x2,y2
        if self == BATTLE_ACTIVE_POKEMON_BOX.PLAYER_ACTIVE_BOX_A:
            return (234, 622, 352, 654)
        if self == BATTLE_ACTIVE_POKEMON_BOX.ENEMY_ACTIVE_BOX_A:
            return (1152, 23, 1263, 57)
        return None

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(rect, BATTLE_ACTIVE_POKEMON_BOX.PLAYER_ACTIVE_BOX_A.get_rect()) > 0.7:
            return BATTLE_ACTIVE_POKEMON_BOX.PLAYER_ACTIVE_BOX_A
        if calculate_overlap(rect, BATTLE_ACTIVE_POKEMON_BOX.ENEMY_ACTIVE_BOX_A.get_rect()) > 0.7:
            return BATTLE_ACTIVE_POKEMON_BOX.ENEMY_ACTIVE_BOX_A

        return None

class BASE_STATS_SCREEN(enum.Enum):
    HP = 0
    SP_ATK = 1
    ATTACK = 2
    SP_DEF = 3
    DEFENSE = 4
    SPEED = 5
    ABILITY = 6

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == BASE_STATS_SCREEN.HP:
            return (249, 121, 380, 154)
        if self == BASE_STATS_SCREEN.SP_ATK:
            return (134, 208, 192, 243)
        if self == BASE_STATS_SCREEN.ATTACK:
            return (416, 204, 496, 245)
        if self == BASE_STATS_SCREEN.SP_DEF:
            return (134, 297, 192, 332)
        if self == BASE_STATS_SCREEN.DEFENSE:
            return (414, 294, 492, 337)
        if self == BASE_STATS_SCREEN.SPEED:
            return (273, 387, 340, 419)
        if self == BASE_STATS_SCREEN.ABILITY:
            return (278, 511, 570, 550)


class ATTACKS_SCREEN(enum.Enum):
    ATTACK_SLOT_1 = 0
    ATTACK_SLOT_2 = 1
    ATTACK_SLOT_3 = 2
    ATTACK_SLOT_4 = 3

    def get_name_rect(self):
        if self == ATTACKS_SCREEN.ATTACK_SLOT_1:
            return (61, 91, 333, 136)
        if self == ATTACKS_SCREEN.ATTACK_SLOT_2:
            return (61, 156, 333, 201)
        if self == ATTACKS_SCREEN.ATTACK_SLOT_3:
            return (61, 216, 333, 261)
        if self == ATTACKS_SCREEN.ATTACK_SLOT_4:
            return (61, 281, 333, 326)
        return None

    def get_pp_count_rect(self):
        if self == ATTACKS_SCREEN.ATTACK_SLOT_1:
            return (507, 88, 594, 138)
        if self == ATTACKS_SCREEN.ATTACK_SLOT_2:
            return (507, 151, 594, 201)
        if self == ATTACKS_SCREEN.ATTACK_SLOT_3:
            return (507, 214, 594, 264)
        if self == ATTACKS_SCREEN.ATTACK_SLOT_4:
            return (507, 275, 594, 325)
        return None

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == ATTACKS_SCREEN.ATTACK_SLOT_1:
            return (334, 84, 507, 143)
        if self == ATTACKS_SCREEN.ATTACK_SLOT_2:
            return (334, 147, 507, 206)
        if self == ATTACKS_SCREEN.ATTACK_SLOT_3:
            return (334, 209, 507, 266)
        if self == ATTACKS_SCREEN.ATTACK_SLOT_4:
            return (334, 271, 507, 329)
        return None

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(rect, ATTACKS_SCREEN.ATTACK_SLOT_1.get_rect()) > 0.7:
            return ATTACKS_SCREEN.ATTACK_SLOT_1
        if calculate_overlap(rect, ATTACKS_SCREEN.ATTACK_SLOT_2.get_rect()) > 0.7:
            return ATTACKS_SCREEN.ATTACK_SLOT_2
        if calculate_overlap(rect, ATTACKS_SCREEN.ATTACK_SLOT_3.get_rect()) > 0.7:
            return ATTACKS_SCREEN.ATTACK_SLOT_3
        if calculate_overlap(rect, ATTACKS_SCREEN.ATTACK_SLOT_4.get_rect()) > 0.7:
            return ATTACKS_SCREEN.ATTACK_SLOT_4

        return None

# Check if item exists first
class SUMMARY_INFO_SCREEN(enum.Enum):
    NAME = 0
    ITEM = 1

    def get_name_rect(self):
        if self == SUMMARY_INFO_SCREEN.NAME:
            return (279, 85, 524, 125)
        if self == SUMMARY_INFO_SCREEN.ITEM:
            return (348, 440, 541, 475)
        return None

class ACTIVE_INFO_NAME_STATUS(enum.Enum):
    NAME = 0
    STATUS = 1
    TRAINER = 2
    LEVEL = 3

    def get_name_rect(self):
        if self == ACTIVE_INFO_NAME_STATUS.NAME:
            return (258, 60, 516, 124)
        if self == ACTIVE_INFO_NAME_STATUS.STATUS:
            return (583, 161, 674, 186)
        if self == ACTIVE_INFO_NAME_STATUS.TRAINER:
            return (12, 629, 204, 665)
        if self == ACTIVE_INFO_NAME_STATUS.LEVEL:
            return (102, 156, 226, 192)
        return None


class MESSAGE_ABILITY_REVEALED(enum.Enum):
    MESSAGE = 0
    PLAYER_ABILITY = 1
    ENEMY_ABILITY = 2

    def get_communicating_rect(self):
        # Style, x1,y1, x2,y2
        if self == MESSAGE_ABILITY_REVEALED.MESSAGE:
            return (1196, 650, 1232, 688)

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == MESSAGE_ABILITY_REVEALED.MESSAGE:
            return (106, 585, 1140, 688)
        if self == MESSAGE_ABILITY_REVEALED.PLAYER_ABILITY:
            return (18, 317, 300, 404)
        if self == MESSAGE_ABILITY_REVEALED.ENEMY_ABILITY:
            return (990, 318, 1269, 404)

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(MESSAGE_ABILITY_REVEALED.MESSAGE.get_rect(), rect) > 0.7:
            return MESSAGE_ABILITY_REVEALED.MESSAGE
        if calculate_overlap(MESSAGE_ABILITY_REVEALED.PLAYER_ABILITY.get_rect(), rect) > 0.7:
            return MESSAGE_ABILITY_REVEALED.PLAYER_ABILITY
        if calculate_overlap(MESSAGE_ABILITY_REVEALED.ENEMY_ABILITY.get_rect(), rect) > 0.7:
            return MESSAGE_ABILITY_REVEALED.ENEMY_ABILITY

        return None

class TEAM_MENU_SWITCH_INFO(enum.Enum):
    MESSAGE = 0

    def get_message_rect(self):
        if self == TEAM_MENU_SWITCH_INFO.MESSAGE:
            return (631, 580, 1217, 667)
        return None

class DISCONNECT_MESSAGE(enum.Enum):
    OK_BOX = 0

    def get_message_rect(self):
        if self == DISCONNECT_MESSAGE.OK_BOX:
            return (256, 442, 1016, 507)
        return None


class RENTAL_TEAM_MENU(enum.Enum):
    CENTER = 0

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == RENTAL_TEAM_MENU.CENTER:
            return (493, 36, 786, 571)

    def get_name_rect(self):
        if self == RENTAL_TEAM_MENU.CENTER:
            return (506, 42, 773, 76)
        return None

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(RENTAL_TEAM_MENU.CENTER.get_rect(), rect) > 0.7:
            return RENTAL_TEAM_MENU.CENTER

        return None

class CONTINUE_BATTLING_DIALOG(enum.Enum):
    CONTINUE_BATTLING = 0
    SWITCH_BATTLE_TEAMS = 1
    QUIT_BATTLING = 2

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == CONTINUE_BATTLING_DIALOG.CONTINUE_BATTLING:
            return (792, 425, 1051, 471)
        if self == CONTINUE_BATTLING_DIALOG.SWITCH_BATTLE_TEAMS:
            return (792, 467, 1051, 513)
        if self == CONTINUE_BATTLING_DIALOG.QUIT_BATTLING:
            return (792, 506, 1051, 552)

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(CONTINUE_BATTLING_DIALOG.CONTINUE_BATTLING.get_rect(), rect) > 0.6:
            return CONTINUE_BATTLING_DIALOG.CONTINUE_BATTLING
        if calculate_overlap(CONTINUE_BATTLING_DIALOG.SWITCH_BATTLE_TEAMS.get_rect(), rect) > 0.6:
            return CONTINUE_BATTLING_DIALOG.SWITCH_BATTLE_TEAMS
        if calculate_overlap(CONTINUE_BATTLING_DIALOG.QUIT_BATTLING.get_rect(), rect) > 0.6:
            return CONTINUE_BATTLING_DIALOG.QUIT_BATTLING

        return None


class CONTINUE_TEAM_DIALOG(enum.Enum):
    YES = 0
    NO = 1

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == CONTINUE_TEAM_DIALOG.YES:
            return (873, 461, 1048, 511)
        if self == CONTINUE_TEAM_DIALOG.NO:
            return (873, 503, 1048, 553)

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(CONTINUE_TEAM_DIALOG.YES.get_rect(), rect) > 0.7:
            return CONTINUE_TEAM_DIALOG.YES
        if calculate_overlap(CONTINUE_TEAM_DIALOG.NO.get_rect(), rect) > 0.7:
            return CONTINUE_TEAM_DIALOG.NO

        return None


class BATTLE_FORMAT(enum.Enum):
    SINGLE_BATTLE = 0
    DOUBLE_BATTLE = 1

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == BATTLE_FORMAT.SINGLE_BATTLE:
            return (338, 197, 949, 285)
        if self == BATTLE_FORMAT.DOUBLE_BATTLE:
            return (338, 287, 949, 375)

    @staticmethod
    def get_item_for_rect(rect):
        if calculate_overlap(BATTLE_FORMAT.SINGLE_BATTLE.get_rect(), rect) > 0.7:
            return BATTLE_FORMAT.SINGLE_BATTLE
        if calculate_overlap(BATTLE_FORMAT.DOUBLE_BATTLE.get_rect(), rect) > 0.7:
            return BATTLE_FORMAT.DOUBLE_BATTLE

        return None

class ONLINE_MESSAGE(enum.Enum):
    MESSAGE = 0

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == ONLINE_MESSAGE.MESSAGE:
            return (349, 576, 906, 675)

class ONLINE_TEAM_PICK_DONE(enum.Enum):
    DONE = 0

    def get_rect(self):
        # Style, x1,y1, x2,y2
        if self == ONLINE_TEAM_PICK_DONE.DONE:
            return (489, 612, 801, 663)


class NetworkNavigationAction(enum.Enum):
    NAVIGATE_TO_TEAM_SELECTION = 0   # Adds items to list for each pokemon that exists
    FIND_NEXT_TEAM = 1  #Adds
    SELECT_CURRENT_TEAM = 2
    PARTY_COUNT_POKEMON = 3 # After counting active pokemon, add a STANDBY_CHECK_NEXT_ACTIVE for each to list
    PARTY_ADD_FIRST_POKEMON = 4
    PARTY_ADD_SECOND_POKEMON = 5
    PARTY_ADD_THIRD_POKEMON = 6
    PARTY_ADD_FOURTH_POKEMON = 7
    PARTY_ADD_FIFTH_POKEMON = 8
    PARTY_ADD_SIXTH_POKEMON = 9
    QUEUE_MATCH = 10


    # This style currently is only forward going
    # No need to support a back button
    def action_for_state(self, state, selectable, submenu=None):

        # Handle sudden disconnect
        if state == NETWORK_STATES.NETWORK_PLAYER_DISCONNECT:
            return BUTTON_ACTION.A_BUTTON

        # Handle needs action dropdown
        if state == NETWORK_STATES.MESSAGE_NEEDS_ACTION:
            return BUTTON_ACTION.A_BUTTON

        # Retry with same team
        if self in [NetworkNavigationAction.PARTY_COUNT_POKEMON]:
            # Assume on first option for main menu
            if state == NETWORK_STATES.NETWORK_CONTINUE_BATTLING:
                if selectable == CONTINUE_BATTLING_DIALOG.CONTINUE_BATTLING:
                    return BUTTON_ACTION.A_BUTTON
                if selectable == CONTINUE_BATTLING_DIALOG.SWITCH_BATTLE_TEAMS:
                    return BUTTON_ACTION.UP_BUTTON


        if self in [NetworkNavigationAction.NAVIGATE_TO_TEAM_SELECTION, NetworkNavigationAction.FIND_NEXT_TEAM, NetworkNavigationAction.SELECT_CURRENT_TEAM]:
            # Assume on first option for main menu
            if state in [NETWORK_STATES.NETWORK_MAIN_MENU, NETWORK_STATES.VS_MENU_OPTION, NETWORK_STATES.BATTLE_STADIUM_MENU_OPTION]:
                return BUTTON_ACTION.A_BUTTON

            # Assume on first option for main menu
            if state == NETWORK_STATES.NETWORK_BATTLE_TYPE_SELECT:
                return BUTTON_ACTION.A_BUTTON

            # Assume on first option for main menu
            if state == NETWORK_STATES.NETWORK_CONTINUE_BATTLING:
                if selectable == CONTINUE_BATTLING_DIALOG.CONTINUE_BATTLING:
                    return BUTTON_ACTION.DOWN_BUTTON
                if selectable == CONTINUE_BATTLING_DIALOG.SWITCH_BATTLE_TEAMS:
                    return BUTTON_ACTION.A_BUTTON


        # Retry with same team
        if self in [NetworkNavigationAction.QUEUE_MATCH]:
            # Assume on first is done and selected
            if state in [NETWORK_STATES.NETWORK_PARTY_SELECT, NETWORK_STATES.NETWORK_PARTY_DONE]:
                return BUTTON_ACTION.A_BUTTON



        if self == NetworkNavigationAction.FIND_NEXT_TEAM:
            # Assume on first option for main menu
            if state == NETWORK_STATES.NETWORK_TEAM_SELECT:
                return BUTTON_ACTION.RIGHT_BUTTON

        if self == NetworkNavigationAction.SELECT_CURRENT_TEAM:
            # Assume on first option for main menu
            if state == NETWORK_STATES.NETWORK_TEAM_SELECT:
                return BUTTON_ACTION.A_BUTTON

            if state == NETWORK_STATES.NETWORK_TEAM_SELECT_OPTION_MENU:
                return BUTTON_ACTION.A_BUTTON

        if self in [NetworkNavigationAction.PARTY_ADD_FIRST_POKEMON, NetworkNavigationAction.PARTY_ADD_SECOND_POKEMON, NetworkNavigationAction.PARTY_ADD_THIRD_POKEMON, NetworkNavigationAction.PARTY_ADD_FOURTH_POKEMON, NetworkNavigationAction.PARTY_ADD_FIFTH_POKEMON, NetworkNavigationAction.PARTY_ADD_SIXTH_POKEMON]:
            if state in [NETWORK_STATES.NETWORK_PARTY_SELECT, NETWORK_STATES.NETWORK_PARTY_SELECT_OPTION_MENU]:
                if selectable is None:
                    return None

                # make sure no submenu selected
                if submenu is not None:
                    return BUTTON_ACTION.A_BUTTON
                #      if self in [NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO]:
                else:
                    # FOr pokemon info selection
                    target_selected = self.value - 4
                    selected_val = selectable.value - 9
                    #              print('selected_val, %d target_val: %d' % (selected_val, target_selected))
                    if selected_val ==  target_selected:
                        return BUTTON_ACTION.A_BUTTON
                    if selected_val < target_selected:
                        return BUTTON_ACTION.DOWN_BUTTON
                    else:
                        return BUTTON_ACTION.UP_BUTTON

        return None


class NETWORK_STATES(enum.Enum):
    VS_MENU_OPTION = 0
    BATTLE_STADIUM_MENU_OPTION = 1
    NETWORK_MAIN_MENU = 2
    NETWORK_BATTLE_TYPE_SELECT = 3
    NETWORK_TEAM_SELECT = 4
    NETWORK_TEAM_SELECT_OPTION_MENU = 5
    NETWORK_WAITING_ROOM = 6
    NETWORK_PARTY_SELECT = 7
    NETWORK_PARTY_SELECT_OPTION_MENU = 8
    NETWORK_PREMATCH_TEAMS_PREVIEW_SELECT = 9
    NETWORK_CONTINUE_BATTLING = 10
    NETWORK_PLAYER_DISCONNECT = 11
    MESSAGE_NEEDS_ACTION = 12
    NETWORK_PARTY_DONE = 13

    @staticmethod
    def state_for_label(label):
        state = None
        if label == 'vs_menu_option':
            return NETWORK_STATES.VS_MENU_OPTION
        if label == 'battle_stadium_menu_option':
            return NETWORK_STATES.BATTLE_STADIUM_MENU_OPTION
        if label == 'network_main_menu':
            return NETWORK_STATES.NETWORK_MAIN_MENU
        if label == 'match_style_menu':
            return NETWORK_STATES.NETWORK_BATTLE_TYPE_SELECT
        if label == 'team_pick_options_menu':
            return NETWORK_STATES.NETWORK_TEAM_SELECT_OPTION_MENU
        if label == 'team_pick_preview':
            return NETWORK_STATES.NETWORK_TEAM_SELECT
        if label == 'waiting_room':
            return NETWORK_STATES.NETWORK_WAITING_ROOM
        if label == 'network_party_select_options':
            return NETWORK_STATES.NETWORK_PARTY_SELECT_OPTION_MENU
        if label == 'network_party_select':
            return NETWORK_STATES.NETWORK_PARTY_SELECT
        if label == 'match_about_to_begin':
            return NETWORK_STATES.NETWORK_PREMATCH_TEAMS_PREVIEW_SELECT
        if label == 'continue_battling_options_menu':
            return NETWORK_STATES.NETWORK_CONTINUE_BATTLING
        if label == 'communication_error':
            return NETWORK_STATES.NETWORK_PLAYER_DISCONNECT
        if label == 'message_need_action':
            return NETWORK_STATES.MESSAGE_NEEDS_ACTION
        if label == 'network_party_done_selected':
            return NETWORK_STATES.NETWORK_PARTY_DONE

        return state


class NETWORK_SELECTABLE(enum.Enum):
    NETWORK_EMPTY_TEAM = 0
    NETWORK_AVAILABLE_TEAM = 1
    NETWORK_CONTINUE_BATTLING = 2

    @staticmethod
    def state_for_label(label):
        state = None
        if label == 'network_main_menu':
            return NETWORK_SELECTABLE.NETWORK_EMPTY_TEAM
        if label == 'match_style_menu':
            return NETWORK_SELECTABLE.NETWORK_AVAILABLE_TEAM

        return state


class NETWORK_SUBMENU_SELECTABLE(enum.Enum):
    NETWORK_EMPTY_TEAM = 0
    NETWORK_AVAILABLE_TEAM = 1

    @staticmethod
    def state_for_label(label):
        state = None
        if label == 'network_main_menu':
            return NETWORK_SELECTABLE.NETWORK_EMPTY_TEAM
        if label == 'match_style_menu':
            return NETWORK_SELECTABLE.NETWORK_AVAILABLE_TEAM

        return state
