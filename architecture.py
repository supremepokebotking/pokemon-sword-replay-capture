import numpy as np
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Lambda
from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers import LSTM
from tensorflow.keras.preprocessing.text import Tokenizer
import tensorflow.keras.preprocessing.sequence as sequence
from tensorflow.keras.layers import Dense, Dropout, Flatten, Reshape, Concatenate
from tensorflow.keras.layers import Conv1D, GlobalAveragePooling1D, MaxPooling1D

# This function selects the probability distribution over actions
from baselines.common.distributions import make_pdtype
from tensorflow.keras import backend as K
from baselines.a2c.utils import fc

MM_EMBEDDINGS_DIM = 50
MM_MAX_WORD_SIZE = 20
MM_MAX_SENTENCE_SIZE = 200
MM_FEATURES_SIZE = 20000
MM_MAX_VOCAB_SIZE = 5000


# Pokemon Constants
POKEMON_MAX_WORD_SIZE = 20     # length limit per word/name/item/etc
POKEMON_MAX_VOCAB_SIZE = 1200  # limit used for item names, and pokemon names
POKEMON_MEDIUM_VOCAB_SIZE = 400  # limit used for pokemon abilities names
POKEMON_SMALL_VOCAB_SIZE = 30  # limit used for elements, status, weather, terrain, etc
POKEMON_EXTRA_SMALL_VOCAB_SIZE = 10  # limit used for elements, status, weather, terrain, etc
POKEMON_LARGE_EMBEDDINGS_DIM = 50
POKEMON_SMALL_EMBEDDINGS_DIM = 15
POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM = 3

POKEMON_FIELD_REMAINDER = 411

SELECTABLE_TARGET_SIZE = 8

# Fully connected layer
def fc_layer(inputs, units, activation_fn=tf.nn.relu, gain=1.0):
	return tf.layers.dense(inputs,
							units=units,
							activation=activation_fn,
							kernel_initializer=tf.orthogonal_initializer(gain))


# LSTM Layer
#def lstm_layer(vocab_size=MM_MAX_VOCAB_SIZE, word_len_limit=MM_MAX_WORD_SIZE, input_length=MM_MAX_SENTENCE_SIZE):
#	return LSTM(Embedding(vocab_size, word_len_limit, input_length=input_length, mask_zero=True), dropout=0.2, recurrent_dropout=0.2, return_sequences=True)
def lstm_layer(em_input, vocab_size=MM_MAX_VOCAB_SIZE, word_len_limit=MM_MAX_WORD_SIZE, input_length=MM_MAX_SENTENCE_SIZE):
	print('em shape', em_input.shape)
	embedding = Embedding(vocab_size, word_len_limit, input_length=input_length )(em_input)
	print('emb shape', embedding.shape)
	return LSTM(units=100, dropout=0.2, recurrent_dropout=0.2, return_sequences=True)(embedding)

# future
#x_train = sequence.pad_sequences(x_train, maxlen=maxlen)   # pre_padding with 0

"""
This object creates the PPO Network architecture
"""

#consts need to be updated whenever data changes

class PPOPolicy(object):
	def __init__(self, sess, ob_space, action_space, nbatch, nsteps, reuse=False):
		# This will use to initialize our kernels
		gain = np.sqrt(2)

		self.tokenizer = Tokenizer(num_words=5000)
		# Based on the action space, will select what probability distribution type
		# we will use to distribute action in our stochastic policy (in our case DiagGaussianPdType
		# aka Diagonal Gaussian, 3D normal distribution)
		self.pdtype = make_pdtype(action_space)

#		print('ob_space:', ob_space)
#		print('ac_space:', action_space.n)
#		height, width = 1, ob_space.n
#		ob_shape = (None, ob_space.n)
		ob_shape = ob_space.shape

		text_shape = ( None, 200 )


		pokemon_category_embedding_shape = ( None, 1)

		# for item
#		text_shape = ( 1, 7, 33 )

		embeddings = []
		player_pokemon_name_inputs_ = []
		player_pokemon_status_inputs_ = []
		player_pokemon_first_element_inputs_ = []
		player_pokemon_second_element_inputs_ = []
		player_pokemon_abilities_inputs_ = []
		player_pokemon_items_inputs_ = []
		player_pokemon_genders_inputs_ = []
		player_attack_slot_1_inputs_ = []
		player_attack_slot_1_element_inputs_ = []
		player_attack_slot_1_category_inputs_ = []
		player_attack_slot_2_inputs_ = []
		player_attack_slot_2_element_inputs_ = []
		player_attack_slot_2_category_inputs_ = []
		player_attack_slot_3_inputs_ = []
		player_attack_slot_3_element_inputs_ = []
		player_attack_slot_3_category_inputs_ = []
		player_attack_slot_4_inputs_ = []
		player_attack_slot_4_element_inputs_ = []
		player_attack_slot_4_category_inputs_ = []

		agent_pokemon_name_inputs_ = []
		agent_pokemon_status_inputs_ = []
		agent_pokemon_first_element_inputs_ = []
		agent_pokemon_second_element_inputs_ = []
		agent_pokemon_abilities_inputs_ = []
		agent_pokemon_items_inputs_ = []
		agent_pokemon_genders_inputs_ = []
		agent_attack_slot_1_inputs_ = []
		agent_attack_slot_1_element_inputs_ = []
		agent_attack_slot_1_category_inputs_ = []
		agent_attack_slot_2_inputs_ = []
		agent_attack_slot_2_element_inputs_ = []
		agent_attack_slot_2_category_inputs_ = []
		agent_attack_slot_3_inputs_ = []
		agent_attack_slot_3_element_inputs_ = []
		agent_attack_slot_3_category_inputs_ = []
		agent_attack_slot_4_inputs_ = []
		agent_attack_slot_4_element_inputs_ = []
		agent_attack_slot_4_category_inputs_ = []

		weather_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="weather_inputs")
		weather_inputs_keras = tf.keras.layers.Input(tensor=weather_inputs_)
		embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(weather_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		terrain_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="terrain_inputs")
		terrain_inputs_keras = tf.keras.layers.Input(tensor=terrain_inputs_)
		embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(terrain_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		room_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="room_inputs")
		room_inputs_keras = tf.keras.layers.Input(tensor=room_inputs_)
		embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(room_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		generations_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="generations_inputs_")
		generations_inputs_keras = tf.keras.layers.Input(tensor=generations_inputs_)
		embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(generations_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		gametypes_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="gametypes_inputs_")
		gametypes_inputs_keras = tf.keras.layers.Input(tensor=gametypes_inputs_)
		embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(gametypes_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		tiers_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="tiers_inputs_")
		tiers_inputs_keras = tf.keras.layers.Input(tensor=tiers_inputs_)
		embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(tiers_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		pending_actions_a_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="pending_actions_a_inputs_")
		pending_actions_a_inputs_keras = tf.keras.layers.Input(tensor=pending_actions_a_inputs_)
		embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(pending_actions_a_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		pending_actions_b_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="pending_actions_b_inputs_")
		pending_actions_b_inputs_keras = tf.keras.layers.Input(tensor=pending_actions_b_inputs_)
		embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(pending_actions_b_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		pending_targets_a_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="pending_targets_a_inputs_")
		pending_targets_a_inputs_keras = tf.keras.layers.Input(tensor=pending_targets_a_inputs_)
		embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(pending_targets_a_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		pending_targets_b_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="pending_targets_b_inputs_")
		pending_targets_b_inputs_keras = tf.keras.layers.Input(tensor=pending_targets_b_inputs_)
		embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(pending_targets_b_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		seen_attacks_a_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="seen_attacks_a_inputs_")
		seen_attacks_a_inputs_keras = tf.keras.layers.Input(tensor=seen_attacks_a_inputs_)
		embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(seen_attacks_a_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		seen_attacks_b_inputs_ = tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="seen_attacks_b_inputs_")
		seen_attacks_b_inputs_keras = tf.keras.layers.Input(tensor=seen_attacks_b_inputs_)
		embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
		embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(seen_attacks_b_inputs_keras)
		embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		# for each pokemon for player and agent
		for i in range(6):
#			break

			player_pokemon_name_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_pokemon_name_inputs_"+str(i)+'_'))
			player_pokemon_name_inputs_keras = tf.keras.layers.Input(tensor=player_pokemon_name_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(player_pokemon_name_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_pokemon_name_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_pokemon_name_inputs_"+str(i)+'_'))
			agent_pokemon_name_inputs_keras = tf.keras.layers.Input(tensor=agent_pokemon_name_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(agent_pokemon_name_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_pokemon_status_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_pokemon_status_inputs_"+str(i)+'_'))
			player_pokemon_status_inputs_keras = tf.keras.layers.Input(tensor=player_pokemon_status_inputs_[i])
			embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_pokemon_status_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_pokemon_status_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_pokemon_status_inputs_"+str(i)+'_'))
			agent_pokemon_status_inputs_keras = tf.keras.layers.Input(tensor=agent_pokemon_status_inputs_[i])
			embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_pokemon_status_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_pokemon_first_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_pokemon_first_element_inputs_"+str(i)+'_'))
			player_pokemon_first_element_inputs_keras = tf.keras.layers.Input(tensor=player_pokemon_first_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(player_pokemon_first_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_pokemon_first_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_pokemon_first_element_inputs_"+str(i)+'_'))
			agent_pokemon_first_element_inputs_keras = tf.keras.layers.Input(tensor=agent_pokemon_first_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(agent_pokemon_first_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_pokemon_second_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_pokemon_second_element_inputs_"+str(i)+'_'))
			player_pokemon_second_element_inputs_keras = tf.keras.layers.Input(tensor=player_pokemon_second_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(player_pokemon_second_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_pokemon_second_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_pokemon_second_element_inputs_"+str(i)+'_'))
			agent_pokemon_second_element_inputs_keras = tf.keras.layers.Input(tensor=agent_pokemon_second_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(agent_pokemon_second_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_pokemon_abilities_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_pokemon_abilities_inputs_"+str(i)+'_'))
			player_pokemon_abilities_inputs_keras = tf.keras.layers.Input(tensor=player_pokemon_abilities_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MEDIUM_VOCAB_SIZE, embedding_size, input_length=1 )(player_pokemon_abilities_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_pokemon_abilities_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_pokemon_abilities_inputs_"+str(i)+'_'))
			agent_pokemon_abilities_inputs_keras = tf.keras.layers.Input(tensor=agent_pokemon_abilities_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MEDIUM_VOCAB_SIZE, embedding_size, input_length=1 )(agent_pokemon_abilities_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_pokemon_items_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_pokemon_items_inputs_"+str(i)+'_'))
			player_pokemon_items_inputs_keras = tf.keras.layers.Input(tensor=player_pokemon_items_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(player_pokemon_items_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_pokemon_items_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_pokemon_items_inputs_"+str(i)+'_'))
			agent_pokemon_items_inputs_keras = tf.keras.layers.Input(tensor=agent_pokemon_items_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(agent_pokemon_items_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_pokemon_genders_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_pokemon_genders_inputs_"+str(i)+'_'))
			player_pokemon_genders_inputs_keras = tf.keras.layers.Input(tensor=player_pokemon_genders_inputs_[i])
			embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_pokemon_genders_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_pokemon_genders_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_pokemon_genders_inputs_"+str(i)+'_'))
			agent_pokemon_genders_inputs_keras = tf.keras.layers.Input(tensor=agent_pokemon_genders_inputs_[i])
			embedding_size = POKEMON_EXTRA_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_pokemon_genders_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_1_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_1_inputs_"+str(i)+'_'))
			player_attack_slot_1_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_1_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_1_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_1_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_1_element_inputs_"+str(i)+'_'))
			player_attack_slot_1_element_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_1_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_1_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_1_category_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_1_category_inputs_"+str(i)+'_'))
			player_attack_slot_1_category_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_1_category_inputs_[i])
			embedding_size = 1
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_1_category_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_1_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_1_inputs_"+str(i)+'_'))
			agent_attack_slot_1_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_1_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_1_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_1_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_1_element_inputs_"+str(i)+'_'))
			agent_attack_slot_1_element_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_1_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_1_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_1_category_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_1_category_inputs_"+str(i)+'_'))
			agent_attack_slot_1_category_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_1_category_inputs_[i])
			embedding_size = 1
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_1_category_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_2_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_2_inputs_"+str(i)+'_'))
			player_attack_slot_2_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_2_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_2_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_2_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_2_element_inputs_"+str(i)+'_'))
			player_attack_slot_2_element_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_2_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_2_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_2_category_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_2_category_inputs_"+str(i)+'_'))
			player_attack_slot_2_category_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_2_category_inputs_[i])
			embedding_size = 1
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_2_category_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_2_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_2_inputs_"+str(i)+'_'))
			agent_attack_slot_2_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_2_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_2_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_2_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_2_element_inputs_"+str(i)+'_'))
			agent_attack_slot_2_element_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_2_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_2_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_2_category_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_2_category_inputs_"+str(i)+'_'))
			agent_attack_slot_2_category_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_2_category_inputs_[i])
			embedding_size = 1
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_2_category_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_3_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_3_inputs_"+str(i)+'_'))
			player_attack_slot_3_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_3_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_3_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_3_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_3_element_inputs_"+str(i)+'_'))
			player_attack_slot_3_element_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_3_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_3_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_3_category_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_3_category_inputs_"+str(i)+'_'))
			player_attack_slot_3_category_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_3_category_inputs_[i])
			embedding_size = 1
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_3_category_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_3_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_3_inputs_"+str(i)+'_'))
			agent_attack_slot_3_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_3_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_3_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_3_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_3_element_inputs_"+str(i)+'_'))
			agent_attack_slot_3_element_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_3_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_3_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_3_category_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_3_category_inputs_"+str(i)+'_'))
			agent_attack_slot_3_category_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_3_category_inputs_[i])
			embedding_size = 1
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_3_category_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_4_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_4_inputs_"+str(i)+'_'))
			player_attack_slot_4_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_4_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_4_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_4_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_4_element_inputs_"+str(i)+'_'))
			player_attack_slot_4_element_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_4_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_4_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			player_attack_slot_4_category_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="player_attack_slot_4_category_inputs_"+str(i)+'_'))
			player_attack_slot_4_category_inputs_keras = tf.keras.layers.Input(tensor=player_attack_slot_4_category_inputs_[i])
			embedding_size = 1
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(player_attack_slot_4_category_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_4_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_4_inputs_"+str(i)+'_'))
			agent_attack_slot_4_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_4_inputs_[i])
			embedding_size = POKEMON_LARGE_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_MAX_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_4_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_4_element_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_4_element_inputs_"+str(i)+'_'))
			agent_attack_slot_4_element_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_4_element_inputs_[i])
			embedding_size = POKEMON_SMALL_EMBEDDINGS_DIM
			embedding = Embedding(POKEMON_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_4_element_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

			agent_attack_slot_4_category_inputs_.append(tf.placeholder(tf.float32, pokemon_category_embedding_shape, name="agent_attack_slot_4_category_inputs_"+str(i)+'_'))
			agent_attack_slot_4_category_inputs_keras = tf.keras.layers.Input(tensor=agent_attack_slot_4_category_inputs_[i])
			embedding_size = 1
			embedding = Embedding(POKEMON_EXTRA_SMALL_VOCAB_SIZE, embedding_size, input_length=1 )(agent_attack_slot_4_category_inputs_keras)
			embeddings.append(Reshape(target_shape=(embedding_size,))(embedding))

		# Create the input placeholder
		non_category_data_input_ = tf.placeholder(tf.float32, (None, POKEMON_FIELD_REMAINDER), name="non_category_data_input")
		combined_inputs_ = tf.placeholder(tf.float32, (None, ob_space.shape[1] + MM_EMBEDDINGS_DIM*2 ), name="combined_input")
		text_inputs_ = tf.placeholder(tf.float32, text_shape, name="text_input")

		available_moves = tf.placeholder(tf.float32, [None, action_space.n], name="availableActions")
		available_targets = tf.placeholder(tf.float32, [None, (action_space.n*SELECTABLE_TARGET_SIZE)], name="availableTargets")

		"""
		Build the model
		Embedding
		LSTM

		3 FC for spatial dependiencies
		1 common FC

		1 FC for policy (actor)
		1 FC for value (critic)

		"""
		with tf.variable_scope('model', reuse=reuse):
			# text reading LSTM
#			lt_layer = lstm_layer()
			text_inputs_keras = tf.keras.layers.Input(tensor=text_inputs_)

			text_out = lstm_layer(text_inputs_keras)

			shape = text_out.get_shape().as_list() [1:]       # a list: [None, 9, 2]
			dim = np.prod(shape)            # dim = prod(9,2) = 18
			print('text_flatten before reshape',text_out.shape)
#			text_flatten = tf.reshape(text_out, [-1, dim])           # -1 means "all"
			text_flatten = tf.reshape(text_out, [1, -1])           # -1 means "all"
#			text_flatten =  tf.reshape(text_out, [-1])

			print('embeds', len(embeddings))
			merged = Concatenate(axis=-1)(embeddings)

			# This returns a tensor
			non_category_data_input_keras = tf.keras.layers.Input(tensor=non_category_data_input_)
			categorical_dense = tf.keras.layers.Dense(512, activation='relu')(merged)
			categorical_dense = Reshape(target_shape=(512,))(categorical_dense)
			non_categorical_dense = tf.keras.layers.Dense(512, activation='relu')(non_category_data_input_keras)

			combined_fields = Concatenate(axis=-1)([non_categorical_dense, categorical_dense])
			#reshape to add dimension?
			comb_shape = combined_fields.get_shape()
#			combined_fields = Reshape(target_shape=(comb_shape[1], 1))(combined_fields)
			combined_fields = K.expand_dims(combined_fields, 2)
#			comb_shape = tf.expand_dims(comb_shape, -1)
#			Y = tf.reshape(X , [shape[0], shape[1]*shape[2], shape[3]])
			print('combined_fields expanded dim', combined_fields.get_shape())

			conv1 = Conv1D(100, 10, activation='relu', batch_input_shape=(None, combined_fields.get_shape()[1]))(combined_fields)
#			conv1 = Conv1D(100, 10, activation='relu', batch_input_shape=(None, ob_space.shape[1]))(field_inputs_)
			conv1 = Conv1D(100, 10, activation='relu')(conv1)
			conv1 = MaxPooling1D(3)(conv1)
			conv1 = Conv1D(160, 10, activation='relu')(conv1)
			conv1 = Conv1D(160, 10, activation='relu')(conv1)
			conv1 = GlobalAveragePooling1D()(conv1)
			conv1 = Dropout(0.5)(conv1)
			print('conv1 before reshape',conv1.get_shape())
			print('text_out before flatten',text_out.get_shape())

			text_out = Flatten()(text_out)
			print('text_out ater flatten',text_out.get_shape())
			text_dense = tf.keras.layers.Dense(512, activation='relu')(text_out)
			field_dense = tf.keras.layers.Dense(512, activation='relu')(conv1)
			print('text_dense after dense',text_dense.get_shape())

#			scaled_image = tf.keras.layers.Lambda(function=lambda tensors: tensors[0] * tensors[1])([image, scale])
#			fc_common_dense = Lambda(lambda x:K.concatenate([x[0], x[1]], axis=1))([text_dense, field_dense])
#			fc_common_dense = tf.keras.layers.Concatenate(axis=-1)(list([text_dense, field_dense]))
			fc_common_dense = tf.keras.layers.Concatenate(axis=-1)(list([text_dense, field_dense]))
			fc_common_dense = tf.keras.layers.Dense(512, activation='relu')(fc_common_dense)

			#available_moves takes form [0, 0, -inf, 0, -inf...], 0 if action is available, -inf if not.
			fc_act = tf.keras.layers.Dense(256, activation='relu')(fc_common_dense)
#			self.pi = tf.keras.layers.Dense(action_space.n, activation='relu')(fc_act)
			self.pi = tf.keras.layers.Dense(action_space.n, activation=tf.nn.softmax)(fc_act)
#			self.pi = fc(fc_act,'pi', action_space.n, init_scale = 0.01)

			# Maybe target should be based off of action sample dist
			self.target_pi = fc(self.pi,'target_pi', SELECTABLE_TARGET_SIZE, init_scale = 0.01)

			# Calculate the v(s)
			h3 = tf.keras.layers.Dense(256, activation='relu')(fc_common_dense)
			fc_vf = tf.keras.layers.Dense(1, activation=None)(h3)[:,0]

#			vf = fc_layer(fc_3, 1, activation_fn=None)[:,0]
#			vf = fc_layer(fc_common_dense, 1, activation_fn=None)[:,0]

		self.initial_state = None

		# perform calculations using available moves lists
		print('self.pi', self.pi)
		availPi = tf.add(self.pi, available_moves)
		tf.print(availPi, [availPi], 'availPi')
		availPi2 = tf.multiply(self.pi, available_moves)
#		availPi = tf.add(self.pi, available_moves)
		availPi = tf.subtract(available_moves, self.pi)


		def sample():
			samples = tf.multinomial(tf.log(availPi2), 1)
#			return [tf.constant(0), tf.constant(0), tf.constant(0), tf.constant(0)]
#			return samples
			return tf.squeeze(samples, -1)

		def sample_deprec():
			print('availPi', availPi)
			u = tf.random_uniform(tf.shape(availPi))
			print('u', u)
			return tf.argmax(availPi - tf.log(-tf.log(u)), axis=-1)

		def sample_targets(action):
			return action
			span = tf.constant(SELECTABLE_TARGET_SIZE)
			index = tf.cast(action, tf.int32)
			start = tf.multiply(index, span)
			end =  tf.add(start, span)
#			sess.run([print_op],input_dict)
#			print_op = tf.print(start)
#			print_op2 = tf.print(end)
#			print_op3 = tf.print(index)
#			with tf.control_dependencies([print_op,print_op2,print_op3]):
#				pass
#				out = tf.add(tensor, tensor)
#				sess.run(print_op)
#				sess.run(print_op2)
#				sess.run(print_op3)

#			sess.run(print_op2)
#			sess.run(print_op3)
			print('span shape', span)
			print('end shape', end)
			print('start shape', start)
			print('index shape', index)

			rangy = tf.range(start, end, 1)

			targets_slice = tf.nn.embedding_lookup(available_targets, rangy)
			print('self.target_pi', self.target_pi)
			availTargetPi = tf.add(self.target_pi, targets_slice)

			u = tf.random_uniform(tf.shape(availTargetPi))
			return tf.argmax(availTargetPi - tf.log(-tf.log(u)), axis=-1)

		a0 = sample()
		t0 = sample_targets(a0)
		el0in = tf.exp(availPi - tf.reduce_max(availPi, axis=-1, keep_dims=True))
		z0in = tf.reduce_sum(el0in, axis=-1, keep_dims = True)
		p0in = el0in / z0in
		onehot = tf.one_hot(a0, availPi.get_shape().as_list()[-1])
		neglogp0 = -tf.log(tf.reduce_sum(tf.multiply(p0in, onehot), axis=-1))


		# Function use to take a step returns action to take and V(s)
		def step(state_in, valid_moves, valid_targets, ob_texts,*_args, **_kwargs):
			# return a0, vf, neglogp0
			# padd text
#			print('ob_text', ob_texts)
			for ob_text in ob_texts:
#				print('ob_text', ob_text)
				self.tokenizer.fit_on_texts([ob_text])

			ob_text_input = []
			for ob_text in ob_texts:
#				print('ob_text', ob_text)
				token = self.tokenizer.texts_to_sequences([ob_text])
				token = sequence.pad_sequences(token, maxlen=MM_MAX_SENTENCE_SIZE)   # pre_padding with 0
				ob_text_input.append(token)
#				print('token', token)
#				print('token shape', token.shape)
			orig_ob_text_input = np.array(ob_text_input)
			shape = orig_ob_text_input.shape
#			print('ob_text_input shape', shape)
			ob_text_input = orig_ob_text_input.reshape(shape[0], shape[2])

			# Reshape for conv1
#			state_in = np.expand_dims(state_in, axis=2)
			input_dict = dict({text_inputs_:ob_text_input, available_moves:valid_moves, available_targets:valid_targets})
			input_dict.update(split_categories_from_state(state_in))
			print_op1 = tf.print(a0,summarize=1000000)
#			sess.run([print_op],input_dict)
			print_op2 = tf.print(el0in,summarize=1000000)
#			sess.run([print_op],input_dict)
			print_op3 = tf.print(availPi,summarize=1000000)
#			sess.run([print_op],input_dict)
#			print_op = tf.print(tensor)
#			with tf.control_dependencies([print_op]):
#				out = tf.add(tensor, tensor)
#			sess.run(out)

			try:
				return sess.run([a0, t0, fc_vf, neglogp0], input_dict)
			except Exception as e:
				print('Issue processing step!!!')
				print('printing data')
				print('state_in:',state_in)
				print('valid_targets:',valid_targets)
				print('valid_moves:',valid_moves)
				print('ob_texts:',ob_texts)
				print('ob_text_input:',ob_text_input)
				print('orig_ob_text_input:',orig_ob_text_input)
				raise e

		# Function that calculates only the V(s)
		def value(state_in, valid_moves, valid_targets, ob_texts, *_args, **_kwargs):
			for ob_text in ob_texts:
#				print('ob_text', ob_text)
				self.tokenizer.fit_on_texts([ob_text])

			ob_text_input = []
			for ob_text in ob_texts:
#				print('ob_text', ob_text)
				token = self.tokenizer.texts_to_sequences([ob_text])
				token = sequence.pad_sequences(token, maxlen=MM_MAX_SENTENCE_SIZE)   # pre_padding with 0
				ob_text_input.append(token)
#				print('token', token)
#				print('token shape', token.shape)
			ob_text_input = np.array(ob_text_input)
			shape = ob_text_input.shape
#			print('ob_text_input shape', shape)
			ob_text_input = ob_text_input.reshape(shape[0], shape[2])

			# Reshape for conv1
#			state_in = np.expand_dims(state_in, axis=2)
			input_dict = dict({text_inputs_:ob_text_input, available_moves:valid_moves, available_targets:valid_targets})
			input_dict.update(split_categories_from_state(state_in))

			try:
				return sess.run(fc_vf, input_dict)
			except Exception as e:
				print('Issue processing step!!!')
				print('printing data')
				print('valid_moves:',valid_moves)
				print('ob_texts:',ob_texts)
				print('ob_text_input:',ob_text_input)
				raise e

		def select_action(state_in, valid_moves, valid_targets, ob_texts, *_args, **_kwargs):
			for ob_text in ob_texts:
#				print('ob_text', ob_text)
				self.tokenizer.fit_on_texts([ob_text])

			ob_text_input = []
			for ob_text in ob_texts:
#				print('ob_text', ob_text)
				token = self.tokenizer.texts_to_sequences([ob_text])
				token = sequence.pad_sequences(token, maxlen=MM_MAX_SENTENCE_SIZE)   # pre_padding with 0
				ob_text_input.append(token)
#				print('token', token)
#				print('token shape', token.shape)
			ob_text_input = np.array(ob_text_input)
			shape = ob_text_input.shape
#			print('ob_text_input shape', shape)
			ob_text_input = ob_text_input.reshape(shape[0], shape[2])

			# Reshape for conv1
#			state_in = np.expand_dims(state_in, axis=2)
			input_dict = dict({text_inputs_:ob_text_input, available_moves:valid_moves, available_targets:valid_targets})
			input_dict.update(split_categories_from_state(state_in))

			try:
				return sess.run(fc_vf, input_dict)
			except Exception as e:
				print('Issue processing step!!!')
				print('printing data')
				print('valid_moves:',valid_moves)
				print('ob_texts:',ob_texts)
				print('ob_text_input:',ob_text_input)
				raise e


		def split_categories_from_state(obs_datas):
			input_mappings = {}
			# Initialize buckets
			generations = np.empty([0,1], dtype=np.float32)
			gametypes_inputs = np.empty([0,1], dtype=np.float32)
			tiers = np.empty([0,1], dtype=np.float32)
			weather = np.empty([0,1], dtype=np.float32)
			terrain = np.empty([0,1], dtype=np.float32)
			room = np.empty([0,1], dtype=np.float32)
			pending_actions_a = np.empty([0,1], dtype=np.float32)
			pending_actions_b = np.empty([0,1], dtype=np.float32)
			pending_targets_a = np.empty([0,1], dtype=np.float32)
			pending_targets_b = np.empty([0,1], dtype=np.float32)
			seen_attacks_a = np.empty([0,1], dtype=np.float32)
			seen_attacks_b = np.empty([0,1], dtype=np.float32)
			non_category_data = np.empty([0,POKEMON_FIELD_REMAINDER], dtype=np.float32)


			#Player Categorical Details
			for i in range(6):
				input_mappings[player_pokemon_name_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_pokemon_status_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_pokemon_first_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_pokemon_second_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_pokemon_abilities_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_pokemon_items_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_pokemon_genders_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_1_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_1_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_1_category_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_2_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_2_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_2_category_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_3_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_3_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_3_category_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_4_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_4_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[player_attack_slot_4_category_inputs_[i]] = np.empty([0,1], dtype=np.float32)

				input_mappings[agent_pokemon_name_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_pokemon_status_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_pokemon_first_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_pokemon_second_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_pokemon_abilities_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_pokemon_items_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_pokemon_genders_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_1_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_1_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_1_category_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_2_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_2_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_2_category_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_3_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_3_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_3_category_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_4_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_4_element_inputs_[i]] = np.empty([0,1], dtype=np.float32)
				input_mappings[agent_attack_slot_4_category_inputs_[i]] = np.empty([0,1], dtype=np.float32)

			# Field Categorical details
			input_mappings[generations_inputs_] = generations
			input_mappings[gametypes_inputs_] = generations
			input_mappings[tiers_inputs_] = tiers
			input_mappings[weather_inputs_] = weather
			input_mappings[terrain_inputs_] = terrain
			input_mappings[room_inputs_] = room
			input_mappings[pending_actions_a_inputs_] = pending_actions_a
			input_mappings[pending_actions_b_inputs_] = pending_actions_b
			input_mappings[pending_targets_a_inputs_] = pending_targets_a
			input_mappings[pending_targets_b_inputs_] = pending_targets_b
			input_mappings[seen_attacks_a_inputs_] = seen_attacks_a
			input_mappings[seen_attacks_b_inputs_] = seen_attacks_b
			input_mappings[non_category_data_input_] = non_category_data

			# Everything above only happens once
			for obs_data in obs_datas:

				input_mappings[generations_inputs_] = np.append(input_mappings[generations_inputs_], np.array([[obs_data[0]]]), axis=0)
				input_mappings[gametypes_inputs_] = np.append(input_mappings[gametypes_inputs_], np.array([[obs_data[1]]]), axis=0)
				input_mappings[tiers_inputs_] = np.append(input_mappings[tiers_inputs_], np.array([[obs_data[2]]]), axis=0)
				input_mappings[weather_inputs_] = np.append(input_mappings[weather_inputs_], np.array([[obs_data[3]]]), axis=0)
				input_mappings[terrain_inputs_] = np.append(input_mappings[terrain_inputs_], np.array([[obs_data[4]]]), axis=0)
				input_mappings[room_inputs_] = np.append(input_mappings[room_inputs_], np.array([[obs_data[5]]]), axis=0)
				input_mappings[pending_actions_a_inputs_] = np.append(input_mappings[pending_actions_a_inputs_], np.array([[obs_data[6]]]), axis=0)
				input_mappings[pending_actions_b_inputs_] = np.append(input_mappings[pending_actions_b_inputs_], np.array([[obs_data[7]]]), axis=0)
				input_mappings[pending_targets_a_inputs_] = np.append(input_mappings[pending_targets_a_inputs_], np.array([[obs_data[8]]]), axis=0)
				input_mappings[pending_targets_b_inputs_] = np.append(input_mappings[pending_targets_b_inputs_], np.array([[obs_data[9]]]), axis=0)
				input_mappings[seen_attacks_a_inputs_] = np.append(input_mappings[seen_attacks_a_inputs_], np.array([[obs_data[10]]]), axis=0)
				input_mappings[seen_attacks_b_inputs_] = np.append(input_mappings[seen_attacks_b_inputs_], np.array([[obs_data[11]]]), axis=0)

				pokemon_details_index = 12

				#Player Categorical Details
				for i in range(6):
					input_mappings[player_pokemon_name_inputs_[i]] = np.append(input_mappings[player_pokemon_name_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_pokemon_status_inputs_[i]] = np.append(input_mappings[player_pokemon_status_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_pokemon_first_element_inputs_[i]] = np.append(input_mappings[player_pokemon_first_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_pokemon_second_element_inputs_[i]] = np.append(input_mappings[player_pokemon_second_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_pokemon_abilities_inputs_[i]] = np.append(input_mappings[player_pokemon_abilities_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_pokemon_items_inputs_[i]] = np.append(input_mappings[player_pokemon_items_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_pokemon_genders_inputs_[i]] = np.append(input_mappings[player_pokemon_genders_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_1_inputs_[i]] = np.append(input_mappings[player_attack_slot_1_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_1_element_inputs_[i]] = np.append(input_mappings[player_attack_slot_1_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_1_category_inputs_[i]] = np.append(input_mappings[player_attack_slot_1_category_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_2_inputs_[i]] = np.append(input_mappings[player_attack_slot_2_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_2_element_inputs_[i]] = np.append(input_mappings[player_attack_slot_2_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_2_category_inputs_[i]] = np.append(input_mappings[player_attack_slot_2_category_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_3_inputs_[i]] = np.append(input_mappings[player_attack_slot_3_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_3_element_inputs_[i]] = np.append(input_mappings[player_attack_slot_3_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_3_category_inputs_[i]] = np.append(input_mappings[player_attack_slot_3_category_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_4_inputs_[i]] = np.append(input_mappings[player_attack_slot_4_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_4_element_inputs_[i]] = np.append(input_mappings[player_attack_slot_4_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[player_attack_slot_4_category_inputs_[i]] = np.append(input_mappings[player_attack_slot_4_category_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1

				# Agent Categorical Details
				for i in range(6):
					input_mappings[agent_pokemon_name_inputs_[i]] = np.append(input_mappings[agent_pokemon_name_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_pokemon_status_inputs_[i]] = np.append(input_mappings[agent_pokemon_status_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_pokemon_first_element_inputs_[i]] = np.append(input_mappings[agent_pokemon_first_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_pokemon_second_element_inputs_[i]] = np.append(input_mappings[agent_pokemon_second_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_pokemon_abilities_inputs_[i]] = np.append(input_mappings[agent_pokemon_abilities_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_pokemon_items_inputs_[i]] = np.append(input_mappings[agent_pokemon_items_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_pokemon_genders_inputs_[i]] = np.append(input_mappings[agent_pokemon_genders_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_1_inputs_[i]] = np.append(input_mappings[agent_attack_slot_1_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_1_element_inputs_[i]] = np.append(input_mappings[agent_attack_slot_1_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_1_category_inputs_[i]] = np.append(input_mappings[agent_attack_slot_1_category_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_2_inputs_[i]] = np.append(input_mappings[agent_attack_slot_2_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_2_element_inputs_[i]] = np.append(input_mappings[agent_attack_slot_2_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_2_category_inputs_[i]] = np.append(input_mappings[agent_attack_slot_2_category_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_3_inputs_[i]] = np.append(input_mappings[agent_attack_slot_3_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_3_element_inputs_[i]] = np.append(input_mappings[agent_attack_slot_3_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_3_category_inputs_[i]] = np.append(input_mappings[agent_attack_slot_3_category_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_4_inputs_[i]] = np.append(input_mappings[agent_attack_slot_4_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_4_element_inputs_[i]] = np.append(input_mappings[agent_attack_slot_4_element_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1
					input_mappings[agent_attack_slot_4_category_inputs_[i]] = np.append(input_mappings[agent_attack_slot_4_category_inputs_[i]], np.array([[obs_data[pokemon_details_index]]]), axis=0)
					pokemon_details_index += 1

				# rest of data is numeric observation
				input_mappings[non_category_data_input_] = np.append(input_mappings[non_category_data_input_], np.array([obs_data[pokemon_details_index:]]), axis=0)

			return input_mappings

		self.availPi = availPi
		self.split_categories_from_state = split_categories_from_state
		self.text_inputs_ = text_inputs_
		self.available_moves = available_moves
		self.available_targets = available_targets
		self.fc_vf = fc_vf
		self.step = step
		self.value = value
		self.select_action = select_action
		print('this did finish')
