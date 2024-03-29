import sys
import gym
from cartesian.cgp import *
from cartesian.algorithm import oneplus
import numpy as np
from atari_config_file import config, loss_fce, save_result
from shutil import copyfile

env = gym.make(config.gym_params['game_name']).env
# # env = gym.make('Centipede-v0')
# observation = env.reset()
# # sys.exit()
# action = 1
# observation, reward, done, info = env.step(action)
# while not done:
#     env.render()
#     print(observation[2][0])
#     print(reward)
#     observation, reward, done, info = env.step(action)
#
# sys.exit()

def save_config():
    # copyfile("atari_config_file.py", "configs/best_res_rand%d.py" % config.oneplus_params["random_state"])
    copyfile("atari_config_file.py", "configs/best_res_rand0.py")

def train():
    # Create CGP graph.
    atari_cgp = Cartesian("atari_cgp", **config.cartesian_params)
    # Optimise it!
    res = oneplus(optimisation_fce, cls=atari_cgp, **config.oneplus_params)
    env.close()
    return res

#def optimisation_fce(individual, consts=()):
def optimisation_fce(individual):
    num_episodes = config.gym_params['num_episodes']
    timesteps = config.gym_params['timesteps']
    # Initialise an array where rewards will be stored.
    rewards = np.zeros((num_episodes, timesteps))
    # Get evolved function.
    evolved_fce = compile(individual)
    for episode in range(num_episodes):
        # observation = env.reset() / 255.0
        ep_reward = 0
        env.reset()
        observation = env.render(mode='rgb_array') / 255.0
        # Go through all timesteps.
        for t in range(timesteps):
            # Evaluate evolved function and get 18 values for 18 actions.
            values = evolved_fce(*np.transpose(observation))
            # If any value is matrix, take the average of it.
            values = np.array([np.mean(y) for y in values])
            # Get the index of the highest value, it's our action.
            action = np.argmax(values)
            # Play the action.
            # observation, reward, done, _ = env.step(action)
            obss, reward, done, _ = env.step(action)
            observation = env.render(mode='rgb_array') / 255.0
            # observation = observation / 255.0
            # Save reward to array of rewards.
            rewards[episode, t] = reward
            ep_reward += reward
            if done:
                break
        print(ep_reward)
    return loss_fce(rewards)

if __name__ == '__main__':
    # Set user-defined random state.
    if len(sys.argv) > 1:
        random_state = int(sys.argv[1])
    else:
        random_state = None
    config.oneplus_params["random_state"] = random_state
    # Save config.
    save_config()
    # Train.
    res = train()
    # Save and print the result.
    save_result(res)
    print(res)
