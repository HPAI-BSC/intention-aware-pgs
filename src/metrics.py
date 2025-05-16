def state_action_similarity(environment, agent, policy, episodes=5):
    observations = []
    for _ in range(episodes):
        obs = environment.reset()
        observations.append(obs)
        done = False

        while not done:
            # We get the action
            action = agent.act(obs)

            obs, _, done, _ = environment.step(action)
            observations.append(obs)

    equal_actions = 0
    for state in observations:
        agent_action = agent.act(state)
        policy_action = policy.act(state)
        equal_actions += 1 if agent_action == policy_action else 0

    return equal_actions / len(observations)
