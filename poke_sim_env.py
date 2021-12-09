import gym
import gym.spaces
from gym.utils import seeding
import enum
import numpy as np

from pokemon_json import *
from poke_common import *
import random
import math
from sklearn.preprocessing import LabelBinarizer
import math
import subprocess

# logic, split on integer, set int to base power
pokemon_attacks_transform = ['return', 'hiddenpowerground']
pokemon_names_transform = ['Type: Null', 'hiddenpowerground']

#Ablities revealed during match come in different ways. Also always use name and not id
#ability: Snow Warning
#[from] ability: Drought
boost_regex = "\|\-boost\|.*"
unboost_regex = "\|\-unboost\|.*"
move_regex = '\|move\|p.*'
fieldstart_regex = "\|\-fieldstart\|.*Terrain\|"
fieldend_regex = "\|\-fieldend\|.*Terrain"
roomstart_regex = '\|\-fieldstart\|.*Room\|'
roomend_regex = '\|\-fieldend\|.*Room'
faint_regex = "\|faint\|.*"
#used for megas and transforms. or some
forme_details_change_regex = "(\|detailschange\|p.*\|)|(\|\-formechange\|p.*\|)"
perish_song_regex = "\|\-start\|.*\|perish\d$"
#attack_missed_or_failed_regex = "(\|\-miss\|p.*\|)|(\|\-fail\|p.*)"
smack_down_regex = '(\|\-start\|p.*\|Smack Down)'
yawned_used_regex = "\|\-start\|.*\|move: Yawn\|\[of\]"
yawned_succeeded_regex = "\|\-end\|.*\|move: Yawn\|"
attack_resisted_regex = '\|\-resisted\|p.*'
attack_super_effective_regex = '\|\-supereffective\|p.*'
attack_immune_regex = '\|\-immune\|p.*'
confusion_ended_regex = '\|\-end\|p.*confusion$'
confusion_started_regex = '\|\-start\|p.*confusion$'
item_removed_regex = '(\|\-enditem\|p.*\|((?!\[of\]).)*$)|(\|\-enditem\|p.*\|\[of\])'
item_used_regex = '\|\-enditem\|p.*\|((?!\[of\]).)*$'
item_removed_by_user_regex = '\|\-enditem\|p.*\|\[of\]'
item_swapped_regex = '\|\-item\|p.*\|\[from\] move'
#|-item|p1a: Weavile|Assault Vest|[from] ability: Pickpocket|[of] p2a: Lurantis
item_frisked_regex = '(\|\-item\|p.*\|\[from\] ability: Pickpocket)|(\|\-item\|p.*\|\[from\] ability: Frisk)'
move_did_not_succeed = '(\|\-fail\|p.*)|(\|\-miss\|p.*)|(\|cant\|p.*)|(\|\-damage\|p.*\|\[from\] confusion)'
move_atk_regex = '\|move\|p.*\|'
#used for skipping second output
damage_detected_regex = '^(\|\-damage\|p.*\|)'
heal_detected_regex = '^(\|\-heal\|p.*\|)'
sticky_web_activated_regex = '\|\-activate\|p.*\|move: Sticky Web'

#start_regex = "\|\-start\|.*"
#end_regex = "\|\-end\|.*"

spike_damage_regex = "\|\-damage\|.*\|\[from\] Spikes"
stealthrock_damage_regex = "\|\-damage\|.*\|\[from\] Stealth Rock"
opponent_ability_damage_regex = "\|\-damage\|.*\|\[from\] ability\:.*\[of\].*"
#order matters
item_damage_from_opponent_regex = "\|\-damage\|.*\|\[from\] item\:.*\[of\].*"
# self inflicted? life orb
item_damage_regex = "\|\-damage\|.*\|\[from\] item\:.*"
field_activate_regex = "\|\-fieldactivate\|.*"
weather_upkeep_regex = "\|\-weather\|.*\|\[[a-z]+\]$"
weather_end_regex = '\|\-weather\|none'
sideend_hazards_activate_regex = "\|\-sideend\|.*\|\[of\] p\d"
sideend_non_hazards_activate_regex = "\|\-sideend\|.*\|(a-z)*((?!\[of\]).)*$"
sidestart_regex = '\|\-sidestart\|p.*'

destiny_bond_regex = '\|\-singlemove\|.*\|Destiny Bond$'
heal_from_target_regex = '\|\-heal\|p.*\|\[from\] .*\|\[of\]'
general_heal_regex = '\|\-heal\|p.*\|\[from\](a-z)*((?!\[of\]).)*$'
pain_split_regex = '\|\-sethp\|p.*\|\[from\].*'
# trace copies ability, and reveals enemy ability
trace_regex = '\|\-ability\|p.*\|\[from\] ability: Trace\|\[of\](a-z)*'

# castform has one ability, so no need to reveal it during use. add for future
caseform_forecast_regex = '\|\-formechange\|p.*\|\[from\] ability: Forecast'

clear_all_boosts_regex = '\|\-clearallboost'
clear_neg_boosts_regex = '\|\-clearnegativeboost'
clear_boost_regex = '\|\-clearboost\|p.*'
#Lazy statuses
status_from_ability_regex = '\|\-status\|p.*\|\[from\] ability'
status_from_enemy_move_regex = '\|\-status\|p.*\|\[from\] ability'
# Maybe do nothing with these
sleep_from_rest_regex = '\|\-status\|p.*\|\[from\] move: Rest'
status_from_item_regex = '\|\-status\|p.*\|\[from\] item:'

curestatus_regex = '\|\-curestatus\|p.*\|'
activate_ability_regex = '.*\[from\] ability.*\|\[of\]'
start_substitute_regex = '\|\-start\|p.*\|Substitute'
end_substitute_regex = '\|\-end\|p.*\|Substitute'

start_dynamax_regex = '\|\-start\|p.*\|Dynamax'
end_dynamax_regex = '\|\-end\|p.*\|Dynamax'


crit_regex = '\|\-crit\|p.*'
switch_regex = '\|switch\|p.*'
drag_regex = '\|drag\|p.*'
#Zoroark specifics
#|replace|p2a: Zoroark|Zoroark, L80, F
zoroark_replace_regex = '\|replace\|.*'
zoroark_end_illusion_regex = '\|\-end\|.*Illusion$'
#Mega reveals items
#|-mega|p1a: Alakazam|Alakazam|Alakazite
#|-zpower|p1a: Charizard
mega_regex = '\|\-mega\|p\d.*'
zpower_regex = '\|\-zpower\|p\d.*'

#|teamsize|p1|4
#|teamsize|p2|5
#|gametype|doubles
#|gen|7
#|tier|[Gen 7] Doubles Ubers
p1_teamsize_regex = '\|teamsize\|p1.*'
p2_teamsize_regex = '\|teamsize\|p2.*'
gametype_regex = '\|gametype\|.*'
gen_number_regex = '\|gen\|\d'
tier_regex = '\|tier\|.*'

force_switch_regex = '\|request\|{"forceSwitch":\['
#if wait for p1, return. if wait for p2, enter a loop until valid p2 move
# dont not want to give p1 a chance to keep selecting attacks during wait for p2
wait_regex = '\|request\|{"wait":true'

level_regex = 'L\d*'
male_gender_regex = ', M'
female_gender_regex = ', F'
update_complete_regex = '\|turn\|\d*'

# This will not trigger a random move, but an update of state and a retry.
# For p1, returns previous observation?? Maybe not. state might change in triples
#reward at time should be zeroish
#TODO: logic might need update for doubles
trapped_regex_1 = '\|error\|\[Unavailable choice\] Can\'t switch: The active Pokémon is trapped'
trapped_regex_2 = '\|error\|\[Invalid choice\] Can\'t switch: The active Pokémon is trapped'
isnt_your_turn_regex = '\|error\|\[.*\] Can\'t do anything: It\'s not your turn'
need_switch_response_regex = '\|error\|\[.*\] Can\'t move: You need a switch response'
cant_switch_to_fainted_regex = '\|error\|\[.*\] Can\'t switch: You can\'t switch to a fainted Pokémon'
cant_switch_to_active_regex = '\|error\|\[.*\] Can\'t switch: You can\'t switch to an active Pokémon'
disabled_move_regex = '\|error\|\[.*\] Can\'t move: .* is disabled'

p1_pokemon_revealed_moves = {}

revealed_items = set()
revealed_attack_names = set()
revealed_pokemon_names = set()
revealed_abilities = set()
side_update_collection = {}
player_team_collection = {}
events_collection = set()

#move_history = []
all_revealed_items = set()
all_revealed_attack_names = set()
all_revealed_pokemon_names = set()
all_revealed_abilities = set()

def get_sample_action(player, action=None):
  action = action
  if action == None:
    actions = len(Action)
    action = random.randint(0,actions-1)
    action = Action(action)
  # lazy avoid shifts
  if(action == Action.Attack_Struggle):
      print(player, 'Struggle Selected')
  action_text = 'move 1'
  if action == Action.Attack_Slot_1 or action == Action.Attack_Struggle:
    action_text = 'move 1'
  if action == Action.Attack_Slot_2:
    action_text = 'move 2'
  if action == Action.Attack_Slot_3:
    action_text = 'move 3'
  if action == Action.Attack_Slot_4:
    action_text = 'move 4'
  if action == Action.Attack_Dyna_Slot_1:
    action_text = 'move 1 dynamax'
  if action == Action.Attack_Dyna_Slot_2:
    action_text = 'move 2 dynamax'
  if action == Action.Attack_Dyna_Slot_3:
    action_text = 'move 3 dynamax'
  if action == Action.Attack_Dyna_Slot_4:
    action_text = 'move 4 dynamax'

  if action == Action.Change_Slot_1:
    action_text = 'switch 1'
  if action == Action.Change_Slot_2:
    action_text = 'switch 2'
  if action == Action.Change_Slot_3:
    action_text = 'switch 3'
  if action == Action.Change_Slot_4:
    action_text = 'switch 4'
  if action == Action.Change_Slot_5:
    action_text = 'switch 5'
  if action == Action.Change_Slot_6:
    action_text = 'switch 6'

  message = '>%s %s' % (player, action_text)
#  move_history.append(message)
  return message
# Converts mega/ultra pokemon to the same name for the purpose of looking up revealed moves/items/abilities
def get_true_name_for_pokemon(name):

    return name

def bool_to_int(value):
    return 1 if value else 0


class ActiveStats():
    def __init__(self):
        self.seeded = False
        self.confused = False
        self.taunted = False
        self.encored = False
        self.substitute = False
        self.attracted = False
        self.seeded = False
        self.must_recharge = False
        self.dynamax_activated = False
        self.dynamax_turns = 0
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

class ActionRequest():
    def __init__(self):
        self.active_pokemon_actions = {'a':Action.Not_Decided,'b':Action.Not_Decided}
        self.active_pokemon_targets = {'a':SELECTABLE_TARGET.DO_NOT_SPECIFY,'b':SELECTABLE_TARGET.DO_NOT_SPECIFY}
        #Important enough for one hot encoding?
        self.action_for_position = SELECTABLE_TARGET.ALLY_SLOT_1


class State:

    def __init__(self, computer_network=None, random_style=RANDOM_STYLES.PRIORITY_ATTACK):
        self.random_style = RANDOM_STYLES.PRIORITY_ATTACK
        self.clear_everything()
        self.computer_network = computer_network
        self.simulate = None
        self.is_doubles = False
        self.is_triples = False

    def clear_everything(self):
        self.turns = 0


        self.p1_teamsize = 0
        self.p2_teamsize = 0
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
        self.p1_reward = 0
        self.p2_reward = 0
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
        self.p1_pokemon = []
        self.p2_pokemon = []
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

        self.p1_used_dynamax = False
        self.p2_used_dynamax = False

        self.display_everything = False


        self.request_outputs = []

    def encode_field_state(self, is_p1_perspective):
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
            all_pokemon_attacks_labels.transform([self.p1_seen_attacks['a']]),     # category
            all_pokemon_attacks_labels.transform([self.p1_seen_attacks['b']]),     # category
        ]

        if not is_p1_perspective:
            seen_attacks_encodes = [
                all_pokemon_attacks_labels.transform([self.p2_seen_attacks['a']]),     # category
                all_pokemon_attacks_labels.transform([self.p2_seen_attacks['b']]),     # category
            ]


        full_category_encodes = []
        full_raw_encodes = []

        if is_p1_perspective:
            full_category_encodes.extend(category_encode)
            full_category_encodes.extend(p1_category_encodes)
            full_category_encodes.extend(seen_attacks_category_encodes)

            full_raw_encodes.extend(field_raw_encodes)
            full_raw_encodes.extend(p1_raw_encodes)
            full_raw_encodes.extend(p2_raw_encodes)
        else:
            full_category_encodes.extend(category_encode)
            full_category_encodes.extend(p2_category_encodes)
            full_category_encodes.extend(seen_attacks_category_encodes)

            full_raw_encodes.extend(field_raw_encodes)
            full_raw_encodes.extend(p2_raw_encodes)
            full_raw_encodes.extend(p1_raw_encodes)

        return full_category_encodes, full_raw_encodes



    def get_observation(self, includeTranscript=False):

        normal_encodes = []
        reverse_encodes = []

        field_cat, field_raw = self.encode_field_state(True)
        p1_pokemon, p2_pokemon = self.get_preprocessed_pokemon(True)

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

        #reverse version
        field_cat, field_raw = self.encode_field_state(False)
        rev_p1_pokemon, rev_p2_pokemon = self.get_preprocessed_pokemon(False)
        p1_cat, p1_raw = self.encode_pokemon_state(rev_p1_pokemon)
        p2_cat, p2_raw = self.encode_pokemon_state(rev_p2_pokemon)

        reverse_encodes.extend(field_cat)
        reverse_encodes.extend(p2_cat)
        reverse_encodes.extend(p1_cat)

        # flatten categories
        reverse_encodes = flatten(reverse_encodes)

        reverse_encodes.extend(field_raw)
        reverse_encodes.extend(p2_raw)
        reverse_encodes.extend(p1_raw)

        p1_actions_targets = self.get_valid_moves_for_player(position='a', is_p1_perspective=True)
        p2_actions_targets = self.get_valid_moves_for_player(position='a', is_p1_perspective=False)

        p1_actions = self.split_actions_from_targets(p1_actions_targets)
        p2_actions = self.split_actions_from_targets(p2_actions_targets)

        p1_targets = self.get_filled_targets_for_actions(p1_actions_targets)
        p2_targets = self.get_filled_targets_for_actions(p2_actions_targets)
        if not includeTranscript:
            return normal_encodes
        results = {
            'transcript': self.p1_transcript,
            'reverse_transcript': self.p2_transcript,
            'field': self.encode_field_state(True),
            'player': self.encode_pokemon_state(p1_pokemon),
            'agent':self.encode_pokemon_state(p2_pokemon),
            'combined': normal_encodes,
            'reversed_combined': reverse_encodes,   # used for ai battles
            'cat_length':categories_length,
            'full_obs_len':obs_length,
            'raw_length':(obs_length-categories_length),
            'valid_moves_player_1': self.get_valid_moves_for_player(),
            'valid_moves_player_2': self.get_valid_moves_for_player(position='a', is_p1_perspective=False),
            'valid_onehot_player_1': self.valid_onehot_moves(p1_actions),
            'valid_onehot_player_2': self.valid_onehot_moves(p2_actions),
            'valid_onehot_p1_targets': self.valid_onehot_targets(p1_targets),
            'valid_onehot_p2_targets': self.valid_onehot_targets(p2_targets),
        }
        return results

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

    def split_actions_from_targets(self, actions_targets):
      actions = []
      for act, tars in actions_targets:
        actions.append(act)

      return actions

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



    def get_preprocessed_pokemon(self, is_p1_perspective):
        p1_poke = None
        p2_poke = None

        if is_p1_perspective:
            p1_poke = get_seen_rep_of_pokemon(self.p1_pokemon, self.p1_seen_details, self.p1_teamsize, a_slot=self.p1_selected['a'], b_slot=self.p1_selected['b'])
            p2_poke = get_seen_rep_of_opponent_pokemon(self.p2_seen_details, self.p2_teamsize, a_slot=self.p2_selected['a'], b_slot=self.p2_selected['b'])
        else:
            p2_poke = get_seen_rep_of_pokemon(self.p2_pokemon, self.p2_seen_details, self.p2_teamsize, a_slot=self.p2_selected['a'], b_slot=self.p2_selected['b'])
            p1_poke = get_seen_rep_of_opponent_pokemon(self.p1_seen_details, self.p1_teamsize, a_slot=self.p1_selected['a'], b_slot=self.p1_selected['b'])

        return p1_poke, p2_poke

    # IF pokemon is not  revealed, pass None.
    # Only opponents/p2s can be none.
    def encode_single_pokemon_state(self, pokemon, show_full_details=False):
        # empty pokemon slot
        # max IV/EV stat
        max_ev_iv_value = 800

        element_2nd_type = ELEMENT_TYPE.TYPELESS.value
        if pokemon.element_2nd_type != None:
            element_2nd_type = pokemon.element_2nd_type.value
        category_encode = [
            all_pokemon_names_labels.transform([pokemon.form]),     # category
            all_status_labels.transform([pokemon.status.value]),   # category
#            all_status_labels.transform([Status.NOTHING.value]),   # category
            all_element_types_labels.transform([pokemon.element_1st_type.value]),     # category
            all_element_types_labels.transform([element_2nd_type]),   # category
            all_abilities_labels.transform([pokemon.ability]),
            all_items_labels.transform([pokemon.item]),
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

    def sample_actions(self, position='a', is_p1_perspective=True):
        is_weak_to_stab = self.get_is_pokemon_weak_to_stab(position=position, is_p1_perspective=is_p1_perspective)
        under_45_percent = self.get_curr_pokemon_health(position, is_p1_perspective)
        actions_targets = self.get_valid_moves_for_player(position, is_p1_perspective)
#        print('p1_perspective', is_p1_perspective, actions)
        weights = [action.get_base_weight() for action, _ in actions_targets]
        if self.random_style == RANDOM_STYLES.PRIORITY_ATTACK:
            weights = [action.get_attack_priority_weight() for action, _ in actions_targets]
#            print('using get_attack_priority_weight distribution')
        elif self.random_style == RANDOM_STYLES.TIL_LAST_BREATH:
            weights = [action.get_till_last_breath_weight() for action, _ in actions_targets]
#            print('using get_till_last_breath_weight distribution')
        elif self.random_style == RANDOM_STYLES.STRATEGIC_WITHDRAWAL:
            weights = [action.get_strategic_withdrawl_weight(is_weak_to_stab, under_45_percent) for action, _ in actions_targets]
#            print('using get_strategic_withdrawl_weight distribution')
        weights = np.asarray(weights)/sum(weights)

        idx = np.random.choice(len(actions_targets), p=weights)
        action_target = actions_targets[idx]
        return action_target[0]

    def get_curr_pokemon_health(self, position='a', is_p1_perspective=False):

        pokemon = self.p1_pokemon
        selected_slots = self.p1_selected
        if not is_p1_perspective:
            pokemon = self.p2_pokemon
            selected_slots = self.p2_selected
        for pkmn in pokemon:
            if selected_slots[position] is not None and pkmn.active:
                if pkmn.max_health == 0:
                    return 0
                return float(pkmn.curr_health)/float(pkmn.max_health)
        return 1


    # should only really be used by opponent i.e random bot
    def get_is_pokemon_weak_to_stab(self, position='a', is_p1_perspective=False):
        target_pokemon = self.p2_pokemon
        attacking_pokemon = self.p1_pokemon
        target_selected_slots = self.p2_selected
        attacking_selected_slots = self.p1_selected
        if is_p1_perspective:
            target_pokemon = self.p1_pokemon
            attacking_pokemon = self.p2_pokemon
            target_selected_slots = self.p1_selected
            attacking_selected_slots = self.p2_selected
        target_curr_pokemon = None
        for pkmn in target_pokemon:
            # Works for single, not for doubles
            if target_selected_slots[position] is not None and pkmn.active:
                target_curr_pokemon = pkmn
        attacking_curr_pokemon = None
        for pkmn in attacking_pokemon:
            # Works for single, not for doubles
            if attacking_selected_slots[position] is not None and pkmn.active:
                attacking_curr_pokemon = pkmn

        if target_curr_pokemon is None or attacking_curr_pokemon is None:
            return False

#        print('comparing target:', target_curr_pokemon.name)
#        print('comparing attacking:', attacking_curr_pokemon.name)
        target_pokemon_element_1 = target_curr_pokemon.element_1st_type.value
        target_pokemon_element_2 = ELEMENT_TYPE.TYPELESS.value
        if target_curr_pokemon.element_2nd_type != None:
            target_pokemon_element_2 = target_curr_pokemon.element_2nd_type.value

        attacking_pokemon_element_1 = attacking_curr_pokemon.element_1st_type.value
        attacking_pokemon_element_2 = ELEMENT_TYPE.TYPELESS.value
        if attacking_curr_pokemon.element_2nd_type != None:
            attacking_pokemon_element_2 = attacking_curr_pokemon.element_2nd_type.value

        element_1_effectiveness = 0
        element_2_effectiveness = 0
        #increase if element is weak to another
        element_1_effectiveness = get_damage_modifier_for_type(target_pokemon_element_1, attacking_pokemon_element_1) * get_damage_modifier_for_type(target_pokemon_element_1, attacking_pokemon_element_2)
        element_2_effectiveness = get_damage_modifier_for_type(target_pokemon_element_2, attacking_pokemon_element_1) * get_damage_modifier_for_type(target_pokemon_element_2, attacking_pokemon_element_2)

#        print('element 1 effectiveness:', element_1_effectiveness)
#        print('element 2 effectiveness:', element_2_effectiveness)

        return element_1_effectiveness == 2 or element_2_effectiveness == 2

    def get_valid_moves_for_player(self, position='a', is_p1_perspective=True):
        DYNA_OFFSET = 4
        CHANGE_OFFSET = 8

        pokemon = self.p1_pokemon
        selected_slots = self.p1_selected
        trapped_player = self.p1_trapped
        must_switch  = self.p1_must_switch
        player_used_dynamax = self.p1_used_dynamax
        if not is_p1_perspective:
            pokemon = self.p2_pokemon
            selected_slots = self.p2_selected
            trapped_player = self.p2_trapped
            must_switch  = self.p2_must_switch
            player_used_dynamax = self.p2_used_dynamax
        curr_pokemon = None
        for pkmn in pokemon:
#            print('pp_name', pkmn.name)
            # Logic before illusion broke it
#            if selected_slots[position] is not None and pkmn.name.startswith(selected_slots[position]) :
#                curr_pokemon = pkmn

            # Works for single, not for doubles
            if selected_slots[position] is not None and pkmn.active:
                curr_pokemon = pkmn
        valid_moves  = []
        # Need to learn
        can_dynamax = False
        if curr_pokemon is not None:
            can_dynamax = curr_pokemon.canDynamax and not player_used_dynamax
        #if trapped, or slot is None, skip attacks
#        print('must switch', must_switch[position])
#        print('curr_pokemon is none', curr_pokemon is None)
#        if curr_pokemon is not None:
#            print('no health', int(curr_pokemon.curr_health) <= 0)
        if not ( must_switch[position] or curr_pokemon is None or int(curr_pokemon.curr_health) <= 0):
            for idx, atk in enumerate(curr_pokemon.attacks):
                if atk is not None and atk.disabled == False:
                    valid_moves.append((Action(idx), self.selectable_targets_for_target(TARGET(atk.target), position)))

                if can_dynamax:
                    valid_moves.append((Action(idx+DYNA_OFFSET), self.selectable_targets_for_target(TARGET(atk.target), position)))
#                else:
#                    print('disabled attack', atk.attack_name)
#                    print('disabled attack?', atk.disabled)
#                    print('disabled attack pp max', atk.pp)
#                    print('disabled attack pp  used', atk.used_pp)

            # Struggle is the same as attack slot one.
            if len(valid_moves) == 0: # can only struggle
                valid_moves.append((Action.Attack_Struggle, self.selectable_targets_for_target(TARGET.SELF, position)))

        unavailable_switches = set()
        if selected_slots['a'] is not None:
            unavailable_switches.add(selected_slots['a'])
#            print('unavailable_switches_a', unavailable_switches)
        if selected_slots['b'] is not None:
            unavailable_switches.add(selected_slots['b'])
#            print('unavailable_switches_b', unavailable_switches)
#        print('unavailable_switches', unavailable_switches)

        # trapped pokemon have no switch options
        if not trapped_player[position]:
            for idx, pkmn in enumerate(pokemon):
                #Illusion broke this logic
                """
                skip = False
                for name in unavailable_switches:
                    if selected_slots[position] is not None and  pkmn.name.startswith(name):
                        skip = True
                if skip:
                    continue
                """
                # ignore active pokemons
                if pkmn.active:
                    continue
                if int(pkmn.curr_health) > 0 and pkmn != curr_pokemon:
                    valid_moves.append((Action(CHANGE_OFFSET+idx), self.selectable_targets_for_target(TARGET.SELF, position)))
        else:
            pass
#            print('Cant switch, pokemon trapped')
            """
            print('p1 trapped22', self.p1_trapped)
            print('p2 trapped22', self.p2_trapped)
            print('p2 trapped_player[position]', trapped_player[position])
            print('valid_moves', valid_moves)
            print('is_p1_perspective', is_p1_perspective)
#            """
#        """
        if len(valid_moves) == 0:
            print('valid_moves', valid_moves)
            print('must switch', must_switch[position])
            print('curr_pokemon is none', curr_pokemon is None)
            if curr_pokemon is not None:
                print('no health', int(curr_pokemon.curr_health) <= 0)
#        """
        return valid_moves


    def reset_state_transcript(self):
        self.p1_transcript = ''
        self.p2_transcript = ''

    def summary_printout(self):
        p1_shield_message = 'P1 shields: safeguard: %r, lightscreen: %r, reflect: %r, tailwind: %r, auraviel: %r' % (self.p1_safeguard, self.p1_lightscreen, self.p1_reflect, self.p1_tailwind, self.p1_aurora_veil)
        p2_shield_message = 'P2 shields: safeguard: %r, lightscreen: %r, reflect: %r, tailwind: %r, auraviel: %r' % (self.p2_safeguard, self.p2_lightscreen, self.p2_reflect, self.p2_tailwind, self.p2_aurora_veil)
        p1_import_message = 'P1 imports: used_z_move: %r, used_mega: %r, has_rocks: %r, has_web: %r, spikes: %d, toxic_spikes: %d' % (self.p1_used_zmove, self.p1_used_mega, self.p1_has_rocks, self.p1_has_web, self.p1_spikes, self.p1_toxic_spikes)
        p2_import_message = 'P2 imports: used_z_move: %r, used_mega: %r, has_rocks: %r, has_web: %r, spikes: %d, toxic_spikes: %d' % (self.p2_used_zmove, self.p2_used_mega, self.p2_has_rocks, self.p2_has_web, self.p2_spikes, self.p2_toxic_spikes)
        print(p1_shield_message)
        print(p2_shield_message)
        print(p1_import_message)
        print(p2_import_message)
        print('p1 trapped', self.p1_trapped)
        print('p2 trapped', self.p2_trapped)

    def printo_magnet(self, message):
        message = message.strip()
        if message == '' or self.should_self_print == False:
#        if message == '':
            return
        player_regex = '_p_'  # for player replace with nothing, for agent replace with opposing
        agent_regex = '_a_'  # for player replace with opposing, for agent replace with nothing
        message = message.replace('_p1_', '')
        message = message.replace('_p2_', 'Opposing ')

        print(message)

    def append_to_transcript(self, message):
        message = message.strip()
        if message == '':
            return
        player_regex = '_p1_'  # for player replace with nothing, for agent replace with opposing
        agent_regex = '_p2_'  # for player replace with opposing, for agent replace with nothing
        self.p1_transcript = '%s\n%s' % (self.p1_transcript, message)
        self.p1_transcript = self.p1_transcript.replace('_p1_', '')
        self.p1_transcript = self.p1_transcript.replace('_p2_', 'Opposing ')

        # apply reverse logic.
        self.p2_transcript = '%s\n%s' % (self.p2_transcript, message)
        self.p2_transcript = self.p2_transcript.replace('_p2_', '')
        self.p2_transcript = self.p2_transcript.replace('_p1_', 'Opposing ')

    def selectable_targets_for_target(self, target, position='a'):
        if target in [TARGET.SELF, TARGET.ALL_ADJACENT_FOES, TARGET.ALLY_SIDE,
                    TARGET.ALLY_TEAM, TARGET.ALL, TARGET.ALL_ADJACENT, TARGET.RANDOM_NORMAL]:
            return [SELECTABLE_TARGET.DO_NOT_SPECIFY]

        if self.is_doubles:
            if target == TARGET.ANY:
                return [SELECTABLE_TARGET.ALLY_SLOT_1, SELECTABLE_TARGET.ALLY_SLOT_2, SELECTABLE_TARGET.FOE_SLOT_1, SELECTABLE_TARGET.FOE_SLOT_2]

            if target == TARGET.ADJACENT_ALLY_OR_SELF:
                if position == 'a':
                    return [SELECTABLE_TARGET.ALLY_SLOT_1, SELECTABLE_TARGET.ALLY_SLOT_2]
                else:
                    return [SELECTABLE_TARGET.ALLY_SLOT_1, SELECTABLE_TARGET.ALLY_SLOT_2]

            if target == TARGET.ADJACENT_ALLY:
                if position == 'a':
                    return [SELECTABLE_TARGET.ALLY_SLOT_2]
                else:
                    return [SELECTABLE_TARGET.ALLY_SLOT_1]

            if target == TARGET.ADJACENT_FOE:
                return [SELECTABLE_TARGET.FOE_SLOT_1, SELECTABLE_TARGET.FOE_SLOT_2]

            if target == TARGET.NORMAL:
                if position == 'a':
                    return [SELECTABLE_TARGET.ALLY_SLOT_2, SELECTABLE_TARGET.FOE_SLOT_1, SELECTABLE_TARGET.FOE_SLOT_2]
                else:
                    return [SELECTABLE_TARGET.ALLY_SLOT_1, SELECTABLE_TARGET.FOE_SLOT_1, SELECTABLE_TARGET.FOE_SLOT_2]


        return [SELECTABLE_TARGET.DO_NOT_SPECIFY]



    def reset(self, computer_network, random_style, should_print=False):
        self.clear_everything()
        self.computer_network = computer_network
        self.random_style = random_style
        self.should_self_print = should_print

        if self.simulate != None:
            self.simulate.stdin.close()
            self.simulate.stdout.close()
            self.simulate.stderr.close()
            self.simulate.kill()
        simulate = subprocess.Popen(["./Pokemon-Showdown/pokemon-showdown", "simulate-battle"],
                    stdin =subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=0)
        self.simulate = simulate
        self.simulate.stdin.write('>start {"formatid":"gen8randombattle"}\n')
        self.simulate.stdin.write('>player p1 {"name":"Alice"}\n')
        self.simulate.stdin.write('>player p2 {"name":"Bob"}\n')
        self.transcripto = []
        self.request_outputs = []
        self.p1_open_request = {'a':True, 'b':False}
        self.p2_open_request = {'a':True, 'b':False}


        self.process_til_turn_1()

        if self.display_everything:
            print('p1 pokemon')
            for pkmn in self.p1_pokemon:
                print(pkmn.name)
                print(pkmn.form)
                print(pkmn.atk)
                print(pkmn.spatk)
                print(pkmn.element_1st_type)
                print(pkmn.item)
                print(pkmn.ability)
                print('Displaying attacks')
                for atk in pkmn.attacks:
                    print(atk.attack_name)
                    print(atk.id)
                    print(atk.element_type)
                    print(atk.power)
                    print()
            print('p2 pokemon')
            for pkmn in self.p2_pokemon:
                print(pkmn.name)
                print(pkmn.form)
                print(pkmn.atk)
                print(pkmn.spatk)
                print(pkmn.element_1st_type)
                print(pkmn.item)
                print(pkmn.ability)
                print('Displaying attacks')
                for atk in pkmn.attacks:
                    print(atk.attack_name)
                    print(atk.id)
                    print(atk.element_type)
                    print(atk.power)
                    print()

    def close(self):
        print('closing state')
        if self.simulate != None:
            self.simulate.stdin.close()
            self.simulate.stdout.close()
            self.simulate.stderr.close()
            self.simulate.kill()
        # Keeps tracks of attacks used last turn
        self.p1_seen_attacks = {'a':'no attack', 'b':'no attack'}
        self.p2_seen_attacks = {'a':'no attack', 'b':'no attack'}

    def reset_for_turn(self):
        self.reset_state_transcript()
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
        # switching moves
#        self.p1_must_switch = {'a':False, 'b':False}
#        self.p2_must_switch = {'a':False, 'b':False}

        #Pending moves - embedding that has selected action
        self.p1_pending_actions = {'a':Action.Not_Decided, 'b':Action.Not_Decided}
        self.p1_pending_targets = {'a':SELECTABLE_TARGET.DO_NOT_SPECIFY, 'b':SELECTABLE_TARGET.DO_NOT_SPECIFY}
        self.p2_pending_actions = {'a':Action.Not_Decided, 'b':Action.Not_Decided}
        self.p2_pending_targets = {'a':SELECTABLE_TARGET.DO_NOT_SPECIFY, 'b':SELECTABLE_TARGET.DO_NOT_SPECIFY}
        # Keeps tracks of attacks used last turn
        self.p1_seen_attacks = {'a':'no attack', 'b':'no attack'}
        self.p2_seen_attacks = {'a':'no attack', 'b':'no attack'}



        self.faint_did_happen = False


    def perform_p2_action(self, p2_action=None):
        # assume p2 will always finish its response before p1, thus no
        # need to reset p2_is_waiting outside normal conditions
        if self.p2_open_request['a'] and (not self.p2_is_waiting or self.p2_must_switch['a']):
            self.p2_open_request['a'] = False
#            print('p2 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=False))
            p2_in_actions = False
            actions_targets = self.get_valid_moves_for_player(position='a', is_p1_perspective=False)
            for act, _ in actions_targets:
                if p2_action == act:
                    p2_in_actions = True
                    break

            if p2_action != None and p2_in_actions:# and p2_action in self.get_valid_moves_for_player(position='a', is_p1_perspective=False):
#                print('using a network action')
                p2_action = get_sample_action('p2', p2_action)
            else:
                p2_action = get_sample_action('p2', self.sample_actions(position='a', is_p1_perspective=False))
            if p2_action == Action.Attack_Struggle:
                print('p2 wh struggle? availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=False))

#            print('p2_action: ', p2_action)
            self.request_outputs.append(p2_action)
            self.simulate.stdin.write(p2_action+'\n')


    def get_p2_network_action(self):
#        print('getting action from network, delete me')
        obs = self._state.encode(includeTranscript=True)
        p2_transcript = obs['reverse_transcript']
        p2_obs = obs['reversed_combined']
        p2_valid_moves = obs['valid_onehot_player_2']
        p2_valid_targets = obs['valid_onehot_p2_targets']
        # Get the action
        action, target, value, _ = computer_network.step(p2_obs, [p2_valid_moves], [p2_valid_targets], [p2_transcript])
        print('using a network action')

        p2_action = p1_action = Action(action)
        if p2_action not in self._state.get_valid_moves_for_player(position='a', is_p1_perspective=False):
            p2_action = self._state.sample_actions(position='a', is_p1_perspective=False)
        p2_action = get_sample_action('p2', p1_action)
        return p2_action


    @property
    def shape(self):
        # player has 6 pokemon with 16 slots
        # computer agent has 6 pokemon with 11 slots since some info hidden.
#        return (len(self.encode()['combined']), )
        return (len(self.encode()), )

    def encode(self, includeTranscript=False):
        """
        Convert current state into numpy array.
        """
        return self.get_observation(includeTranscript)


    def step(self, p1_action, p2_action=None):
        # increment turns
        self.turns += 1

        self.request_outputs.append(p1_action)
        self.perform_p2_action(p2_action)
#        print('p1_action: ', p1_action)

        # should always be the case
        if self.p1_open_request['a']:
            self.p1_open_request['a'] = False
            self.simulate.stdin.write(p1_action+'\n')
        output = ''
        update_complete = False
        turn_complete = False
        winner = None
        done = False
        while not update_complete:
#            print('self.p1_open_request', self.p1_open_request)
#            print('self.p2_open_request', self.p2_open_request)
            output = self.simulate.stdout.readline().strip()
#            print(output)

            if output == 'sideupdate':
                p1_is_trapped = self.process_sideupdate()
                if p1_is_trapped:
                    break

            if output == 'update':
                self.faint_did_happen = False
                turn_complete = self.process_update()
                # if a faint happened, we need to keep going for the upkeep
                update_complete = True

            if 'winner' in output.strip(): #'|win|' in output or '|tie|' in output:
#                print('sequence over')
#                self.summary_printout()
                winner_json = json.loads(output)
                winner = winner_json['winner']
                done = True
                break

            # If p1 is waiting, request p2 actions
            if self.p1_is_waiting and self.p2_open_request['a']:
                # if p2 chooses bad move, assume a loop would keep polling
                self.p1_is_waiting = False
                self.perform_p2_action()
                # poll for new info.
                update_complete = False
            elif self.p1_is_waiting or not self.p1_open_request['a']:
                #p2 may not received open request yet
                # undo update complete
                # p1 also needs to wait for updates
                update_complete = False

#        self.summary_printout()
        # Uturn makes partial complete
        if turn_complete:
            self.reset_for_turn()
            # Apply dynamax counter
            self.apply_dynamax_counter()

        # Penalty for taking too long
        if self.turns >= 150:
            done = True
            self.p1_reward = -500
            winner = 'p2'

        return self.p1_reward, done, winner

    def apply_dynamax_counter(self):
        positions = ['a', 'b']
        for position in positions:
            if self.p1_active_pokemon_stats[position].dynamax_activated:
                self.p1_active_pokemon_stats[position].dynamax_turns += 1
#                print('p1 dynamax turns %d: ' % (self.p1_active_pokemon_stats[position].dynamax_turns) )
            if self.p2_active_pokemon_stats[position].dynamax_activated:
                self.p2_active_pokemon_stats[position].dynamax_turns += 1
#                print('p2 dynamax turns %d: ' % (self.p2_active_pokemon_stats[position].dynamax_turns) )

    # turn 1 is unique. by the time  of the sideupdate p1 and p2,
    # we dont even know who we're fighting against. This would cripple
    # ai's decision on who to use. Lazy work around make ai p2, but then same
    # situation would arise in bot vs bot fights
    def process_til_turn_1(self):
        output = None
        while output != '|turn|1':
            output = self.simulate.stdout.readline().strip()
#            print(output)
            if re.search(switch_regex, output) or re.search(drag_regex, output):
#|switch|p2a: Zygarde|Zygarde, L78|75/100|[from]move: U-turn
#|drag|p2a: Politoed|Politoed, L84, M|288/288
#|switch|p2a: Garchomp|Garchomp, L80, F|304/304
                level = 80
                gender = ''
                level_regex = 'L\d*'
                male_gender_regex = ', M'
                female_gender_regex = ', F'
                level_gender_split = output.split('|')[3]
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                self.handle_switch(is_player_1, pkmn, position)

            if output == 'sideupdate':
                self.process_sideupdate()

            # turn 1 doesnt process update
#            if output == 'update':
#                self.process_update()

    def process_sideupdate(self):
        player = output = self.simulate.stdout.readline().strip()
        output = self.simulate.stdout.readline().strip()
        #reset only relevant player
#        print(player)
#        print(output)
        self.transcripto.append(player)
        self.transcripto.append(output)
        self.request_outputs.append(player)
        self.request_outputs.append(output)

        if player not in side_update_collection:
            side_update_collection[player] = set()
        side_update_collection[player].add(output)
        if self.display_everything:
            print(player)
            print(output)

        if re.search(wait_regex, output):
            # depending on player, enter wait loop. else continue
            if 'p1' in player:
                self.p1_is_waiting = True
            else:
                self.p2_is_waiting = True
            self.update_player_side(player, output)
            return

        if re.search(force_switch_regex, output):
#            print(player)
#            print(output)
            switch_details = json.loads(output.split('|')[2])['forceSwitch']
            positions = ['a', 'b']
            #mark player as need to switch
            # reset trapped. i.e. killed by wobbuffet
            if 'p1' in player:
                for idx, switch in enumerate(switch_details):
                    self.p1_must_switch[positions[idx]] = switch
                    self.p1_open_request[positions[idx]] = switch
                    # Maybe other pokemon are trapped by other slot
                    if switch:
                        self.p1_trapped[positions[idx]] = False
            elif 'p2' in player:
                for idx, switch in enumerate(switch_details):
                    self.p2_must_switch[positions[idx]] = switch
                    self.p2_open_request[positions[idx]] = switch
                    # Maybe other pokemon are trapped by other slot
                    if switch:
                        self.p2_trapped[positions[idx]] = False
            self.update_player_side(player, output)
#            print('Printintg stats on first pokemon')
#            if 'p1' in player:
#                print('p1 health',self.p1_pokemon[0].curr_health)
#            else:
#                print('p2 health',self.p2_pokemon[0].curr_health)
            return

        # Need logic for doubles/triples
        if re.search(trapped_regex_1, output) or re.search(trapped_regex_2, output):
#            print('special trapped happened.')
#            print('p1 special trapped', self.p1_trapped)
#            print('p2 special trapped', self.p2_trapped)
#            print(player)
#            print(output)
            #Eat empty line and side update line and call recursion to update info.
            # return trapped and break to poll p1 for new move.
            # if p2, just request new action.
            _empty = self.simulate.stdout.readline().strip()
            _sideupdate = self.simulate.stdout.readline().strip()
            _player = self.simulate.stdout.readline().strip()
            _output = self.simulate.stdout.readline().strip()
            self.update_player_side(_player, _output)
            if 'p1' in player:
                self.p1_trapped['a'] = True
                self.p1_open_request['a'] = True
            elif 'p2' in player:
                self.p2_trapped['a'] = True
                self.p2_open_request['a'] = True
                self.perform_p2_action()
            return True

        elif re.search(isnt_your_turn_regex, output):
            print(player)
            print(output)
            #Maybe related to a bad wait logic
            print('Player needs to switch.')
            if 'p1' in player:
                print('p1 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=True))
            else:
                print('p2 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=False))
            print('self.p1_is_waiting', self.p1_is_waiting)
            print('self.p2_is_waiting', self.p2_is_waiting)
            print('self.p1_must_switch', self.p1_must_switch)
            print('self.p2_must_switch', self.p2_must_switch)
            print('last 6 requests', self.request_outputs[-12:])
            print('Player tried to move early.')
            for i in range(min(12, len(self.request_outputs))):
                neg = (i + 1) * -1
                print(self.request_outputs[neg])
            b=1/0
            return
        elif re.search(need_switch_response_regex, output):
            # Seems triggered by volt switch, u turn or maybe a faint and upkeep didnt trigger
            print(player)
            print(output)
            print('Player needs to switch.')
            if 'p1' in player:
                print('p1 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=True))
            else:
                print('p2 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=False))
            print('self.p1_is_waiting', self.p1_is_waiting)
            print('self.p2_is_waiting', self.p2_is_waiting)
            print('self.p1_must_switch', self.p1_must_switch)
            print('self.p2_must_switch', self.p2_must_switch)
            print('last 6 requests', self.request_outputs[-12:])
            for i in range(min(12, len(self.request_outputs))):
                neg = (i + 1) * -1
                print(self.request_outputs[neg])
            if 'p1' in player:
                self.p1_must_switch['a'] = True
            else:
                self.p2_must_switch['a'] = True
            if 'p1' in player:
                print('p1 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=True))
            else:
                print('p2 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=False))
            b=1/0
            return
        elif re.search(cant_switch_to_fainted_regex, output):
            print('Player tried switching to a fainted pokemon.')
            if 'p1' in player:
                print('p1 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=True))
            else:
                print('p2 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=False))
            for i in range(min(12, len(self.request_outputs))):
                neg = (i + 1) * -1
                print(self.request_outputs[neg])
            if 'p1' in player:
                response = get_sample_action('p1', self.sample_actions(position='a', is_p1_perspective=True))
                print('p1_action: ', response)
                self.simulate.stdin.write(response+'\n')
      #        print(response)
            if 'p2' in player:
                response = get_sample_action('p2', self.sample_actions(position='a', is_p1_perspective=False))
                print('p2_action: ', response)
                self.simulate.stdin.write(response+'\n')
      #        print(response)
            b=1/0
            return
        elif re.search(cant_switch_to_active_regex, output):
            #Maybe a weird naming issue like alola
            #Might be related to illusion switching into self
            print('Player tried switching to an active pokemon. Check naming - multi form?')
            print('self.p1_selected', self.p1_selected)
            print('self.p2_selected', self.p2_selected)
            if 'p1' in player:
                print('p1 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=True))
            else:
                print('p2 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=False))
            for i in range(min(12, len(self.request_outputs))):
                neg = (i + 1) * -1
                print(self.request_outputs[neg])
            if 'p1' in player:
                response = get_sample_action('p1', self.sample_actions(position='a', is_p1_perspective=True))
                print('p1_action: ', response)
                self.simulate.stdin.write(response+'\n')
      #        print(response)
            if 'p2' in player:
                response = get_sample_action('p2', self.sample_actions(position='a', is_p1_perspective=False))
                print('p2_action: ', response)
                self.simulate.stdin.write(response+'\n')
      #        print(response)
            b=1/0
            return
        elif re.search(disabled_move_regex, output):
            print('Silent ignore, pkmn used disabled move, maybe taunted same turn')
            print(player)
            print(output)

            if 'p1' in player:
                print('p1 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=True))
                for atk in self.p2_pokemon[0].attacks:
                    print(atk.attack_name)
                    print('disabled', atk.disabled)
            else:
                print('p2 availables: ', self.get_valid_moves_for_player(position='a', is_p1_perspective=False))
                for atk in self.p2_pokemon[0].attacks:
                    print(atk.attack_name)
                    print('disabled', atk.disabled)

            for i in range(min(8, len(self.request_outputs))):
                neg = (i + 1) * -1
                print(self.request_outputs[neg])
            return
        elif '|error|[Invalid choice]' in output or '|error|[Unavailable choice]' in output:
        # check last output for p1 vs p2
            print(player)
            print(output)
            for i in range(min(6, len(self.request_outputs))):
                neg = (i + 1) * -1
                print(self.request_outputs[neg])
            if 'p1' in player:
                response = get_sample_action('p1', self.sample_actions(position='a', is_p1_perspective=True))
                print('p1_action: ', response)
                self.simulate.stdin.write(response+'\n')
      #        print(response)
            if 'p2' in player:
                response = get_sample_action('p2', self.sample_actions(position='a', is_p1_perspective=False))
                print('p2_action: ', response)
                self.simulate.stdin.write(response+'\n')
      #        print(response)
            # in the case of force switch, pokemon fainted needs new logic in future
            # maybe affected by u turn. will observe logs.
            return
        self.request_outputs.append(player)
        self.request_outputs.append(output)

        # If we get here, we know we got a valid move for both parties
        self.p1_is_waiting = False
        self.p2_is_waiting = False
        # Assume force/wait has been dealt with
        self.p1_must_switch = {'a':False, 'b':False}
        self.p2_must_switch = {'a':False, 'b':False}

        self.update_player_side(player, output)


    def update_player_side(self, player, output):
#        if 'U-turn' in output:
        if self.display_everything:
            print(player)
            print(output)

        player_details_str = output
        # Piece1 is just the request
        player_details_json = json.loads(player_details_str.split('|')[2])

        if player not in player_team_collection:
            player_team_collection[player] = set()
        player_team_collection[player].add(output)


        pokemon_json = player_details_json['side']['pokemon']
        player_pokemon = []
        for pkmn in pokemon_json:
            player_pokemon.append(sim_pokemon_from_json(pkmn))

        for pkmn in player_pokemon:
            # Storing gen 8 info
            all_revealed_items.add(pkmn.item)

            all_revealed_abilities.add(pkmn.ability)
            all_revealed_pokemon_names.add(pkmn.name)
            all_revealed_pokemon_names.add(pkmn.form)
            if pkmn.attacks is not None:
                for atk in pkmn.attacks:
                    all_revealed_attack_names.add(atk.attack_name)


        # if waiting, dont update active pokemon
        if 'active' in player_details_json:
            attacks_json = player_details_json['active']
            #update active pokemon attacks
            positions = ['a', 'b']
            for i in range(len(attacks_json)):
                # Update based on fainted logic here
                if 'p1' in player:
                    self.p1_open_request[positions[i]] = True
                else:
                    self.p2_open_request[positions[i]] = True
                # For now, assume these line up.
                pkmn = player_pokemon[i]
                atk_set = attacks_json[i]['moves']
                if 'trapped' in attacks_json[i]:
#                    print(pkmn.name, 'is trapped', attacks_json[i]['trapped'])
                    if 'p1' in player:
                        self.p1_trapped[positions[i]] = attacks_json[i]['trapped']
                    else:
                        self.p2_trapped[positions[i]] = attacks_json[i]['trapped']
                else:
                    if 'p1' in player:
                        self.p1_trapped[positions[i]] = False
                    else:
                        self.p2_trapped[positions[i]] = False

                canMegaEvolve = False
                if "canMegaEvo" in attacks_json[i]:
#                    print(pkmn, 'can mega evolve.')
                    canMegaEvolve = attacks_json[i]['canMegaEvo']
                pkmn.canMegaEvolve = canMegaEvolve

                zmoves  = [None, None, None, None]
                if "canZMove" in attacks_json[i]:
                    zmoves = attacks_json[i]['canZMove']
                    print(pkmn, ' has z moves', zmoves)

                canDynamax = False
                if "canDynamax" in attacks_json[i]:
#                    print(pkmn, 'can dyna max.')
                    canDynamax = attacks_json[i]['canDynamax']
                pkmn.canDynamax = canDynamax


                new_attacks = []
                for idx, update_atk in enumerate(atk_set):
                    zmove  = zmoves[idx]
                    for pk_atk in pkmn.attacks:
                        # cant do this because of moves like hidden power rock
                        if update_atk['move'] == pk_atk.attack_name or ('hiddenpower' in update_atk['id'] and pk_atk.id.startswith(update_atk['id'])):
                            if 'disabled' in update_atk:
                                pk_atk.disabled = update_atk['disabled']
#                                if pk_atk.disabled:
#                                    print(pk_atk.attack_name, 'is disabled', update_atk['disabled'])
#                                    print('update_atk data', update_atk)
                            new_attacks.append(pk_atk)
                            if zmove != None:
                                pk_atk.isZ = True
                            break
                for atk in pkmn.attacks:
                    if atk not in new_attacks:
                        # not revealed.
                        atk.disabled = True
                        new_attacks.append(atk)
                pkmn.attacks = new_attacks

        if 'p1' in player:
            self.p1_pokemon = player_pokemon
        else:
            self.p2_pokemon = player_pokemon


    def process_update(self):
        # consume next line since it is only pipe
        output = self.simulate.stdout.readline().strip()

        update_finished = False

        while output != '':
            output = self.simulate.stdout.readline().strip()
            if '|heal|' in output or '|switch|' in output or '|move|' in output or '|-mega|' in output:
                pass
            else:
                pass
            if self.display_everything:
                print(output)
            events_collection.add(output)

            if re.search(update_complete_regex, output):
                update_finished = True

            message  = ''
            #Used to observe failure for that game while ignoring other games
            self.transcripto.append(output)
#            continue
            # damage comes in pairs. ignore the second one.
            if re.search(damage_detected_regex, output) or re.search(heal_detected_regex, output):

                #ignore second damage/heal output
                self.simulate.stdout.readline().strip()

            if re.search(damage_detected_regex, output):
#|-damage|p2a: Whiscash|0 fnt|[from] item: Life Orb
#|-damage|p2a: Whiscash|2/100 psn|[from] item: Rocky Helmet|[of] p1a: Ferrothorn
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                health_status = output.split('|')[3]
                if is_player_1:
                    self.p1_reward -= 3
                    message = '_p1_%s hurt by attack' % (pkmn,)
                else:
                    self.p1_reward += 3
                    message = '_p2_%s hurt by attack' % (pkmn,)
                self.update_curr_health(is_player_1, pkmn, health_status)

            if re.search(boost_regex, output) is not None:
                self.process_boost_unboost(output, True)
            if re.search(unboost_regex, output) is not None:
                self.process_boost_unboost(output, False)
            if re.search(forme_details_change_regex, output) is not None:
                self.process_form_update(output)
            if re.search(perish_song_regex, output) is not None:
                self.update_perish_song(output)
#            if re.search(output, attack_missed_or_failed_regex) is not None:
#                update_missed_failed(output)
            if re.search(smack_down_regex, output) is not None:
#'|-start|p1a: Gliscor|Smack Down'
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_smack_down[position] = True
                    message = '_p1_%s is smacked_down' % (pkmn,)
                else:
                    self.p2_smack_down[position] = True
                    message = '_p2_%s is smacked_down' % (pkmn,)
            if re.search(yawned_used_regex, output) is not None:
#|-start|p2a: Emboar|move: Yawn|[of] p1a: Uxie
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_yawned[position] = True
                    message = '_p1_%s is yawned' % (pkmn,)
                else:
                    self.p2_yawned[position] = True
                    message = '_p2_%s is yawned' % (pkmn,)
            if re.search(yawned_succeeded_regex, output):
                # Yawn succeeded. doc target player
#|-end|p2a: Emboar|move: Yawn|[silent]
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_reward -= 5
                    message = '_p1_%s is asleep by yawn' % (pkmn,)
                else:
                    self.p2_reward -= 5
                    message = '_p2_%s is asleep by yawn' % (pkmn,)

        #Level 1 logic, convert each turn. from ints to enums. == 0 Neutral < 1 Resisted > 1 Super
        #Level 2 logic, decrease if player hurts ally regardless  -  ignore for now until doubles data is collected.
#        self.p1_effective = {'a':0, 'b':0}
#        self.p2_effective = {'a':0, 'b':0}
            if re.search(attack_resisted_regex, output):
                # resist -1, super +1, immune -2
                # hurt ally logic should be in damage -2
#|-resisted|p1a: Kyurem
                #opposite
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_effective[position] += 1
                    self.p1_reward += 1
                    self.p2_reward -= 1
                    message = '_p1_%s resisted' % (pkmn,)
                else:
                    self.p2_effective[position] += 1
                    self.p2_reward += 1
                    self.p1_reward -= 1
                    message = '_p2_%s resisted' % (pkmn,)
            if re.search(attack_super_effective_regex, output):
                # resist -1, super +1, immune -2
                # hurt ally logic should be in damage -2
#|-supereffective|p2a: Tangrowth
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_effective[position] += -1
                    self.p1_reward -= 1
                    self.p2_reward += 1
                else:
                    self.p2_effective[position] += -1
                    self.p2_reward -= 1
                    self.p1_reward += 1
                message = 'attack was super effective'
            if re.search(attack_immune_regex, output):
                # resist -1, super +1, immune -2
                # hurt ally logic should be in damage -2
#|-immune|p2a: Landorus
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_effective[position] += 2
                    self.p1_reward += 2
                    self.p2_reward -= 2
                    message = 'doesnt affect _p1_%s' % (pkmn,)
                else:
                    self.p2_effective[position] += 2
                    self.p2_reward += 2
                    self.p1_reward -= 2
                    message = 'doesnt affect _p2_%s' % (pkmn,)
            if re.search(confusion_started_regex, output):
#|-start|p1a: Dragonite|confusion|[fatigue]
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_active_pokemon_stats[position].confused = True
                    self.p1_reward -= 2
                    message = '_p1_%s is confused' % (pkmn,)
                else:
                    self.p2_active_pokemon_stats[position].confused = True
                    self.p2_reward -= 2
                    message = '_p2_%s is confused' % (pkmn,)
            if re.search(confusion_ended_regex, output):
#|-end|p1a: Dragonite|confusion|
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_active_pokemon_stats[position].confused = False
                    self.p1_reward += 2
                    message = '_p1_%s confusion ended' % (pkmn,)
                else:
                    self.p2_active_pokemon_stats[position].confused = False
                    self.p2_reward += 2
                    message = '_p2_%s confusion ended' % (pkmn,)
            if re.search(item_removed_by_user_regex, output):
#|-enditem|p1a: Darmanitan|Life Orb|[from] move: Knock Off|[of] p2a: Meloetta
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_reward -= 2
                    self.p2_reward += 2
                    message = '_p1_%s item knocked off' % (pkmn,)
                else:
                    self.p2_reward -= 2
                    self.p1_reward += 2
                    message = '_p2_%s item knocked off' % (pkmn,)
                no_item = 'noitem'
                self.update_item(pkmn, no_item, is_player_1)
            if re.search(item_used_regex, output):
#|-enditem|p1a: Magcargo|White Herb
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                no_item = 'noitem'
                message = '_p1_%s used item' % (pkmn,)
                if not is_player_1:
                    message = '_p2_%s used item' % (pkmn,)
                self.update_item(pkmn, no_item, is_player_1)
            if re.search(item_swapped_regex, output):
#|-item|p2a: Solgaleo|Choice Band|[from] move: Switcheroo
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                new_item = output.split('|')[3]
                message = '_p1_%s has item %s' % (pkmn,new_item)
                if not is_player_1:
                    message = '_p2_%s has item %s' % (pkmn,new_item)
                self.update_item(pkmn, new_item, is_player_1)
            if re.search(item_frisked_regex, output):
#|-item|p1a: Swalot|Black Sludge|[from] ability: Frisk|[of] p2a: Exeggutor|[identify]
#|-item|p1a: Sableye|Sablenite|[from] ability: Frisk|[of] p2a: Exeggutor|[identify]
#|-item|p1a: Weavile|Assault Vest|[from] ability: Pickpocket|[of] p2a: Lurantis
                frisk_split = output.replace('|[identify]', '')
                frisk_split = frisk_split.split('|')
                item, item_player_pokemon = frisk_split[3], frisk_split[2]
                it_play, it_pkmn = item_player_pokemon.split(': ', 1)

                ability_player_pokemon = frisk_split[-1].split('[of] ')[1]
                ab_play, ab_pkmn = ability_player_pokemon.split(': ', 1)

                new_item = output.split('|')[3]
                message = '_p1_%s identified %s %s' % (ab_pkmn,it_pkmn,item)
                if 'p1' not in ab_play:
                    message = '_p2_%s identified %s %s' % (ab_pkmn,it_pkmn,item)

                self.update_item(it_pkmn, item, 'p1' == it_play[:2])
                self.update_seen_ability('p1' in ab_play, ab_pkmn, 'Frisk')
            if re.search(move_did_not_succeed, output):
#|-fail|p1a: Zapdos
#|cant|p1a: Lanturn|flinch
#|-miss|p1a: Victreebel|p2a: Malamar
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_move_succeeded[position] = False
                    self.p1_reward -= 2
                else:
                    self.p2_move_succeeded[position] = False
                    self.p2_reward -= 2
                message = 'Move failed'

            if re.search(sticky_web_activated_regex, output):
#|-activate|p2a: Venomoth|move: Sticky Web
#|-unboost|p2a: Venomoth|spe|1
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_reward -= 5
                    self.p2_reward += 5
                    message = '_p1_%s slowed down' % (pkmn,)
                else:
                    self.p1_reward += 5
                    self.p2_reward -= 5
                    message = '_p2_%s slowed down' % (pkmn,)
# Damage dealt by opponent hazards/items/abilities
            if re.search(spike_damage_regex, output) or re.search( stealthrock_damage_regex, output) or re.search(opponent_ability_damage_regex, output) or re.search(item_damage_from_opponent_regex, output) :
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_reward -= 5
                    self.p2_reward += 5
                    message = '_p1_%s hurt by spikes' % (pkmn,)
                else:
                    self.p1_reward += 5
                    self.p2_reward -= 5
                    message = '_p2_%s hurt by spikes' % (pkmn,)
# Damage dealt by own item like life orb
            if re.search(item_damage_regex, output)  :
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_reward -= 2
                    message = '_p1_%s hurt by item' % (pkmn,)
                else:
                    self.p1_reward += 2
                    message = '_p2_%s hurt by item' % (pkmn,)
            if re.search(field_activate_regex, output)  :
#perison song, ion deluge, normalize? dont care for now.
                pass
            if re.search(weather_upkeep_regex, output)  :
#weather upkeep
                new_weather = output.split('|')[2]
                if self.weather_condition == new_weather:
                    self.weather_turns += 1
                else:
                    self.weather_turns = 1
                self.weather_condition = new_weather
                message = 'weather is %s' % (new_weather,)
            if re.search(weather_end_regex, output):
                #|-weather|RainDance|[upkeep]
                self.weather_turns = 0
                self.weather_condition = 'none'
                message = 'weather ended'
            if re.search(fieldstart_regex, output)  :
#terrain upkeep
                new_terrain = output.split('|')[2]
                if 'Grassy Terrain' in new_terrain:
                    self.terrain_condition = 'Grassy Terrain'
                if 'Misty Terrain' in new_terrain:
                    self.terrain_condition = 'Misty Terrain'
                if 'Electric Terrain' in new_terrain:
                    self.terrain_condition = 'Electric Terrain'
                if 'Psychic Terrain' in new_terrain:
                    self.terrain_condition = 'Psychic Terrain'
                message = 'terrain is %s' % (new_terrain,)
            if re.search(fieldend_regex, output):
                #|-fieldstart|move: Grassy Terrain|
                self.terrain_condition = 'none'
                message = 'terrain ended'
            if re.search(roomstart_regex, output)  :
#trick room/magic room
                new_room = output.split('|')[2]
                if 'Trick Room' in new_room:
                    self.current_room = 'Trick Room'
                if 'Magic Room' in new_room:
                    self.current_room = 'Magic Room'
                message = 'Room is %s' % (new_room,)
            if re.search(roomend_regex, output):
                #|-fieldstart|move: Grassy Terrain|
                self.current_room = 'none'
                message = 'room ended'
            if re.search(sideend_hazards_activate_regex, output)  :
#sideend hazards
                #p1/p2
                player = output.split('|')[2][:2]
                hazard = output.split('|')[3]

                if player == 'p1':
                    self.p1_reward += 10
                    message = '_p1_player lost %s' % (hazard,)
                else:
                    self.p2_reward += 10
                    message = '_p2_player lost %s' % (hazard,)
                if hazard == 'Sticky Web':
                    if player == 'p1':
                        self.p1_has_web = False
                    else:
                        self.p2_has_web = False
                if hazard == 'Stealth Rock':
                    if player == 'p1':
                        self.p1_has_rocks = False
                    else:
                        self.p2_has_rocks = False
                if hazard == 'Spikes':
                    if player == 'p1':
                        self.p1_spikes = 0
                    else:
                        self.p2_spikes = 0
                # Toxic spikes formatted differently
                if 'Toxic Spikes' in hazard:
                    if player == 'p1':
                        self.p1_toxic_spikes = 0
                    else:
                        self.p2_toxic_spikes = 0
            if re.search(sideend_non_hazards_activate_regex, output)  :
#sideend non hazards
                #p1/p2
                player = output.split('|')[2][:2]
                non_hazard = output.split('|')[3]

                if player == 'p1':
                    self.p1_reward += -3
                    message = '_p1_player lost %s' % (non_hazard,)
                else:
                    self.p2_reward += -3
                    message = '_p2_player lost %s' % (non_hazard,)
                if 'Safeguard' in non_hazard:
                    if player == 'p1':
                        self.p1_safeguard = False
                    else:
                        self.p2_safeguard = False
                if 'Light Screen' in non_hazard:
                    if player == 'p1':
                        self.p1_lightscreen = False
                    else:
                        self.p2_lightscreen = False
                if 'Reflect' in non_hazard:
                    if player == 'p1':
                        self.p1_reflect = False
                    else:
                        self.p2_reflect = False
                if 'Tailwind' in non_hazard:
                    if player == 'p1':
                        self.p1_tailwind = False
                    else:
                        self.p2_tailwind = False
                if 'Aurora Veil' in non_hazard:
                    if player == 'p1':
                        self.p1_aurora_veil = False
                    else:
                        self.p2_aurora_veil = False

            if re.search(sidestart_regex, output)  :
#sidestart  hazards and blizards
                side_split = output.split('|')
                player, move = side_split[2][:2], side_split[-1]
                #p1/p2
                # make negative if hazard
                hzard_shield_reward = 10

                if 'Safeguard' in move:
                    if player == 'p1':
                        self.p1_safeguard = True
                    else:
                        self.p2_safeguard = True
                if 'Light Screen' in move:
                    if player == 'p1':
                        self.p1_lightscreen = True
                    else:
                        self.p2_lightscreen = True
                if 'Reflect' in move:
                    if player == 'p1':
                        self.p1_reflect = True
                    else:
                        self.p2_reflect = True
                if 'Tailwind' in move:
                    if player == 'p1':
                        self.p1_tailwind = True
                    else:
                        self.p2_tailwind = True
                if 'Aurora Veil' in move:
                    if player == 'p1':
                        self.p1_aurora_veil = True
                    else:
                        self.p2_aurora_veil = True
                if 'Sticky Web' in move:
                    hzard_shield_reward = -10
                    if player == 'p1':
                        self.p1_has_web = True
                    else:
                        self.p2_has_web = True
                if 'Stealth Rock' in move:
                    hzard_shield_reward = -10
                    if player == 'p1':
                        self.p1_has_rocks = True
                    else:
                        self.p2_has_rocks = True
                if 'Spikes' in move and 'Toxic Spikes' not in move:
                    hzard_shield_reward = -10
                    if player == 'p1':
                        self.p1_spikes += 1
                    else:
                        self.p2_spikes += 1
                # Toxic spikes formatted differently
                if 'Toxic Spikes' in move:
                    hzard_shield_reward = -10
                    if player == 'p1':
                        self.p1_toxic_spikes += 1
                    else:
                        self.p2_toxic_spikes += 1
                if player == 'p1':
                    self.p1_reward += hzard_shield_reward
                    message = '_p1_player has %s' % (move,)
                else:
                    self.p2_reward += hzard_shield_reward
                    message = '_p2_player has %s' % (move,)


            if re.search(destiny_bond_regex, output):
#|-singlemove|p1a: Sharpedo|Destiny Bond
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_destined[position] = True
                    self.p1_reward += 2
                    message = '_p1_%s trying to take down with it' % (pkmn,)
                else:
                    self.p2_destined[position] = True
                    self.p2_reward += 2
                    message = '_p2_%s trying to take down with it' % ( pkmn,)
            if re.search(heal_from_target_regex, output) or re.search(general_heal_regex, output) :
#|-heal|p2a: Venusaur|31/100|[from] drain|[of] p1a: Flygon
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_reward += 2
                    message = '_p1_%s healed a little' % (pkmn,)
                else:
                    self.p2_reward += 2
                    message = '_p2_%s healed a little' % (pkmn,)
                health_status = output.split('|')[3]
                self.update_curr_health(is_player_1, pkmn, health_status)
            # Currently painsplit?
            if re.search(pain_split_regex, output) :
#|-sethp|p2a: Mismagius|77/100|[from] move: Pain Split
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_reward += 2
                    message = '_p1_%s shared the pain' % (pkmn,)
                else:
                    self.p2_reward += 2
                    message = '_p2_%s shared the pain' % (pkmn,)
            if re.search(trace_regex, output) :
#|-ability|p2a: Gardevoir|Water Absorb|[from] ability: Trace|[of] p1a: Jellicent
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                ability = output.split('|')[3]
                target_pkmn = output.split('|')[-1].split(': ', 1)[1]
                target_player = output.split('|')[-1].split(': ', 1)[0]
                self.update_seen_ability(is_player_1, pkmn, ability)
                self.update_seen_ability('p1' in target_player, target_pkmn, ability)
                if is_player_1:
                    message = '_p1_%s traced %s' % (pkmn, ability)
                else:
                    message = '_p2_%s traced %s' % (pkmn, ability)
            if re.search(clear_all_boosts_regex, output) :
#|-clearallboost
                self.p1_active_pokemon_stats['a'].clear_all_boosts()
                self.p1_active_pokemon_stats['b'].clear_all_boosts()
                self.p2_active_pokemon_stats['a'].clear_all_boosts()
                self.p2_active_pokemon_stats['b'].clear_all_boosts()
                message = 'All stats cleared'
            if re.search(clear_neg_boosts_regex, output) :
#|-clearnegativeboost|p2a: Cloyster|[silent]
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_active_pokemon_stats[position].clear_neg_boosts()
                    message = '_p1_%s negative stats cleared' % (pkmn, )
                else:
                    self.p2_active_pokemon_stats[position].clear_neg_boosts()
                    message = '_p2_%s negative stats cleared' % (pkmn, )
            if re.search(clear_boost_regex, output) :
#|-clearboost|p2a: Zeraora
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    message = '_p1_%s boosts cleared' % (pkmn, )
                    self.p1_active_pokemon_stats[position].clear_all_boosts()
                else:
                    self.p2_active_pokemon_stats[position].clear_all_boosts()
                    message = '_p2_%s boosts cleared' % (pkmn, )
# Punish all statuses equally. even if self inflicted like poison heal with toxic orb.
            if re.search(status_from_ability_regex, output) or re.search(status_from_enemy_move_regex, output) or re.search(sleep_from_rest_regex, output) or re.search(status_from_item_regex, output) :
#|-status|p1a: Carracosta|psn
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
#                status = output.split('|')[-3]
                status = 'statused'
                if is_player_1:
                    self.p1_reward -= 5
                    message = '_p1_%s is %s' % (pkmn, status)
                else:
                    self.p2_reward -= 5
                    message = '_p2_%s is %s' % (pkmn, status)
            if re.search(curestatus_regex, output) :
#|-curestatus|p2a: Spiritomb|slp|[msg]
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                status = output.replace('|[msg]', '').split('|')[-1]
                if is_player_1:
                    self.p1_reward += 5
                    message = '_p1_%s is cured of %s' % (pkmn, status)
                else:
                    self.p2_reward += 5
                    message = '_p2_%s is cured of %s' % (pkmn, status)
            # lazy regex, make sure Frisk doesnt exist
            if re.search(activate_ability_regex, output) and 'Frisk' not in output and 'Pickpocket' not in output:
#|-fieldstart|move: Grassy Terrain|[from] ability: Grassy Surge|[of] p1a: Tapu Bulu
                output_1 = output.split('[from] ability: ')
                ability, player_pkmn = output_1[1].split('|[of] ')
                player, pkmn = player_pkmn.split(': ', 1)
                self.update_seen_ability('p1' in player, pkmn, ability)
                if 'p1' in player:
                    message = '_p1_%s used ability %s' % (pkmn, ability)
                else:
                    message = '_p2_%s used ability %s' % (pkmn, ability)

            if re.search(start_dynamax_regex, output):
#|-start|p2a: Lapras|Dynamax
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_used_dynamax = True
                    self.p1_active_pokemon_stats[position].dynamax_activated = True
                    self.p1_active_pokemon_stats[position].dynamax_turns = 0
                    message = '_p1_%s used dynamax' % (pkmn, )
                else:
                    self.p2_used_dynamax = True
                    self.p2_active_pokemon_stats[position].dynamax_activated = True
                    self.p2_active_pokemon_stats[position].dynamax_turns = 0
                    message = '_p2_%s used dynamax' % (pkmn, )
#                print(message)
            if re.search(end_dynamax_regex, output):
#|-end|p2a: Farfetch'd|Dynamax
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_active_pokemon_stats[position].dynamax_activated = False
                    self.p1_active_pokemon_stats[position].dynamax_turns = 0
                    message = '_p1_%s dynamax ended' % (pkmn, )
                else:
                    self.p2_active_pokemon_stats[position].dynamax_activated = False
                    self.p2_active_pokemon_stats[position].dynamax_turns = 0
                    message = '_p2_%s dynamax ended' % (pkmn, )
#                print(message)
            if re.search(start_substitute_regex, output):
#|-start|p2a: Cresselia|Substitute
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_active_pokemon_stats[position].substitute = True
                    message = '_p1_%s used substitute' % (pkmn, )
                else:
                    self.p2_active_pokemon_stats[position].substitute = True
                    message = '_p2_%s used substitute' % (pkmn, )
            if re.search(end_substitute_regex, output):
#|-end|p2a: Serperior|Substitute
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_active_pokemon_stats[position].substitute = False
                    message = '_p1_%s substitute broken' % (pkmn, )
                else:
                    self.p2_active_pokemon_stats[position].substitute = False
                    message = '_p2_%s substitute broken' % (pkmn, )
            if re.search(crit_regex, output):
#|-crit|p2a: Ambipom
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_reward -= 5
                else:
                    self.p2_reward -= 5
                message = 'Critical hit!'
            if re.search(switch_regex, output) or re.search(drag_regex, output):
#|switch|p2a: Zygarde|Zygarde, L78|75/100|[from]move: U-turn
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                self.handle_switch(is_player_1, pkmn, position)
                if is_player_1:
                    message = '_p1_%s entered' % (pkmn, )
                else:
                    message = '_p2_%s entered' % (pkmn, )
                health_status = output.split('|')[4]
                self.update_curr_health(is_player_1, pkmn, health_status)
            if re.search(move_regex, output):
#|move|p2a: Garchomp|Outrage|p1a: Ninetales|[from]lockedmove
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                atk_name = output.split('|')[3]
                self.update_seen_moves(is_player_1, pkmn, atk_name)
                if is_player_1:
                    message = '_p1_%s used %s' % (pkmn, atk_name)
                    self.p1_seen_attacks[position] = atk_name
                else:
                    message = '_p2_%s used %s' % (pkmn, atk_name)
                    self.p2_seen_attacks[position] = atk_name
            if re.search(faint_regex, output):
#|faint|p1a: Hawlucha
                self.faint_did_happen = True
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
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
            if re.search(zoroark_end_illusion_regex, output):
#|-end|p2a: Zoroark|Illusion
                #reward goes to oppposite player
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p2_reward += 15
                    message = '_p1_%s illusion ended' % (pkmn, )
                else:
                    self.p1_reward += 15
                    message = '_p2_%s illusion ended' % (pkmn, )
                self.update_seen_pokemon(is_player_1, pkmn)
            if re.search(zoroark_replace_regex, output):
#|replace|p2a: Zoroark|Zoroark, L80, F
                #reward goes to oppposite player
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                self.update_seen_pokemon(is_player_1, pkmn)
            if re.search(zpower_regex, output):
#|-zpower|p1a: Charizard
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                if is_player_1:
                    self.p1_used_zmove = True
                    message = '_p1_%s used zmove' % (pkmn, )
                else:
                    self.p2_used_zmove = True
                    message = '_p2_%s used zmove' % (pkmn, )
            if re.search(mega_regex, output):
#|-mega|p1a: Alakazam|Alakazam|Alakazite
                is_player_1, pkmn, position = self.get_player_pkmn_position(output)
                new_item = output.split('|')[-1]
                if is_player_1:
                    self.p1_used_mega = True
                    message = '_p1_%s used mega' % (pkmn, )
                else:
                    self.p2_used_mega = True
                    message = '_p2_%s used mega' % (pkmn, )
                self.update_item(pkmn, new_item, is_player_1)
            self.append_to_transcript(message)
            self.printo_magnet(message)

        return update_finished


    def process_boost_unboost(self, output, is_boost=True):
#|-boost|p1a: Flygon|atk|1
#|-boost|p2a: Malamar|atk|1|[zeffect]
#|-boost|p2a: Malamar|def|1|[zeffect]
#|-boost|p2a: Malamar|spa|1|[zeffect]
#|-boost|p2a: Malamar|spd|1|[zeffect]
#|-unboost|p1a: Hitmontop|def|1
#|-unboost|p1a: Hitmontop|spd|1
#|-unboost|p2a: Lunala|evasion|1
        boost_pieces = output.split('|')
        _, _, player_pkmn, stat, amt, *rest = boost_pieces
        player = player_pkmn.split(': ', 1)[0]
        pkmn_position =player[-1]
        if 'p1' == player[:-1]:
            self.p1_active_pokemon_stats[pkmn_position].boost_stat(stat, amt, is_boost)
        if 'p2' == player[:-1]:
            self.p2_active_pokemon_stats[pkmn_position].boost_stat(stat, amt, is_boost)

    def process_form_update(self, output):
#'|detailschange|p2a: Venusaur|Venusaur-Mega, L81, M'
#'|-formechange|p2a: Minior|Minior-Meteor||[from] ability: Shields Down'
        details_split = output.split('|')
        player_pkmn = details_split[2]
        player, pkmn = player_pkmn.split(': ', 1)
        pkmn_new_form = details_split[3].split(', ')[0]
        self.update_form(pkmn, pkmn_new_form, 'p1' == player[:-1])

    def update_form(self, pkmn, pkmn_new_form, is_player_1):
        if is_player_1:
            self.p1_seen_details[pkmn]['form'] = pkmn_new_form
        else:
            self.p2_seen_details[pkmn]['form'] = pkmn_new_form
        revealed_pokemon_names.add(pkmn_new_form)

    def update_item(self, pkmn, new_item, is_player_1):
        if is_player_1:
            self.p1_seen_details[pkmn]['item'] = new_item
        else:
            self.p2_seen_details[pkmn]['item'] = new_item
        revealed_items.add(new_item)

    def update_perish_song(self, output):
#'|-start|p2a: Hydreigon|perish3'
        perish_turn_count = int(output[-1])
        perish_split = output.split('|')
        player_pkmn = perish_split[2]
        player, pkmn = player_pkmn.split(': ', 1)
        pkmn_position = player[-1]
        if 'p1' == player[:-1]:
            self.p1_perished[pkmn_position] = perish_turn_count
        if 'p2' == player[:-1]:
            self.p2_perished[pkmn_position] = perish_turn_count

    def update_missed_failed(self, output):
#'|-miss|p1a: Victreebel|p2a: Malamar'
#'|-fail|p2a: Jellicent|heal'
        missed_fail_split = output.split('|')
        player_pkmn = missed_fail_split[2]
        player, pkmn = player_pkmn.split(': ', 1)
        pkmn_position = player[-1]
        if 'p1' == player[:-1]:
            self.p1_missed_failed[pkmn_position] = True
        if 'p2' == player[:-1]:
            self.p2_missed_failed[pkmn_position] = True

    def get_player_pkmn_position(self, output):
        output_split = output.split('|')
        player_pkmn = output_split[2]
        player, pkmn = player_pkmn.split(': ', 1)
        pkmn_position = player[-1]
        return ('p1' == player[:-1]), pkmn, pkmn_position


    def update_seen_moves(self, is_player_1, pkmn_name, atk_name):
        seen_attacks = self.p1_seen_details
        if not is_player_1:
            seen_attacks = self.p2_seen_details
        pkmn_attacks = {}
        atk_count = 0
        if pkmn_name in seen_attacks:
            pkmn_attacks = seen_attacks[pkmn_name]['attacks']

        if atk_name in pkmn_attacks:
            atk_count = pkmn_attacks[atk_name]

        atk_count += 1
        pkmn_attacks[atk_name] = atk_count
        seen_attacks[pkmn_name]['attacks'] = pkmn_attacks
        revealed_attack_names.add(atk_name)

    def get_pp_used_for_move(self, is_player_1, pkmn_name, atk_name):
        seen_attacks = self.p1_seen_details
        if not is_player_1:
            seen_attacks = self.p2_seen_details

        if pkmn_name not in seen_attacks:
            return 0

        pkmn_attacks = seen_attacks[pkmn_name]['attacks']
        if atk_name not in pkmn_attacks:
            return 0

        return pkmn_attacks[atk_name]

    # Call upon switchin/every turn when getting active moves
    def update_seen_pokemon(self, is_player_1, pkmn_name, gender='', level=80):
        revealed_pokemon_names.add(pkmn_name)
        seen_attacks = self.p1_seen_details
        if not is_player_1:
            seen_attacks = self.p2_seen_details
        if pkmn_name not in seen_attacks:
            seen_attacks[pkmn_name] = {}
            seen_attacks[pkmn_name]['attacks'] = {}
            seen_attacks[pkmn_name]['form'] = pkmn_name
            seen_attacks[pkmn_name]['item'] = 'hidden_item'
            seen_attacks[pkmn_name]['status'] = Status.NOTHING
            seen_attacks[pkmn_name]['gender'] = ''
            seen_attacks[pkmn_name]['health'] = 1
            seen_attacks[pkmn_name]['last_health'] = 1
            seen_attacks[pkmn_name]['level'] = 80
            seen_attacks[pkmn_name]['ability'] = 'hidden_ability'

    # Call upon ability being revealed, either side
    # Also called on transorms if only 1 ability
    def update_seen_ability(self, is_player_1, pkmn_name, ability):
        seen_attacks = self.p1_seen_details
        if not is_player_1:
            seen_attacks = self.p2_seen_details
        seen_attacks[pkmn_name]['ability'] = ability
        revealed_abilities.add(ability)

    def handle_switch(self, is_player_1, pkmn_name, position, is_transform_or_baton=False):
        if is_player_1:
            self.p1_active_pokemon_stats[position] = ActiveStats()
            self.p1_selected[position] = pkmn_name
            self.p1_reward -= 5
        else:
            self.p2_active_pokemon_stats[position] = ActiveStats()
            self.p2_selected[position] = pkmn_name
            self.p2_reward -= 5
        self.update_seen_pokemon(is_player_1, pkmn_name)

    def update_curr_health(self, is_player, pkmn_name, health_status):
        status = Status.NOTHING
        health_ratio = 0
        if 'fnt' not in health_status:
            curr_health, health_status = health_status.split('/')
            health_status = health_status.split(' ')
            max_health = int(health_status[0])
            if len(health_status) == 2:
                status = Status(health_status[1])
            health_ratio = int(curr_health)/float(max_health)
        else:
            curr_health = 0
            max_health = 0
            status = Status('fnt')
        seen_attacks = self.p1_seen_details
        if not is_player:
            seen_attacks = self.p2_seen_details
        seen_attacks[pkmn_name]['health'] = health_ratio
        delta_change = seen_attacks[pkmn_name]['health'] - seen_attacks[pkmn_name]['last_health']
        seen_attacks[pkmn_name]['last_health'] = health_ratio
        seen_attacks[pkmn_name]['status'] = Status.NOTHING

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


class PokeSimEnv(gym.Env):
    NETWORK_MODEL = None
    metadata = {'render.modes': ['human']}
    # Store later for other formats but not now
    #Gen Number
    # Game type singles, doubles, triples
    # Battle Format
    # Sleep mod rule. Anything goes, etc.

#    'pikachu': {'thundershock': 1}
#    p1 seen_attacks = {}

    def __init__(self, random_style=RANDOM_STYLES.NORMAL_RANDOM, use_network_model=False, computer_network=None):
        self.random_style = random_style
        # if network exists, use that decide moves. Otherwise use random move.
        self._state = State(computer_network, self.random_style)

        self.action_space = gym.spaces.Discrete(n=len(Action)-1)
#        self.observation_space = gym.spaces.Discrete(n=self._state.shape[0])
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(1, self._state.shape[0]), dtype=np.float32)
        self.seed()
        self.computer_network = computer_network
        self.use_network_model2 = use_network_model
        print('style',random_style)
        print('use network',use_network_model)



    def step(self, action_as_int):
#        print('pre action_as_int',action_as_int)
        p2_action = None
        if isinstance(action_as_int, tuple):
            p2_action = Action(action_as_int[1])
            action_as_int = action_as_int[0]
        if self.use_network_model2 == False:
            p2_action = None
#        print('post p2_action',p2_action)
#        print('post self.use_network_model2',self.use_network_model2)
#        print('p1 availables: ', self._state.get_valid_moves_for_player(position='a', is_p1_perspective=True))
#        p1_action = get_sample_action('p1', self._state.sample_actions(position='a', is_p1_perspective=True))
        p1_action = Action(action_as_int)
        actions_targets = self._state.get_valid_moves_for_player(position='a', is_p1_perspective=True)
        p1_in_actions = False
        for act, _ in actions_targets:
            if p1_action == act:
                p1_in_actions = True
                break
        if not p1_in_actions:
            old_p1_action = p1_action
            p1_action = self._state.sample_actions(position='a', is_p1_perspective=True)
            print('Tried using %s, using %s instead' % (old_p1_action, p1_action))
            print('p1 should availables: ', self._state.get_valid_moves_for_player(position='a', is_p1_perspective=True))
        neg_reward = 0
        # Punish struggle heavily
        if p1_action == Action.Attack_Struggle:
            neg_reward = -150
            print('p1 why struggle? availables: ', self._state.get_valid_moves_for_player(position='a', is_p1_perspective=True))
            print('last 12 requests', self._state.request_outputs[-12:])

        p1_action = get_sample_action('p1', p1_action)
        reward, done, winner = self._state.step(p1_action, p2_action)

        reward = reward + neg_reward

        obs = self._state.encode(includeTranscript=True)
        info = {"transcript":obs['transcript'], "valid_onehot_player_1": obs['valid_onehot_player_1'],
         "valid_onehot_p1_targets": obs['valid_onehot_p1_targets'],
         'cat_length':obs['cat_length'], 'full_obs_len':obs['full_obs_len'], 'raw_length':obs['raw_length'],
         'reverse_transcript': obs['reverse_transcript'], 'reversed_combined':obs['reversed_combined'],
          'valid_onehot_player_2':obs['valid_onehot_player_2'], 'valid_onehot_p2_targets':obs['valid_onehot_p2_targets'],
         'winner': winner}
#        print('valid_onehot', obs['valid_onehot_player'])
        return obs['combined'], reward, done, info


    def reset(self):
        self._state.reset(self.computer_network, self.random_style)
        return self._state.encode()

    def get_current_transcript(self):
        return self._state.state_transcript

    def get_current_transcript(self):
        return self._state.state_transcript

    def sample_actions(self):
        return self._state.sample_actions(position='a', is_p1_perspective=True).value

    def seed(self, seed=None):
        self.np_random, seed1 = seeding.np_random(seed)
        seed2 = seeding.hash_seed(seed1 + 1) % 2 ** 31
        return [seed1, seed2]

    def set_network(computer_network):
        self.computer_network = computer_network

    def close(self):
        print('closing env')
        self._state.close()

class RewardScaler(gym.RewardWrapper):
    """  may not be needed for fake pokemon?
        Bring rewards to a reasonable scale for PPO.
        This is incrediably important and effects performance drastically
    """
    def reward(self, reward):
        return reward * 0.01


def make_env(random_style=RANDOM_STYLES.NORMAL_RANDOM, use_network_model=False):
    env = PokeSimEnv(random_style=random_style, use_network_model=use_network_model)
    env = RewardScaler(env)

    return env

def make_poke_env():
    def _init():
        env = make_env(random_style=RANDOM_STYLES.NORMAL_RANDOM)
        return env
    return _init

def make_poke_env_mirror():
    def _init():
        env = make_env(random_style=RANDOM_STYLES.NORMAL_RANDOM, use_network_model=True)
        print('creating mirror')
        print('mirror env', env.use_network_model2)
        return env
    return _init

def make_poke_env_strategic():
    def _init():
        env = make_env(random_style=RANDOM_STYLES.STRATEGIC_WITHDRAWAL)
        return env
    return _init

def make_poke_env_last_breath():
    def _init():
        env = make_env(random_style=RANDOM_STYLES.TIL_LAST_BREATH)
        return env
    return _init

def make_poke_env_priority_attack():
    def _init():
        env = make_env(random_style=RANDOM_STYLES.PRIORITY_ATTACK)
        return env
    return _init
