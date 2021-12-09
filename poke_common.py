#Type
#Attack
#SP Attack
# Defense
#SP Defense
# health
# speed
#Ability

import enum
import json
from pokemon_json import *
import numpy as np
#from dask_ml.preprocessing import LabelEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
import re
from collections import deque
from image_text_processing import *

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

  def get_base_weight(self):
      return 1

  def get_attack_priority_weight(self):
      if self in ATTACK_ACTIONS:
          return 0.3
      if self in SWITCH_ACTIONS:
          return 0.1
      if self == Action.Attack_Struggle:
          return 0.01
      return 0.05

  def get_till_last_breath_weight(self):
      if self in ATTACK_ACTIONS:
          return 0.3
      if self in SWITCH_ACTIONS:
          return 0.01
      if self == Action.Attack_Struggle:
          return 0.1
      return 0.05

  def get_strategic_withdrawl_weight(self, is_weak_to_stab=False, under_45_percent=False):
      # if nothing special going on. randomly pick between the other styles.
      other_options = [self.get_base_weight(), self.get_till_last_breath_weight(), self.get_attack_priority_weight()]

      if is_weak_to_stab == False or under_45_percent == False:
          return np.random.choice(other_options, 1)[0]


      if self in ATTACK_ACTIONS:
          return 0.1
      if self in SWITCH_ACTIONS:
          return 0.4
      if self == Action.Attack_Struggle:
          return 0.01
      return 0.05

class RANDOM_STYLES(enum.Enum):
    # No change
    NORMAL_RANDOM = 0
    # higher weights to attacking moves.
    PRIORITY_ATTACK = 1
    # Does not leave the battlefield outside a casket (low weights on switches. u-turn ok)
    TIL_LAST_BREATH = 2
    # weights assigned if curr_pokemon is weak to a STAB move.
    # change slots given more weight to pokemon who can resist a STAB attack
    STRATEGIC_WITHDRAWAL = 3

ATTACK_ACTIONS =  (Action.Attack_Slot_1, Action.Attack_Slot_2, Action.Attack_Slot_3, Action.Attack_Slot_4,
                    Action.Attack_Dyna_Slot_1, Action.Attack_Dyna_Slot_2, Action.Attack_Dyna_Slot_3, Action.Attack_Dyna_Slot_4,)

SWITCH_ACTIONS =  (Action.Change_Slot_1, Action.Change_Slot_2, Action.Change_Slot_3, Action.Change_Slot_4,
                    Action.Change_Slot_5, Action.Change_Slot_6 )


class Ability(enum.Enum):
    LEVITATE = 1
    ILLUSION = 2
    PRANKSTER = 3
    PURE_POWER = 4
    HARVEST = 5
    NATURAL_CURE = 6
    BIG_FIST = 7

class CurrentPokemon(enum.Enum):
    Pokemon_Slot_1 = 12
    Pokemon_Slot_2 = 13
    Pokemon_Slot_3 = 14
    Pokemon_Slot_4 = 15
    Pokemon_Slot_5 = 16
    Pokemon_Slot_6 = 17

class SelectedAttack(enum.Enum):
    Attack_Slot_1 = 1
    Attack_Slot_2 = 2
    Attack_Slot_3 = 3
    Attack_Slot_4 = 4


class GameType(enum.Enum):
    SINGLES = 1
    DOUBLES = 2
    TRIPLES = 3

class GEN(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8

class ITEMS(enum.Enum):
    BLUE_BERRY = 1
    CHOICE_SCARF = 2
    LEFT_OVERS = 3
    TOXIC_ORB = 5
    WHITE_HERB = 6
    Z_STONE = 7

class VOLATILE_STATUS(enum.Enum):
    NOTHING = 'Nothing'
    CONFUSION = 'Confusion'

class GENDER(enum.Enum):
    UNKNOWN = ''
    MALE = 'M'
    FEMALE = 'F'


class Status(enum.Enum):
    NOTHING = ''
    BURN = 'brn'
    SLEEP = 'slp'
    FROZEN = 'frz'
    PARALYSIS = 'par'
    POISON = 'psn'
    TOXIC = 'tox'
    FAINTED = 'fnt'

class WEATHER(enum.Enum):
    NONE = 'none'
    SUN = 'SunnyDay'
    RAIN = 'RainDance'
    HARSH_SUNLIGHT = 'DesolateLand'
    DOWNPOUR = 'PrimordialSea'
    HAIL = 'Hail'
    SANDSTORM = 'Sandstorm'

class TERRAIN(enum.Enum):
    NO_TERRAIN = 'none'
    ELECTRIC_TERRAIN = 'Electric Terrain'
    GRASSY_TERRAIN = 'Grassy Terrain'
    MISTY_TERRAIN = 'Misty Terrain'
    PSYCHIC_TERRAIN = 'Psychic Terrain'


#Triples       Doubles     Singles
# 3  2  1         2  1         1
#-1 -2 -3        -1 -2        -1


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

class ELEMENT_TYPE(enum.Enum):
    BUG = "Bug"
    DARK = "Dark"
    DRAGON = "Dragon"
    ELECTRIC = "Electric"
    FAIRLY = "Fairy"
    FIGHTING = "Fighting"
    FIRE = "Fire"
    FLYING = "Flying"
    GHOST = "Ghost"
    GRASS = "Grass"
    GROUND = "Ground"
    ICE = "Ice"
    NORMAL = "Normal"
    POISON = "Poison"
    PSYCHIC = "Psychic"
    ROCK = "Rock"
    STEEL = "Steel"
    WATER = "Water"
    TYPELESS = "Typeless"
    BIRD = "Bird"       # For missing No?

class ELEMENT_MODIFIER(enum.Enum):
    NUETRAL = 0
    SUPER_EFFECTIVE = 1
    RESISTED = 2
    IMMUNE = 3

def get_damage_modifier_for_type(target_pokemon_element, attacking_pokemon_element):
    damage_modifier = 1
    element_modifier = get_damage_taken(target_pokemon_element, attacking_pokemon_element)
    if element_modifier == ELEMENT_MODIFIER.NUETRAL:
        damage_modifier = 1
    if element_modifier == ELEMENT_MODIFIER.SUPER_EFFECTIVE:
        damage_modifier = 2
    if element_modifier == ELEMENT_MODIFIER.RESISTED:
        damage_modifier = 0.5
    if element_modifier == ELEMENT_MODIFIER.IMMUNE:
        damage_modifier = 0

    return damage_modifier




"""
    second param is string in case someone wants to test against things like
    paralysis, prankster etc. Not just elements
"""
def get_damage_taken(element_type, to_test_against_name):
    modifier = ELEMENT_MODIFIER.NUETRAL
    if element_type not in damage_taken_dict:
        return modifier
    element_damage_map = damage_taken_dict[element_type]
    if to_test_against_name in element_damage_map:
        element_damage_map = ELEMENT_MODIFIER(element_damage_map[to_test_against_name])
    return element_damage_map


class CATEGORY(enum.Enum):
    STATUS = 'Status'
    PHYSICAL = 'Physical'
    SPECIAL = 'Special'

class Secondary():
    def __init__(self, chance='100', boosts=[], status=None, volatileStatus=None, is_target_self=False):
        self.chance = float(chance) / 100
        self.boosts = boosts
        self.status = status
        self.volatileStatus = volatileStatus
        self.is_target_self = is_target_self

class Attack():
    def __init__(self):
        self.id = ''
        self.attack_name = ''
        self.target = 'normal'
        self.pp  = 0
        self.used_pp = 0
        self.element_type = None
        self.power = 0
        self.accuracy = 0
        self.status = None
        self.category = None
        self.priority = 1
        self.disabled = False
        self.isZ = False


class Pokemon():
    def __init__(self):
        self.name = ''
        #Only used for sending to neural network
        self.form = ''
        self.is_hidden = True
        self.level  = 0
        self.max_health = 1
        self.curr_health = 1
        self.health_ratio = 1
        self.atk = 0
        self.spatk = 0
        self.defense = 0
        self.spdef = 0
        self.speed = 0
        self.weight = 0
        self.ability = ''
        self.element_1st_type = None
        self.element_2nd_type = None
        self.attacks = None
        self.accuracy_modifier = 1
        self.attack_modifier = 1
        self.spatk_modifier = 1
        self.defense_modifier = 1
        self.spdef_modifier = 1
        self.speed_modifier = 1
        self.evasion_modifier = 1
        self.status = Status.NOTHING
        self.item = 'no item'
        self.gender = GENDER.UNKNOWN
        self.is_active = False
        self.canMegaEvolve = False
        self.canUltra = False
        self.canDynamax = False
        self.active = False

    def get_hidden_info(self):
        self.name = ''
        self.is_hidden = True
        self.level  = 0
        self.max_health = 1
        self.curr_health = 1
        self.atk = atk
        self.spatk = spatk
        self.defense = defense
        self.spdef = spdef
        self.speed = speed
        self.weight = weight
        self.ability = ability
        self.element_1st_type = element_1st_type
        self.element_2nd_type = element_2nd_type
        self.attacks = attacks
        self.status = Status.NOTHING
        self.item = ''


# 'side_conditions': {'stealthrock': 0, 'spikes': 0, 'toxic_spikes':0}, 'trapped': False, attack_locked:False,
# Attack_Slot_1_disabled:False, Attack_Slot_2_disabled:False, Attack_Slot_4_disabled:False, Attack_Slot_4_disabled:False, },
# 'weather': None, 'terrain': None, 'forceSwitch': False, 'wait': False}

class Ability(enum.Enum):
    LEVITATE = 1
    ILLUSION = 2
    PRANKSTER = 3
    PURE_POWER = 4
    HARVEST = 5
    NATURAL_CURE = 6
    BIG_FIST = 7

class ITEMS(enum.Enum):
    BLUE_BERRY = 1
    CHOICE_SCARF = 2
    LEFT_OVERS = 3
    TOXIC_ORB = 5
    WHITE_HERB = 6
    Z_STONE = 7

def pokemon_from_json(pokemon_data, attacks=None):
    name = pokemon_data['species']
    num = pokemon_data['num']
    # for one hot encoding of pokemon
    all_pokemon_names.add(name)
    level  = 5
    health = pokemon_data['baseStats']['hp']
    atk = pokemon_data['baseStats']['atk']
    spatk = pokemon_data['baseStats']['spa']
    defense = pokemon_data['baseStats']['def']
    spdef = pokemon_data['baseStats']['spd']
    speed = pokemon_data['baseStats']['spe']
    weight = pokemon_data['weightkg']
    ability = pokemon_data['abilities']['0']
    element_1st_type = ELEMENT_TYPE(pokemon_data['types'][0])
    element_2nd_type = None
    if len(pokemon_data['types']) > 1:
        element_2nd_type = ELEMENT_TYPE(pokemon_data['types'][1])


    pokemon = Pokemon()
    pokemon.name = name
    pokemon.form = name
    pokemon.level  = level
    pokemon.max_health = 1
    pokemon.curr_health = 1
    pokemon.health_ratio = 1
    pokemon.atk = atk
    pokemon.spatk = spatk
    pokemon.defense = defense
    pokemon.spdef = spdef
    pokemon.speed = speed
    pokemon.weight = weight
    pokemon.ability = ability
    pokemon.element_1st_type = element_1st_type
    pokemon.element_2nd_type = element_2nd_type
    pokemon.attacks = deque([hidden_attack(), hidden_attack(), hidden_attack(), hidden_attack()], maxlen=4)
    return pokemon



all_pokemon_by_name = {}
all_pokemon_by_key = {}
all_items_by_name = {}
all_items_by_key = {}
all_abilities_by_name = {}
all_abilities_by_key = {}
all_attacks_by_name = {}
all_attacks_by_key = {}


all_attacks_data_by_name = {}


#configured by adding pokemon
all_items = set()
all_generations = set()
all_gametypes = set()
all_tiers = set()
all_genders = set()
all_pokemon_attacks = set()
all_abilities = set()
all_pokemon_names = set()
all_weather = set()
all_status = set()
all_element_types = set()
all_terrains = set()
all_targets = set()
all_selectable_targets = set()
all_categories = set()
all_effectiveness = set()
all_pokemon_slots = set()
all_attack_slots = set()
all_actions = set()
all_rooms = set()

all_items_labels = None
all_generations_labels = None
all_gametypes_labels = None
all_tiers_labels = None
all_genders_labels = None
all_pokemon_attacks_labels = None
all_abilities_labels = None
all_pokemon_names_labels = None
all_weather_labels = None
all_status_labels = None
all_element_types_labels = None
all_terrains_labels = None
all_targets_labels = None
all_selectable_targets_labels = None
all_categories_labels = None
all_effectiveness_labels = None
all_pokemon_slot_labels = None
all_attack_slot_labels = None
all_actions_labels = None
all_rooms_labels = None


"""
all_status.add('brn')
all_status.add('par')
all_status.add('slp')
all_status.add('frz')
all_status.add('psn')
all_status.add('tox')
all_status.add('nothing')
"""
class GameType(enum.Enum):
    SINGLES = 1
    DOUBLES = 2
    TRIPLES = 3

class GEN(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8

class Tier(enum.Enum):
    UBERS = 'Ubers'
    OVER_USED = 'Over Used'
    UNDER_USED = 'Under Used'
    RARELY_USED = 'Rarely Used'
    NEVER_USED = 'Never Used'
    LITTLE_CUP = 'Little Cup'




def fill_all_category_sets():
    all_status.add(Status.NOTHING.value)
    all_status.add(Status.BURN.value)
    all_status.add(Status.SLEEP.value)
    all_status.add(Status.FROZEN.value)
    all_status.add(Status.PARALYSIS.value)
    all_status.add(Status.POISON.value)
    all_status.add(Status.TOXIC.value)
    all_status.add(Status.FAINTED.value)

    all_genders.add(GENDER.UNKNOWN.value)
    all_genders.add(GENDER.MALE.value)
    all_genders.add(GENDER.FEMALE.value)

    all_gametypes.add(GameType.SINGLES.value)
    all_gametypes.add(GameType.DOUBLES.value)
    all_gametypes.add(GameType.TRIPLES.value)

    all_generations.add(GEN.ONE.value)
    all_generations.add(GEN.TWO.value)
    all_generations.add(GEN.THREE.value)
    all_generations.add(GEN.FOUR.value)
    all_generations.add(GEN.FIVE.value)
    all_generations.add(GEN.SIX.value)
    all_generations.add(GEN.SEVEN.value)
    all_generations.add(GEN.EIGHT.value)

    all_tiers.add(Tier.UBERS.value)
    all_tiers.add(Tier.OVER_USED.value)
    all_tiers.add(Tier.UNDER_USED.value)
    all_tiers.add(Tier.RARELY_USED.value)
    all_tiers.add(Tier.NEVER_USED.value)
    all_tiers.add(Tier.LITTLE_CUP.value)

    all_rooms.add('none')
    all_rooms.add('Trick Room')
    all_rooms.add('Magic Room')
    all_rooms.add('Wonder Room')


    all_abilities.add('empty_ability')
    all_abilities.add('hidden_ability')
    all_abilities.add('unregistered_ability')
    pokemon_abilities_json = json.loads(pokemon_abilities_str)
    for ability_key in pokemon_abilities_json.keys():
        ability_id = pokemon_abilities_json[ability_key]['id'].lower()
        ability_name = pokemon_abilities_json[ability_key]['name']
        all_abilities.add(ability_id)
        all_abilities_by_name[ability_name] = ability_id
        all_abilities_by_key[ability_id] = ability_id


    all_items.add('empty_item')
    all_items.add('hidden_item')
    all_items.add('unregistered_item')
    pokemon_items_json = json.loads(pokemon_items_str)
    for item_key in pokemon_items_json.keys():
        item_id = pokemon_items_json[item_key]['id'].lower()
        item_name = pokemon_items_json[item_key]['name']
        all_items.add(item_id)
        all_items_by_name[item_name] = item_id
        all_items_by_key[item_id] = item_id

    all_pokemon_names.add('empty_pokemon')
    all_pokemon_names.add('hidden_pokemon')
    all_pokemon_names.add('unregistered_pokemon')

    attacks_json = json.loads(attacks_json_str)
    all_pokemon_attacks.add('no attack')
    all_pokemon_attacks.add('empty')
    all_pokemon_attacks.add('hidden')
    all_pokemon_attacks.add('unregistered')
    for attack_key in attacks_json.keys():
        attack_id = attacks_json[attack_key]['id'].lower()
        attack_name = attacks_json[attack_key]['name']
        all_pokemon_attacks.add(attack_id)
        all_attacks_by_name[attack_name] = attack_id
        all_attacks_by_key[attack_id] = attack_id


    all_weather.add(WEATHER.NONE.value)
    all_weather.add(WEATHER.SUN.value)
    all_weather.add(WEATHER.RAIN.value)
    all_weather.add(WEATHER.HARSH_SUNLIGHT.value)
    all_weather.add(WEATHER.DOWNPOUR.value)
    all_weather.add(WEATHER.HAIL.value)
    all_weather.add(WEATHER.SANDSTORM.value)


    all_terrains.add(TERRAIN.NO_TERRAIN.value)
    all_terrains.add(TERRAIN.ELECTRIC_TERRAIN.value)
    all_terrains.add(TERRAIN.GRASSY_TERRAIN.value)
    all_terrains.add(TERRAIN.MISTY_TERRAIN.value)
    all_terrains.add(TERRAIN.PSYCHIC_TERRAIN.value)

    all_targets.add(TARGET.NORMAL.value)
    all_targets.add(TARGET.SELF.value)
    all_targets.add(TARGET.ANY.value)
    all_targets.add(TARGET.ALL_ADJACENT_FOES.value)
    all_targets.add(TARGET.ALLY_SIDE.value)
    all_targets.add(TARGET.ALLY_TEAM.value)
    all_targets.add(TARGET.FOE_SIDE.value)
    all_targets.add(TARGET.ADJACENT_FOE.value)
    all_targets.add(TARGET.ADJACENT_ALLY.value)
    all_targets.add(TARGET.ALL_ADJACENT.value)
    all_targets.add(TARGET.ADJACENT_ALLY_OR_SELF.value)
    all_targets.add(TARGET.ALL.value)
    all_targets.add(TARGET.SCRIPTED.value)
    all_targets.add(TARGET.RANDOM_NORMAL.value)

    all_selectable_targets.add(SELECTABLE_TARGET.DO_NOT_SPECIFY.value)
    all_selectable_targets.add(SELECTABLE_TARGET.SELF.value)
    all_selectable_targets.add(SELECTABLE_TARGET.FOE_SLOT_1.value)
    all_selectable_targets.add(SELECTABLE_TARGET.FOE_SLOT_2.value)
    all_selectable_targets.add(SELECTABLE_TARGET.FOE_SLOT_3.value)
    all_selectable_targets.add(SELECTABLE_TARGET.ALLY_SLOT_1.value)
    all_selectable_targets.add(SELECTABLE_TARGET.ALLY_SLOT_2.value)
    all_selectable_targets.add(SELECTABLE_TARGET.ALLY_SLOT_3.value)

    #configured by elements map - Typeless and Bird might not be in map...
    all_element_types.add(ELEMENT_TYPE.BUG.value)
    all_element_types.add(ELEMENT_TYPE.DARK.value)
    all_element_types.add(ELEMENT_TYPE.DRAGON.value)
    all_element_types.add(ELEMENT_TYPE.ELECTRIC.value)
    all_element_types.add(ELEMENT_TYPE.FAIRLY.value)
    all_element_types.add(ELEMENT_TYPE.FIGHTING.value)
    all_element_types.add(ELEMENT_TYPE.FIRE.value)
    all_element_types.add(ELEMENT_TYPE.FLYING.value)
    all_element_types.add(ELEMENT_TYPE.GHOST.value)
    all_element_types.add(ELEMENT_TYPE.GRASS.value)
    all_element_types.add(ELEMENT_TYPE.GROUND.value)
    all_element_types.add(ELEMENT_TYPE.ICE.value)
    all_element_types.add(ELEMENT_TYPE.NORMAL.value)
    all_element_types.add(ELEMENT_TYPE.POISON.value)
    all_element_types.add(ELEMENT_TYPE.PSYCHIC.value)
    all_element_types.add(ELEMENT_TYPE.ROCK.value)
    all_element_types.add(ELEMENT_TYPE.STEEL.value)
    all_element_types.add(ELEMENT_TYPE.WATER.value)
    all_element_types.add(ELEMENT_TYPE.TYPELESS.value)
    all_element_types.add(ELEMENT_TYPE.BIRD.value)

    all_categories.add(CATEGORY.STATUS.value)
    all_categories.add(CATEGORY.PHYSICAL.value)
    all_categories.add(CATEGORY.SPECIAL.value)

    all_effectiveness.add(ELEMENT_MODIFIER.NUETRAL.value)
    all_effectiveness.add(ELEMENT_MODIFIER.SUPER_EFFECTIVE.value)
    all_effectiveness.add(ELEMENT_MODIFIER.RESISTED.value)
    all_effectiveness.add(ELEMENT_MODIFIER.IMMUNE.value)

    all_pokemon_slots.add(CurrentPokemon.Pokemon_Slot_1.value)
    all_pokemon_slots.add(CurrentPokemon.Pokemon_Slot_2.value)
    all_pokemon_slots.add(CurrentPokemon.Pokemon_Slot_3.value)
    all_pokemon_slots.add(CurrentPokemon.Pokemon_Slot_4.value)
    all_pokemon_slots.add(CurrentPokemon.Pokemon_Slot_5.value)
    all_pokemon_slots.add(CurrentPokemon.Pokemon_Slot_6.value)

    all_attack_slots.add(SelectedAttack.Attack_Slot_1.value)
    all_attack_slots.add(SelectedAttack.Attack_Slot_2.value)
    all_attack_slots.add(SelectedAttack.Attack_Slot_3.value)
    all_attack_slots.add(SelectedAttack.Attack_Slot_4.value)

    all_actions.add(Action.Attack_Slot_1.value)
    all_actions.add(Action.Attack_Slot_2.value)
    all_actions.add(Action.Attack_Slot_3.value)
    all_actions.add(Action.Attack_Slot_4.value)
    all_actions.add(Action.Attack_Dyna_Slot_1.value)
    all_actions.add(Action.Attack_Dyna_Slot_2.value)
    all_actions.add(Action.Attack_Dyna_Slot_3.value)
    all_actions.add(Action.Attack_Dyna_Slot_4.value)
    all_actions.add(Action.Change_Slot_1.value)
    all_actions.add(Action.Change_Slot_2.value)
    all_actions.add(Action.Change_Slot_3.value)
    all_actions.add(Action.Change_Slot_4.value)
    all_actions.add(Action.Change_Slot_5.value)
    all_actions.add(Action.Change_Slot_6.value)
    all_actions.add(Action.Not_Decided.value)
    all_actions.add(Action.Attack_Struggle.value)


def get_encodings_for_all_sets():
    # one-hot encode the zip code categorical data (by definition of
    # one-hot encoding, all output features are now in the range [0, 1])

    all_status_labels = LabelEncoder().fit(list(all_status))
    all_items_labels = LabelEncoder().fit(list(all_items))
    all_abilities_labels = LabelEncoder().fit(list(all_abilities))
    all_pokemon_names_labels = LabelEncoder().fit(list(all_pokemon_names))
    all_weather_labels = LabelEncoder().fit(list(all_weather))
    all_status_labels = LabelEncoder().fit(list(all_status))
    all_element_types_labels = LabelEncoder().fit(list(all_element_types))
    all_terrains_labels = LabelEncoder().fit(list(all_terrains))
    all_targets_labels = LabelEncoder().fit(list(all_targets))
    all_selectable_targets_labels = LabelEncoder().fit(list(all_selectable_targets))
    all_categories_labels = LabelEncoder().fit(list(all_categories))
    all_effectiveness_labels = LabelEncoder().fit(list(all_effectiveness))
    all_pokemon_slot_labels = LabelEncoder().fit(list(all_pokemon_slots))
    all_attack_slot_labels = LabelEncoder().fit(list(all_attack_slots))
    all_pokemon_attacks_labels = LabelEncoder().fit(list(all_pokemon_attacks))
    all_genders_labels = LabelEncoder().fit(list(all_genders))
    all_generations_labels = LabelEncoder().fit(list(all_generations))
    all_gametypes_labels = LabelEncoder().fit(list(all_gametypes))
    all_tiers_labels = LabelEncoder().fit(list(all_tiers))
    all_actions_labels = LabelEncoder().fit(list(all_actions))
    all_rooms_labels = LabelEncoder().fit(list(all_rooms))





    return all_status_labels, all_items_labels, all_abilities_labels, all_pokemon_names_labels, all_weather_labels, \
        all_status_labels, all_element_types_labels, all_terrains_labels, all_targets_labels, \
        all_categories_labels, all_effectiveness_labels, all_pokemon_slot_labels, all_attack_slot_labels, all_pokemon_attacks_labels, \
        all_genders_labels, all_generations_labels, all_gametypes_labels, all_tiers_labels, all_actions_labels, all_rooms_labels, all_selectable_targets_labels


unknown_items = set()
unknown_attack_names = set()
unknown_pokemon_names = set()
unknown_abilities = set()

def flatten(items):
    new_items = []
    for x in items:
        if isinstance(x, list) or isinstance(x, np.ndarray):
            new_items.extend(x)
        else:
            new_items.append(x)
    return new_items

def sim_fetch_attack_by_name_id(name_id, base_attack=None):
    for atk in attacks_data_json:
        atk_details = attacks_data_json[atk]
        if atk == name_id:
            attack = sim_attack_from_json(atk, atk_details)
            if base_attack != None:
                attack.power = base_attack
            return attack
#    print('attack returning %s instead of %s' % (atk, name_id))
    unknown_attack_names.add(name_id)
    return sim_attack_from_json(atk, atk_details)
    return unregistered_attack()

def sim_fetch_attack_by_name(name):
    for atk in attacks_data_json:
        atk_details = attacks_data_json[atk]
        if atk_details['name'] == name:
            attack = sim_attack_from_json(atk, atk_details)
            return attack

#    print(name_id)
    unknown_attack_names.add(name_id)
    return unregistered_attack()
    raise Exception('Cannot find above attack by name')

def sim_attack_from_json(key, attack_data):
    id = key
    # Dont mix num and strings hidden power ruins this
    basePower = attack_data['basePower']
    category = CATEGORY(attack_data['category'])
    accuracy = attack_data['accuracy']
    if accuracy is not True:
        accuracy = accuracy / 100.0
    name = attack_data['name']
    pp = attack_data['pp']
    element_type = ELEMENT_TYPE(attack_data['type'])
    status = Status.NOTHING
    if 'status' in attack_data:
        status = Status(attack_data['status'])
    priority = attack_data['priority']
    target = TARGET(attack_data['target'])

    isZ = False
    if 'isZ' in attack_data:
        isZ = True


    target = 'normal'
    if 'target' in attack_data:
        target = attack_data['target']

    attack = Attack()
    attack.id = id
    attack.attack_name = name
    attack.pp  = pp
    attack.element_type = element_type
    attack.power = basePower
    attack.accuracy = accuracy
    attack.status = status
    attack.category = category
    attack.priority = priority
    attack.isZ = isZ
    attack.target = target
    return attack

# used to detect pokemon from galar/alola versions
def get_species_for_name_and_types(name, element_1st_type, element_2nd_type):
    for pkmn in pokemon_data_json:
        pkmn_details = pokemon_data_json[pkmn]
        detail_element_1 = ELEMENT_TYPE(pkmn_details['types'][0])
        detail_element_2 = None
        if len(pkmn_details['types']) > 1:
            detail_element_2 = ELEMENT_TYPE(pkmn_details['types'][1])
        detail_elements = [detail_element_1, detail_element_2]
        if pkmn_details['species'] == name.strip() and (element_1st_type in detail_elements) and (element_2nd_type in detail_elements):
            return pkmn_details['species']
        if 'baseSpecies' in pkmn_details:
            if pkmn_details['baseSpecies'] == name.strip() and (element_1st_type in detail_elements) and (element_2nd_type in detail_elements):
                return pkmn_details['species']
#    print(name)
    unknown_pokemon_names.add(name)
    print('pokemon returning %s instead of %s' % (pkmn, name))
    return pkmn_details['species']
    raise Exception('Cannot find above pokemon by species')

# Can only detect
def sim_fetch_pokemon_by_species(name, element_1st_type, element_2nd_type):
    bypass = (element_1st_type == None) and (element_2nd_type == None)
    if element_1st_type is not None:
        element_1st_type = ELEMENT_TYPE(element_1st_type)
    if element_2nd_type is not None:
        element_2nd_type = ELEMENT_TYPE(element_2nd_type)
    for pkmn in pokemon_data_json:
        pkmn_details = pokemon_data_json[pkmn]
        detail_element_1 = ELEMENT_TYPE(pkmn_details['types'][0])
        detail_element_2 = None
        if len(pkmn_details['types']) > 1:
            detail_element_2 = ELEMENT_TYPE(pkmn_details['types'][1])
        detail_elements = [detail_element_1, detail_element_2]
        element_check = bypass or ((element_1st_type in detail_elements) and (element_2nd_type in detail_elements))
        if pkmn_details['species'] == name.strip() and element_check:
            return pkmn_details
        if 'baseSpecies' in pkmn_details:
            if pkmn_details['baseSpecies'] == name.strip() and element_check:
                return pkmn_details
#    print(name)
    unknown_pokemon_names.add(name)
#    print('pokemon returning %s instead of %s' % (pkmn_details['species'], name))
    return pkmn_details
    raise Exception('Cannot find above pokemon by species')

def sim_pokemon_from_json(team_pokemon, element_1=None, element_2=None):

    species_name = team_pokemon['name']
    pokemon_data = sim_fetch_pokemon_by_species(species_name, element_1, element_2)

    name = pokemon_data['species']
    # for one hot encoding of pokemon
    atk = team_pokemon['atk']
    spatk = team_pokemon['sp_atk']
    defense = team_pokemon['defense']
    spdef = team_pokemon['sp_def']
    speed = team_pokemon['speed']
    max_health = team_pokemon['hp']
    weight = pokemon_data['weightkg']
    ability = team_pokemon['ability']
    item = team_pokemon['item']
    element_1st_type = ELEMENT_TYPE(pokemon_data['types'][0])
    element_2nd_type = None
    if len(pokemon_data['types']) > 1:
        element_2nd_type = ELEMENT_TYPE(pokemon_data['types'][1])

    attacks = []
    for atk_pp in team_pokemon['attacks']:
        print(atk_pp)
        atk_name = atk_pp[0]
        atk_info = get_attack_by_name_or_unregistered(atk_name)
        attacks.append(atk_info)
        print(atk_info.__dict__)

    #Overwrite negatives with base stats
    if max_health == -1:
        max_health = pokemon_data['baseStats']['hp']
    if atk == -1:
        atk = pokemon_data['baseStats']['atk']
    if spatk == -1:
        spatk = pokemon_data['baseStats']['spa']
    if defense == -1:
        defense = pokemon_data['baseStats']['def']
    if spdef == -1:
        spdef = pokemon_data['baseStats']['spd']
    if speed == -1:
        speed = pokemon_data['baseStats']['spe']

    pokemon = Pokemon()
    pokemon.name = name
    pokemon.form = name
    pokemon.max_health = max_health
    pokemon.atk = atk
    pokemon.spatk = spatk
    pokemon.defense = defense
    pokemon.spdef = spdef
    pokemon.speed = speed
    pokemon.weight = weight
    pokemon.ability = ability
    pokemon.item = item
    pokemon.element_1st_type = element_1st_type
    pokemon.element_2nd_type = element_2nd_type
    pokemon.attacks = attacks
    return pokemon

def attacks_from_json(attack_data, key=None):
    id = attack_data['id']
    # Dont mix num and strings hidden power ruins this
    if 'num' not in attack_data or True:
        num = key
    else:
        num = attack_data['num']
    all_pokemon_attacks.add(num)
    basePower = attack_data['basePower']
    category = CATEGORY(attack_data['category'])
    accuracy = attack_data['accuracy']
    if accuracy is not True:
        accuracy = accuracy / 100.0
    name = attack_data['name']
    pp = attack_data['pp']
    element_type = ELEMENT_TYPE(attack_data['type'])
    ignoreImmunity = False
    if 'ignoreImmunity' in attack_data:
        ignoreImmunity = True
    status = None
    if 'status' in attack_data:
        status = attack_data['status']
    priority = attack_data['priority']
    is_zmove = 'isZ' in attack_data
    target = TARGET(attack_data['target'])
    boosts = None
    volatileStatus = None
    has_recoil = True if 'recoil' in attack_data else False
    if 'boosts' in attack_data:
        boosts = attack_data['boosts']
    if 'volatileStatus' in attack_data:
        volatileStatus = attack_data['volatileStatus']
    secondary = None
    if 'secondary' in attack_data and attack_data['secondary'] is not False:
        sec_boosts = []
        status = None
        is_target_self = False
        if 'boosts' in attack_data['secondary']:
            sec_boosts = attack_data['secondary']['boosts']
        if 'status' in attack_data['secondary']:
            status = attack_data['secondary']['status']

        if 'self' in attack_data['secondary']:
            is_target_self = True
            if 'boosts' in attack_data['secondary']['self']:
                sec_boosts = attack_data['secondary']['self']['boosts']
            if 'status' in attack_data['secondary']['self']:
                status = attack_data['secondary']['self']['status']

        secondary = Secondary(attack_data['secondary']['chance'], sec_boosts, status, volatileStatus, is_target_self)

    isZ = False
    if 'isZ' in attack_data:
        isZ = True


    target = 'normal'
    if 'target' in attack_data:
        target = attack_data['target']

    attack = Attack()
    attack.id = id
    attack.attack_name = name
    attack.pp  = pp
    attack.element_type = element_type
    attack.power = basePower
    attack.accuracy = accuracy
    attack.status = status
    attack.category = category
    attack.priority = priority
    attack.target = target
    attack.isZ = isZ
    return attack



def get_seen_rep_of_opponent_pokemon(seen_pokemon, teamsize, a_slot=None, b_slot=None):
    # configure these based on player
    seen_names = set()

    obs_pkmn = deque([], maxlen=6)

    team_count = 0
    if a_slot is not None:
        team_count += 1
        seen_names.add(a_slot)
        form_name = seen_pokemon[a_slot]['form']
        seen_data = seen_pokemon[a_slot]
        obs_pkmn.appendleft(get_pokemon_opposing_with_pp_applied(form_name, seen_data))

    if b_slot is not None:
        team_count += 1
        seen_names.add(b_slot)
        form_name = seen_pokemon[b_slot]['form']
        seen_data = seen_pokemon[b_slot]
        obs_pkmn.appendleft(get_pokemon_opposing_with_pp_applied(form_name, seen_data))

    for pk_name in seen_pokemon:
        # if added anyone from slot a,b,c then continue
        if pk_name in seen_names:
            continue
        seen_names.add(pk_name)
        team_count += 1
        form_name = seen_pokemon[pk_name]['form']
        pk_data = seen_pokemon[pk_name]
        obs_pkmn.appendleft(get_pokemon_opposing_with_pp_applied(form_name, pk_data))

    #Slot A in first position
    obs_pkmn.reverse()

    # fill in hidden spots if the team size larger than whats seen
    while team_count < teamsize:
        obs_pkmn.append(hidden_pokemon())
        team_count += 1

    # fill in hidden spots if the team size larger than whats seen
    while team_count < 6:
        obs_pkmn.append(empty_pokemon())
        team_count += 1

    return obs_pkmn

def get_seen_rep_of_pokemon(pokemon, seen_pokemon, teamsize, a_slot=None, b_slot=None):
    # configure these based on player
    seen_names = set()

    obs_pkmn = deque([], maxlen=6)

    team_count = 0
    if a_slot is not None:
        for name_pkmn_pair in pokemon:
            team_name = name_pkmn_pair[0]
            pkmn = name_pkmn_pair[1]
            if isEditDistanceWithinTwo(team_name, a_slot):
                team_count += 1
                seen_names.add(team_name)
                seen_data = seen_pokemon[a_slot]
                obs_pkmn.appendleft(get_pokemon_with_pp_applied(pkmn, seen_data))
                break

    if b_slot is not None:
        for name_pkmn_pair in pokemon:
            team_name = name_pkmn_pair[0]
            pkmn = name_pkmn_pair[1]
            if isEditDistanceWithinTwo(team_name, b_slot):
                team_count += 1
                seen_names.add(b_slot)
                seen_data = seen_pokemon[b_slot]
                obs_pkmn.appendleft(get_pokemon_with_pp_applied(pkmn, seen_data))
                break

    for name_pkmn_pair in pokemon:
        team_name = name_pkmn_pair[0]
        pkmn = name_pkmn_pair[1]
        # if added anyone from slot a,b,c then continue
        if team_name in seen_names:
            continue
        seen_names.add(team_name)
        team_count += 1
        pk_data = None
        for pk_name in seen_pokemon:
            if isEditDistanceWithinTwo(team_name, pk_name):
                pk_data = seen_pokemon[pk_name]
                break
        obs_pkmn.appendleft(get_pokemon_with_pp_applied(pkmn, pk_data))

    #Slot A in first position
    obs_pkmn.reverse()

    # fill in hidden spots if the team size larger than whats seen
    while team_count < 6:
        obs_pkmn.append(empty_pokemon())
        team_count += 1

    return obs_pkmn


def get_pokemon_opposing_with_pp_applied(pokemon_name, seen_data):
    element_1st_type = None
    element_2nd_type = None

    if seen_data['element_1'] is not None:
      element_1st_type = ELEMENT_TYPE(seen_data['element_1'])
    if seen_data['element_2'] is not None:
      element_2nd_type = ELEMENT_TYPE(seen_data['element_2'])

    species_name = get_species_for_name_and_types(pokemon_name, element_1st_type, element_2nd_type)
    print(species_name)
    pk_info = get_pokemon_by_species_or_unregistered(species_name)
    pk_info.form = seen_data['form']
    pk_info.item = get_item_by_id_or_name(seen_data['item'])
    pk_info.ability = get_ability_by_id_or_name(seen_data['ability'])
    pk_info.health_ratio = float(seen_data['health'])
    pk_info.gender = GENDER(seen_data['gender'])
    pk_info.level = seen_data['level']
    pk_info.status = seen_data['status']

    if seen_data['element_1'] is not None:
      pk_info.element_1st_type = ELEMENT_TYPE(seen_data['element_1'])
    if seen_data['element_2'] is not None:
      pk_info.element_2nd_type = ELEMENT_TYPE(seen_data['element_2'])

    #Update attacks
    # skip z moves since they can only be used once
    for pp_atk in seen_data['attacks']:
        atk_info = get_attack_by_name_or_unregistered(pp_atk)
        # skip dynamax moves in future?
        if atk_info.isZ:
            continue
        if atk_info.id != 'unregisted':
            atk_info.used_pp = seen_data['attacks'][pp_atk]
        pk_info.attacks.appendleft(atk_info)
        print(atk_info.__dict__)
    return pk_info

def get_pokemon_with_pp_applied(pokemon, seen_data):

    # For team members who were not summoned
    if seen_data is None:
        return pokemon

#    pokemon = copy_pokemon(pokemon)

    # seen data posses info such as current form
        #Update revealed stats
#    if seen_data['form'] is not None:
#        pokemon.form = seen_data['form']
    if seen_data['item'] is not None:
        pokemon.item = seen_data['item']
    if seen_data['ability'] is not None:
        pokemon.ability = seen_data['ability']
    pokemon.health_ratio = float(seen_data['health'])
    pokemon.gender = GENDER(seen_data['gender'])
    if seen_data['level'] is not None:
        pokemon.level = seen_data['level']

    attacks = pokemon.attacks
    # deque
    new_attacks = deque([empty_attack(), empty_attack(), empty_attack(), empty_attack()], maxlen=4)
    # if attacks a provided, then assume p1 and update attack and do not fetch.
    # Player needs to see all of their own moves not just revealed ones.
    for attack in attacks:
        # skip unregistered attacks
        if attack is None or attack.id == 'empty':
            continue
        if attack.id == 'unregisted':
            new_attacks.appendleft(attack)
            continue
        if seen_data != None:
            for pp_info in seen_data['attacks']:
                if attack.attack_name == pp_info:
                    attack.used_pp = seen_data['attacks'][pp_info]
                    break
        new_attacks.appendleft(attack)
    pokemon.attacks = new_attacks
    return pokemon


#missing attack
def empty_attack():
    attack = Attack()
    attack.id = 'empty'
    attack.attack_name = 'empty_attack'
    attack.pp  = 1
    attack.element_type = ELEMENT_TYPE.TYPELESS
    attack.power = 0
    attack.accuracy = 0
    attack.status = Status.NOTHING
    attack.category = CATEGORY.STATUS
    attack.priority = 0
    return attack

#Used by hidden pokemon and seen pokemon with hidden attacks
def hidden_attack():
    attack = empty_attack()
    attack.id = 'hidden'
    attack.attack_name = 'hidden_attack'
    attack.pp  = 1
    return attack

# to be used when an attack isnt registered
def unregistered_attack():
    attack = empty_attack()
    attack.id = 'unregistered'
    attack.attack_name = 'unregistered_attack'
    attack.pp  = 1
    return attack

#missing pokemon
def empty_pokemon():
    pokemon = Pokemon()
    pokemon.name = 'empty_pokemon'
    pokemon.form = 'empty_pokemon'
    pokemon.level  = 0
    pokemon.max_health = 0
    pokemon.curr_health = 0
    pokemon.health_ratio = 0
    pokemon.atk = 0
    pokemon.spatk = 0
    pokemon.defense = 0
    pokemon.spdef = 0
    pokemon.speed = 0
    pokemon.weight = 0
    pokemon.ability = 'empty_ability'
    pokemon.element_1st_type = ELEMENT_TYPE.TYPELESS
    pokemon.element_2nd_type = ELEMENT_TYPE.TYPELESS
    pokemon.attacks = deque([empty_attack(), empty_attack(), empty_attack(), empty_attack()], maxlen=4)
    pokemon.status = Status.NOTHING
    pokemon.gender = GENDER.UNKNOWN
    pokemon.item = 'empty_item'
    return pokemon

#missing pokemon
def hidden_pokemon():
    pokemon = empty_pokemon()
    pokemon.name = 'hidden_pokemon'
    pokemon.form = 'hidden_pokemon'
    pokemon.max_health = 1
    pokemon.curr_health = 1
    pokemon.health_ratio = 1
    pokemon.ability = 'hidden_ability'
    pokemon.item = 'hidden_item'
    pokemon.attacks = deque([hidden_attack(), hidden_attack(), hidden_attack(), hidden_attack()], maxlen=4)
    return pokemon

#missing pokemon
def unregistered_pokemon():
    pokemon = empty_pokemon()
    pokemon.name = 'unregistered_pokemon'
    pokemon.form = 'unregistered_pokemon'
    pokemon.max_health = 1
    pokemon.curr_health = 1
    pokemon.health_ratio = 1
    pokemon.ability = 'unregistered_ability'
    pokemon.item = 'unregistered_item'
    pokemon.attacks = deque([unregistered_attack(), unregistered_attack(), unregistered_attack(), unregistered_attack()], maxlen=4)
    return pokemon


def get_pokemon_by_species_or_unregistered(species):
    if species in all_pokemon_by_species:
        pk_data = all_pokemon_by_species[species]
        return copy_pokemon(pk_data)
    return unregistered_pokemon()

def get_attack_by_name_or_unregistered(atk_name):
    if atk_name in all_attacks_data_by_name:
        atk_data = all_attacks_data_by_name[atk_name]
        return copy_attack(atk_data)
    return unregistered_attack()


def get_item_by_id_or_name(item_name):
    item = 'unregistered_item'
    item_name = item_name.lower()
    if item_name in all_items_by_name:
        return all_items_by_name[item_name]
    if item_name in all_items_by_key:
        return all_items_by_key[item_name]

    if item_name in ['unregistered_item', 'hidden_item', 'empty_item']:
        return item_name

    return item


def get_ability_by_id_or_name(ability_name):
    ability = 'unregistered_ability'
    ability_name = ability_name.lower()
    if ability_name in all_abilities_by_name:
        return all_abilities_by_name[ability_name]
    if ability_name in all_abilities_by_key:
        return all_abilities_by_key[ability_name]

    if ability_name in ['unregistered_ability', 'hidden_ability', 'empty_ability']:
        return ability_name

    return ability




def copy_pokemon(pk_data):
    pokemon = Pokemon()
    pokemon.name = pk_data.name
    pokemon.form = pk_data.form
    pokemon.level  = pk_data.level
    pokemon.max_health = pk_data.max_health
    pokemon.curr_health = pk_data.curr_health
    pokemon.health_ratio = pk_data.health_ratio
    pokemon.atk = pk_data.atk
    pokemon.spatk = pk_data.spatk
    pokemon.defense = pk_data.defense
    pokemon.spdef = pk_data.spdef
    pokemon.speed = pk_data.speed
    pokemon.weight = pk_data.weight
    pokemon.ability = pk_data.ability
    pokemon.element_1st_type = pk_data.element_1st_type
    pokemon.element_2nd_type = pk_data.element_2nd_type
    pokemon.attacks = deque([hidden_attack(), hidden_attack(), hidden_attack(), hidden_attack()], maxlen=4)
    pokemon.status = pk_data.status
    pokemon.gender = pk_data.gender
    pokemon.item = pk_data.item
    return pokemon

def copy_attack(atk_data):
    attack = Attack()
    attack.id = atk_data.id
    attack.isZ = atk_data.isZ
    attack.attack_name = atk_data.attack_name
    attack.pp  = atk_data.pp
    attack.element_type = atk_data.element_type
    attack.power = atk_data.power
    attack.accuracy = atk_data.accuracy
    attack.status = atk_data.status
    attack.category = atk_data.category
    attack.priority = atk_data.priority
    return attack



damage_taken_json = json.loads(damage_taken_json_str)
damage_taken_dict = {}
for element in damage_taken_json.keys():
    damage_taken_dict[element] = damage_taken_json[element]['damageTaken']


pokemon_data_json = json.loads(pokemon_data_json_str)
all_pokemon_by_species = {}
all_pokemon_by_key = {}

# Maybe update to use species name
for pokemon_key in pokemon_data_json.keys():
    #example:  species -> Shaymin-Sky
    species = pokemon_data_json[pokemon_key]['species']
    all_pokemon_by_species[species] = pokemon_from_json(pokemon_data_json[pokemon_key])
    all_pokemon_by_key[pokemon_key] = pokemon_from_json(pokemon_data_json[pokemon_key])
    all_pokemon_by_name[species] = pokemon_key
    all_pokemon_by_key[pokemon_key] = pokemon_key

attacks_data_json = json.loads(attacks_json_str)

#"""
#all_attacks_data_by_name = {}
#all_attacks_by_key = {}
for attack_key in attacks_data_json.keys():
    attack_name = attacks_data_json[attack_key]['name']
#    all_attacks_by_key[attack_key] = attacks_from_json(attacks_data_json[attack_key], key=attack_key)
    all_attacks_data_by_name[attack_name] = attacks_from_json(attacks_data_json[attack_key], key=attack_key)
"""


#configured by adding moves
#handling differently
player_flinched = 1
agent_flinched = 1
player_confused = 1
agent_confused = 1
#"""

pokemon_abilities_json = json.loads(pokemon_abilities_str)
pokemon_items_json = json.loads(pokemon_items_str)


def id_for_pokemon_name(name):
    for pkmn_name in all_pokemon_by_name:
        if name == pkmn_name:
            return all_pokemon_by_name[pkmn_name]
    if name in ['empty_pokemon', 'hidden_pokemon', 'unregistered_pokemon']:
        return name
    return 'hidden_pokemon'

def id_for_attack_name(name):
    for attack_name in all_attacks_by_name:
        if name == attack_name:
            return all_attacks_by_name[attack_name]
    if name in ['no attack', 'empty', 'hidden', 'unregistered']:
        return name
    return 'hidden'


def id_for_ability_name(name):
    for ability_name in all_abilities_by_name:
        if name == ability_name:
            return all_abilities_by_name[ability_name]
    if name in ['empty_ability', 'hidden_ability', 'unregistered_ability']:
        return name
    return 'hidden_ability'

def id_for_item_name(name):
    for item_name in all_items_by_name:
        if name == item_name:
            return all_items_by_name[item_name]
    if name in ['empty_item', 'hidden_item', 'unregistered_item']:
        return name
    return 'hidden_item'




fill_all_category_sets()
all_status_labels, all_items_labels, all_abilities_labels, all_pokemon_names_labels, all_weather_labels, \
all_status_labels, all_element_types_labels, all_terrains_labels, all_targets_labels, \
all_categories_labels, all_effectiveness_labels, all_pokemon_slot_labels, all_attack_slot_labels, all_pokemon_attacks_labels, \
all_genders_labels, all_generations_labels, all_gametypes_labels, all_tiers_labels, all_actions_labels, all_rooms_labels, \
all_selectable_targets_labels = get_encodings_for_all_sets()
#"""
