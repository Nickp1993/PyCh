'''
This script is used to showcase a very simple model
'''


from PyCh import *

# =================================
# Machine
# =================================
@process
def P(env, i):
    yield env.timeout(1)
    print("I am process. %2d.\n", i)


@process
def P22(env, i):
    yield env.timeout(0.5)
    yield env.timeout(0.5)
    print("I am process. %2d.\n", i)


# =================================
# Model
# =================================
def model():

    env = Environment()
    P1 = P22(env, 1)
    P2 = P(env, 2)
    env.run()

    env.run()
    print("simulation has ended")


# =================================
# Main
# =================================
model()
