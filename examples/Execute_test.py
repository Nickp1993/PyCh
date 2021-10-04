'''
This model is used to showcase the env.execute function.
'''

from PyCh import *
import math

# =================================
# # Machine definition
# =================================
def M1(env, receiving_channel ):
    while True:
        receiving = receiving_channel.receive()
        x = yield env.execute(receiving)
        print(x)

def M2(env, sending_channel ):
    for j in range(1,100):
        sending = sending_channel.send(j)
        yield env.execute(sending)

# =================================
# # Main
# =================================
env = Environment()
Cs = [Channel(env) for z in range(1,5)]  # a channel for each tier, each sending totes

M1s = [env.process(M1(env, c)) for c in Cs]
M2s = [env.process(M2(env, c)) for c in Cs]

env.run()
print("simulation has ended")
