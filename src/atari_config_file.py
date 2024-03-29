import numpy as np
from collections import namedtuple
from atari_primitive_set import primitiveSet
import tensorflow as tf
from tensorflow.core.framework import summary_pb2
import pickle
import os

# Create necessary folders, if they do not exist.
if not os.path.exists("tb/"):
    os.makedirs("tb/")
if not os.path.exists("pickles/"):
    os.makedirs("pickles/")
if not os.path.exists("configs/"):
    os.makedirs("configs/")

def save_result(res):
    # Save result object to file.
    # with open('pickles/best_res_rand%d.pickle' % config.oneplus_params["random_state"], 'wb') as f:
    with open('pickles/best_res_rand0.pickle', 'wb') as f:
        pickle.dump(res, f)

# Stores the best achieved loss so far.
best_loss = np.inf

tb_writer = tf.summary.FileWriter('tb/')
def tb_callback(res):
    # A callback function saving results to TensorBoard.
    print("Loss of the last generation (lower is better): %.3f" % res.fun)
    # val = summary_pb2.Summary.Value(tag="Training loss rand%d" % config.oneplus_params["random_state"], simple_value=res.fun)
    val = summary_pb2.Summary.Value(tag="Training loss rand0", simple_value=res.fun)
    summary = summary_pb2.Summary(value=[val])
    tb_writer.add_summary(summary, tb_callback.cntr)
    tb_callback.cntr += 1
    global best_loss
    if res.fun < best_loss:
        best_loss = res.fun
        save_result(res)
tb_callback.cntr = 0

def loss_fce(rewards):
    """
    Computes loss from 2D array of rewards.
    :param rewards: numpy ndarray of rewards, shape = (episodes, timesteps).
    :return: loss
    """

    # Double the number of timesteps when agent plays well.
    global best_loss
    if best_loss < -14.0:
        config.gym_params['timesteps'] *= 2
        best_loss = np.inf
        print("Timesteps doubled to %d" % config.gym_params['timesteps'])

    # Emphasize opponent's punches.
    rewards = np.where(rewards < 0, rewards * 2, rewards)
    # Sum the rewards and consider the worst episode.
    return -np.min(np.sum(rewards, axis=1))

#######################################
# Here we define a config for training.
#######################################

Config = namedtuple('Config', "cartesian_params oneplus_params gym_params")
config = Config(
    # Parameters defining the CGP graph.
    cartesian_params = {
        'primitive_set': primitiveSet,
        'n_columns': 11,
        'n_rows': 1,
        'n_back': 7, # How far can a node in the matrix look back for its inputs?
        'n_out': 2, # Number of output nodes, we have 18 actions.
    },
    # Parameters defining the optimisation process by one plus lambda.
    # https://cartesian.readthedocs.io/en/latest/_modules/cartesian/algorithm.html#oneplus
    oneplus_params = {
        'lambda_': 4, # Number of offsprings per generation.
        'n_mutations': 3, # Number of mutations per offspring.
        'mutation_method': "active",
        'maxiter': 100, # Maximum number of generations.
        'maxfev': None, # Maximum number of function evaluations, None means infinite.
        'f_tol': -100, # Stopping criterion of loss to detect convergence.
        'n_jobs': 1, # Number of parallel jobs, if we go parallel.
        'random_state': None,
        'seed': None,
        'callback': tb_callback,
    },
    # Parameters defining the openAI gym game.
    gym_params = {
        'game_name': 'CartPole-v0',
        'num_episodes': 10, # Number of episodes (box rounds).
        'timesteps': 1000, # Time steps of one episode (box round).
    }
)