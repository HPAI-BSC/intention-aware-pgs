import numpy as np
from rl.agents.dqn import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import Policy, GreedyQPolicy
from tensorflow.keras.layers import Activation, Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam


def _build_model(nb_actions, obs_space_shape):
    # It privides the neural network model
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + obs_space_shape))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))

    # print(model.summary())
    return model


def load_DQNAgent(path):
    n_actions = 2
    observation_shape = (4, )

    model = _build_model(n_actions, observation_shape)
    memory = SequentialMemory(limit=10000, window_length=1)
    # As it does not have to be trained, always use a greedy policy
    greedy_policy = GreedyQPolicy()
    dqn = DQNAgent(model=model, nb_actions=n_actions, memory=memory, nb_steps_warmup=100,
                   target_model_update=1e-2, policy=greedy_policy)
    dqn.compile(Adam(lr=1e-3), metrics=['mae'])
    dqn.load_weights(path)

    # Alias forward() as act() to be coherent with the API
    dqn.act = dqn.forward

    return dqn