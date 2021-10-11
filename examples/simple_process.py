'''
This script is used to showcase a very simple model
'''


from PyCh import *

# =================================
# Machine
# =================================
@process
def PA(env, i):
    yield env.timeout(1)
    print("I am process. %2d.\n", i)


@process
def PB(env, i):
    yield env.timeout(0.5)
    yield env.timeout(0.5)
    print("I am process. %2d.\n", i)

@process
def PC(env, i):
    delay = env.timeout(1.0)
    yield env.timeout(0.5)
    print("I am process. %s. The time is %s" % (i,env.now))
    yield delay
    print("I am process. %s. The time is %s" % (i,env.now))


# =================================
# Model
# =================================
def model():

    env = Environment()
    P1 = PB(env, 1)
    P2 = PA(env, 2)
    P3 = PC(env, 3)
    env.run()

    env.run()
    print("simulation has ended")


# =================================
# Main
# =================================
model()
