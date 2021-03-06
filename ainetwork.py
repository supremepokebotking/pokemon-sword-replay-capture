import tensorflow as tf
import numpy as np
import gym
import math
import os

import model
import architecture as policies
import poke_sim_env as env
from math import inf
from tensorflow.keras import backend as K

class AiNetwork:
    def step(self, combined, valid_moves, valid_targets, transcript):
        action, target, value, _  = self.model.step([combined], [valid_moves], [valid_targets], [transcript])
        print('raw action', action)

        return action

    def __init__(self):
        model_to_use = model.get_trained_model(policy=policies.PPOPolicy, env=env.make_env(), update=40)

        self.model = model_to_use

        combined = [[7, 0, 4, 6, 4, 3, 15, 15, 0, 0, 489, 489, 345, 0, 9, 14, 79, 157, 0, 443, 13, 2, 399, 9, 0, 676, 9, 2, 508, 2, 0, 1076, 0, 9, 18, 79, 157, 0, 140, 13, 2, 487, 9, 1, 29, 9, 0, 74, 2, 0, 641, 0, 2, 18, 79, 157, 0, 724, 13, 2, 559, 13, 0, 655, 2, 1, 345, 2, 2, 424, 0, 4, 13, 79, 157, 0, 559, 13, 0, 528, 13, 0, 475, 11, 1, 745, 4, 1, 1101, 0, 18, 18, 51, 98, 0, 183, 18, 2, 183, 18, 2, 183, 18, 2, 183, 18, 2, 1101, 0, 18, 18, 51, 98, 0, 183, 18, 2, 183, 18, 2, 183, 18, 2, 183, 18, 2, 1102, 0, 18, 18, 79, 157, 0, 323, 18, 2, 323, 18, 2, 323, 18, 2, 323, 18, 2, 1101, 0, 18, 18, 51, 98, 0, 183, 18, 2, 183, 18, 2, 183, 18, 2, 183, 18, 2, 1101, 0, 18, 18, 51, 98, 0, 183, 18, 2, 183, 18, 2, 183, 18, 2, 183, 18, 2, 1101, 0, 18, 18, 51, 98, 0, 183, 18, 2, 183, 18, 2, 183, 18, 2, 183, 18, 2, 1101, 0, 18, 18, 51, 98, 0, 183, 18, 2, 183, 18, 2, 183, 18, 2, 183, 18, 2, 1101, 0, 18, 18, 51, 98, 0, 183, 18, 2, 183, 18, 2, 183, 18, 2, 183, 18, 2, 0, 0, 0, 0, 0, False, False, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.025, 4.536381781890764e-05, 0.0, 1, 0.0, 0.0, 0, 0.1875, 1, 0.0, 0.0, 0, 0.0, 1, 0.0, 0.0, 0, 0.3125, 1, 0.0, 0.0, 0, 0.0, 0.022727272727272728, 0.0006804572672836146, 0.0, 1, 0.0, 0.0, 0, 0.0, 1, 0.0, 0.0, 0, 0.1875, 1, 0.0, 0.0, 0, 0.375, 1, 0.0, 0.0, 0, 0.0, 0.02631578947368421, 0.00403737978588278, 0.0, 1, 0.0, 0.0, 0, 0.25, 1, 0.16666666666666666, 0.0, 0, 0.34375, 0.95, 0.0, 0.0, 0, 0.0, 1, 0.0, 0.0, 0, 0.8, 0.022222222222222223, 0.0027218290691344584, 0.25, 1, 0.16666666666666666, 0.0, 0, 0.25, 1, 0.0, 0.0, 0, 0.125, 1, 0.0, 0.0, 0, 0.25, 1, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 1.0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0.0, 0.0, 0]]

        valid_moves = [np.ones(15)]

        valid_targets = [[  1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1.,
       0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0.,
       0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0.]]
        transcript = ['turn 1']
        action, target, value, _  = model_to_use.step(combined, valid_moves, valid_targets, transcript)
        print('raw action', action)
