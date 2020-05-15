from gym.envs.registration import register

register(
    id='zb-v0',
    entry_point='gym_zombiediceAI.envs:ZombieDiceENV',
    )


def agent():
    return None