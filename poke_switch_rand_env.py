import enum
import switch_button_press
from time import sleep


class BattleAction(enum.Enum):
  Attack_Slot_1 = 0
  Attack_Slot_2 = 1
  Attack_Slot_3 = 2
  Attack_Slot_4 = 3
  Attack_Z_Slot_1 = 4
  Attack_Z_Slot_2 = 5
  Attack_Z_Slot_3 = 6
  Attack_Z_Slot_4 = 7
  Attack_Mega_Slot_1 = 8
  Attack_Mega_Slot_2 = 9
  Attack_Mega_Slot_3 = 10
  Attack_Mega_Slot_4 = 11
  Attack_Ultra_Slot_1 = 12
  Attack_Ultra_Slot_2 = 13
  Attack_Ultra_Slot_3 = 14
  Attack_Ultra_Slot_4 = 15
  Change_Slot_1 = 16
  Change_Slot_2 = 17
  Change_Slot_3 = 18
  Change_Slot_4 = 19
  Change_Slot_5 = 20
  Change_Slot_6 = 21
  Attack_Struggle = 22
  Shift_Left = 23           # Triples Only
  Shift_Right = 24          # Triples Only
  Not_Decided = 25          # position hasn't been decided yet


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
          return [BATTLE_STATES.STANDBY]
      if self in [NavigationAction.STANDBY_ATTACK_SLOT_1, NavigationAction.STANDBY_ATTACK_SLOT_2, NavigationAction.STANDBY_ATTACK_SLOT_3, NavigationAction.STANDBY_ATTACK_SLOT_4]:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.FIGHT_MENU]
      if self in [NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]:
          return [BATTLE_STATES.STANDBY, BATTLE_STATES.TEAM_MENU, BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU]

  def action_for_state(self, state, selectable, submenu=None):
      if state not in self.get_supported_battle_states():
          return BUTTON_ACTION.BACK_BUTTON

      if self in [NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO]:
          if selectable == BATTLE_SELECTABLES.STANDBY_FIGHT:
              return BUTTON_ACTION.DOWN_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_POKEMON:
              return BUTTON_ACTION.A_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_BAG:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_RUN:
              return BUTTON_ACTION.UP_BUTTON

      if self in [NavigationAction.STANDBY_ATTACK_SLOT_1, NavigationAction.STANDBY_ATTACK_SLOT_2, NavigationAction.STANDBY_ATTACK_SLOT_3, NavigationAction.STANDBY_ATTACK_SLOT_4]:
          if selectable == BATTLE_SELECTABLES.STANDBY_FIGHT:
              return BUTTON_ACTION.A_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_POKEMON:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_BAG:
              return BUTTON_ACTION.UP_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_RUN:
              return BUTTON_ACTION.UP_BUTTON

          target_val = self.value - 11
          selected_val = selectable.value - 5
          if selected_val ==  target_val:
              return BUTTON_ACTION.A_BUTTON
          if selected_val >  target_val:
              return BUTTON_ACTION.UP_BUTTON
          if selected_val <  target_val:
              return BUTTON_ACTION.DOWN_BUTTON

      if self in [NavigationAction.STANDBY_UPDATE_PP_USAGE]:
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
          if self in [NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO, NavigationAction.STANDBY_ADD_SECOND_POKEMON_INFO, NavigationAction.STANDBY_ADD_THIRD_POKEMON_INFO, NavigationAction.STANDBY_ADD_FOURTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_FIFTH_POKEMON_INFO, NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO]:
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
          if self in [NavigationAction.STANDBY_CHANGE_SLOT_1, NavigationAction.STANDBY_CHANGE_SLOT_2, NavigationAction.STANDBY_CHANGE_SLOT_3, NavigationAction.STANDBY_CHANGE_SLOT_4, NavigationAction.STANDBY_CHANGE_SLOT_5, NavigationAction.STANDBY_CHANGE_SLOT_6]:
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

      if self in [NavigationAction.STANDBY_ATTACK_SLOT_1, NavigationAction.STANDBY_ATTACK_SLOT_2, NavigationAction.STANDBY_ATTACK_SLOT_3, NavigationAction.STANDBY_ATTACK_SLOT_4]:
          target_selected = self.value - 11
          selected_val = selectable.value - 5
          if selected_val ==  target_selected:
              return BUTTON_ACTION.A_BUTTON
          if selected_val < target_selected:
              return BUTTON_ACTION.DOWN_BUTTON
          else:
              return BUTTON_ACTION.UP_BUTTON

      if self == NavigationAction.STANDBY_ACTIVATE_DYNAMAX:
          if selectable in [BATTLE_SELECTABLES.STANDBY_FIGHT, BATTLE_SELECTABLES.STANDBY_POKEMON, BATTLE_SELECTABLES.STANDBY_BAG, BATTLE_SELECTABLES.STANDBY_RUN]:
              return BUTTON_ACTION.LEFT_BUTTON
          if selectable == BATTLE_SELECTABLES.STANDBY_DYNAMAX:
              return BUTTON_ACTION.A_BUTTON

      print('emergency back')
      return BUTTON_ACTION.BACK_BUTTON


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

class BATTLE_SUBMENU_SELECTABLES(enum.Enum):
    SWAP_POKEMON = 0
    CHECK_SUMMARY = 1
    RESTORE = 2
    CANCEL = 3

def simulate_button_press(state, selectable, submenu, button_action, nav_action=None):
    next_state = state
    next_selectable = selectable
    submenu_selectable = submenu
    done = False

    # Fight options
    if selectable == BATTLE_SELECTABLES.STANDBY_FIGHT:
        if button_action == BUTTON_ACTION.A_BUTTON:
            next_state = BATTLE_STATES.FIGHT_MENU
            next_selectable = BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1
        if button_action == BUTTON_ACTION.LEFT_BUTTON:
            next_selectable = BATTLE_SELECTABLES.STANDBY_DYNAMAX
        if button_action == BUTTON_ACTION.DOWN_BUTTON:
            next_selectable = BATTLE_SELECTABLES.STANDBY_POKEMON
    # Pokemon options
    if selectable == BATTLE_SELECTABLES.STANDBY_POKEMON:
        if button_action == BUTTON_ACTION.A_BUTTON:
            next_state = BATTLE_STATES.TEAM_MENU
            next_selectable = BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1
            count_team_pokemon()
            done = True
        if button_action == BUTTON_ACTION.LEFT_BUTTON:
            next_selectable = BATTLE_SELECTABLES.STANDBY_DYNAMAX
        if button_action == BUTTON_ACTION.UP_BUTTON:
            next_selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
        if button_action == BUTTON_ACTION.DOWN_BUTTON:
            next_selectable = BATTLE_SELECTABLES.STANDBY_BAG
    # active states menu
    if state == BATTLE_STATES.STANDBY:
        if button_action == BUTTON_ACTION.Y_BUTTON:
            next_state = BATTLE_STATES.ACTIVE_MENU
            count_active_pokemon()
            done = True
    if state == BATTLE_STATES.ACTIVE_MENU:
        if button_action == BUTTON_ACTION.A_BUTTON:
            next_state = BATTLE_STATES.ACTIVE_POKEMON_STATS
    if state == BATTLE_STATES.ACTIVE_MENU:
        if button_action == BUTTON_ACTION.BACK_BUTTON:
            next_state = BATTLE_STATES.STANDBY
    # active states info
    if state == BATTLE_STATES.ACTIVE_POKEMON_STATS:
        analyze_active_pokemon()
        if button_action == BUTTON_ACTION.R_BUTTON:
            done = True
    if state == BATTLE_STATES.ACTIVE_POKEMON_STATS:
        if button_action == BUTTON_ACTION.BACK_BUTTON:
            next_state = BATTLE_STATES.ACTIVE_MENU

    #Pokemon team info page 1
    if state == BATTLE_STATES.POKEMON_SUMMARY_INFO:
        analyze_team_pokemon()
        construct_pokemon_info_page_1()
        if button_action == BUTTON_ACTION.RIGHT_BUTTON:
            next_state = BATTLE_STATES.POKEMON_SUMMARY_BASE_STATS
    elif state == BATTLE_STATES.POKEMON_SUMMARY_BASE_STATS:
        construct_pokemon_info_page_2()
        if button_action == BUTTON_ACTION.RIGHT_BUTTON:
            next_state = BATTLE_STATES.POKEMON_SUMMARY_ATTACKS
    elif state == BATTLE_STATES.POKEMON_SUMMARY_ATTACKS:
        construct_pokemon_info_page_3()
        if button_action == BUTTON_ACTION.BACK_BUTTON:
            next_state = None
            done = True

    # specific for pp Usage
    if nav_action == NavigationAction.STANDBY_UPDATE_PP_USAGE:
        if selectable == BATTLE_SELECTABLES.STANDBY_FIGHT:
            if button_action == BUTTON_ACTION.A_BUTTON:
                update_pp_usage()
                next_state = BATTLE_STATES.FIGHT_MENU
                done = True

    #Pokemon team info page 1
    if submenu == None and selectable in [BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_1, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_2, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_3, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_4, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_5, BATTLE_SELECTABLES.TEAM_POKEMON_SELECTED_6]:
        selected_val = selectable.value - 9
        if button_action ==  BUTTON_ACTION.A_BUTTON:
          next_state = BATTLE_STATES.TEAM_MEMBER_OPTIONS_MENU
          submenu_selectable = BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON
        if button_action ==  BUTTON_ACTION.UP_BUTTON:
          next_selectable = BATTLE_SELECTABLES(selectable.value - 1)
        if button_action ==  BUTTON_ACTION.DOWN_BUTTON:
          next_selectable = BATTLE_SELECTABLES(selectable.value + 1)

    if submenu in [BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON, BATTLE_SUBMENU_SELECTABLES.CHECK_SUMMARY]:
        submenu_val = submenu_selectable.value
        if button_action ==  BUTTON_ACTION.A_BUTTON and submenu == BATTLE_SUBMENU_SELECTABLES.CHECK_SUMMARY:
          next_state = BATTLE_STATES.POKEMON_SUMMARY_INFO
          submenu_selectable = None
        if button_action ==  BUTTON_ACTION.A_BUTTON and submenu == BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON:
          swapping_pokemon()
          submenu_selectable = None
          done = True
        if button_action ==  BUTTON_ACTION.BACK_BUTTON:
          next_state = BATTLE_STATES.BACK_BUTTON
          submenu_selectable = None
        if button_action ==  BUTTON_ACTION.UP_BUTTON:
          submenu_selectable = BATTLE_SUBMENU_SELECTABLES(submenu_selectable.value - 1)
        if button_action ==  BUTTON_ACTION.DOWN_BUTTON:
          submenu_selectable = BATTLE_SUBMENU_SELECTABLES(submenu_selectable.value + 1)

    if selectable == BATTLE_SELECTABLES.STANDBY_DYNAMAX and button_action == BUTTON_ACTION.A_BUTTON:
        activate_dynamax()
        next_state = BATTLE_STATES.FIGHT_MENU
        next_selectable = BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1
        done = True

    if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1 and button_action == BUTTON_ACTION.A_BUTTON:
        select_attack_1()
        done = True

    if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_1 and button_action == BUTTON_ACTION.DOWN_BUTTON:
        next_selectable = BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2

    if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2 and button_action == BUTTON_ACTION.A_BUTTON:
        select_attack_2()
        done = True

    if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_2 and button_action == BUTTON_ACTION.DOWN_BUTTON:
        next_selectable = BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3

    if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3 and button_action == BUTTON_ACTION.A_BUTTON:
        select_attack_3()
        done = True

    if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_3 and button_action == BUTTON_ACTION.DOWN_BUTTON:
        next_selectable = BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4

    if selectable == BATTLE_SELECTABLES.FIGHT_MENU_ATTACK_4 and button_action == BUTTON_ACTION.A_BUTTON:
        select_attack_4()
        done = True

#    if state == BATTLE_STATES.STANDBY and button_action == BUTTON_ACTION.Y_BUTTON:
#        counting_active_pokemon()
#        done = True
#        next_state = BATTLE_STATES.ACTIVE_MENU

#  if state == BATTLE_STATES.ACTIVE_MENU and button_action BUTTON_ACTION.A_BUTTON:
#      counting_active_pokemon()
#      done = True
#      next_state = BATTLE_STATES.ACTIVE_POKEMON_STATS


#    if state in [BATTLE_STATES.POKEMON_SUMMARY_INFO, BATTLE_STATES.POKEMON_SUMMARY_BASE_STATS] and button_action == BUTTON_ACTION.RIGHT_BUTTON:
#        next_state = BATTLE_STATES(state.value + 1)
#    elif state == BATTLE_STATES.POKEMON_SUMMARY_ATTACKS and button_action == BUTTON_ACTION.BACK_BUTTON:
#        submenu_selectable = None
#        done = True
#        finish_pokemon_scan()

    return done, next_state, next_selectable, submenu_selectable

navigation_action = NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO
battle_states = BATTLE_STATES.STANDBY
battle_selectables = BATTLE_SELECTABLES.STANDBY_FIGHT
submenu_selectables = BATTLE_SUBMENU_SELECTABLES.SWAP_POKEMON


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

def print_game_state(navigation_action, state, selectable, submenu):
    print('nav: %s, bat_state: %s, bat_select: %s, submenu_sel: %s' %(navigation_action, state, selectable, submenu))

def construct_pokemon_info_page_1():
    print('constructing page one info')

def construct_pokemon_info_page_2():
    print('constructing page two info')

def construct_pokemon_info_page_3():
    print('constructing page three info')

def count_active_pokemon():
    print('counting active pokemon')

def analyze_active_pokemon():
    print('analyzing active pokemon')

def count_team_pokemon():
    print('counting team pokemon')

def analyze_team_pokemon():
    print('analyzing team pokemon')

def swapping_pokemon():
    print('Swapping a pokemon')

def finish_pokemon_scan():
    print('finished scanning a team pokemon')

def activate_dynamax():
    print('Activating Dynamax')

def select_attack_1():
    print('Using Attack 1')

def select_attack_2():
    print('Using Attack 2')

def select_attack_3():
    print('Using Attack 3')

def select_attack_4():
    print('Using Attack 4')

def counting_active_pokemon():
    print('Counting active pokemon')

def update_pp_usage():
    print('Updating PP Usage')

def test_button_sequence1():
    navigation_action = NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO
    state = BATTLE_STATES.STANDBY
    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
        real_press = action.serial_rep()
        switch_button_press.send(real_press, 0.1)
        # Time for animation to complete between actions
        sleep(0.5)
    print()

def test_button_sequence():
    navigation_action = NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO
    state = BATTLE_STATES.STANDBY
    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
        real_press = action.serial_rep()
        switch_button_press.send(real_press, 0.1)
        # Time for animation to complete between actions
        sleep(2)
    print()

    navigation_action = NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
        real_press = action.serial_rep()
        switch_button_press.send(real_press, 0.1)
        # Time for animation to complete between actions
        sleep(2)
    print()

def simulate_team_construction():
    navigation_action = NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO
    state = BATTLE_STATES.STANDBY
    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()


    navigation_action = NavigationAction.STANDBY_ADD_FIRST_POKEMON_INFO
#    state = BATTLE_STATES.STANDBY
#    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()

    navigation_action = NavigationAction.STANDBY_CHANGE_SLOT_1
    state = BATTLE_STATES.TEAM_MENU
#    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
#    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()

    navigation_action = NavigationAction.STANDBY_CONSTRUCT_TEAM_INFO
    state = BATTLE_STATES.STANDBY
    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()

    navigation_action = NavigationAction.STANDBY_ADD_SIXTH_POKEMON_INFO
#    state = BATTLE_STATES.STANDBY
#    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()

    navigation_action = NavigationAction.STANDBY_ATTACK_SLOT_4
    state = BATTLE_STATES.STANDBY
    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()

    navigation_action = NavigationAction.STANDBY_ACTIVATE_DYNAMAX
    state = BATTLE_STATES.STANDBY
    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()

    navigation_action = NavigationAction.STANDBY_COUNT_ACTIVE_POKEMON
    state = BATTLE_STATES.STANDBY
    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()

    navigation_action = NavigationAction.STANDBY_CHECK_NEXT_ACTIVE
#    state = BATTLE_STATES.STANDBY
#    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()

    navigation_action = NavigationAction.STANDBY_CHECK_NEXT_ACTIVE
#    state = BATTLE_STATES.STANDBY
#    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()

    navigation_action = NavigationAction.STANDBY_UPDATE_PP_USAGE
    state = BATTLE_STATES.STANDBY
    selectable = BATTLE_SELECTABLES.STANDBY_FIGHT
    submenu = None
    done = False

    print_game_state(navigation_action, state, selectable, submenu)
    while done == False:
        action = navigation_action.action_for_state(state, selectable, submenu)
        print(action)
        done, state, selectable, submenu = simulate_button_press(state, selectable, submenu, action, navigation_action)
        print_game_state(navigation_action, state, selectable, submenu)
    print()


if __name__ == "__main__":
    test_button_sequence()
