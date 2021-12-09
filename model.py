


"""Operations for clipping (gradient, weight) tensors to min/max values."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
import numpy as np
import os.path as osp
import tensorflow as tf
from baselines import logger

from collections import deque

import cv2

import matplotlib.pyplot as plt

from poke_sim_env import *
import architecture as policies

# Calculate cross entropy
#from baselines.a2c.utils import cat_entropy
from utilities import make_path, find_trainable_variables, discount_with_dones

#from baselines.common.vec_env.dummy_vec_env import DummyVecEnv

from baselines.common import explained_variance
#from baselines.common.runners import AbstractEnvRunner



from stable_baselines.common.runners import AbstractEnvRunner
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines.common.vec_env import DummyVecEnv, VecNormalize

from tensorflow.keras import backend as K

from tensorflow.keras.preprocessing.text import Tokenizer
import tensorflow.keras.preprocessing.sequence as sequence
import poke_sim_env as env




import six

from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import ops
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import gen_array_ops
from tensorflow.python.ops import gen_nn_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.util import deprecation
from tensorflow.python.util import dispatch
from tensorflow.python.util.tf_export import tf_export

SELECTABLE_TARGET_SIZE = 8
NETWORK_MODEL = None

class Model(object):
	"""
	We use this object to:
	__init__:
	- Creates the step_model
	- Creates the train_model

	train():
	- Make the training part (feedforward and retropropagation of gradients)

	save/load():
	- Save load the model
	"""
	def __init__(self, policy, ob_space, action_space, nenvs, nsteps, ent_coef, vf_coef, max_grad_norm):
		sess = tf.get_default_session()
		K.set_session(sess)

		# Create the placeholders
		actions_ = tf.placeholder(tf.int32, [None], name='actions_')
		advantages_ = tf.placeholder(tf.float32, [None], name='advantages_')
		rewards_ = tf.placeholder(tf.float32, [None], name='rewards_')
		lr_ = tf.placeholder(tf.float32, name='learning_rate_')
		# keep track of old actor
		oldneglopac_ = tf.placeholder(tf.float32, [None], name='oldneglopac_')
		# Keep track of old critic
		oldvpred_ = tf.placeholder(tf.float32, [None], name='oldvpred_')
		# Cliprange
		cliprange_ = tf.placeholder(tf.float32, [])

		# Create our two models
		# Step model that is used for sampling
		step_model = policy(sess, ob_space, action_space, nenvs, 1, reuse=False)

		# Test model for testing our agent
		#test_model = policy(sess, ob_space, action_space, 1, 1, reuse=False)

		# Train model for training
		train_model = policy(sess, ob_space, action_space, nenvs*nsteps, nsteps, reuse=True)


		print('availPi', train_model.availPi)
		tf.print(train_model.availPi, [train_model.availPi], 'train_model.availPi')
		l0 = train_model.availPi - tf.reduce_max(train_model.availPi, axis=-1, keep_dims=True)
		el0 = tf.exp(l0)
		z0 = tf.reduce_sum(el0, axis=-1, keep_dims=True)
		p0 = el0 / z0
		entropy = -tf.reduce_sum((p0+1e-8) * tf.log(p0+1e-8), axis=-1)
		oneHotActions = tf.one_hot(actions_, train_model.pi.get_shape().as_list()[-1])
		neglogpac = -tf.log(tf.reduce_sum(tf.multiply(p0, oneHotActions), axis=-1))


		def neglogp(state, valid_ins, valid_tars, actions):
			return sess.run(neglogpac, {network.X: state, network.available_moves: valid_ins, network.available_targets: valid_tars, actions_:actions})

		self.neglogp = neglogp


		# CALCULATE THE LOSS
		# Total loss = Policy gradient loss - entropy * entropy coefficient + Value coefficient * value loss

		# Clip the value
		# Get the value predicted
		value_prediction = train_model.fc_vf

		# Clip the value = Oldvalue + clip(value - oldvalue, min = -cliprange, max = cliprange)
		value_prediction_clipped = oldvpred_ + tf.clip_by_value(train_model.fc_vf - oldvpred_, -cliprange_, cliprange_)

		# Unclipped value
		value_loss_unclipped = tf.square(value_prediction - rewards_)

		# Clipped value
		value_loss_clipped = tf.square(value_prediction_clipped - rewards_)

		# Value loss 0.5 * SUM [max(unclipped, clipped)]
		vf_loss = 0.5 * tf.reduce_mean(tf.maximum(value_loss_unclipped, value_loss_clipped))

		# Clip the policy
		# Output -log(pi) (new - log(pi))

		# Remember we want ratio (pi current policy / pi old policy)
		# But neglogpac returns us -log(policy)
		# So we want to transform it into ratio
		# e^(-log old - (ilog new)) == e^(log new - log old) == e^(log(new / old))
		# = new/old (since expoenential function cancels log)
		# wish we can use latex in comments
		ratio = tf.exp(oldneglopac_ - neglogpac) # ratio = pi new / pi old

		# remember also that we're doing gradient ascent, aka we want to maximize the objective function
		# which Loss = - J
		# To make objective function negative we  put a negation on the multiplcation (pi new/pi old) * - Advantages
		pg_loss_unclipped = -advantages_ * ratio

		# value, min [1-e], max[1+e]
		pg_loss_clipped = -advantages_ * tf.clip_by_value(ratio, 1.0 - cliprange_, 1.0 + cliprange_)

		# Final PG Loss
		# Why maximum because log_loss_unclipped and pg_loss_clipped are negative, gitting the min of positive elements = getting
		# the max of negative elements
		pg_loss = tf.reduce_mean(tf.maximum(pg_loss_unclipped, pg_loss_clipped))

		# Calculate the entropy
		# Entropy is usedto improve exploration by limiting the premature convergence to suboptimal policy.
		entropy_loss = tf.reduce_mean(entropy)

		# Total loss (Remember that L = - J because it's the same thing than max J)
		loss = pg_loss - entropy_loss * ent_coef + vf_loss * vf_coef

		# UPDATE THE PARAMETERS USING LOSS
		# 1. Get the model parameters
		params = find_trainable_variables('model')

		# 2. Calculate the gradients
		grads = tf.gradients(loss, params)
		print('loss', loss)
		print('params', params)
		print('grads', grads)
		if max_grad_norm is not None:
			# Clip the gradients (normalize)
			grads, grad_norm = clip_by_global_norm(grads, max_grad_norm)
		grads = list(zip(grads, params))
		# zip aggregate each gradient with parameters associated
		# For instance zip(ABCD, xyza) => Ax, By, Cz, Da

		# 3. Build our training
		trainer = tf.train.RMSPropOptimizer(learning_rate=lr_, epsilon=1e-5)

		# 4. Backpropagation
		_train = trainer.apply_gradients(grads)

		# Train function
		def train(states_in, valid_ins, valid_targets, text_ins, actions, targets, returns, values, neglogpacs, lr, cliprange):

			for ob_text in text_ins:
#				print('ob_text', ob_text)
				train_model.tokenizer.fit_on_texts([ob_text.decode("utf-8")])

			# preprocess text. maybe do inside of env later?
			ob_text_input = []
			for ob_text in text_ins:
#				print('ob_text utf8', ob_text.decode("utf-8"))
				token = train_model.tokenizer.texts_to_sequences([ob_text.decode("utf-8")])
				token = sequence.pad_sequences(token, maxlen=200)   # pre_padding with 0
				ob_text_input.append(token)
#				print('token', token)
#				print('token shape', token.shape)
			ob_text_input = np.array(ob_text_input)
			shape = ob_text_input.shape
#			print('ob_text_input shape', shape)
			ob_text_input = ob_text_input.reshape(shape[0], shape[2])

			# Here we calculate advantage A(s,a) = R + yV(s') - V(s)
			# Retruns = R + yV(s')
			advantages = returns - values

			#Normalize the advantages (taken from aborghi implementation)
			advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

			td_map = {
						train_model.text_inputs_:ob_text_input,
						train_model.available_moves:valid_ins,
						train_model.available_targets:valid_targets,
						actions_:actions,
						advantages_:advantages, # Use to calculate our policy loss
						rewards_:returns,		# Use as a bootstrap for reward value
						lr_:lr,
						cliprange_:cliprange,
						oldneglopac_:neglogpacs,
						oldvpred_:values}
			td_map.update(train_model.split_categories_from_state(states_in))

#			print('obs shape', states_in)
#			print('text_ins shape', text_ins)
#			print('ob_text_input shape', ob_text_input)
#			print('valid_ins shape', valid_ins)
			policy_loss, value_loss, policy_entropy, _ = sess.run([pg_loss, vf_loss, entropy_loss, _train], td_map)

			return policy_loss, value_loss, policy_entropy

		def save(save_path):
			"""
			Save the model
			"""
			saver = tf.train.Saver()
			saver.save(sess, save_path)

		def load(load_path):
			"""
			Load the model
			"""
			saver = tf.train.Saver()
			print('Loading ' + load_path)
			saver.restore(sess, load_path)

		self.train = train
		self.train_model = train_model
		self.step_model = step_model
		self.step = step_model.step
		self.value = step_model.value
		self.initial_state = step_model.initial_state
		self.save = save
		self.load = load
		tf.global_variables_initializer().run(session=sess)

class Runner2():
	"""
	We use this object to make a mini batch of experiences
	__init__:
	- Initialize the runner

	run():
	- Make a mini batch
	"""
	def __init__(self, env, model, nsteps, total_timesteps, gamma, lam):
		self.env = env
		self.model = model
		self.nenv = nenv = env.num_envs if hasattr(env, 'num_envs') else 1
		self.batch_ob_shape = (nenv*nsteps,) + env.observation_space.shape
		self.obs = np.zeros((nenv, env.observation_space.shape[1]) , dtype=env.observation_space.dtype.name)
		self.opp_obs = np.zeros((nenv, env.observation_space.shape[1]) , dtype=env.observation_space.dtype.name)
		raw_obs = env.reset()
		self.obs[:] =raw_obs
		self.opp_obs[:] =raw_obs
		self.nsteps = nsteps
		self.states = model.initial_state
		self.dones = [False for _ in range(nenv)]
		print(self.obs.shape)

		# Discount rate
		self.gamma = gamma

		# Lambda used in GAE (General Advantage Estimation)
		self.lam = lam

		# Total timesteps taken
		self.total_timesteps = total_timesteps

		# default transcript
		self.transcript = np.full(nenv, 'a')
		self.opp_transcript = np.full(nenv, 'a')

		# default valid moves - maybe default to some negatives for middle actions
		self.valid_moves = np.zeros((nenv, env.action_space.n))
		self.opp_valid_moves = np.zeros((nenv, env.action_space.n))

		# Attempt to avoid turn 1 struggles
		self.valid_moves = np.ones((nenv, env.action_space.n))
		self.valid_moves[:, 14] = 0
		self.valid_moves[:, 8] = 0
		self.opp_valid_moves = np.ones((nenv, env.action_space.n))
		self.opp_valid_moves[:, 14] = 0
		self.opp_valid_moves[:, 8] = 0

		# default valid targets - maybe default to some negatives for middle actions
		self.valid_targets = np.zeros((nenv, env.action_space.n * SELECTABLE_TARGET_SIZE))
		self.opp_valid_targets = np.zeros((nenv, env.action_space.n * SELECTABLE_TARGET_SIZE))



	def run(self):
		# Here, we init the lists that will contain the mv of experiences
		mb_obs, mb_valid_moves, mb_valid_targets, mb_txts, mb_actions, mb_targets, mb_rewards, mb_values, mb_neglopacs, mb_dones = [],[],[],[],[],[],[],[],[],[]

		# For n in range number of steps
		for n in range(self.nsteps):
			# Given observations, get action value and neglopacs
			# We already have self.obs because AbstractEnvRunner run self.obs[:] = env.reset()

			actions, target, values, neglopacs= self.model.step(self.obs, self.valid_moves, self.valid_targets, self.transcript)
#			opp_actions, _, _, _= self.model.step(self.opp_obs, self.opp_valid_moves, self.opp_valid_targets, self.opp_transcript)
#			zipped_actions = zip(actions, opp_actions)

			# Append the observations into the mb
			mb_obs.append(np.copy(self.obs)) # obs len nenvs(1 step per env)

			# Append the text transcript into the mb
			mb_txts.append(np.copy(self.transcript))

			# Append the valid moves into the mb
			mb_valid_moves.append(np.copy(self.valid_moves))

			# Append the valid moves into the mb
			mb_valid_targets.append(np.copy(self.valid_targets))

			# Append the actions taken into the mb
			mb_actions.append(actions)

			# Append the actions taken into the mb
			mb_targets.append(target)

			#Append the values calculated into the mb
			mb_values.append(values)

			# Append the negative log probability into the mb
			mb_neglopacs.append(neglopacs)

			#Append the dones situations into the mb
			mb_dones.append(self.dones)

			# Take actions in env and look the results
			# Infos contains a ton of useful informations: below sonic example
			# {'level_end_bonus': 0, 'rings': 0, 'score': 0, 'zone': 1, 'act': 0, 'screen_x_end': 6591, 'screen_y': 12, 'lives': 3, 'x': 96, 'y': 108, 'screen_x': 0}
			raw_obs, rewards, self.dones, infos = self.env.step(actions)
#			raw_obs, rewards, self.dones, infos = self.env.step(zipped_actions)
			self.obs[:], self.transcript = raw_obs, [info['transcript'] for info in infos]
			self.valid_moves[:] = [info['valid_onehot_player_1'] for info in infos]
			self.valid_targets[:] = [info['valid_onehot_p1_targets'] for info in infos]

			self.opp_transcript = [info['reverse_transcript'] for info in infos]
			self.opp_obs = [info['reversed_combined'] for info in infos]
			self.opp_valid_moves = [info['valid_onehot_player_2'] for info in infos]
			self.opp_valid_targets = [info['valid_onehot_p2_targets'] for info in infos]

#			print('transcript:', [info['transcript'] for info in infos])
#			print('trans2', self.transcript)
#			print('valid moves22',self.valid_moves)

			mb_rewards.append(rewards)

		# batch of steps to batch of rollouts
		mb_obs = np.asarray(mb_obs, dtype=np.float32)
		mb_valid_moves = np.asarray(mb_valid_moves, dtype=np.float32)
		mb_valid_targets = np.asarray(mb_valid_targets, dtype=np.float32)
		mb_rewards = np.asarray(mb_rewards, dtype=np.float32)
		mb_txts = np.asarray(mb_txts, dtype='S')
		mb_actions = np.asarray(mb_actions, dtype=np.int32)
		mb_targets = np.asarray(mb_targets, dtype=np.int32)
		mb_values = np.asarray(mb_values, dtype=np.float32)
		mb_neglopacs = np.asarray(mb_neglopacs, dtype=np.float32)
		mb_dones = np.asarray(mb_dones, dtype=np.bool)
		last_values = self.model.value(self.obs, self.valid_moves, self.valid_targets, self.transcript)

		### GENERALIZED ADVANTAGE ESTIMATION
		# discount/boostrap off value fn
		# We create mb_returns and mb_advantages
		# mb_returns will contain Advantage + value
		mb_returns = np.zeros_like(mb_rewards)
		mb_advantages = np.zeros_like(mb_rewards)

		lastgaelam = 0

		# From last step to first step
		for t in reversed(range(self.nsteps)):
			# IF t == before last step
			if t == self.nsteps - 1:
				#If a state is done, nextnonterminal = 0
				# In fact nextnonterminal allows us to do that logic

				# if done(so nextnonterminal = 0):
				#	delta = R - V(s) (because self.gamma * nextvalues * nextnonterminal = 0)
				# else (note done)
				#	delta = R + gamma * V(st+1)
				nextnonterminal = 1.0 - self.dones
				# V(t+1)
				nextvalues = last_values
			else:
				nextnonterminal = 1.0 - mb_dones[t+1]

				nextvalues = mb_values[t+1]

			# Delta = R(st) + gamma * V(t+1) * nextnonterminal - V(st)
			delta = mb_rewards[t] + self.gamma * nextvalues * nextnonterminal - mb_values[t]

			# Advantage = delta + gamma * lambda * nextnonterminal * lastgaelam
			mb_advantages[t] = lastgaelam = delta + self.gamma * self.lam * nextnonterminal * lastgaelam

		# Returns
		mb_returns = mb_advantages + mb_values

#		return map(sf01_09, (mb_obs, mb_valid_moves, mb_txts, mb_actions, mb_returns, mb_values, mb_neglopacs))
		return map(sf01, (mb_obs, mb_valid_moves, mb_valid_targets, mb_txts, mb_actions, mb_targets, mb_returns, mb_values, mb_neglopacs))


def sf01_09(arr):
	return arr

def sf01(arr):
	""" Swap and then flatten axes 0 and 1"""
	s = arr.shape
	return arr.swapaxes(0, 1).reshape(s[0] * s[1], *s[2:])

def constfn(val):
	def f(_):
		return val
	return f

def learn(policy, env, nsteps, total_timesteps, gamma, lam, vf_coef, ent_coef, lr, cliprange, max_grad_norm, log_interval, envs_for_models=None):
	noptepochs = 4
	nminibatches = 8
	MIN_UPDATES_BEFORE_FIRST_PROMO = 120

	if isinstance(lr, float): lr = constfn(lr)
	else: assert callable(lr)
	if isinstance(cliprange, float): cliprange = constfn(cliprange)
	else: assert callable(cliprange)

	# Get the nb of env
	nenvs = env.num_envs

	# Get state_space and action_space
	ob_space = env.observation_space
	ac_space = env.action_space

	#Calculate the batch size
	batch_size = nenvs * nsteps # For instance if we take 5 steps and we have 5 environments batch_size = 25

	batch_train_size = batch_size // nminibatches

	assert batch_size % nminibatches == 0

	#Instantiate the model object (that creates step_model and train_model)
	model = Model(policy=policy, ob_space=ob_space, action_space=ac_space,nenvs=nenvs, nsteps=nsteps,
		ent_coef=ent_coef,vf_coef=vf_coef,max_grad_norm=max_grad_norm)

	updates = 0
	# Load the model
	# If you want to continue training
	continue_training = False
	if continue_training:
		updates = 90
		load_path = './models/'+str(updates)+'/model.ckpt'
		model.load(load_path)
		updates += 1

	def load_model(model_path):
		#Instantiate the model object (that creates step_model and train_model)
		model_to_load = Model(policy=policy, ob_space=ob_space, action_space=ac_space,nenvs=nenvs, nsteps=nsteps,
			ent_coef=ent_coef,vf_coef=vf_coef,max_grad_norm=max_grad_norm)

		# Load the model
		# If you want to continue training
		load_path = model_path#'./models/410/model.ckpt'
		return model_to_load.load(load_path)

	# Instantiate the runner object
	runner = Runner2(env, model, nsteps=nsteps, total_timesteps=total_timesteps, gamma=gamma, lam=lam)
	# Start total timer
	tfirststart = time.time()

	nupdates = total_timesteps//batch_size+1
	promotion_models = deque(maxlen=5)

	# Begin with random bots
	promotion_models.append(None)
	promotion_models.append(None)
	promotion_models.append(None)
	promotion_models.append(None)
	promotion_models.append(None)

	half_envs = nenvs // 2
	# start envs with nothing.
	env.set_attr('use_network_model', True, indices=range(half_envs, nenvs))
#	if envs_for_models is not None:
#		for env in envs_for_models:
#			env.set_network(model)

	consecutive_wins = 0
	previous_model = None

	for update in range(updates, updates+41):
#	for update in range(updates, nupdates+1):
		# Start timer
		tstart = time.time()

		frac = 1.0 - (update - 1.0) / nupdates

		# Calculate the learning rate
		lrnow = lr(frac)

		# Calculate the cliprange
		cliprangenow = cliprange(frac)

		# Get minibatch
		obs, valid_moves, valid_targets, txts, actions, targets, returns, values, neglogpacs = runner.run()

		# Here what we're going to do is for each minibatch calculate the loss and append it.
		mb_losses = []
		total_batches_train = 0

		# Index of each element of batch_size
		# Create the indices array
		indices = np.arange(batch_size)

		for _ in range(noptepochs):
			# Randomize the indexes
			np.random.shuffle(indices)

			# 0 to batch_size with batch_train_size step
			for start in range(0, batch_size, batch_train_size):
				end = start + batch_train_size
				mbinds = indices[start:end]
				slices = (arr[mbinds] for arr in (obs, valid_moves, valid_targets, txts, actions, targets, returns, values, neglogpacs))
				mb_losses.append(model.train(*slices, lrnow, cliprangenow))

		# Feedforward --> get losses --> update
		lossvalues = np.mean(mb_losses, axis=0)

		# End timer
		tnow = time.time()

		# Calculate the fps (frame per second)
		fps = int(batch_size / (tnow - tstart))

		if update % log_interval == 0 or update == 1:
			"""
			Computes fraction of variance that ypred explains about y.
			Returns 1 - Var[y-ypred] / Var[y]
			interpretation:
			ev=0 => might as well have predicted zero
			ev=1 => perfect prediction
			ev<0 => worse than just predicting zero
			"""
			ev = explained_variance(values, returns)
			print('update:', update)
			logger.record_tabular('serial_timesteps', update*nsteps)
			logger.record_tabular('nupdates', update)
			logger.record_tabular('total_timesteps', update*batch_size)
			logger.record_tabular('fps', fps)
			logger.record_tabular('policy_loss', float(lossvalues[0]))
			logger.record_tabular('policy_entropy', float(lossvalues[2]))
			logger.record_tabular('value_loss', float(lossvalues[1]))
			logger.record_tabular('explained_variance', float(ev))
			logger.record_tabular('time elapsed', float(tnow - tfirststart))

			savepath = './models/' + str(update) + '/model.ckpt'
			model.save(savepath)
			print('Saving to', savepath)

			# Test our agent with 3 trials andmean the score
			# This will be usefule to see if our agent is improving
			test_score = testing(model, previous_model)

			if test_score > 0.1:
				consecutive_wins += 1
			else:
				consecutive_wins = 0

			if consecutive_wins >= 5:
				consecutive_wins = 0
				print('Training Opponent Grew Stronger')
				if False:
					print('fix promo logic')
					promotion_models.append(load_model(savepath))
					# start envs with nothing.
					env.set_attr('computer_network', load_model(savepath), indices=None)
					previous_model = load_model(savepath)

			# skipping for now, too slow
			if False and update > MIN_UPDATES_BEFORE_FIRST_PROMO and consecutive_wins >= 3:
				consecutive_wins = 0
				print('Going for promotion')
				promo_wins = 0
				promo_losses = 0
				for promo_model in promotion_models:
					test_score = testing(model, promo_model)
					if test_score > 0.1:
						promo_wins += 1
					else:
						promo_losses += 1

				print('Promo results %d wins, %d losses' % (promo_wins, promo_losses))
				if promo_wins == 5:
					print('Training Opponent Grew Stronger')
					print('fix promo logic')
					promotion_models.append(load_model(savepath))
					# start envs with nothing.
					env.set_attr('computer_network', load_model(savepath), indices=None)

				else:
					print('Committee has rejected your promotion. Keep training!')


			logger.record_tabular('Mean score test level', test_score)
			logger.dump_tabular()

	"""
	Computes fraction of variance that ypred explains about y.
	Returns 1 - Var[y-ypred] / Var[y]
	interpretation:
	ev=0 => might as well have predicted zero
	ev=1 => perfect prediction
	ev<0 => worse than just predicting zero
	"""
	ev = explained_variance(values, returns)
	print('update:', update)
	logger.record_tabular('serial_timesteps', update*nsteps)
	logger.record_tabular('nupdates', update)
	logger.record_tabular('total_timesteps', update*batch_size)
	logger.record_tabular('fps', fps)
	logger.record_tabular('policy_loss', float(lossvalues[0]))
	logger.record_tabular('policy_entropy', float(lossvalues[2]))
	logger.record_tabular('value_loss', float(lossvalues[1]))
	logger.record_tabular('explained_variance', float(ev))
	logger.record_tabular('time elapsed', float(tnow - tfirststart))

	savepath = './models/' + str(update) + '_final/model.ckpt'
	model.save(savepath)
	print('Saving to', savepath)

	logger.record_tabular('Mean score test level', test_score)
	logger.dump_tabular()


	env.close()

# Avoid error when calculate the mean (in our case if epinfo is empty returns np.nan, not return an error)
def safemean(xs):
	return np.nan if len(xs) == 0 else np.mean(xs)

def testing(model, computer_network=None):
	"""
	We'll use this function to calculate the score on test levels for each saved model,
	to generate the video version to generate the map version
	"""
	test_env = DummyVecEnv([env.make_poke_env()])

	# start envs with nothing.
	test_env.set_attr('computer_network', computer_network, indices=None)

	# Get state_space and action_space
	ob_space = test_env.observation_space
	ac_space = test_env.action_space

	#Play
	total_score = 0
	trial = 0

	# We make 3 trials
	for trial in range(3):
		obs = test_env.reset()[0]
		done = False
		score = 0
		# default transcript
		transcript = 'a'

		# default valid moves
		valid_moves = np.zeros(test_env.action_space.n)
		# Attempt to avoid turn 1 struggles
		valid_moves = np.ones(test_env.action_space.n)
		valid_moves[14] = 0
		valid_moves[8] = 0
		valid_targets = np.zeros(test_env.action_space.n * SELECTABLE_TARGET_SIZE)

		while done == False:
			# Get the action
			action, target, value, _  = model.step(obs, [valid_moves], [valid_targets], [transcript])


			# Take action in env and look at the results
			obs, reward, done, info = test_env.step(action)
			obs = obs[0]
			done = done[0]

			transcript = info[0]['transcript']
			valid_moves = info[0]['valid_onehot_player_1']
			valid_targets = info[0]['valid_onehot_p1_targets']
#			print('combined',obs[:20])
#			print('transcript',transcript)
#			print('valid_moves',valid_moves)
#			print('valid_targets',valid_targets)


#			print('raw action', action)
#			print('combined',repr(obs))
#			print('transcript',transcript)
#			print('valid_moves',repr(valid_moves))
#			print('valid_targets',repr(valid_targets))

			score += reward[0]
		total_score += score
		trial += 1
	test_env.close()

	# Divide the score by the number of trials
	total_test_score = total_score / 3
	return total_test_score

def deep_testing(model):
	"""
	We'll use this function to calculate the score on test levels for each saved model,
	to generate the video version to generate the map version
	"""
	test_env = DummyVecEnv([env.make_poke_env()])

	# Get state_space and action_space
	ob_space = test_env.observation_space
	ac_space = test_env.action_space

	#Play
	total_score = 0
	trial = 0
	results = {'player':0, 'agent':0}
	eps_steps = []

	# We make 3 trials
	for trial in range(1000):
		obs = test_env.reset()[0]
		done = False
		score = 0
		steps = 0
		# default transcript
		transcript = 'a'

		# default valid moves
		valid_moves = np.zeros(test_env.action_space.n)
		valid_targets = np.zeros(test_env.action_space.n * SELECTABLE_TARGET_SIZE)

		while done == False:
			steps += 1
			# Get the action
			action, target, value, _  = model.step(obs, [valid_moves], [valid_targets], [transcript])

			# Take action in env and look at the results
			obs, reward, done, info = test_env.step(action)
			obs = obs[0]
			done = done[0]

			transcript = info[0]['transcript']
			valid_moves = info[0]['valid_onehot_player_1']
			winner = info[0]['winner']
			valid_targets = info[0]['valid_onehot_p1_targets']

			score += reward[0]


		results[winner] += 1
		eps_steps.append(steps)
		total_score += score
		trial += 1
		if trial % 100 == 0:
			print('trail:',trial)
	test_env.close()

	# Divide the score by the number of trials
	total_test_score = total_score / 1000
	return total_test_score, results, eps_steps

def generate_output(policy, test_env):
	"""
	We'll use this function to calculate the score on tests levels for each saved model,
	to generate the video version. to generate the map version
	"""

	# Get state_space and action_space
	ob_space = test_env.observation_space
	ac_space = test_env.action_space

	test_score = []

	# Instantiate the model object (that creates step_model and train_model)
	validation_model = Model(policy=policy, ob_space=ob_space, action_space=ac_space, nenvs=1, nsteps=1,
		ent_coef=0, vf_coef=0, max_grab_norm=0)

	for model_index in models_indexes:
		# Load the model
		load_path = './models/' + str(model_index) + '/model.ckpt'
		validation_model.load(load_path)

		# Play
		score = 0
		timesteps  = 0

		# Play during 5000 timesteps
		while timesteps < 5000:
			timesteps += 1

			# Get the actions
			actions, values, _ = validation_model.step(obs)

			# Take actions in envs and look at the results
			obs, text, dones, infos = test_env.step(actions)

			score += rewards
		# Divide the score by the number of testing environments
		total_score = score / test_env.num_envs

		test_score.append(total_score)
	env.close()

	return test_score

def play(policy, env, update):
	# Get state_space and action_space
	ob_space = env.observation_space
	ac_space = env.action_space

	# Instantiate the model object (that creates step_model and train_model)
	model = Model(policy=policy, ob_space=ob_space, action_space=ac_space, nenvs=1, nsteps=1, ent_coef=0, vf_coef=0, max_grad_norm=0)

	# Load the model
	load_path = './models/' + str(update) + '/model.ckpt'
	print(load_path)

	obs = env.reset()

	# Play
	score = 0
	done = False

	while done == False:
		# Get the action
		actions, values, _ = model.step(obs, text)

		# Take actions in env and look the results
		obs, rewards, done, info = env.step(actions)

		score += rewards

		env.render()

	print('Score ', score)
	env.close()



def clip_by_global_norm(t_list, clip_norm, use_norm=None, name=None):
  """Clips values of multiple tensors by the ratio of the sum of their norms.
  Given a tuple or list of tensors `t_list`, and a clipping ratio `clip_norm`,
  this operation returns a list of clipped tensors `list_clipped`
  and the global norm (`global_norm`) of all tensors in `t_list`. Optionally,
  if you've already computed the global norm for `t_list`, you can specify
  the global norm with `use_norm`.
  To perform the clipping, the values `t_list[i]` are set to:
      t_list[i] * clip_norm / max(global_norm, clip_norm)
  where:
      global_norm = sqrt(sum([l2norm(t)**2 for t in t_list]))
  If `clip_norm > global_norm` then the entries in `t_list` remain as they are,
  otherwise they're all shrunk by the global ratio.
  If `global_norm == infinity` then the entries in `t_list` are all set to `NaN`
  to signal that an error occurred.
  Any of the entries of `t_list` that are of type `None` are ignored.
  This is the correct way to perform gradient clipping (for example, see
  [Pascanu et al., 2012](http://arxiv.org/abs/1211.5063)
  ([pdf](http://arxiv.org/pdf/1211.5063.pdf))).
  However, it is slower than `clip_by_norm()` because all the parameters must be
  ready before the clipping operation can be performed.
  Args:
    t_list: A tuple or list of mixed `Tensors`, `IndexedSlices`, or None.
    clip_norm: A 0-D (scalar) `Tensor` > 0. The clipping ratio.
    use_norm: A 0-D (scalar) `Tensor` of type `float` (optional). The global
      norm to use. If not provided, `global_norm()` is used to compute the norm.
    name: A name for the operation (optional).
  Returns:
    list_clipped: A list of `Tensors` of the same type as `list_t`.
    global_norm: A 0-D (scalar) `Tensor` representing the global norm.
  Raises:
    TypeError: If `t_list` is not a sequence.
  """
  t_list = list(t_list)
  if use_norm is None:
    use_norm = global_norm(t_list, name)

  with ops.name_scope(name, "clip_by_global_norm",
                      t_list + [clip_norm]) as name:
    # Calculate L2-norm, clip elements by ratio of clip_norm to L2-norm
    scale_for_finite = clip_norm * math_ops.minimum(
        1.0 / use_norm,
        constant_op.constant(1.0, dtype=use_norm.dtype) / clip_norm)
    scale = array_ops.where(
        math_ops.is_finite(use_norm),
        scale_for_finite,
        # Return NaN if use_norm is not finite.
        constant_op.constant(float("nan"), dtype=use_norm.dtype))

    values = [
        ops.convert_to_tensor(
            t.values if isinstance(t, ops.IndexedSlices) else t,
            name="t_%d" % i)
        if t is not None else t
        for i, t in enumerate(t_list)]

    values_clipped = []
    for i, v in enumerate(values):
      if v is None:
        values_clipped.append(None)
      else:
        with ops.colocate_with(v):
          values_clipped.append(
              array_ops.identity(v * scale, name="%s_%d" % (name, i)))

    list_clipped = [
        ops.IndexedSlices(c_v, t.indices, t.dense_shape)
        if isinstance(t, ops.IndexedSlices)
        else c_v
        for (c_v, t) in zip(values_clipped, t_list)]

  return list_clipped, use_norm

def global_norm(t_list, name=None):
  """Computes the global norm of multiple tensors.
  Given a tuple or list of tensors `t_list`, this operation returns the
  global norm of the elements in all tensors in `t_list`. The global norm is
  computed as:
  `global_norm = sqrt(sum([l2norm(t)**2 for t in t_list]))`
  Any entries in `t_list` that are of type None are ignored.
  Args:
    t_list: A tuple or list of mixed `Tensors`, `IndexedSlices`, or None.
    name: A name for the operation (optional).
  Returns:
    A 0-D (scalar) `Tensor` of type `float`.
  Raises:
    TypeError: If `t_list` is not a sequence.
  """
  t_list = list(t_list)
  with ops.name_scope(name, "global_norm", t_list) as name:
    values = [
        ops.convert_to_tensor(
            t.values if isinstance(t, ops.IndexedSlices) else t,
            name="t_%d" % i)
        if t is not None else t
        for i, t in enumerate(t_list)]
    half_squared_norms = []
    for v in values:
      if v is not None:
        with ops.colocate_with(v):
          half_squared_norms.append(gen_nn_ops.l2_loss(v))

    half_squared_norm = math_ops.reduce_sum(array_ops.stack(half_squared_norms))

    norm = math_ops.sqrt(
        half_squared_norm *
        constant_op.constant(2.0, dtype=half_squared_norm.dtype),
        name="global_norm")

  return norm



def get_trained_model(policy, env, update):
	# Get state_space and action_space
	ob_space = env.observation_space
	ac_space = env.action_space

	# Instantiate the model object (that creates step_model and train_model)
	model = Model(policy=policy, ob_space=ob_space, action_space=ac_space, nenvs=1, nsteps=1, ent_coef=0.01, vf_coef=0.5, max_grad_norm=0.5)

	# Load the model
	load_path = './models/' + str(update) + '/model.ckpt'
	print(load_path)
	model.load(load_path)

	return model
